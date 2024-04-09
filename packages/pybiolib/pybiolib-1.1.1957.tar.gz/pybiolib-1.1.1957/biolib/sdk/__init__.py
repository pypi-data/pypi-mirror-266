# Imports to hide and use as private internal utils
from biolib._internal.push_application import push_application as _push_application
from biolib._internal.push_application import set_app_version_as_active as _set_app_version_as_active
from biolib.app import BioLibApp as _BioLibApp
from biolib.typing_utils import Optional as _Optional

# Imports to expose as public API
from biolib._internal.data_record import DataRecord
from biolib._internal.runtime import Runtime


def push_app_version(uri: str, path: str) -> _BioLibApp:
    push_data = _push_application(
        app_uri=uri,
        app_path=path,
        app_version_to_copy_images_from=None,
        is_dev_version=True,
    )
    uri = f'{push_data["app_uri"]}:{push_data["sematic_version"]}'
    return _BioLibApp(uri)


def set_app_version_as_default(app_version: _BioLibApp) -> None:
    app_version_uuid = app_version.version['public_id']
    _set_app_version_as_active(app_version_uuid)


def get_app_version_pytest_plugin(app_version: _BioLibApp):
    try:
        import pytest  # type: ignore # pylint: disable=import-outside-toplevel,import-error
    except BaseException:
        raise Exception('Failed to import pytest; please make sure it is installed') from None

    class AppVersionFixturePlugin(object):
        def __init__(self, app_version_ref):
            self.app_version_ref = app_version_ref

        @pytest.fixture(scope='session')
        def app_version(self, request):  # pylint: disable=unused-argument
            return self.app_version_ref

    return AppVersionFixturePlugin(app_version)


def create_data_record(destination: str, data_path: str, name: _Optional[str] = None) -> DataRecord:
    return DataRecord.create(destination, data_path, name)
