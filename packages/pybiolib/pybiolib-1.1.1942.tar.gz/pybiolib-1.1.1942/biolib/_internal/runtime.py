import json
import re

from biolib import api
from biolib.typing_utils import Optional, TypedDict, cast


class RuntimeJobDataDict(TypedDict):
    version: str
    job_requested_machine: str
    job_uuid: str
    job_auth_token: str
    app_uri: str


class BioLibRuntimeError(Exception):
    pass


class BioLibRuntimeNotRecognizedError(BioLibRuntimeError):
    def __init__(self, message='The runtime is not recognized as a BioLib app'):
        self.message = message
        super().__init__(self.message)


class Runtime:
    _job_data: Optional[RuntimeJobDataDict] = None

    @staticmethod
    def check_is_environment_biolib_app() -> bool:
        return bool(Runtime._try_to_get_job_data())

    @staticmethod
    def get_job_id() -> str:
        return Runtime._get_job_data()['job_uuid']

    @staticmethod
    def get_job_auth_token() -> str:
        return Runtime._get_job_data()['job_auth_token']

    @staticmethod
    def get_job_requested_machine() -> str:
        return Runtime._get_job_data()['job_requested_machine']

    @staticmethod
    def get_app_uri() -> str:
        return Runtime._get_job_data()['app_uri']

    @staticmethod
    def get_secret(secret_name: str) -> bytes:
        assert re.match(
            '^[a-zA-Z0-9_-]*$', secret_name
        ), 'Secret name can only contain alphanumeric characters and dashes or underscores '
        try:
            with open(f'/biolib/secrets/{secret_name}', 'rb') as file:
                return file.read()
        except BaseException as error:
            raise BioLibRuntimeError(f'Unable to get system secret: {secret_name}') from error

    @staticmethod
    def set_main_result_prefix(result_prefix: str) -> None:
        job_data = Runtime._get_job_data()
        api.client.patch(
            data={'result_name_prefix': result_prefix},
            headers={'Job-Auth-Token': job_data['job_auth_token']},
            path=f"/jobs/{job_data['job_uuid']}/main_result/",
        )

    @staticmethod
    def create_result_note(note: str) -> None:
        job_id = Runtime.get_job_id()
        # Note: Authentication is added by app caller proxy in compute node
        api.client.post(data={'note': note}, path=f'/jobs/{job_id}/notes/')

    @staticmethod
    def _try_to_get_job_data() -> Optional[RuntimeJobDataDict]:
        if not Runtime._job_data:
            try:
                with open('/biolib/secrets/biolib_system_secret') as file:
                    job_data: RuntimeJobDataDict = json.load(file)
            except BaseException:
                return None

            if not job_data['version'].startswith('1.'):
                raise BioLibRuntimeError(f"Unexpected system secret version {job_data['version']} expected 1.x.x")

            Runtime._job_data = job_data

        return cast(RuntimeJobDataDict, Runtime._job_data)

    @staticmethod
    def _get_job_data() -> RuntimeJobDataDict:
        job_data = Runtime._try_to_get_job_data()
        if not job_data:
            raise BioLibRuntimeNotRecognizedError() from None
        return job_data
