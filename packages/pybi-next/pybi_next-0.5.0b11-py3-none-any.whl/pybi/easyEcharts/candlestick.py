from __future__ import annotations


from .base import BaseChart
import pybi as pbi


from typing import TYPE_CHECKING, Optional
from . import utils as easyUtils

if TYPE_CHECKING:
    from pybi.core.dataSource import DataSourceTable


class CandleStickChart(BaseChart):
    def __init__(
        self,
        data: DataSourceTable,
        date="date",
        open="open",
        close="close",
        lowest="lowest",
        highest="highest",
    ):
        super().__init__()
        self.data = data
        self.date = date
        self.open = open
        self.close = close
        self.lowest = lowest
        self.open = open
        self.highest = highest
        self._series_configs = {}

    def _create_default_click_filter(self):
        pass

    def _create_options_ex(self):
        opts = super().get_options()

        base_opt = {
            "xAxis": [{}],
            "yAxis": [{}],
            "series": [],
            "dataZoom": [
                {
                    "textStyle": {"color": "#8392A5"},
                    "handleIcon": "path://M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z",
                    "dataBackground": {
                        "areaStyle": {"color": "#8392A5"},
                        "lineStyle": {"opacity": 0.8, "color": "#8392A5"},
                    },
                    "brushSelect": True,
                },
                {"type": "inside"},
            ],
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"},
                "borderWidth": 1,
                "borderColor": "#ccc",
                "padding": 10,
                "textStyle": {"color": "#000"},
            },
        }

        # base_opt = easyUtils.merge_user_options(base_opt, opts)
        base_opt.update(opts)

        base_opt["series"].append(
            {
                "type": "candlestick",
                "data": pbi.sql(
                    f"select {self.open},{self.close},{self.lowest},{self.highest}  from {self.data} order by {self.date}"
                ).toflatlist(),
                "universalTransition": {"enabled": True, "divideShape": "clone"},
            }
        )

        base_opt["xAxis"][0]["data"] = pbi.sql(
            f"select distinct {self.date} from {self.data} order by {self.date}"
        ).toflatlist()

        return base_opt, self._updateInfos, []
