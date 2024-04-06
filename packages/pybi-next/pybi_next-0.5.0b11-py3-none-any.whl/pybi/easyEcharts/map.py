from __future__ import annotations
from .base import BaseChart
import pybi as pbi
import pybi.utils.sql as sqlUtils

from typing import TYPE_CHECKING, Optional
from pybi.core.components.reactiveComponent import EChartDatasetInfo
from .utils import merge_user_options

if TYPE_CHECKING:
    from pybi.core.dataSource import DataSourceTable


class MapChart(BaseChart):
    def __init__(self, map_name: str):
        super().__init__()
        self.map_name = map_name

    def _create_default_click_filter(self):
        pass

    def _create_options_ex(self):
        opts = super().get_options()

        geo = {
            "map": self.map_name,
            "roam": True,
            "label": {"show": True, "position": "top"},
            "itemStyle": {
                "normal": {
                    "areaColor": "#c6e2ff",
                    "borderColor": "#389dff",
                    "borderWidth": 1,
                },
                "emphasis": {
                    "areaColor": "#337ecc",
                    "shadowOffsetX": 0,
                    "shadowOffsetY": 0,
                    "shadowBlur": 5,
                    "borderWidth": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                },
            },
        }

        base_opt = {"xAxis": None, "yAxis": None, "series": [], "geo": geo}
        base_opt.update(opts)

        series_config = {
            "type": "map",
            "geoIndex": 0,
        }

        base_opt["series"].append(series_config)

        # opts["tooltip"] = {"trigger": "item"}

        return base_opt, self._updateInfos, [self.map_name]
