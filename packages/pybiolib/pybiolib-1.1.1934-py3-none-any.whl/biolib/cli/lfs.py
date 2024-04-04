import json
import logging
import os
import sys
from typing import Dict, List

import click

from biolib import biolib_errors
from biolib._internal.data_record import DataRecord
from biolib.biolib_logging import logger, logger_no_user_data
from biolib.lfs import create_large_file_system, prune_lfs_cache, push_large_file_system
from biolib.typing_utils import Optional


@click.group(help='Manage Large File Systems')
def lfs() -> None:
    pass


@lfs.command(help='Create a Large File System')
@click.argument('uri', required=True)
def create(uri: str) -> None:
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)
    create_large_file_system(lfs_uri=uri)


@lfs.command(help='Push a new version of a Large File System')
@click.argument('uri', required=True)
@click.option('--path', required=True, type=click.Path(exists=True))
@click.option('--chunk-size', default=None, required=False, type=click.INT, help='The size of each chunk (In MB)')
def push(uri: str, path: str, chunk_size: Optional[int]) -> None:
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)
    try:
        push_large_file_system(lfs_uri=uri, input_dir=path, chunk_size_in_mb=chunk_size)
    except biolib_errors.BioLibError as error:
        print(f'An error occurred:\n{error.message}', file=sys.stderr)
        exit(1)


@lfs.command(help='Download a file from a Large File System')
@click.argument('uri', required=True)
@click.option('--file-path', required=True, type=str)
def download_file(uri: str, file_path: str) -> None:
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)
    try:
        record = DataRecord(uri=uri)
        try:
            file_obj = [file_obj for file_obj in record.list_files() if file_obj.path == file_path][0]
        except IndexError:
            raise Exception('File not found in data record') from None

        assert not os.path.exists(file_obj.name), 'File already exists in current directory'
        with open(file_obj.name, 'wb') as file_handle:
            file_handle.write(file_obj.get_data())

    except biolib_errors.BioLibError as error:
        print(f'An error occurred:\n{error.message}', file=sys.stderr)
        exit(1)


@lfs.command(help='Describe a Large File System')
@click.argument('uri', required=True)
@click.option('--json', 'output_as_json', is_flag=True, default=False, required=False, help='Format output as JSON')
def describe(uri: str, output_as_json: bool) -> None:
    data_record = DataRecord(uri)
    files_info: List[Dict] = []
    total_size_in_bytes = 0
    for file in data_record.list_files():
        files_info.append({'path': file.path, 'size_bytes': file.length})
        total_size_in_bytes += file.length

    if output_as_json:
        print(
            json.dumps(
                obj={'uri': data_record.uri, 'size_bytes': total_size_in_bytes, 'files': files_info},
                indent=4,
            )
        )
    else:
        print(f'Large File System {data_record.uri}\ntotal {total_size_in_bytes} bytes\n')
        print('size bytes    path')
        for file_info in files_info:
            size_string = str(file_info['size_bytes'])
            leading_space_string = ' ' * (10 - len(size_string))
            print(f"{leading_space_string}{size_string}    {file_info['path']}")


@lfs.command(help='Prune LFS cache', hidden=True)
@click.option('--dry-run', type=click.BOOL, default=True, required=False)
def prune_cache(dry_run: bool) -> None:
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)
    prune_lfs_cache(dry_run)
