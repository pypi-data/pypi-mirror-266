from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict


from pybi.core.components import ComponentTag
from .base import ReactiveComponent


if TYPE_CHECKING:
    from pybi.core.sql import SqlInfo


class QsInput(ReactiveComponent):
    def __init__(self, where_expr: str) -> None:
        super().__init__(ComponentTag.QsInput)
        self.whereExpr = where_expr

    def set_props(self, props: Dict):
        """
        [input props](http://www.quasarchs.com/vue-components/input#qinput-api)
        e.g
        >>> .add_input(...).set_props({'placeholder':'my define placeholder'})
        """
        return super().set_props(props)
