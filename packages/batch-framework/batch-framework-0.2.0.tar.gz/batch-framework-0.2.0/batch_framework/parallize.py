"""
Divide and conquer module
"""
from typing import List
from typing_extensions import TypeAlias
import vaex as vx
import pandas as pd
import pyarrow as pa
from dill.source import getsource
from batch_framework.etl import ETL, ObjProcessor, ETLGroup, SQLExecutor
from batch_framework.storage import Storage, VaexStorage, PandasStorage, PyArrowStorage
from batch_framework.filesystem import FileSystem
from batch_framework.rdb import DuckDBBackend

__all__ = ['MapReduce']


class MapReduce(ETLGroup):
    """
    Decorating an ETL object into MapReduced version
    """

    def __init__(self, map: ObjProcessor, parallel_count: int,
                 tmp_fs: FileSystem, has_external_input: bool = False):
        assert isinstance(
            map, ObjProcessor), f'map object {map} passing to MapReduce should be ObjProcessor'
        self._map = map
        map_name = str(map)
        self._map_name = map_name
        self._tmp_fs = tmp_fs
        self._parallel_count = parallel_count
        self._has_external_input = has_external_input
        InputAlias: TypeAlias = self._map.get_input_type()  # type: ignore[valid-type]
        OutputAlias: TypeAlias = self._map.get_output_type()  # type: ignore[valid-type]

        class MapClass(ObjProcessor):
            def __init__(self, input_storage: Storage, partition_id: int):
                self._partition_id = partition_id
                super().__init__(input_storage)

            def __repr__(self):
                return f'{map_name}.MapClass.{self._partition_id}'

            @property
            def input_ids(self):
                return [
                    f'{map_name}_{id}_{self._partition_id}' for id in map.input_ids]

            @property
            def output_ids(self):
                return [
                    f'{map_name}_{id}_{self._partition_id}' for id in map.output_ids]

            def transform(
                    self, inputs: List[InputAlias], **kwargs) -> List[OutputAlias]:
                try:
                    assert len(inputs) == len(
                        map.input_ids), f'inputs of transform does not equals input id count. inputs: {inputs}; input_ids: {self.input_ids}'
                    return map.transform(inputs, **kwargs)
                except BaseException:
                    content = getsource(map.transform)
                    raise ValueError(
                        f'Error happened on {self._partition_id}th MapClass execution - transform of {map}:\n{content}')

            def start(self, **kwargs):
                return map.start(**kwargs)

        assert self._map._input_storage is not None, f'input_storage of ObjProcessor `{self._map}` send to MapReduce should not be None'
        mappers = [MapClass(type(self._map._input_storage)(tmp_fs), i)
                   for i in range(parallel_count)]
        self._mappers = mappers
        self._partition_preprocessor = AddPartitionKey(
            map_name,
            self._map.input_ids,
            self._map._input_storage._backend,
            tmp_fs,
            parallel_count)
        units: List[ETL] = []
        units.append(self._partition_preprocessor)
        for id in self._map.input_ids:
            units.append(
                EfficientDivide(
                    map_name,
                    id,
                    parallel_count,
                    tmp_fs,
                    tmp_fs))
        units.extend(self._mappers)
        assert self._map._output_storage is not None, f'output_storage of ObjProcessor `{self._map}` send to MapReduce should not be None'
        for id in self._map.output_ids:
            units.append(
                VaexMerge(
                    id,
                    parallel_count,
                    tmp_fs,
                    self._map._output_storage._backend,
                    map_name=map_name
                )
            )
        super().__init__(*units)

    @property
    def external_input_ids(self) -> List[str]:
        if self._has_external_input:
            return self.input_ids
        else:
            return []

    @property
    def input_ids(self):
        return self._map.input_ids

    @property
    def output_ids(self):
        return self._map.output_ids


class AddPartitionKey(SQLExecutor):
    """Adding Automic Partition Key before Dividing Input Tables"""

    def __init__(self,
                 map_name: str,
                 obj_ids: List[str],
                 input_fs: FileSystem,
                 output_fs: FileSystem,
                 divide_count: int
                 ):
        self._map_name = map_name
        self._obj_ids = obj_ids
        self._divide_count = divide_count
        super().__init__(rdb=DuckDBBackend(), input_fs=input_fs, output_fs=output_fs)

    def __repr__(self):
        return f'{self._map_name}.AddPartitionKey'

    @property
    def input_ids(self):
        return self._obj_ids

    @property
    def output_ids(self):
        return [f'{self._map_name}_{id}_full' for id in self._obj_ids]

    def sqls(self, **kwargs):
        results = dict()
        for in_id, out_id in zip(self.input_ids, self.output_ids):
            results[out_id] = f"""
            WITH row_table AS (
                SELECT
                    *,
                    (row_number() OVER ()) AS row_id
                FROM {in_id}
            )
            SELECT
                *,
                row_id % {self._divide_count} AS partition
            FROM row_table
            """
        return results


class EfficientDivide(ObjProcessor):
    """Divide Table for MapReduce"""

    def __init__(self,
                 map_name: str,
                 obj_id: str,
                 divide_count: int,
                 input_fs: FileSystem,
                 output_fs: FileSystem
                 ):
        self._map_name = map_name
        self._obj_id = obj_id
        self._divide_count = divide_count
        super().__init__(VaexStorage(input_fs), VaexStorage(output_fs))

    def __repr__(self):
        return f'{self._map_name}.Divide'

    @property
    def input_ids(self):
        return [f'{self._map_name}_{self._obj_id}_full']

    @property
    def output_ids(self):
        return [f'{self._map_name}_{self._obj_id}_{i}' for i in range(
            self._divide_count)]

    def transform(self, inputs: List[vx.DataFrame],
                  **kwargs) -> List[vx.DataFrame]:
        table = inputs[0]
        columns = table.get_column_names()
        columns.remove('partition')
        columns.remove('row_id')
        results = []
        for i, df in table.groupby('partition'):
            size = len(df)
            assert size > 0, 'output dataframes of EfficientDivide should not be 0 size.'
            results.append(df[columns])
            print(f'[transform] i: {i} - size: {size}')
        assert len(
            results) == self._divide_count, f'# of results {len(results)} does not equal self._divide_count: {self._divide_count}'
        return results
# PyArrowStorage


class DataFrameMerge(ObjProcessor):
    def __init__(self, storage_cls, obj_id: str, divide_count: int,
                 input_fs: FileSystem, output_fs: FileSystem, map_name: str = ''):
        self._obj_id = obj_id
        self._divide_count = divide_count
        self._map_name = map_name
        super().__init__(storage_cls(input_fs), storage_cls(output_fs))

    def __repr__(self):
        return f'{self._map_name}.Merge'

    @property
    def input_ids(self):
        return [f'{self._map_name}_{self._obj_id}_{i}' for i in range(
            self._divide_count)]

    @property
    def output_ids(self):
        return [self._obj_id]


class PyArrowMerge(DataFrameMerge):
    def __init__(self, obj_id: str, divide_count: int,
                 input_fs: FileSystem, output_fs: FileSystem, map_name: str = ''):
        super().__init__(
            PyArrowStorage,
            obj_id,
            divide_count,
            input_fs,
            output_fs,
            map_name=map_name)

    def transform(self, inputs: List[pa.Table], **kwargs) -> List[pa.Table]:
        return [pa.concat_tables(inputs)]


class PandasMerge(DataFrameMerge):
    def __init__(self, obj_id: str, divide_count: int,
                 input_fs: FileSystem, output_fs: FileSystem, map_name: str = ''):
        super().__init__(
            PandasStorage,
            obj_id,
            divide_count,
            input_fs,
            output_fs,
            map_name=map_name)

    def transform(self, inputs: List[pd.DataFrame],
                  **kwargs) -> List[pd.DataFrame]:
        return [pd.concat(inputs)]


class VaexMerge(DataFrameMerge):
    def __init__(self, obj_id: str, divide_count: int,
                 input_fs: FileSystem, output_fs: FileSystem, map_name: str = ''):
        super().__init__(
            VaexStorage,
            obj_id,
            divide_count,
            input_fs,
            output_fs,
            map_name=map_name)

    def transform(self, inputs: List[vx.DataFrame],
                  **kwargs) -> List[vx.DataFrame]:
        return [vx.concat(inputs)]


class EfficientMerge(SQLExecutor):
    def __init__(self, obj_id: str, divide_count: int,
                 input_fs: FileSystem, output_fs: FileSystem, map_name: str = ''):
        self._obj_id = obj_id
        self._divide_count = divide_count
        self._map_name = map_name
        super().__init__(DuckDBBackend(), input_fs, output_fs)

    def __repr__(self):
        return super().__repr__().replace(
            'SQLExecutor', 'EfficientMerge') + '-' + self._map_name

    @property
    def input_ids(self):
        return [f'{self._map_name}_{self._obj_id}_{i}' for i in range(
            self._divide_count)]

    @property
    def output_ids(self):
        return [self._obj_id]

    def sqls(self, **kwargs):
        sql = '\nUNION ALL\n'.join(
            [f"SELECT * FROM {id}" for id in self.input_ids])
        return {
            self._obj_id: sql
        }
