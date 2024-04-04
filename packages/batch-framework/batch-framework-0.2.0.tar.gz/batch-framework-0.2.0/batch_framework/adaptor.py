from typing import List, Dict, Any
import yaml
from paradag import dag_run
from paradag import SequentialProcessor
from paradag import DAG
from .etl import ETLGroup
from .executor import DagExecutor

__all__ = ['GithubActionAdaptor']


class GithubActionAdaptor:
    def __init__(self, etl_group: ETLGroup):
        dag = DAG()
        etl_group.build(dag=dag)
        self._dag = dag
        self.vertices = sorted(
            dag_run(
                self._dag,
                processor=SequentialProcessor()),
            key=str)
        self._check_repeatness(self.vertices)
        self._id2obj_map = self._build_id2obj_mapping(dag)

    def create_yml(self, job_yml_path='./.github/workflows/job.yml',
                   template_yml_path='./.github/workflow/template.yml', target_yml_path='./.github/workflows/etl.yml'):
        jobs_config = self._get_jobs_config(job_yml_path)
        with open(template_yml_path, 'r') as f:
            result = yaml.safe_load(f)
            print('template:\n', result)
        result.update(jobs_config)
        with open(target_yml_path, 'w') as file:
            yaml.safe_dump(result, file)
            print(target_yml_path, 'generated')

    def run_by_id(self, id: str):
        param = self._id2obj_map[id]
        DagExecutor.execute_vertex(param)

    def _check_repeatness(self, vertices: List[Any]):
        task_ids = list(map(str, vertices))
        assert len(task_ids) == len(
            set(task_ids)), f'Please avoid repeat task ids: {GithubActionAdaptor.get_repeat_items(task_ids)}'

    @staticmethod
    def get_repeat_items(items: List[Any]) -> Dict[Any, int]:
        results = dict()
        for item in items:
            cnt = items.count(item)
            if cnt > 1:
                results[item] = cnt
        return results

    def _build_id2obj_mapping(self, dag: DAG) -> Dict[str, object]:
        results = dict()
        for vertex in dag.vertices():
            id = self.obj2id(vertex)
            results[id] = vertex
        return results

    def obj2id(self, vertex: object) -> str:
        return 'id_' + str(self.vertices.index(vertex))

    def _get_jobs_config(self, job_yml_path) -> Dict[str, Any]:
        results = dict()
        for vertex in self.vertices:
            results.update(self._get_job_block(vertex, job_yml_path))
        return {'jobs': results}

    def _get_job_block(self, param, job_yml_path):
        needs = self._dag.predecessors(param)
        needs = [self.obj2id(obj) for obj in needs]
        id = self.obj2id(param)
        if isinstance(param, str):
            job_value = {
                'runs-on': 'ubuntu-latest',
                'steps': [
                    {
                        'name': param,
                        'run': f'echo {param}'
                    }
                ]
            }
        else:
            job_value = {
                'uses': job_yml_path,
                'with': {
                    'task-id': id,
                    'task-name': str(param)
                },
                'secrets': 'inherit'
            }
        job_value['name'] = str(param)
        job_value['needs'] = needs
        return {id: job_value}
