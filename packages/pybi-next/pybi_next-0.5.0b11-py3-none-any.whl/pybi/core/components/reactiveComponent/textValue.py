from __future__ import annotations
from typing import List, Union, TYPE_CHECKING


from pybi.core.components import ComponentTag
from .base import ReactiveComponent


if TYPE_CHECKING:
    from pybi.core.sql import SqlInfo, ForeachRowInfo


class TextValue(ReactiveComponent):
    def __init__(self, contexts: List[Union[str, SqlInfo, ForeachRowInfo]]) -> None:
        super().__init__(ComponentTag.TextValue)
        self.contexts = contexts
