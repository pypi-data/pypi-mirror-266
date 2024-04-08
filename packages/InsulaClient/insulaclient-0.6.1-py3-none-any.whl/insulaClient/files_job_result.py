import requests
from .InsulaApiConfig import InsulaApiConfig
from .job_status import InsulaJobStatus
from .step_result import StepResult


class InsulaFilesJobResult(object):
    def __init__(self, insula_config: InsulaApiConfig):
        super().__init__()
        self.__insula_api_config = insula_config

    @staticmethod
    def __get_files_from_result_job(raw_results: dict):
        results = []
        for platform_file in raw_results['_embedded']['platformFiles']:
            results.append(StepResult(
                id=platform_file['id'],
                output_id=platform_file['filename'].split('/')[1],
                default=platform_file['uri'],
                download=platform_file["_links"]["download"]['href'],
                type='job_result'
            ))

        return results

    def get_result_from_job(self, job_id) -> list:

        res = self.__insula_api_config.get_job_output_file_api_path(job_id)
        run_request = requests.get(res,
                                   headers=self.__insula_api_config.headers)

        if run_request.status_code != 200:
            raise Exception(
                f'cant retrieve result from job: {job_id}, status: {run_request.status_code}, text: {run_request.text}')

        a = run_request.json()
        return self.__get_files_from_result_job(run_request.json())

    def get_result_from_job_status(self, job_status: InsulaJobStatus) -> list:
        return self.get_result_from_job(job_status.get_job_id())
