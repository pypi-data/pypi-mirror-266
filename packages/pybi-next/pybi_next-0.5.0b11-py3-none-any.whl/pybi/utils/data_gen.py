import base64
import datetime
from enum import Enum
from pathlib import Path
import simplejson as json
from functools import partial
from typing import Callable, Sequence, List, Dict
import numpy as np
import pandas as pd
import inspect

from abc import abstractmethod
import pybi.utils.echarts_opts_utils as echarts_opts_utils
import pybi.utils.pyecharts_utils as pybi_pyecharts_utils

_global_id = 0


class Jsonable:
    @abstractmethod
    def _to_json_dict(self):
        data = {k: v for k, v in self.__dict__.items() if k[:1] != "_"}

        return data


def fn2str(fn: Callable):
    return inspect.getsource(fn)


def random_ds_name():
    return f"ds_{get_global_id()}"


def random_dv_name():
    return f"dv_{get_global_id()}"


def get_global_id():
    global _global_id
    _global_id += 1
    return str(_global_id)


_m_project_root = Path(__file__).absolute().parent.parent


def get_project_root():
    return _m_project_root


def pybi_json_default(obj):
    if isinstance(obj, float) and pd.isna(obj):
        return None
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Jsonable):
        return obj._to_json_dict()


class JsonUtils:
    def __init__(self) -> None:
        self.json_defalut_fns: List[Callable] = [pybi_json_default]

    def mark_pyecharts(self):
        if len(self.json_defalut_fns) >= 2:
            return

        from pyecharts.options.series_options import BasicOpts
        from pyecharts.commons import utils as pyecharts_utils

        self.json_defalut_fns.append(
            partial(
                pybi_pyecharts_utils.pyecharts_json_default,
                utils=pyecharts_utils,
                basicOptsType=BasicOpts,
            )
        )

    def dumps(self, obj, *args, **kws):
        def json_default(obj):
            for fn in self.json_defalut_fns:
                res = fn(obj)
                if res is not None:
                    return res

        return json.dumps(
            obj, *args, **kws, ignore_nan=True, default=json_default, ensure_ascii=False
        )


# json_dumps_fn = partial(json.dumps, ignore_nan=True, default=json_default)


def data2html_img_src(data: bytes):
    b64 = base64.b64encode(data).decode("utf8")
    value = f"data:image/png;base64,{b64}"
    return value


def file2html_base64_src(file: str, format: str):

    with open(file, mode="rb") as f:
        b64 = base64.b64encode(f.read())
        b64 = str(b64, "utf8")
        value = f"data:{format};base64,{b64}"
        return value


class StrEnum(str, Enum):
    def __new__(cls, value, *args, **kwargs):
        return super().__new__(cls, value, *args, **kwargs)

    def __str__(self):
        return str(self.value)

    def _generate_next_value_(name, *_):
        return name
