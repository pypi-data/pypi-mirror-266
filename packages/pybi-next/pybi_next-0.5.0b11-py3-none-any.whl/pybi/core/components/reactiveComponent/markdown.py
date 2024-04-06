from __future__ import annotations
from typing import TYPE_CHECKING, List, Union
from pybi.utils.markdown2 import markdown


from pybi.core.components import ComponentTag
from .base import ReactiveComponent


if TYPE_CHECKING:
    from pybi.core.sql import SqlInfo


class Markdown(ReactiveComponent):
    def __init__(self, contexts: List[Union[str, SqlInfo]]) -> None:
        super().__init__(ComponentTag.Markdown)
        self.contexts = contexts

    def _to_json_dict(self):
        data = super()._to_json_dict()

        # data["html"] = markdown(
        #     self._md, extras=["fenced-code-blocks", "task_list", "code-color"]
        # )
        return data
