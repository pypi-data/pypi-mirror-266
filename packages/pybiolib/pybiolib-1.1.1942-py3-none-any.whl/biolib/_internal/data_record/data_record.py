import os
from collections import namedtuple
from datetime import datetime
from fnmatch import fnmatch
from struct import Struct
from typing import Callable, Dict, List, Optional, Union, cast

from biolib import lfs
from biolib._internal.data_record.remote_storage_endpoint import DataRecordRemoteStorageEndpoint
from biolib._internal.http_client import HttpClient
from biolib.api import client as api_client
from biolib.biolib_api_client import AppGetResponse
from biolib.biolib_binary_format import LazyLoadedFile
from biolib.biolib_binary_format.utils import RemoteIndexableBuffer
from biolib.biolib_logging import logger
from biolib.utils.app_uri import parse_app_uri
from biolib.utils.zip.remote_zip import RemoteZip  # type: ignore

PathFilter = Union[str, Callable[[str], bool]]


class DataRecord:
    def __init__(self, uri: str):
        self._uri = uri
        uri_parsed = parse_app_uri(uri, use_account_as_name_default=False)
        if not uri_parsed['app_name']:
            raise ValueError('Expected parameter "uri" to contain resource name')

        self._name = uri_parsed['app_name']

    def __repr__(self):
        return f'DataRecord: {self._uri}'

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def name(self) -> str:
        return self._name

    def list_files(self, path_filter: Optional[PathFilter] = None) -> List[LazyLoadedFile]:
        app_response: AppGetResponse = api_client.get(path='/app/', params={'uri': self._uri}).json()
        remote_storage_endpoint = DataRecordRemoteStorageEndpoint(
            resource_version_uuid=app_response['app_version']['public_id'],
        )
        files: List[LazyLoadedFile] = []
        with RemoteZip(url=remote_storage_endpoint.get_remote_url()) as remote_zip:
            central_directory = remote_zip.get_central_directory()
            for file_info in central_directory.values():
                files.append(self._get_file(remote_storage_endpoint, file_info))

        return self._get_filtered_files(files=files, path_filter=path_filter) if path_filter else files

    def download_zip(self, output_path: str):
        app_response: AppGetResponse = api_client.get(path='/app/', params={'uri': self._uri}).json()
        remote_storage_endpoint = DataRecordRemoteStorageEndpoint(
            resource_version_uuid=app_response['app_version']['public_id'],
        )
        HttpClient.request(url=remote_storage_endpoint.get_remote_url(), response_path=output_path)

    def download_files(self, output_dir: str, path_filter: Optional[PathFilter] = None) -> None:
        filtered_files = self.list_files(path_filter=path_filter)

        if len(filtered_files) == 0:
            logger.debug('No files to save')
            return

        for file in filtered_files:
            file_path = os.path.join(output_dir, file.path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, mode='wb') as file_handle:
                for chunk in file.get_data_iterator():
                    file_handle.write(chunk)

    def save_files(self, output_dir: str, path_filter: Optional[PathFilter] = None) -> None:
        self.download_files(output_dir=output_dir, path_filter=path_filter)

    @staticmethod
    def create(destination: str, data_path: str, name: Optional[str] = None) -> 'DataRecord':
        assert os.path.isdir(data_path), f'The path "{data_path}" is not a directory.'
        record_name = name if name else 'data-record-' + datetime.now().isoformat().split('.')[0].replace(':', '-')
        record_uri = lfs.create_large_file_system(lfs_uri=f'{destination}/{record_name}')
        record_version_uri = lfs.push_large_file_system(lfs_uri=record_uri, input_dir=data_path)
        return DataRecord(uri=record_version_uri)

    @staticmethod
    def fetch(uri: Optional[str] = None, count: Optional[int] = None) -> List['DataRecord']:
        max_page_size = 1_000
        params: Dict[str, Union[str, int]] = {
            'page_size': str(count or max_page_size),
            'resource_type': 'data-record',
        }
        if uri:
            uri_parsed = parse_app_uri(uri, use_account_as_name_default=False)
            params['account_handle'] = uri_parsed['account_handle_normalized']
            if uri_parsed['app_name_normalized']:
                params['app_name'] = uri_parsed['app_name_normalized']

        results = api_client.get(path='/apps/', params=params).json()['results']
        if count is None and len(results) == max_page_size:
            logger.warning(
                f'Fetch results exceeded maximum count of {max_page_size}. Some data records might not be fetched.'
            )

        return [DataRecord(result['resource_uri']) for result in results]

    @staticmethod
    def _get_file(remote_storage_endpoint: DataRecordRemoteStorageEndpoint, file_info: Dict) -> LazyLoadedFile:
        local_file_header_signature_bytes = b'\x50\x4b\x03\x04'
        local_file_header_struct = Struct('<H2sHHHIIIHH')
        LocalFileHeader = namedtuple(
            'LocalFileHeader',
            (
                'version',
                'flags',
                'compression_raw',
                'mod_time',
                'mod_date',
                'crc_32_expected',
                'compressed_size_raw',
                'uncompressed_size_raw',
                'file_name_len',
                'extra_field_len',
            ),
        )

        local_file_header_start = file_info['header_offset'] + len(local_file_header_signature_bytes)
        local_file_header_end = local_file_header_start + local_file_header_struct.size

        def file_start_func() -> int:
            local_file_header_response = HttpClient.request(
                url=remote_storage_endpoint.get_remote_url(),
                headers={'range': f'bytes={local_file_header_start}-{local_file_header_end - 1}'},
                timeout_in_seconds=300,
            )
            local_file_header = LocalFileHeader._make(
                local_file_header_struct.unpack(local_file_header_response.content)
            )
            file_start: int = (
                local_file_header_end + local_file_header.file_name_len + local_file_header.extra_field_len
            )
            return file_start

        return LazyLoadedFile(
            buffer=RemoteIndexableBuffer(endpoint=remote_storage_endpoint),
            length=file_info['file_size'],
            path=file_info['filename'],
            start=None,
            start_func=file_start_func,
        )

    @staticmethod
    def _get_filtered_files(files: List[LazyLoadedFile], path_filter: PathFilter) -> List[LazyLoadedFile]:
        if not (isinstance(path_filter, str) or callable(path_filter)):
            raise Exception('Expected path_filter to be a string or a function')

        if callable(path_filter):
            return list(filter(lambda x: path_filter(x.path), files))  # type: ignore

        glob_filter = cast(str, path_filter)

        def _filter_function(file: LazyLoadedFile) -> bool:
            return fnmatch(file.path, glob_filter)

        return list(filter(_filter_function, files))
