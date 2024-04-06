from __future__ import annotations


from .base import BaseChart
import pybi as pbi
import pybi.utils.sql as sqlUtils


from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pybi.core.dataSource import DataSourceTable


class BarChart(BaseChart):
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
        self._reverse_axis = False
        self._series_configs = {}

    def reverse_axis(self):
        self._reverse_axis = True
        return self

    def _create_default_click_filter(self):
        valueType, field = "x", self.x
        if self._reverse_axis:
            valueType, field = "y", self.y

        self.click_filter(valueType, self.data, self.x)

    def _create_options_ex(self):
        opts = super().get_options()

        base_opt = {
            "xAxis": [
                {
                    "type": "",
                    # "data": [],
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
            row_map_x, row_map_y = "r[fields[0]]", "r[fields[1]]"
            if self._reverse_axis:
                row_map_x, row_map_y = row_map_y, row_map_x

            base_opt["series"] = pbi.sql(
                f"select {self.x},{self.y},{self.color} from {dv} order by {self.order}"
            ).split_group(
                self.color,
                f"""
                const data = rows.map(r=> [{row_map_x},{row_map_y}])
                return {{id:key,data,type:'bar',name:key,universalTransition: {{enabled: true, divideShape: 'clone'}}}}""",
            )
        else:
            base_opt["series"].append(
                {
                    "name": self.x,
                    "type": "bar",
                    "id": self.x,
                    "data": pbi.sql(
                        f"select {self.y} as value,{self.x} as groupId from {dv} order by {self.order}"
                    ),
                    "universalTransition": {"enabled": True, "divideShape": "clone"},
                }
            )

        catAxis = base_opt["xAxis"][0]
        valueAxis = base_opt["yAxis"][0]

        if self._reverse_axis:
            catAxis, valueAxis = valueAxis, catAxis

        catAxis["data"] = pbi.sql(
            f"select distinct {self.x} from {dv} order by {self.order}"
        ).toflatlist()
        catAxis["type"] = "category"
        valueAxis["type"] = "value"

        return base_opt, self._updateInfos, []
