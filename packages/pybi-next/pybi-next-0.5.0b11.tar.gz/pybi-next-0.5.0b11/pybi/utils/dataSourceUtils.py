from __future__ import annotations
from typing import TYPE_CHECKING, List
import sqlite3
import base64
import uuid
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import tempfile
import os


if TYPE_CHECKING:
    from pybi.core.dataSource import DataSource


def file2base64(file_path: Path):
    with open(file_path, mode="rb") as f:
        return base64.b64encode(f.read()).decode("utf8")


def _create_file_name():
    return uuid.uuid4().hex


def ds2sqlite(path: str, dataSources: List[DataSource], clear_data=False):
    with sqlite3.connect(path) as con:
        for ds in dataSources:
            data = ds._data
            if clear_data:
                data = data.head(0)
            data.to_sql(ds.name, con, if_exists="replace", index=False)


def ds2sqlite_file_base64(dataSources: List[DataSource], clear_data=False):

    filename = None
    need_remove_temp_files = False
    with tempfile.TemporaryFile() as tp:
        filename = tp.name

    # has a number name in some env
    if (filename is None) or not isinstance(filename, str):
        filename = _create_file_name()
        need_remove_temp_files = True

    ds2sqlite(filename, dataSources, clear_data)

    zipfile_name = f"{filename}.zip"

    with ZipFile(zipfile_name, "w", compression=ZIP_DEFLATED) as myzip:
        myzip.write(filename)

    res = file2base64(zipfile_name)

    if need_remove_temp_files:
        os.remove(filename)
        os.remove(zipfile_name)
    return res
