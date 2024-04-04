from typing import Optional
from threading import Semaphore
import traceback
from .base import ETL

__all__ = ['DagExecutor']


class DagExecutor:
    """Executing Unit for Tasks in the Dag"""

    def __init__(self, limit_pool: Optional[Semaphore] = None):
        self._limit_pool = limit_pool

    def param(self, vertex):
        return vertex

    def execute(self, param):
        if self._limit_pool is not None:
            self._limit_pool.acquire()
        try:
            DagExecutor.execute_vertex(param)
        except Exception as e:
            content = traceback.format_exc()
            raise ValueError(
                f'something wrong on {param}: \n{content}') from e
        finally:
            if self._limit_pool is not None:
                self._limit_pool.release()

    @staticmethod
    def execute_vertex(param):
        if isinstance(param, str):
            print(f'@Passing Object: {param}')
        elif isinstance(param, ETL):
            print(
                '@Start:',
                type(param),
                'inputs:',
                param.input_ids,
                'outputs:',
                param.output_ids)
            param.execute()
            print(
                '@End:',
                type(param),
                'inputs:',
                param.input_ids,
                'outputs:',
                param.output_ids)
        elif callable(param):
            print('@Start:', param, 'of', type(param))
            param()
            print('@End:', param, 'of', type(param))
        else:
            raise ValueError(
                f'param of DagExecutor should be str, ETL, or callable, but it is: {type(param)}')
