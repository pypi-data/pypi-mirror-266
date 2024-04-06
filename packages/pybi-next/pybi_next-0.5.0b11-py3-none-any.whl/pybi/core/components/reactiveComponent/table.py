from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional, Union


from pybi.core.components import ComponentTag
from .base import SingleReactiveComponent


if TYPE_CHECKING:
    from pybi.core.sql import SqlInfo


_TColumnprops = Dict[str, Dict[str, Any]]


class Table(SingleReactiveComponent):
    def __init__(
        self,
        sql: SqlInfo,
    ) -> None:
        super().__init__(ComponentTag.Table, sql)
        self.pageSize = 10
        self.tableHeight = "initial"
        self.tableWidth = "initial"
        self.column_props: _TColumnprops = {}
        self._showCopyButton: Optional[bool] = None

    def show_copy_button(self):
        self._showCopyButton = True
        return self

    def set_page_size(self, size: int):
        """
        设置表格每页行数
        size: >=5 ,默认10
        """
        self.pageSize = max(size, 5)
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
        """配置每列的属性。可配置的属性参考[table columns 文档](https://element-plus.org/zh-CN/component/table.html#table-column-%E5%B1%9E%E6%80%A7)

        Args:
            props (_TColumnprops): 每列的配置项。格式:`{列名:配置项字典}`


        ### 使用
        >>>
        ```python
        col_props = {
            "日期": {"width": "500px", "sortable": True},
            "计数单位": {"width": "200px", "sortable": True},
        }
        pbi.add_table(dv1).set_column_props(col_props)
        ```
        """
        self.column_props.update(props)
        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if len(self.column_props):
            data["columnProps"] = self.column_props

        if self._showCopyButton:
            data["showCopyButton"] = self._showCopyButton

        return data
