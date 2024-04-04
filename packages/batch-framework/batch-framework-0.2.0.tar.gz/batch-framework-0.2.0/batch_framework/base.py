import abc
from typing import Optional, List
from paradag import DAG
from .storage import Storage

__all__ = ['ETL']


class ETL:
    """
    Basic Interface for defining a unit of ETL flow.
    """

    def __init__(self, input_storage: Optional[Storage] = None,
                 output_storage: Optional[Storage] = None, make_cache: bool = False):
        assert isinstance(
            self.input_ids, list), f'property input_ids is not a list of string but {type(self.input_ids)} on {self}'
        assert isinstance(
            self.output_ids, list), f'property output_ids is not a list of string but {type(self.output_ids)} on {self}'
        assert len(set(self.input_ids) & set(self.output_ids)
                   ) == 0, 'There should not be an object_id on both input_ids and output_ids'
        assert len(self.input_ids) == len(set(self.input_ids)
                                          ), 'There should no be repeated id in self.input_ids'
        assert len(self.output_ids) == len(set(self.output_ids)
                                           ), 'There should no be repeated id in self.output_ids'
        assert all([id in self.input_ids for id in self.external_input_ids]
                   ), 'external input ids should be defined in input ids'
        self._input_storage = input_storage
        self._output_storage = output_storage
        self._make_cache = make_cache

    def __repr__(self):
        class_name = '-'.join([self.__module__.replace('.',
                              '-'), self.__class__.__name__])
        repr = class_name
        if len(self.input_ids) > 0:
            inputs = '-'.join(self.input_ids)
            repr += f'-in-{inputs}'
        if len(self.output_ids) > 0:
            outputs = '-'.join(self.output_ids)
            repr += f'-out-{outputs}'
        return repr

    @abc.abstractproperty
    def input_ids(self) -> List[str]:
        """
        Returns:
            List[str]: a list of input object ids
        """
        raise NotImplementedError

    @abc.abstractproperty
    def output_ids(self) -> List[str]:
        """
        Returns:
            List[str]: a list of output object ids
        """
        raise NotImplementedError

    @property
    def external_input_ids(self) -> List[str]:
        """
        Returns:
            List[str]: a list of input object ids passed from external scope
        """
        return []

    def execute(self, **kwargs):
        self.start(**kwargs)
        self._execute(**kwargs)
        self._end(**kwargs)

    def start(self, **kwargs) -> None:
        """Define some action before execute start
        e.g., creating output table if not exists
        """
        pass

    def _end(self, **kwargs) -> None:
        self.end(**kwargs)
        if self._make_cache:
            self._save_cache()

    @property
    def exists_cache(self) -> bool:
        assert self._make_cache, 'cannot check cache existence when make_cache=False'
        for id in self.input_ids:
            if self._input_storage is None:
                return False
            elif not self._input_storage.check_exists(id + '_cache'):
                print(f'{id}_cache does not exists')
                return False
        for id in self.output_ids:
            if self._output_storage is None:
                return False
            elif not self._output_storage.check_exists(id + '_cache'):
                print(f'{id}_cache does not exists')
                return False
        return True

    def _save_cache(self):
        assert self._make_cache, 'cannot save cache when make_cache=False'
        for id in self.input_ids:
            self._input_storage.copy(
                id,
                id + '_cache'
            )
            print(id + '_cache', 'copied')
        for id in self.output_ids:
            self._output_storage.copy(
                id,
                id + '_cache'
            )
            print(id + '_cache', 'copied')

    def load_cache(self, id: str):
        assert self._make_cache, 'cannot load cache when make_cache=False'
        if id in self.input_ids:
            assert self._input_storage is not None, 'input_storage cannot be None for load_cache'
            return self._input_storage.download(id + '_cache')
        elif id in self.output_ids:
            assert self._output_storage is not None, 'input_storage cannot be None for load_cache'
            return self._output_storage.download(id + '_cache')
        else:
            raise ValueError(
                'id to be loaded in load_cache should be in self.input_ids or self.output_ids')

    def end(self, **kwargs) -> None:
        """Define some action after execute end
        e.g., validate the ouput data
        """
        pass

    @abc.abstractmethod
    def _execute(self, **kwargs):
        """Execute ETL
        """
        raise NotImplementedError

    def build(self, dag: DAG):
        """Connecting input_ids, output_ids and execution method
        as nodes into dag.
        """
        try:
            # Step0: add external_ids to dag
            for id in self.external_input_ids:
                dag.add_vertex(id)
            # Step1: add execute to dag
            dag.add_vertex(self)
            # Step2: connect input_id to execute
            for input_id in self.input_ids:
                dag.add_edge(input_id, self)
            # Step3: add all output_ids into dag
            for output_id in self.output_ids:
                dag.add_vertex(output_id)
            # Step4: connect execute to ouput_id
            for output_id in self.output_ids:
                dag.add_edge(self, output_id)
        except BaseException as e:
            raise ValueError(f'Dag Build Error on {self}') from e

    def drop(self, id: str):
        assert id in self.input_ids or id in self.output_ids, f'id {id} is not in input_ids or output_ids'
        if id in self.input_ids:
            if self._input_storage is not None:
                if self._input_storage.check_exists(id):
                    self._input_storage.drop(id)
        else:
            if self._output_storage is not None:
                if self._output_storage.check_exists(id):
                    self._output_storage.drop(id)
