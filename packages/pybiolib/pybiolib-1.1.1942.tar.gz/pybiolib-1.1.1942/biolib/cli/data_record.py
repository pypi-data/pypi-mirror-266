import logging
import os

import click

from biolib._internal.data_record import DataRecord
from biolib.biolib_logging import logger, logger_no_user_data
from biolib.typing_utils import Optional


@click.group(help='Data Records')
def data_record() -> None:
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)


@data_record.command(help='Create a Data Record')
@click.option('--destination', type=str, required=True)
@click.option('--data-path', required=True, type=click.Path(exists=True))
@click.option('--name', type=str, required=False)
def create(destination: str, data_path: str, name: Optional[str] = None) -> None:
    DataRecord.create(destination, data_path, name)


@data_record.command(help='Download files from a Data Record')
@click.argument('uri', required=True)
@click.option('--file', required=False, type=str)
@click.option('--path-filter', required=False, type=str, hide_input=True)
def download(uri: str, file: Optional[str], path_filter: Optional[str]) -> None:
    record = DataRecord(uri=uri)
    if file is not None:
        try:
            file_obj = [file_obj for file_obj in record.list_files() if file_obj.path == file][0]
        except IndexError:
            raise Exception('File not found in data record') from None

        assert not os.path.exists(file_obj.name), 'File already exists in current directory'
        with open(file_obj.name, 'wb') as file_handle:
            file_handle.write(file_obj.get_data())

    else:
        assert not os.path.exists(record.name), f'Directory with name {record.name} already exists in current directory'
        record.save_files(output_dir=record.name, path_filter=path_filter)
