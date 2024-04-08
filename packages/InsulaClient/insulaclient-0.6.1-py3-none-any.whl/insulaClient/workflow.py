from snakenest import Poisoned
from .InsulaApiConfig import InsulaApiConfig
from .workflow_step import InsulaWorkflowStep
from .job_status import InsulaJobStatus
from .files_job_result import InsulaFilesJobResult
from .workflow_step_runner import InsulaWorkflowStepRunner
from .results_manager import ResultsManager
from .workflow_manager import WorkflowManager


class InsulaWorkflow(object):
    @Poisoned(workflow_manager='native_workflow_manager', result_manager='memory_results_manager')
    def __init__(self, insula_config: InsulaApiConfig, workflow: str, parameters: dict, external_name,
                 workflow_manager: WorkflowManager, result_manager: ResultsManager):

        self.__workflow_data = workflow_manager.parse(workflow, parameters)
        self.__result_manager = result_manager

        self.__external_name = external_name
        self.__insula_api_config = insula_config
        self.__steps_order = []
        self.__get_workflow_info()
        self.__validate_version()
        self.__get_workflow_steps_order()
        self.__init_job_requirements()
        self.__check_parameters(parameters)

    # TODO: remove from here and move in WorkflowDataManager
    def __check_parameters(self, parameters):
        for key, value in self.__workflow_data.parameters.items():
            if isinstance(value, str):
                pass
            elif isinstance(value, list):
                for v in value:
                    if not isinstance(v, str):
                        raise Exception(f'Parameter {key} format type not supported')
            else:
                raise Exception(f'Parameter {key} format type not supported')

    def __get_workflow_info(self):
        self.__name = self.__workflow_data.name
        self.__type = self.__workflow_data.type

        if self.__external_name:
            self.__name = self.__external_name

    def __validate_version(self):
        self.__version = self.__workflow_data.version

        if not self.__version:
            print('This workflow requires insulaClient version 0.0.1')
            exit(1)

        if self.__version != 'beta/1':
            print('Version not compatible with beta/1')
            exit(1)

    def __get_workflow_steps_order(self):
        for step in self.__workflow_data.steps:
            self.__steps_order.append(InsulaWorkflowStep(step))

    def __init_job_requirements(self):
        for job in self.__workflow_data.requirements['jobs']:
            name = job['name']
            job_id = job['id']
            # TODO: the step_resoult should be a class
            run = {
                'name': name,
                'service_id': 0,
                'status': {
                    "config_id": 0,
                    "job_id": job_id,
                    "status": "REQUIREMENTS_RETRIEVED"
                },
                'results':
                    InsulaFilesJobResult(self.__insula_api_config).get_result_from_job(job_id)
            }

            self.__result_manager.add_result_step(self.__workflow_data.identifier, run)

    def __filter_log_properties(self):
        to_save = {
            'steps': self.__result_manager.get_result_steps(self.__workflow_data.identifier)
        }
        return to_save

    def run(self):
        print('Running WORKFLOW\n')
        insula_job_status = InsulaJobStatus()
        insula_job_status.set_job_id(f'wf_{self.__name}')
        insula_job_status.set_properties(self.__filter_log_properties()).save()

        try:
            for step in self.__steps_order:
                print(f'running:\n\tstep: Step: {step}')
                _ = InsulaWorkflowStepRunner(
                    self.__insula_api_config,
                    step,
                    self.__workflow_data
                )
                results = _.run()
                for result in results['results']:
                    self.__result_manager.add_result_step(self.__workflow_data.identifier, result['run'])
                insula_job_status.set_properties(self.__filter_log_properties()).save()

                if results['error']:
                    print(results)
                    if not self.__workflow_data.config['continue_on_error']:
                        raise Exception('there is an error, check the pid file')

            if self.__workflow_data.config['delete_workflow_log']:
                insula_job_status.remove()
            return self.__result_manager.get_result_steps(self.__workflow_data.identifier)

        except Exception as error:
            insula_job_status.set_job_error('ERROR', error).save()
            raise Exception(error)
