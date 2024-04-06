from __future__ import annotations
from .base import BaseChart
import pybi as pbi

from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pybi.core.dataSource import DataSourceTable


class ScatterChart(BaseChart):
    def __init__(
        self,
        data: DataSourceTable,
        x: str,
        y: str,
        color: Optional[str] = None,
        size: Optional[str] = None,
        agg="round(avg(${}),2)",
    ):
        super().__init__()
        self.data = data
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.agg = agg
        self._series_configs = {}

    def _create_default_click_filter(self):
        # TODO:
        self.click_filter("x", self.data, self.x)

    def _create_options_ex(self):
        opts = super().get_options()

        base_opt = {
            "xAxis": {},
            "yAxis": {},
            "series": [],
        }
        base_opt.update(opts)

        series_config = {"type": "scatter", "symbolSize": 15}
        series_config.update(self._series_configs)

        sql = None
        if self.color:
            sql = pbi.sql(
                f"select {self.x},{self.y},{self.color} from {self.data}"
            ).split_group(
                self.color,
                """
                const need_fields = fields.slice(0,2)
                const data = rows.map(r=> need_fields.map(f=> r[f]))
                return {data,type:'scatter',name:key,symbolSize:15}""",
            )

            base_opt["series"] = sql
        else:
            sql = pbi.sql(f"select {self.x},{self.y} from {self.data}").toflatlist()
            series = {"type": "scatter", "symbolSize": 15, "data": sql}
            base_opt["series"].append(series)

        opts["tooltip"] = {"trigger": "item"}

        return base_opt, self._updateInfos, []
