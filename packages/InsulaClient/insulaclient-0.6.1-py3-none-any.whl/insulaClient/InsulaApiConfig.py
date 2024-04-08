import base64


class InsulaApiConfig(object):
    def __init__(self, insula_host, username, token, **kwargs):
        self.__insula_host = insula_host
        self.__username = username
        self.__token = token
        self.__headers = {
            'Authorization': f"Basic {base64.b64encode(bytes(str(self.__username) + ':' + str(self.__token), 'utf-8')).decode('utf-8')}",
            'Content-Type': 'application/hal+json;charset=UTF-8'}

        self.__init_kwargs_options(**kwargs)

    def __init_kwargs_options(self, **kwargs):
        self.__status_polling_interval = 60 * 5
        if 'status_polling_interval' in kwargs.keys():
            self.__status_polling_interval = int(kwargs['status_polling_interval'])

        self.__interval_between_requests = 5
        if 'interval_between_requests' in kwargs.keys():
            self.__interval_between_requests = int(kwargs['interval_between_requests'])

        self.__max_processor_attempts = 3
        if 'max_processor_attempts' in kwargs.keys():
            self.__max_processor_attempts = int(kwargs['max_processor_attempts'])

        self.__delete_file_interval = 5

    @property
    def delete_interval(self):
        return self.__delete_file_interval

    @property
    def max_processor_attempts(self):
        return self.__max_processor_attempts

    @property
    def status_polling_interval(self) -> int:
        return self.__status_polling_interval

    @property
    def interval_between_requests(self) -> int:
        return int(self.__interval_between_requests)

    @property
    def headers(self):
        return self.__headers

    @property
    def authorization_header(self):
        return {'Authorization': self.__headers['Authorization']}

    @property
    def job_config_api_path(self):
        return f'{self.__insula_host}/secure/api/v2.0/jobConfigs/'

    @property
    def search_api_path(self):
        return f'{self.__insula_host}/secure/api/v2.0/search'

    def get_job_logs_api_path(self, job_id):
        return f'{self.__insula_host}/secure/api/v2.0/jobs/{job_id}/logs'

    def get_delete_platform_file(self, file_id):
        return f'{self.__insula_host}/secure/api/v2.0/platformFiles/{file_id}'

    def get_job_output_file_api_path(self, job_id):
        return f'{self.__insula_host}/secure/api/v2.0/jobs/{job_id}/outputFiles?projection=detailedPlatformFile'

    def get_job_lunch_api_path(self, config_id):
        return f'{self.__insula_host}/secure/api/v2.0/jobConfigs/{config_id}/launch'

    def get_job_status_api_path(self, job_id):
        return f'{self.__insula_host}/secure/api/v2.0/jobs/{job_id}'

    def get_platform_service_url_api_path(self, service_id):
        return f'{self.__insula_host}/secure/api/v2.0/services/{service_id}'
