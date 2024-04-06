from datetime import datetime, timedelta

from biolib.api import client as api_client
from biolib.biolib_api_client.lfs_types import LargeFileSystemVersion
from biolib.biolib_binary_format.utils import RemoteEndpoint
from biolib.biolib_logging import logger


class DataRecordRemoteStorageEndpoint(RemoteEndpoint):
    def __init__(self, resource_version_uuid: str):
        self._resource_version_uuid: str = resource_version_uuid
        self._expires_at = None
        self._presigned_url = None

    def get_remote_url(self):
        if not self._presigned_url or datetime.utcnow() > self._expires_at:
            lfs_version: LargeFileSystemVersion = api_client.get(
                path=f'/lfs/versions/{self._resource_version_uuid}/',
            ).json()
            self._presigned_url = lfs_version['presigned_download_url']
            self._expires_at = datetime.utcnow() + timedelta(minutes=8)
            logger.debug(
                f'DataRecord "{self._resource_version_uuid}" fetched presigned URL '
                f'with expiry at {self._expires_at.isoformat()}'
            )

        return self._presigned_url
