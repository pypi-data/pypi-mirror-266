from __future__ import annotations
from .line import LineChart
from .bar import BarChart
from .pie import PieChart
from .scatter import ScatterChart
from .map import MapChart
from .candlestick import CandleStickChart
from .radar import RadarChart
from .dictChart import OptionsDictChart
from typing import TYPE_CHECKING, Dict, Optional
import pybi as pbi

if TYPE_CHECKING:
    from pybi.core.dataSource import DataSourceTable


__all__ = ["easy_echarts"]


class EasyEChartsSettings:
    def __init__(self) -> None:
        self.drill_down_default_set_click_filter = True


class EasyEChartsMeta:
    def __init__(self) -> None:
        self._settings = EasyEChartsSettings()

    def off_drill_down_default_set_click_filter(self):
        """
        默认情况下,多个组合图表配置会自动为其每个图表添加 `click_filter` 联动。
        此函数调用后,会关闭其功能
        """
        self._settings.drill_down_default_set_click_filter = False

    def make_by_dict(self, options_dict: Dict):
        return OptionsDictChart(options_dict)

    def make_line(
        self,
        data: DataSourceTable,
        x: str,
        y: str,
        color: Optional[str] = None,
        agg="round(avg(${}),2)",
        order: Optional[str] = None,
    ):
        order = order or x
        return LineChart(data, x, y, order, color, agg)

    def make_bar(
        self,
        data: DataSourceTable,
        *,
        x: str,
        y: str,
        color: Optional[str] = None,
        agg="round(avg(${}),2)",
        order: Optional[str] = None,
    ):
        order = order or x
        return BarChart(data, x, y, order, color, agg)

    def make_pie(
        self,
        data: DataSourceTable,
        *,
        name: str,
        value: str,
        agg="round(avg(${}),2)",
    ):
        return PieChart(data, name, value, agg)

    def make_scatter(
        self,
        data: DataSourceTable,
        *,
        x: str,
        y: str,
        color: Optional[str] = None,
        agg="round(avg(${}),2)",
    ):
        return ScatterChart(data, x, y, color, agg)

    def make_map(self, level="province"):
        return MapChart(level)

    def make_candleStick(
        self,
        data: DataSourceTable,
        *,
        date="date",
        open="open",
        close="close",
        lowest="lowest",
        highest="highest",
    ):
        """
        candleStick 即我们常说的 K线图
        [date,open, close, lowest, highest] (即：[日期, 开盘值, 收盘值, 最低值, 最高值])
        """
        return CandleStickChart(data, date, open, close, lowest, highest)

    def make_radar(
        self,
        data: DataSourceTable,
        *,
        indicator="indicator",
        name="name",
        value="value",
        agg="round(avg(${}),2)",
    ):
        """
        雷达图
        ---
        indicator:雷达图的指示器，用来指定雷达图中的多个变量（维度）
        name:数据项名称
        value:具体的数据，每个值跟 indicator 一一对应。
        ---
        示例：
        ```python
        data = pd.DataFrame(
            {
                "指标": ["A", "B", "C", "D", "E", "F", "A", "B", "C", "D", "F"],
                "值": [8150, 1035, 3393, 7919, 4244, 6237, 3537, 5676, 8306, 6388, 3889],
                "类别": ["X", "X", "X", "X", "X", "X", "Y", "Y", "Y", "Y", "Y"],
            }
        )

        data = pbi.set_source(data)
        pbi.add_table(data)
        opts = charts.make_radar(data, indicator="指标", name="类别", value="值")
        pbi.add_echart(opts).set_height("30em")
        ```
        """
        return RadarChart(data, indicator, name, value, agg)


easy_echarts = EasyEChartsMeta()
