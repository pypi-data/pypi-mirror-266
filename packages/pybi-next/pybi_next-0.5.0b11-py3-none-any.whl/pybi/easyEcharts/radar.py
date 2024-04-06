from __future__ import annotations


from .base import BaseChart
import pybi as pbi
import pybi.utils.sql as sqlUtils


from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pybi.core.dataSource import DataSourceTable


class RadarChart(BaseChart):
    def __init__(
        self,
        data: DataSourceTable,
        indicator: str,
        name: str,
        value: str,
        agg="round(avg(${}),2)",
    ):
        super().__init__()
        self.data = data
        self.indicator = indicator
        self.value = value
        self.name = name
        self.agg = agg
        self._series_configs = {}

    def _create_default_click_filter(self):
        pass

    def _create_options_ex(self):
        opts = super().get_options()

        agg_field = f"{sqlUtils.apply_agg(self.agg, self.value)} as value"

        dv_summary = pbi.set_dataView(
            f"select {self.name} as name,{self.indicator} as indicator,{agg_field} from {self.data} group by {self.name},{self.indicator}"
        )

        dv_indicator = pbi.set_dataView(
            f"""select indicator,max(value) as max,
                    row_number() OVER (ORDER BY indicator) as row_num
            from {dv_summary} 
            group by indicator"""
        )

        dv_idc_name = pbi.set_dataView(
            f"""
        select t1.indicator,t1.row_num ,t2.name
        from {dv_indicator} as t1
        cross join (select distinct name from {dv_summary}) as t2
        """
        )

        dv_data = pbi.set_dataView(
            f"""select t1.indicator, t1.name,t2.value
            from {dv_idc_name} as t1 
            left join {dv_summary} as t2 
            on t1.indicator=t2.indicator and t1.name=t2.name 
            order by t1.name,t1.row_num
            """
        )

        base_opt = {
            "tooltip": {},
            "series": [],
            "radar": {
                "indicator": pbi.sql(
                    f"select indicator as name,max from {dv_indicator}"
                ).js_map("return rows")
            },
        }

        base_opt.update(opts)

        data_query = pbi.sql(f"select * from {dv_data}").split_group(
            "name",
            """
const value = rows.map(r=> r.value)
return {name:key,value}      
                """,
        )

        base_opt["series"].append(
            {
                "type": "radar",
                "data": data_query,
                # "universalTransition": {"enabled": True, "divideShape": "clone"},
                "areaStyle": {"opacity": 0.1},
            }
        )

        return base_opt, self._updateInfos, []
