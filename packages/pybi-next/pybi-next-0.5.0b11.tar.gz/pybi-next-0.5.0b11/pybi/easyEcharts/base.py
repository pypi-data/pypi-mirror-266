from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple, List, Any, Union

from pybi.core.components.reactiveComponent.echarts import EChartUpdateInfo
from pybi.core.dataSource import DataSourceTable
import pybi.utils.echarts_opts_utils as echarts_opts_utils
import copy
from typing_extensions import Literal


_T_PIE_FILTER_VALUE_TYPE = Literal["x", "y", "value", "color", "name"]

if TYPE_CHECKING:
    pass


class BaseChart:
    def __init__(self) -> None:
        self.__base_opt = {
            "legend": [{}],
            "series": [],
            "title": [{}],
            "grid": [{"containLabel": True}],
            "tooltip": [{}],
        }
        self._merge_opt = {}
        self._updateInfos: List[EChartUpdateInfo] = []
        self._prop_by_paths: List[Tuple[str, Any]] = []

    def __add__(self, other: BaseChart):
        return ChartCollector().append(self).append(other)

    def merge(self, options: Dict):
        list_item_opts = {
            key: value if isinstance(value, List) or key == "series" else [value]
            for key, value in options.items()
        }

        self._merge_opt.update(list_item_opts)
        return self

    def get_options(self):
        return copy.deepcopy(self.__base_opt)

    def set_title(self, text: str):
        self.merge({"title": {"text": text}})

        return self

    def hover_filter(
        self,
        value_type: _T_PIE_FILTER_VALUE_TYPE,
        table: Union[str, DataSourceTable],
        field: str,
    ):
        """
        value_type: Literal["x", "y", "value","color","name"]
        """
        if isinstance(table, DataSourceTable):
            table = table.source_name

        self._updateInfos.append(EChartUpdateInfo("hover", value_type, table, field))

        return self

    def click_filter(
        self,
        value_type: _T_PIE_FILTER_VALUE_TYPE,
        table: Union[str, DataSourceTable],
        field: str,
    ):
        """
        value_type: Literal["x", "y", "value","color","name"]
        """
        if isinstance(table, DataSourceTable):
            table = table.source_name

        self._updateInfos.append(EChartUpdateInfo("click", value_type, table, field))

        return self

    def _post_options(self, opts: Dict):
        # opts = merge_user_options(opts, self._merge_opt)
        self._update_props_by_path(opts)
        return opts

    def _remove_filters(self, actionType: str):
        """
        actionType : 'click' | 'hover'
        """
        self._updateInfos = [
            info for info in self._updateInfos if info.actionType != actionType
        ]
        return self

    def remove_all_click_filter(self):
        return self._remove_filters("click")

    def _create_default_click_filter(self):
        pass

    def _create_options_ex(self):
        raise NotImplementedError

    def get_options_infos(
        self,
    ) -> Tuple[Dict, List[EChartUpdateInfo], List[str]]:
        opts, updateInfos, mapIds = self._create_options_ex()
        opts = self._post_options(opts)
        return opts, updateInfos, mapIds

    def set_prop_by_path(self, path: str, value):
        """
        >>> .set_prop_by_path('xAxis[0].axisLabel.interval',1)
        """
        self._prop_by_paths.append((path, value))
        return self

    def _update_props_by_path(self, opts: Dict):
        for path, value in self._prop_by_paths:
            echarts_opts_utils.set_prop_by_path(opts, path, value)


class ChartCollector:
    def __init__(self) -> None:
        self._collector: List[BaseChart] = []

    def append(self, other: BaseChart):
        self._collector.append(other)
        return self

    def __add__(self, other: Union[ChartCollector, BaseChart]):
        if isinstance(other, BaseChart):
            other = ChartCollector().append(other)

        self._collector.extend(other._collector)
        return self
