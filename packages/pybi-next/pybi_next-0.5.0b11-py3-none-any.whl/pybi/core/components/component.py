from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Union, Dict


from pybi.utils.data_gen import Jsonable, get_global_id
from pybi.utils.helper import style_text2dict
from .componentTag import ComponentTag
from pybi.core.styles.styles import StyleBuilder

if TYPE_CHECKING:
    from pybi.app import App
    from pybi.core.styles.styles import Style
    from pybi.core.sql import SqlWrapper


class Component(Jsonable):
    def __init__(self, tag: ComponentTag, *, appHost: Optional[App] = None) -> None:
        self.id = get_global_id()
        self.tag = tag
        self._debugTag: Optional[str] = None
        self._styles: List[Style] = []
        self.visible: Union[bool, SqlWrapper] = True
        self.__gridArea: str = ""
        self._props = {}
        self.classes = []

        self._appHost = appHost

    def set_props(self, props: Dict):
        self._props.update(props)
        return self

    def set_debugTag(self, tag: str):
        self._debugTag = tag
        return self

    def set_classes(self, value: str):
        """
        set_classes('text-primary bg-positive')
        """
        values = (v for v in value.split(" ") if v)
        self.classes.extend(values)
        return self

    def set_gridArea(self, area_name: str):
        self.__gridArea = area_name
        return self

    def set_style(self, content: str):
        """添加样式

        Args:
            content (str): 样式字符串,多个样式用分号相隔

        ### 示例
        >>> .set_style('color: #6E93D6; font-size: 200%; font-weight: 300')
        """
        styles = style_text2dict(content)

        self._styles.append(StyleBuilder(styles))
        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()
        styles_dict = {}
        for style in self._styles:
            styles_dict.update(style._get_styles_dict())
        data["styles"] = styles_dict

        if isinstance(self.visible, bool) and self.visible == True:
            del data["visible"]

        if self.__gridArea:
            data["gridArea"] = self.__gridArea

        data["debugTag"] = self._debugTag
        data["props"] = self._props
        data["classes"] = list(dict.fromkeys(data["classes"]).keys())

        return data

    def __add__(self, other: Style):
        self._styles.append(other)
        return self

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, self.__class__):
            return hash(__o.id) == hash(self.id)

        return False
