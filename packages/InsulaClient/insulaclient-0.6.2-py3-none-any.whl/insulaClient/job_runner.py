import requests
from time import sleep
from .InsulaApiConfig import InsulaApiConfig
from .job_params import InsulaJobParams
from .job_status import InsulaJobStatus
from .logger import logger


class InsulaRunner(object):
    def __init__(self, insula_config: InsulaApiConfig):
        super().__init__()
        self.__insula_api_config = insula_config
        self.__status_attempts = 0

    def __set_job_config(self, params: InsulaJobParams):

        attempt = 0
        last_response = ''
        while attempt < 3:
            r = requests.post(
                self.__insula_api_config.job_config_api_path,
                data=str(params),
                headers=self.__insula_api_config.headers
            )

            if r.status_code != 201:
                attempt += 1
                last_response = r.text
                sleep(5)
            else:
                resp_dict = r.json()
                return resp_dict['id']

        raise Exception(f'Cant create Job_config: {last_response}')

    def __lunch_job(self, config_id):
        attempt = 0
        last_response = ''
        while attempt < 3:
            url = self.__insula_api_config.get_job_lunch_api_path(config_id)
            run_request = requests.post(url, headers=self.__insula_api_config.headers)
            if run_request.status_code != 202:
                attempt += 1
                last_response = run_request.text
                sleep(5)
            else:
                run_request_dict = run_request.json()
                return run_request_dict['content']['id']

        raise Exception(f'Cant lunch the Job_config: {config_id}, error: {last_response}')

    def __get_job_status(self, job_id):
        url_status = self.__insula_api_config.get_job_status_api_path(job_id)
        status = requests.get(url_status, headers=self.__insula_api_config.headers)

        if status.status_code != 200:
            if self.__status_attempts >= 3:
                raise Exception(f'Cant get status job: {job_id}')
            else:
                logger.info(f'Cant get status job: {job_id} at attempt {self.__status_attempts}')
                self.__status_attempts += 1
                return 'RUNNING'

        self.__status_attempts = 0

        url_status_dict = status.json()

        job_status = url_status_dict['status']
        if job_status == 'COMPLETED' or job_status == 'ERROR' or job_status == 'CANCELLED':
            return job_status

        return 'RUNNING'

    # TODO: To create run from config_id
    def run(self, job_params: InsulaJobParams, **kwargs) -> InsulaJobStatus:
        insula_job_status = InsulaJobStatus()
        insula_job_status.set_properties({'params': str(job_params), 'kwargs': kwargs})

        try:
            insula_job_status.set_config_id(self.__set_job_config(job_params)).save()
            sleep(self.__insula_api_config.interval_between_requests)
            insula_job_status.set_job_status('LUNCHING').save()
            insula_job_status.set_job_id(self.__lunch_job(insula_job_status.get_config_id())).save()
            insula_job_status.set_job_status('RUNNING')
            while insula_job_status.get_job_status() == 'RUNNING':
                sleep(self.__insula_api_config.status_polling_interval)
                insula_job_status.set_job_status(self.__get_job_status(insula_job_status.get_job_id())).save()

        except Exception as error:
            insula_job_status.set_job_error('ERROR', error).save()

        insula_job_status.remove_if_completed()
        return insula_job_status
