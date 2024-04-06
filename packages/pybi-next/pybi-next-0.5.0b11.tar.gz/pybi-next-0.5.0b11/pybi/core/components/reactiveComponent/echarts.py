from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Dict, Set, Any, Union
from pybi.core.sql import SqlWrapper

from pybi.utils.data_gen import Jsonable
from pybi.core.components import ComponentTag
from .base import ReactiveComponent
from pybi.core.dataSource import DataSourceTable
import pybi.utils.echarts_opts_utils as echarts_opts_utils

if TYPE_CHECKING:
    from pybi.core.dataSource import DataSourceTable
    from pybi.core.sql import SqlInfo


class EChartSqlInfo(Jsonable):
    def __init__(
        self, seriesConfig: Dict, path: str, sql: SqlInfo, chartType: str
    ) -> None:
        self.path = path
        self._sql = sql
        self.chartType = chartType
        self.seriesConfig = seriesConfig

    def _to_json_dict(self):
        data = super()._to_json_dict()
        sql_data = self._sql._to_json_dict()

        data = {**data, **sql_data}
        return data


class EChartDatasetInfo(Jsonable):
    def __init__(self, seriesConfig: Dict, path: str, sql_info: SqlInfo) -> None:
        self.path = path
        self.sqlInfo = sql_info
        self.seriesConfig = seriesConfig


class EChartJscode(Jsonable):
    def __init__(self, path: str, code: str) -> None:
        self.path = path
        self.code = code


class EChartUpdateInfo(Jsonable):
    def __init__(
        self,
        action_type: str,
        value_type: str,
        table: str,
        field: str,
    ) -> None:
        """
        action_type : Literal["hover", "click"]
        value_type: Literal["x", "y", "value","color","name"]
        """
        super().__init__()
        self.actionType = action_type
        self.valueType = value_type
        self.table = table
        self.field = field


class EChartJsCode:
    js_code_flag = "--x_x--0_0--"

    def __init__(self, code: str) -> None:
        self.code = code

    def __str__(self) -> str:
        return f"{EChartJsCode.js_code_flag}{self.code}{EChartJsCode.js_code_flag}"


class OptionsExtractor:
    @staticmethod
    def extract_and_remove_from_dict(
        data: Dict,
        out_datasets: List[tuple[str, SqlWrapper]],
        out_jscodes: List[tuple[str, str]],
    ):
        for target, path in echarts_opts_utils.iter_each_items(data):
            if isinstance(target, SqlWrapper):
                rpath = path[1:]
                out_datasets.append((rpath, target))
                OptionsExtractor.set_none_prop(data, rpath)

            if isinstance(target, EChartJsCode):
                rpath = path[1:]
                out_jscodes.append((rpath, target.code))
                OptionsExtractor.set_none_prop(data, rpath)

            if (
                isinstance(target, str)
                and target[: len(EChartJsCode.js_code_flag)]
                == EChartJsCode.js_code_flag
                and target[-len(EChartJsCode.js_code_flag) :]
                == EChartJsCode.js_code_flag
            ):
                target = target[
                    len(EChartJsCode.js_code_flag) : -len(EChartJsCode.js_code_flag)
                ]
                rpath = path[1:]
                out_jscodes.append((rpath, target))
                OptionsExtractor.set_none_prop(data, rpath)

    @staticmethod
    def set_none_prop(options: Dict, path: str):
        """
        path: 'sreies[0].data[0].item.value'
        """
        echarts_opts_utils.set_prop_by_path(options, path, None)


class EChartInfo(Jsonable):
    def __init__(
        self,
        options: Dict,
        datasetInfos: List[EChartDatasetInfo],
        updateInfos: List[EChartUpdateInfo],
        jscodes: List[EChartJscode],
        mapIds: Optional[List[str]] = None,
        postMergeSettings: Optional[Dict] = None,
    ):
        self.options = options
        self.datasetInfos = datasetInfos
        self.updateInfos = updateInfos
        self.jsCodes = jscodes
        self.mapIds = mapIds or []
        self.postMergeSettings = postMergeSettings or {}


class EChart(ReactiveComponent):
    def __init__(self, *, option_type="dict") -> None:
        super().__init__(ComponentTag.EChart)
        self._chart_mappings = {}
        self._chartInfos: List[EChartInfo] = []
        self.optionType = option_type
        self.height = "100%"

    def set_height(self, value: str):
        """
        15em:15字体大小
        300px:300像素
        """
        self.height = value
        return self

    def _add_chart_info(self, info: EChartInfo):
        self._chartInfos.append(info)
        return self

    def hover_filter(
        self, value_type: str, table: Union[str, DataSourceTable], field: str
    ):
        """
        value_type: , Literal["x", "y", "value","color","name"]
        """
        if isinstance(table, DataSourceTable):
            table = table.source_name

        self._chartInfos[0].updateInfos.append(
            EChartUpdateInfo("hover", value_type, table, field)
        )

        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["chartInfos"] = self._chartInfos
        return data
