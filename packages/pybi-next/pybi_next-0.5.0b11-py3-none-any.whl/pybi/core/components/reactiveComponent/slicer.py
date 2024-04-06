from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict


from pybi.core.components import ComponentTag
from .base import SingleReactiveComponent


if TYPE_CHECKING:
    from pybi.core.sql import SqlInfo


class Slicer(SingleReactiveComponent):
    def __init__(self, sql: SqlInfo) -> None:
        super().__init__(ComponentTag.Slicer, sql)
        self.title = ""
        self.multiple = True
        self.__hidden_title = None
        self.__default_selected = None

    def set_title(self, title: str):
        self.title = title
        return self

    def _set_default_selected(self, value=True):
        """
        首次显示时，默认选中第一项
        """
        self.__default_selected = value
        return self

    def set_hiddenTitle(self, value=True):
        """
        不显示标题
        """
        self.__hidden_title = value
        return self

    def set_multiple(self, multiple: bool):
        self.multiple = multiple
        return self

    def set_props(self, props: Dict):
        """
        [slicer props](https://element-plus.gitee.io/zh-CN/component/select.html#select-attributes)
        e.g
        >>> .add_slicer(...).set_props({'placeholder':'my define placeholder'})
        """
        return super().set_props(props)

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self.__hidden_title:
            data["hiddenTitle"] = self.__hidden_title

        if self.__default_selected:
            data["defaultSelected"] = self.__default_selected
        return data
