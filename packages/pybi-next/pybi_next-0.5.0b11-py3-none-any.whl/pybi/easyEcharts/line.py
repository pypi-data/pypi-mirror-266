from __future__ import annotations
from .base import BaseChart
import pybi as pbi
import pybi.utils.sql as sqlUtils

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pybi.core.dataSource import DataSourceTable


class LineChart(BaseChart):
    def __init__(
        self,
        data: DataSourceTable,
        x: str,
        y: str,
        order: str,
        color: Optional[str] = None,
        agg="round(avg(${}),2)",
    ):
        super().__init__()
        self.data = data
        self.x = x
        self.y = y
        self.order = order or x
        self.color = color
        self.agg = agg
        self._series_configs = {}
        self._xAxis = {}

    def stack(self):
        self._series_configs["stack"] = "Total"
        return self

    def area(self):
        """
        线以下区域填充颜色,使其成为区域图
        """
        self._series_configs["areaStyle"] = {}
        return self

    def _create_default_click_filter(self):
        self.click_filter("x", self.data, self.x)

    def set_xAxis(self, value):
        self._xAxis = value
        return self

    def _create_options_ex(self):
        opts = super().get_options()

        base_opt = {
            "xAxis": [
                {
                    "type": "",
                    "data": [],
                }
            ],
            "yAxis": [{"type": ""}],
            "series": [],
        }
        base_opt.update(opts)

        sql = ""
        agg_field = f"{sqlUtils.apply_agg(self.agg, self.y)} as {self.y}"
        if self.color:
            sql = f"select {self.x},{agg_field},{self.color},{self.order} from {self.data} group by {self.color},{self.x}"
        else:
            sql = f"select {self.x},{agg_field},{self.order} from {self.data} group by {self.x}"

        dv = pbi.set_dataView(sql)

        if self.color:
            base_opt["series"] = pbi.sql(
                f"select {self.x},{self.y},{self.color} from {dv} order by {self.order}"
            ).split_group(
                self.color,
                """
                const data = rows.map(r=> [r[fields[0]],r[fields[1]]])
                return {id:key,data,type:'line',name:key,universalTransition: {enabled: true}}""",
            )
        else:
            base_opt["series"].append(
                {
                    "name": self.x,
                    "id": self.x,
                    "universalTransition": {"enabled": True, "divideShape": "clone"},
                    "type": "line",
                    "data": pbi.sql(
                        f"select {self.y} as value,{self.x} as groupId from {dv} order by {self.order}"
                    ),
                }
            )

        catAxis = base_opt["xAxis"][0]
        valueAxis = base_opt["yAxis"][0]

        catAxis["data"] = pbi.sql(
            f"select distinct {self.x} from {dv} order by {self.order}"
        ).toflatlist()
        catAxis.update(self._xAxis)
        # catAxis["axisLabel"] = {"formatter": "{value}月"}
        catAxis["boundaryGap"] = False
        valueAxis["type"] = "value"

        opts["tooltip"] = {
            "trigger": "axis",
            "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}},
        }

        return base_opt, self._updateInfos, []
