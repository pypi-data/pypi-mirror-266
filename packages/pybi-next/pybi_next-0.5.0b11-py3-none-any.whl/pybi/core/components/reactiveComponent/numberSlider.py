from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict


from pybi.core.components import ComponentTag
from .base import ReactiveComponent


class NumberSlider(ReactiveComponent):
    def __init__(self, where_expr: str) -> None:
        super().__init__(ComponentTag.NumberSlider)
        self.whereExpr = where_expr

    def set_props(self, props: Dict):
        """
        [slider props](https://element-plus.gitee.io/zh-CN/component/slider.html#%E5%B1%9E%E6%80%A7)
        e.g
        >>> .add_numberSlider(...).set_props({'show-stops':True})
        """
        return super().set_props(props)
