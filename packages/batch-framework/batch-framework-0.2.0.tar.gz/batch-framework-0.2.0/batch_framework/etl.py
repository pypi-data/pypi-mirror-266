"""
ETL Class
TODO:
- [X] Split SQL executor and Processor
- [X] Rename DFProcessor as Object Processor
- [ ] Add multi-threading to SQLExecutor
"""
from typing_extensions import TypeAlias
from paradag import dag_run, DAG
from paradag import MultiThreadProcessor, SequentialProcessor
from typing import List, Dict, Optional, Any
import abc
from threading import Semaphore
from .base import ETL
from .storage import Storage, PyArrowStorage
from .filesystem import FileSystem
from .rdb import RDB
from .executor import DagExecutor

__all__ = [
    'ObjProcessor',
    'SQLExecutor',
    'ETLGroup'
]


class ETLGroup(ETL):
    """Interface for connecting multiple ETL units
    """

    def __init__(self, *etl_units: ETL):
        self.etl_units = etl_units

    def execute(self, **kwargs):
        self._execute(**kwargs)

    def _execute(self, **kwargs):
        """Execute ETL units
        """
        dag = DAG()
        self.build(dag)
        if 'sequential' in kwargs and kwargs['sequential']:
            dag_run(dag, processor=SequentialProcessor(),
                    executor=DagExecutor()
                    )
        elif 'max_active_run' in kwargs:
            limit_pool = Semaphore(value=kwargs['max_active_run'])
            dag_run(dag, processor=MultiThreadProcessor(),
                    executor=DagExecutor(limit_pool=limit_pool)
                    )
        else:
            dag_run(dag, processor=MultiThreadProcessor(),
                    executor=DagExecutor()
                    )

    def build(self, dag: DAG):
        # Step0: add external_ids to dag
        for id in self.external_input_ids:
            dag.add_vertex(id)
        # Step1: connecting dag with all etl units
        for etl_unit in self.etl_units:
            etl_unit.build(dag)
        # Step2: make sure all output ids are already in the dag
        for _id in self.output_ids:
            assert _id in dag.vertices(
            ), f'output_id {_id} is not in dag input vertices'
        # Step3: Add start and end to dag
        dag.add_vertex(self.start)
        dag.add_vertex(self._end)
        # Step4: Connect end to all output_ids
        for id in self.input_ids:
            dag.add_edge(self.start, id)
        # Step5: connect execute to ouput_id
        for id in self.output_ids:
            dag.add_edge(id, self._end)

    @property
    def internal_ids(self) -> Dict[str, ETL]:
        """
        Get internal inputs ids and its located ETL units
        """
        results = dict()
        for etl_unit in self.etl_units:
            for id in etl_unit.input_ids:
                results[id] = etl_unit
            for id in etl_unit.output_ids:
                results[id] = etl_unit
        for id in self.input_ids:
            del results[id]
        for id in self.output_ids:
            del results[id]
        return results

    def drop_internal_objs(self):
        for id, etl_unit in self.internal_ids.items():
            if isinstance(etl_unit, ETLGroup):
                etl_unit.drop_internal_objs()
            else:
                etl_unit.drop(id)

    def _end(self):
        self.end()
        self.drop_internal_objs()


class SQLExecutor(ETL):
    """Basic interface for SQL executor
    """

    def __init__(
            self, rdb: RDB, input_fs: Optional[FileSystem] = None, output_fs: Optional[FileSystem] = None, make_cache: bool = False):
        assert isinstance(rdb, RDB), 'rdb is not RDB type'
        self._rdb = rdb
        if input_fs is not None:
            assert isinstance(
                input_fs, FileSystem), 'input_storage of SQLExecutor should be FileSystem'
            input_storage = PyArrowStorage(input_fs)
        else:
            input_storage = None
        if output_fs is not None:
            assert isinstance(
                output_fs, FileSystem), 'output_storage of SQLExecutor should be FileSystem'
            output_storage = PyArrowStorage(output_fs)
        else:
            output_storage = None

        if make_cache:
            assert input_storage is not None and output_storage is not None, 'In SQLExecutor, cache mechanism only support when input/output file system (input/output_fs) provided.'

        assert all(['.' not in id for id in self.input_ids]
                   ), f'using . in SQLExecutor input id is not allowed. See: {self.input_ids}'
        assert all(['.' not in id for id in self.output_ids]
                   ), f'using . in SQLExecutor output id is not allowed. See: {self.output_ids}'
        for id in self.output_ids:
            assert id in self.sqls(
            ), f'output_id {id} does not have corresponding sql'
        for key in self.sqls():
            assert key in self.output_ids, f'sql of field {key} does not have corresponding output_id'
        super().__init__(input_storage, output_storage, make_cache=make_cache)

    @abc.abstractmethod
    def sqls(self, **kwargs) -> Dict[str, str]:
        """Select SQL for transforming the input tables.

        Args:
            **kwargs: some additional variable passed from scheduling engine (e.g., Airflow)

        Returns:
            Dict[str, str]: The transformation SQLs. The key
            is the output_id to be insert into. The value is
            the corresponding SQL.
        """
        raise NotImplementedError

    def _execute(self, **kwargs):
        """
        Args:
            **kwargs: some additional variable passed from scheduling engine (e.g., Airflow)
        """
        assert set(self.sqls(**kwargs).keys()) == set(
            self.output_ids), 'sqls key should corresponds to the output_ids'
        # Extract Table and Load into RDB from FileSystem
        cursor = self._rdb.get_conn()
        try:
            if self._input_storage is not None:
                for id in self.input_ids:
                    if self._input_storage.check_exists(id):
                        print(f'@{self} Start Registering Input: {id}')
                        cursor.register(id, self._input_storage.download(id))
                        print(f'@{self} End Registering Input: {id}')
                    else:
                        raise ValueError(f'{id} does not exists')
            if self._output_storage is not None:
                for output_id, sql in self.sqls(**kwargs).items():
                    print(f'@{self} Start Uploading Output: {output_id}')
                    table = cursor.execute(f'SELECT * FROM ({sql})').arrow()
                    self._output_storage.upload(table, output_id)
                    print(f'@{self} End Uploading Output: {output_id}')
            else:
                for output_id, sql in self.sqls(**kwargs).items():
                    cursor.execute(f'''
                    CREATE TABLE {output_id} AS ({sql});
                    ''')

        finally:
            cursor.close()


class ObjProcessor(ETL):
    """
    Basic Interface for defining an object processing unit of ETL flow.
    """

    def __init__(self, input_storage: Storage,
                 output_storage: Optional[Storage] = None, make_cache: bool = False):
        input_storage = input_storage
        if output_storage is None:
            output_storage = input_storage
        assert isinstance(
            input_storage, Storage), f'input_storage should be Storage rather than: {type(self._input_storage)}'
        assert isinstance(
            output_storage, Storage), f'output_storage should be Storage rather than: {type(self._output_storage)}'
        assert self.get_input_type() == input_storage.get_download_type(
        ), f'storage download type: {input_storage.get_download_type()} != transform input type: {self.get_input_type()}'
        assert self.get_output_type() == output_storage.get_upload_type(
        ), f'storage upload type: {output_storage.get_upload_type()} != transform output type: {self.get_output_type()}'
        super().__init__(input_storage, output_storage, make_cache=make_cache)

    @abc.abstractmethod
    def transform(self, inputs: List[Any], **kwargs) -> List[Any]:
        """
        Args:
            Inputs: List of object to be load from storage.
        Returns:
            List[object]: List of object to be saved to storage.
        """
        raise NotImplementedError

    def _execute(self, **kwargs):
        """
        Args:
            **kwargs: some additional variable passed from scheduling engine (e.g., Airflow)
        Run ETL (extract, transform, and load)
        """
        # Extraction Step
        if len(self.input_ids):
            input_objs = self._extract_inputs()
            assert all([isinstance(obj, self.get_input_type()) for obj in input_objs]
                       ), f'One of the input_obj {input_objs} is not {self.get_input_type()}'
        else:
            input_objs = []
        # Transformation Step
        output_objs = self.transform(input_objs, **kwargs)
        # Output Validation
        assert isinstance(
            output_objs, list), 'Output of transform should be a list of object'
        assert all([isinstance(obj, self.get_output_type()) for obj in output_objs]
                   ), f'One of the output_obj {output_objs} is not {self.get_output_type()}'
        # Load Step
        self._load(output_objs)

    def get_input_type(self) -> TypeAlias:
        return self.transform.__annotations__['inputs'].__args__[0]

    def get_output_type(self) -> TypeAlias:
        return self.transform.__annotations__['return'].__args__[0]

    def _extract_inputs(self) -> List[object]:
        """
        Returns:
            List[object]: List of dataframe object to be passed to `transform`.
        """
        assert self._input_storage is not None, 'input_storage should not be None when executing _extract_inputs'
        input_tables = []
        for id in self.input_ids:
            print(f'@{self} Start Extracting Input: {id}')
            table = self._input_storage.download(id)
            input_tables.append(table)
            print(f'@{self} End Extracting Input: {id}')
        return input_tables

    def _load(self, output_tables: List[object]):
        """
        Args:
            output_tables: List[object]: List of dataframe object passed from `transform`.
        """
        assert self._output_storage is not None, 'output_storage should not be None when executing _load'
        for id, table in zip(self.output_ids, output_tables):
            print(f'@{self} Start Loading Output: {id}')
            self._output_storage.upload(table, id)
            print(f'@{self} End Loading Output: {id}')
