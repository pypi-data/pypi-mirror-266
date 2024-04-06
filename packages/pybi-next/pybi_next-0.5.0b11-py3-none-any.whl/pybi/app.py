from __future__ import annotations
from pathlib import Path

from pybi.core import DataSource
import pandas as pd

from typing import Dict, List, Optional, Union
import os
from pybi.core.actions import ActionInfo

from pybi.core.components import (
    ContainerComponent,
    ComponentTag,
    BoxComponent,
    ForeachBoxComponent,
    FlowBoxComponent,
    SizebarComponent,
    UploadComponent,
    GridBoxComponent,
    TabsComponent,
    Markdown,
    IconComponent,
    AffixComponent,
    Mermaid,
    Input,
    NumberSlider,
    SpaceComponent,
    Checkbox,
    ButtonComponent,
    ImgComponent,
)
from pybi.core.components.containerComponent import QsDrawerComponent, QsTabsComponent
from pybi.core.components.reactiveComponent import EChart, Slicer, Table, TextValue
from pybi.core.components.reactiveComponent.qsSlicer import QsSlicer
from pybi.core.components.reactiveComponent.qsTable import QsTable
from pybi.core.components.reactiveComponent.qsInput import QsInput

from pybi.core.dataSource import (
    DataSourceField,
    DataSourceTable,
    DataView,
    DataViewBase,
    PivotDataView,
)
from pybi.utils.dataSourceUtils import ds2sqlite_file_base64, ds2sqlite
from pybi.utils.data_gen import (
    JsonUtils,
    random_ds_name,
    random_dv_name,
    get_project_root,
)
from pybi.utils.markdown2 import markdown
from pybi.core.uiResource import ResourceManager

from pybi.core.sql import SqlInfo, SqlWrapper, ForeachRowInfo, extract_sql_text
import pybi.utils.sql as sqlUtils
from pybi.easyEcharts.base import BaseChart, ChartCollector
from pybi.easyEcharts import easy_echarts
from pybi.core.components.reactiveComponent.echarts import (
    EChartInfo,
    EChartDatasetInfo,
    EChartJscode,
    OptionsExtractor,
)
import pybi.utils.pyecharts_utils as pyecharts_utils
from pybi.core.imgManager import ImgManager
from pybi.core.webResources import WebResourceManager
from pybi.core.styles.styleTag import StyleTagInfo
import pybi as pbi


class AppMeta:
    def __init__(self, app: App) -> None:
        self.__app = app

    def set_dbLocalStorage(self, on: bool):
        """
        是否开启数据库本地缓存
        """
        self.__app.dbLocalStorage = on
        return self

    def set_echarts_renderer(self, renderer="canvas"):
        """
        echarts renderer type: 'canvas' or 'svg'
        'canvas' is default
        """
        self.__app.echartsRenderer = renderer
        return self

    def set_doc_title(self, title: str):
        self.__app._doc_title = title
        return self

    def add_style_tag(
        self, css: str, id: Optional[str] = None, media: Optional[str] = None
    ):
        self.__app._style_tags.append(StyleTagInfo(css, id, media))
        return self


class AppActions:
    def __init__(self, app: "App") -> None:
        self._app = app

    @property
    def reset_filters(self):
        """清除页面所有筛选器"""
        return ActionInfo("app", "reset_filters")


class App(ContainerComponent):
    def __init__(self) -> None:
        super().__init__(ComponentTag.App)
        self.dataSources: List[DataSource] = []
        self.dataViews: List[DataViewBase] = []
        self.__dataSetNames = set()
        self._with_temp_host_stack: List[ContainerComponent] = []
        self._clear_data = False
        self.dbLocalStorage = False
        self.echartsRenderer = "canvas"
        self._doc_title: Optional[str] = None
        self.__meta = AppMeta(self)
        self.__json_utils = JsonUtils()
        self._resourceManager = ResourceManager()
        self._resourceManager.register_quasar_cps()
        self._img_manager = ImgManager()

        self.__webResourceManager = WebResourceManager()
        self.webResources = []
        self._style_tags: List[StyleTagInfo] = []
        self.drawer: Optional[QsDrawerComponent] = None
        self.__actions = AppActions(self)

    def __record_and_check_dataset_name(self, name: str):
        if name in self.__dataSetNames:
            raise Exception(f"dataset name '{name}' is duplicate")
        self.__dataSetNames.add(name)

    @property
    def meta(self):
        return self.__meta

    @property
    def actions(self):
        """全局动作，用于绑定到支持执行 action 的组件(例如按钮组件)"""
        return self.__actions

    def clear_all_data(self):
        self._clear_data = True

    def _get_temp_host(self):
        if self._with_temp_host_stack:
            return self._with_temp_host_stack[len(self._with_temp_host_stack) - 1]
        return None

    def set_source(self, data: pd.DataFrame, *, name: Optional[str] = None):
        name = name or random_ds_name()
        self.__record_and_check_dataset_name(name)

        ds = DataSource(name, data)
        self.dataSources.append(ds)
        return DataSourceTable(ds.name, data.columns.tolist(), host=self)

    def set_dataView(
        self,
        sql: str,
        exclude_source: Optional[List[DataSourceTable]] = None,
        *,
        name: Optional[str] = None,
    ):
        exclude_source = exclude_source or []
        name = name or random_dv_name()
        self.__record_and_check_dataset_name(name)
        dv = DataView(name, sql)

        for es in exclude_source:
            dv.exclude_source(es.source_name)

        self.dataViews.append(dv)
        return DataSourceTable(
            dv.name, sqlUtils.extract_fields_head_select(sql), host=self
        )

    def set_pivot_dataView(
        self,
        source: str,
        row: str,
        column: str,
        cell: str,
        agg="min",
        exclude_source: Optional[List[DataSourceTable]] = None,
        excludeRowFields=False,
        *,
        name: Optional[str] = None,
    ):
        exclude_source = exclude_source or []
        name = name or random_dv_name()
        self.__record_and_check_dataset_name(name)
        pdv = PivotDataView(name, source, row, column, cell, agg, excludeRowFields)

        for es in exclude_source:
            pdv.exclude_source(es.source_name)

        self.dataViews.append(pdv)
        return DataSourceTable(pdv.name, [], host=self)

    def sql(self, sql: str):
        return SqlWrapper(sql)

    def add_upload(
        self,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        cp = UploadComponent()

        host = host or self._get_temp_host() or self
        host._add_children(cp)

        self._resourceManager.register_element_cps()
        return cp

    def add_text(
        self,
        text: Union[str, SqlWrapper, ForeachRowInfo],
        *,
        host: Optional[ContainerComponent] = None,
    ):
        if isinstance(text, (SqlWrapper, ForeachRowInfo)):
            text = str(text)

        contexts = list(extract_sql_text(text))

        cp = TextValue(contexts)

        host = host or self._get_temp_host() or self
        host._add_children(cp)

        return cp

    def add_checkbox(
        self,
        field: Union[DataSourceField, DataSourceTable],
        *,
        orderby: Optional[str] = "1",
        host: Optional[ContainerComponent] = None,
    ):
        """
        orderby:
            Defaults '1' : select distinct colA from data order by 1
            `None`:  select distinct colA from data
            '1 desc' : select distinct colA from data order by 1 desc
            'colX desc' : select distinct colA from data order by colX desc
        """
        if isinstance(field, DataSourceTable):
            field = field[field.columns[0]]

        assert isinstance(field, DataSourceField)
        orderSql = "" if orderby is None else f"order by {orderby}"
        sql = f"select distinct {field._get_sql_field_name()} from {field.source_name} {orderSql}"
        cp = Checkbox(SqlInfo(sql))
        cp.title = field.name
        cp.add_updateInfo(field.source_name, field._get_sql_field_name())

        host = host or self._get_temp_host() or self
        host._add_children(cp)

        # self.__resourceManager.register_element_cps()
        return cp

    def add_echart(
        self,
        options: Union[Dict, BaseChart, ChartCollector],
        *,
        host: Optional[ContainerComponent] = None,
    ):
        cp = None

        if not isinstance(options, (BaseChart, ChartCollector, dict)):
            from pyecharts.charts.base import Base

            if isinstance(options, Base):
                options = options.get_options()
                assert isinstance(options, dict)
                pyecharts_utils.replace_jscode(options)
                #
                self.__json_utils.mark_pyecharts()

        if isinstance(options, (BaseChart, ChartCollector)):
            opts = options

            if isinstance(opts, BaseChart):
                opts = ChartCollector().append(opts)

            cp = EChart(option_type="dict")

            if (
                len(opts._collector) > 1
                and easy_echarts._settings.drill_down_default_set_click_filter
            ):
                for chart in opts._collector:
                    chart._create_default_click_filter()

            for chart in opts._collector:
                opts, updateInfos, mapIds = chart.get_options_infos()

                ds_infos = []
                jscodes = []

                OptionsExtractor.extract_and_remove_from_dict(opts, ds_infos, jscodes)

                ds_infos = [
                    EChartDatasetInfo({}, path, sql._sql_info) for path, sql in ds_infos
                ]

                jscodes = [EChartJscode(path, jscode) for path, jscode in jscodes]

                for map_name in mapIds:
                    self.__webResourceManager.mark_echarts_map(map_name)

                info = EChartInfo(
                    opts, ds_infos, updateInfos, jscodes, mapIds, chart._merge_opt
                )
                cp._add_chart_info(info)

        elif isinstance(options, dict):
            cp = EChart(option_type="dict")

            ds_infos = []
            jscodes = []

            OptionsExtractor.extract_and_remove_from_dict(options, ds_infos, jscodes)

            ds_infos = [
                EChartDatasetInfo({}, path, sql._sql_info) for path, sql in ds_infos
            ]

            jscodes = [EChartJscode(path, jscode) for path, jscode in jscodes]

            info = EChartInfo(options, ds_infos, [], jscodes)
            cp._add_chart_info(info)

        host = host or self._get_temp_host() or self

        assert cp is not None
        host._add_children(cp)

        self._resourceManager.register_echarts()
        return cp

    def flowBox(
        self,
        align: Optional[str] = None,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """行容器，里面的组件会横向放置，在超过屏幕宽度时，自动换行

        Args:
            align (Optional[str], optional): 容器中的元素组件靠向哪个位置。'left' | 'center' | 'right' | 'between' | 'around' |'evenly' |'stretch'. Defaults to None('left').

                - left : 从行首起始位置开始排列
                - center:居中排列
                - right:从行尾位置开始排列
                - between: 均匀排列每个元素,首个元素放置于起点，末尾元素放置于终点
                - around:  均匀排列每个元素,每个元素周围分配相同的空间
                - evenly:  均匀排列每个元素, 每个元素之间的间隔相等

        ## 示例

        >>> # 2个文本放置在同一行，并且靠左放置
        >>> with pbi.flowBox():
                pbi.add_text('text A')
                pbi.add_text('text B')

        >>> # 2个文本放置在同一行，并且居中放置
        >>> with pbi.flowBox('center'):
                pbi.add_text('text A')
                pbi.add_text('text B')
        """
        cp = FlowBoxComponent(align=align, appHost=self)

        host = host or self._get_temp_host() or self
        host._add_children(cp)

        return cp

    def gridBox(
        self,
        areas: Union[List[List[str]], str],
        align: Optional[str] = None,
        vertical_align: Optional[str] = None,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """网格布局

        Args:
            areas (Union[List[List[str]], str]): 网格布局文本
        ---
        ### 示例
        ```python
        grid='''
            a b c
            a e .
        '''

        with pbi.gridBox(grid):
            pbi.add_slicer(...).set_gridArea('a')
            pbi.add_slicer(...).set_gridArea('b')
        ```


        当 `areas` 设置为 '' 时,默认为动态布局，每行放置3格
        ```python
        with pbi.gridBox(''):
            # 3个切片器在第1行
            pbi.add_slicer(...)
            pbi.add_slicer(...)
            pbi.add_slicer(...)

            # 2个切片器在第2行
            pbi.add_slicer(...)
            pbi.add_slicer(...)
        ```

        可以通过 `auto_fill_fixed_num` 修改动态配置

        >>> with pbi.gridBox('').auto_fill_fixed_num(2):
                ...

        """
        if isinstance(areas, str):
            areas = GridBoxComponent.areas_str2array(areas)

        cp = GridBoxComponent(areas, align, vertical_align, self)

        if len(areas) == 0:
            cp.auto_fill_by_num()

        host = host or self._get_temp_host() or self
        host._add_children(cp)

        return cp

    def colBox(
        self,
        spec: List[int] | None = None,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        spec = spec or [1, 1]
        grid_text = " ".join(f"x{n}" for n in range(len(spec)))
        cp = self.gridBox(grid_text).set_columns_sizes(spec)  # type: ignore

        return cp

    def box(
        self,
        align: Optional[str] = None,
        vertical_align: Optional[str] = None,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """盒容器，里面的组件竖向放置

        Args:
            align (Optional[str], optional): 容器中的元素组件横向靠哪个位置。
                'left' | 'center' | 'right' | 'between' | 'around' |'evenly'|'stretch'. Defaults to None('left').

                - left : 从行首起始位置开始排列
                - center:居中排列
                - right:从行尾位置开始排列

            vertical_align (Optional[str], optional): 容器中的元素垂直方向靠哪个位置。
                'top' | 'center' | 'bottom' | 'between' | 'around' . Defaults to None('top').

                - top : 靠顶部
                - center:居中
                - bottom:靠底部
                - between:项目在行与行之间留有间隔
                - around:项目在行之前、行之间和行之后留有空间

        ## 示例

        """
        cp = BoxComponent(align=align, vertical_align=vertical_align, appHost=self)
        host = host or self._get_temp_host() or self
        host._add_children(cp)
        return cp

    def foreach(
        self,
        sql: str,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """ """

        cp = ForeachBoxComponent(sql=pbi.sql(sql)._sql_info, appHost=self)
        host = host or self._get_temp_host() or self
        host._add_children(cp)
        return cp

    def save_zip_db(self, path: str):
        with open(path, mode="w", encoding="utf8") as f:
            f.write(ds2sqlite_file_base64(self.dataSources))

    def save_db(self, path: str):
        if Path(path).exists():
            os.remove(path)
        ds2sqlite(path, self.dataSources)

    def _to_json_dict(self):
        self.webResources.append(
            {
                "id": "DbFile",
                "type": "DbFile",
                "input": ds2sqlite_file_base64(
                    self.dataSources, clear_data=self._clear_data
                ),
                "actionPipe": [],
            }
        )

        wrs = self.__webResourceManager.create_webResources()
        self.webResources.extend(wrs)

        data = super()._to_json_dict()

        if self._doc_title:
            data["docTitle"] = self._doc_title

        if self._style_tags:
            data["styleTags"] = self._style_tags

        data["version"] = pbi.__version__

        data["imgResources"] = self._img_manager.create_resource()

        return data

    def __reset_data(self):
        """support for run on ipython env"""
        self.children = []
        self.dataSources = []
        self.dataViews = []

    def to_json(self, *args, **kws):
        return self.__json_utils.dumps(self, *args, **kws)
        # return json_dumps_fn(self, indent=2, ensure_ascii=False)

    def to_raw_html(self):
        try:
            symbol = '"__{{__config_data__}}___"'

            config = self.__json_utils.dumps(self)

            with open(
                get_project_root() / "template/index.html", mode="r", encoding="utf8"
            ) as html:
                res = html.read().replace(symbol, config)
                return res
        except Exception as e:
            raise e
        else:
            self.__reset_data()

    def to_html(self, file, display_output_path=False):
        try:
            file = Path(file)
            # raw = self.to_raw_html()

            raw = self._resourceManager.build_html(self.to_json())
            file.write_text(raw, "utf8")

            if display_output_path:
                print(f"to html:{file.absolute()}")
        except Exception as e:
            raise e
        else:
            self.__reset_data()

    def add_markdown(
        self,
        md: str,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        # if isinstance(md, SqlWrapper):
        #     md = str(md)
        md = SqlInfo.around_backticks(md)

        html = markdown(
            md,
            extras=[
                "fenced-code-blocks",
                "target-blank-links",
                "task_list",
                "code-color",
                "tag-friendly",
            ],
        )

        contents = list(SqlInfo.extract_sql_from_text(html))

        cp = Markdown(contents)

        host = host or self._get_temp_host() or self
        host._add_children(cp)

        return cp

    def add_mermaid(
        self,
        graph: str,
        name="main",
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """
        [mermaid文档](https://github.com/mermaid-js/mermaid/blob/develop/README.zh-CN.md)
        ---
        >>> graph = '''
        flowchart LR
        A[Hard] -->|Text| B(Round)
        B --> C{Decision}
        C -->|One| D[Result 1]
        C -->|Two| E[Result 2]
        '''
        >>> add_mermaid(graph)
        """
        cp = Mermaid(graph, name)
        host = host or self._get_temp_host() or self
        host._add_children(cp)

        self._resourceManager.register_mermaid_cps()
        return cp

    def space(
        self,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """迫使后续的组件往右靠
        ---
        >>> pbi.space()
        """
        cp = SpaceComponent()
        host = host or self._get_temp_host() or self
        host._add_children(cp)

        return cp


class ElementUi:
    def __init__(self, app: App) -> None:
        self.__app = app
        self.__has_sizebar = False

    def add_slicer(
        self,
        field: Union[DataSourceField, DataSourceTable],
        *,
        orderby: Optional[str] = None,
        host: Optional[ContainerComponent] = None,
    ):
        """
        orderby:
            Defaults `None`:  select distinct colA from data
            '1' : select distinct colA from data order by 1
            '1 desc' : select distinct colA from data order by 1 desc
            'colX desc' : select distinct colA from data order by colX desc
        """
        if isinstance(field, DataSourceTable):
            field = field[field.columns[0]]

        assert isinstance(field, DataSourceField)
        orderSql = "" if orderby is None else f"order by {orderby}"
        sql = f"select distinct {field._get_sql_field_name()} from {field.source_name} {orderSql}"
        cp = Slicer(SqlInfo(sql))
        cp.title = field.name
        cp.add_updateInfo(field.source_name, field._get_sql_field_name())

        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_element_cps()
        return cp

    def add_table(
        self,
        dataSourceTable: DataSourceTable,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        sql = ""
        if dataSourceTable._user_specified_field:
            sql = dataSourceTable._to_sql()
        else:
            sql = f"select * from {dataSourceTable.source_name}"
        cp = Table(SqlInfo(sql))

        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_element_cps()
        return cp

    def sizebar(
        self,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        raise NotImplementedError('sizebar not supported in "element-ui"')

    def add_tabs(
        self,
        names: List[str],
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """ """
        cp = TabsComponent(names, appHost=self.__app)
        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_element_cps()
        return cp

    def affix(
        self,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        cp = AffixComponent(self.__app)
        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_element_cps()
        return cp

    def add_input(
        self,
        field: Union[DataSourceField, DataSourceTable],
        where_expr="like '%${}%'",
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """ """
        if isinstance(field, DataSourceTable):
            field = field[field.columns[0]]

        assert isinstance(field, DataSourceField)

        cp = Input(where_expr).add_updateInfo(field.source_name, field.name)
        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_element_cps()
        return cp

    def add_numberSlider(
        self,
        data: DataSourceTable,
        field: str,
        where_expr=" between ${0} and ${1}",
        range=True,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """ """
        cp = (
            NumberSlider(where_expr)
            .add_updateInfo(data.source_name, field)
            .set_props({"range": range})
        )
        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_element_cps()
        return cp


class Quasar:
    def __init__(self, app: App) -> None:
        self.__app = app

    def add_button(
        self,
        label: Optional[str] = None,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """按钮组件

        Args:
            label (Optional[str], optional): 按钮文字. Defaults to None.

        Returns:
            _type_: 按钮组件
        """

        cp = ButtonComponent(label)

        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_quasar_cps()
        return cp

    def add_img(
        self,
        file: Union[str, Path],
        *,
        host: Optional[ContainerComponent] = None,
    ):
        r"""添加图片.
        具体属性可以参考文档:
        [点击打开文档](http://www.quasarchs.com/vue-components/img#qimg-api)

        Args:
            file (Union[str, Path]): 图片文件路径

        ---

        ```python
        pbi.add_img(r"C:\temp\t1.png").set_props(
            {"width": "20rem", "height": "20rem", "fit": "contain"}
        )
        ```

        """
        file_path = Path(file)
        img_id = self.__app._img_manager.mark_img(file_path)

        cp = ImgComponent(img_id)

        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_quasar_cps()
        return cp

    def add_table(
        self,
        dataSourceTable: DataSourceTable,
        *,
        title: Optional[str] = None,
        host: Optional[ContainerComponent] = None,
    ):
        sql = ""
        if dataSourceTable._user_specified_field:
            sql = dataSourceTable._to_sql()
        else:
            sql = f"select * from {dataSourceTable.source_name}"
        cp = QsTable(SqlInfo(sql), self.__app)

        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        if title:
            with cp.top_slot:
                with pbi.box():
                    pbi.add_text("test cp top slot")

                    with pbi.flowBox():
                        pbi.add_button("copy").bind_action(
                            cp.actions.copy_to_clipboard_by_excel_format
                        )
                        pbi.space()
                        cp.add_visible_columns_slicer()
                        pbi.add_button().bind_action(
                            cp.actions.toggleFullscreen
                        ).set_props(
                            {
                                "flat": True,
                                "round": True,
                                "dense": True,
                                "icon": "fullscreen",
                            }
                        )

        self.__app._resourceManager.register_quasar_cps()
        return cp

    def add_slicer(
        self,
        field: Union[DataSourceField, DataSourceTable],
        *,
        orderby: Optional[str] = None,
        host: Optional[ContainerComponent] = None,
    ):
        """
        orderby:
            Defaults `None`:  select distinct colA from data
            '1' : select distinct colA from data order by 1
            '1 desc' : select distinct colA from data order by 1 desc
            'colX desc' : select distinct colA from data order by colX desc
        """
        if isinstance(field, DataSourceTable):
            field = field[field.columns[0]]

        assert isinstance(field, DataSourceField)
        orderSql = "" if orderby is None else f"order by {orderby}"
        sql = f"select distinct {field._get_sql_field_name()} from {field.source_name} {orderSql}"
        cp = QsSlicer(SqlInfo(sql))
        cp.title = field.name
        cp.add_updateInfo(field.source_name, field._get_sql_field_name())

        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_quasar_cps()
        return cp

    def add_icon(
        self,
        name: str,
        size: Optional[str] = None,
        color: Optional[str] = None,
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """ """

        cp = IconComponent(name, size, color)

        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_quasar_cps()

        return cp

    def add_input(
        self,
        field: Union[DataSourceField, DataSourceTable],
        where_expr="like '%${}%'",
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """ """
        if isinstance(field, DataSourceTable):
            field = field[field.columns[0]]

        assert isinstance(field, DataSourceField)

        cp = QsInput(where_expr).add_updateInfo(field.source_name, field.name)
        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_element_cps()
        return cp

    def add_tabs(
        self,
        names: List[str],
        *,
        host: Optional[ContainerComponent] = None,
    ):
        """ """
        cp = QsTabsComponent(names, appHost=self.__app)
        host = host or self.__app._get_temp_host() or self.__app
        host._add_children(cp)

        self.__app._resourceManager.register_quasar_cps()
        return cp

    def drawer(self, value: bool = True):
        """侧边栏

        具体属性可以参考文档:
        [点击打开文档](http://www.quasarchs.com/layout/drawer)


        ## 示例

        ```python
        with pbi.drawer():
            pbi.add_slicer(data["name"])
        ```

        """

        cp = QsDrawerComponent(appHost=self.__app, value=value)
        app = self.__app
        app.drawer = cp
        self.__app._resourceManager.register_quasar_cps()
        return cp
