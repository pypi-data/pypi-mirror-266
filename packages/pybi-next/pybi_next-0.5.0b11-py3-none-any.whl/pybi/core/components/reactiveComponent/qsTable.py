from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional
from pybi.core.actions import ActionInfo


from pybi.core.components import ComponentTag
from pybi.core.components.component import Component
from pybi.core.components.containerComponent import ContainerComponent
from .base import SingleReactiveComponent
import pybi as pbi

if TYPE_CHECKING:
    from pybi.core.sql import SqlInfo
    from pybi.app import App


_TColumnprops = Dict[str, Dict[str, Any]]


class QsTable(SingleReactiveComponent):
    def __init__(
        self,
        sql: SqlInfo,
        appHost: App,
    ) -> None:
        super().__init__(ComponentTag.QsTable, sql, appHost)
        self.set_page_size(10)
        self.tableHeight = "initial"
        self.tableWidth = "initial"
        self.column_props: _TColumnprops = {}
        self._showCopyButton: Optional[bool] = None
        self._topSlot: ContainerComponent = ContainerComponent("temp", appHost=appHost)  # type: ignore

    @property
    def top_slot(self):
        return self._topSlot

    def set_page_size(self, size: int):
        """
        设置表格每页行数
        size: >=5 ,默认10
        """
        self.pageSize = max(size, 5)
        if "pagination" not in self._props:
            self.set_props({"pagination": {"rowsPerPage": self.pageSize}})

        else:
            self._props["pagination"].update({"rowsPerPage": self.pageSize})

        return self

    def set_table_height(self, height="initial"):
        """
        表格高度
        height: 'initial'(默认值),'30em','30%','30vh'
        如果设置为initial,则表格会以展示一页所有数据的高度作为固定高度
        """
        self.tableHeight = height
        return self

    def set_table_width(self, width="initial"):
        """
        表格高度
        width: 'initial'(默认值),'30em','30%','30vh'
        """
        self.tableWidth = width
        return self

    def set_props(self, props: Dict):
        """设置表格属性。可配置的属性参考[Table 属性](https://element-plus.org/zh-CN/component/table.html#table-%E5%B1%9E%E6%80%A7)

        Args:
            props (Dict): 属性键值对

        ### 使用
        >>>
        ```python
        pbi.add_table(dv1).set_props({"show-summary": True})
        ```
        """
        return super().set_props(props)

    def set_column_props(self, props: _TColumnprops):
        """配置每列的属性。可配置的属性参考[table columns 文档](http://www.quasarchs.com/vue-components/table#%E5%AE%9A%E4%B9%89%E5%88%97)

        Args:
            props (_TColumnprops): 每列的配置项。格式:`{列名:配置项字典}`


        ### 使用
        >>>
        ```python
        col_props = {
            "日期": {"style": "width:500px", "sortable": True},
            "计数单位": {"style": "width:200px", "sortable": True},
        }
        pbi.add_table(dv1).set_column_props(col_props)
        ```
        """
        self.column_props.update(props)
        return self

    @property
    def actions(self):
        return TableActions(self)

    def add_visible_columns_slicer(self):
        assert self._appHost
        cp = VisibleColumnsSlicer(self)
        host = self._appHost._get_temp_host() or self._appHost
        assert host
        host._add_children(cp)

        return cp

    def default_top_slot(
        self,
        title: Optional[str] = None,
        copy_button_label="copy",
        visible_columns=True,
        toggle_fullscreen=False,
    ):
        with self.top_slot:
            with pbi.box():
                if title:
                    pbi.add_text(title)

                with pbi.flowBox():
                    if visible_columns:
                        self.add_visible_columns_slicer()

                    pbi.space()

                    if copy_button_label:
                        pbi.add_button(copy_button_label).bind_action(
                            self.actions.copy_to_clipboard_by_excel_format
                        )

                    if toggle_fullscreen:
                        pbi.add_button().bind_action(
                            self.actions.toggleFullscreen
                        ).set_props(
                            {
                                "flat": True,
                                "round": True,
                                "dense": True,
                                "icon": "fullscreen",
                            }
                        )

        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if len(self.column_props):
            data["columnProps"] = self.column_props

        if self._showCopyButton:
            data["showCopyButton"] = self._showCopyButton

        if len(self._topSlot.children):
            data["topSlot"] = self._topSlot.children

        return data


class VisibleColumnsSlicer(Component):
    def __init__(self, table: QsTable, *, appHost: App | None = None) -> None:
        super().__init__("VisibleColumnsSlicer", appHost=appHost)  # type: ignore
        self.tableId = table.id


class TableActions:
    def __init__(self, table: QsTable) -> None:
        self._table = table

    @property
    def copy_to_clipboard_by_excel_format(self):
        return ActionInfo(self._table.id, "copy_to_clipboard_by_excel_format")

    @property
    def toggleFullscreen(self):
        return ActionInfo(self._table.id, "toggleFullscreen")
