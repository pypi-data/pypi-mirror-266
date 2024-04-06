from __future__ import annotations
from pybi.core.components.component import Component
from .componentTag import ComponentTag
import re

from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from pybi.core.actions import ActionInfo


class TextComponent(Component):
    def __init__(self, content: str) -> None:
        super().__init__(ComponentTag.Text)
        self.content = content


class UploadComponent(Component):
    def __init__(self) -> None:
        super().__init__(ComponentTag.Upload)


class SvgIconComponent(Component):
    replace_svg_size_pat = re.compile(r"(width|height)=.+?\s", re.I | re.DOTALL)

    def __init__(self, svg: str, size: str, color: str) -> None:
        super().__init__(ComponentTag.SvgIcon)

        svg = SvgIconComponent.replace_svg_size_pat.sub("", svg)
        self.svg = svg
        self.size = size
        self.color = color


class IconComponent(Component):
    def __init__(
        self,
        name: str,
        size: Optional[str] = None,
        color: Optional[str] = None,
    ) -> None:
        super().__init__(ComponentTag.Icon)

        self.set_props({"name": name})
        if size:
            self.set_props(({"size": size}))

        if color:
            self.set_props(({"color": color}))


class SpaceComponent(Component):
    def __init__(
        self,
    ) -> None:
        super().__init__(ComponentTag.Space)


class ButtonComponent(Component):
    def __init__(
        self,
        label: Optional[str] = None,
    ) -> None:
        super().__init__(ComponentTag.QsButton)

        if label is not None:
            self.set_props({"label": label})
        self._action: Optional[ActionInfo] = None

    def bind_action(self, action_info: ActionInfo):
        """绑定动作，当点击按钮时，可以执行指定的操作

        @中文文档: https://gitee.com/carson_add/pybi-next#button-bind_action

        Args:
            action_info (ActionInfo): 待绑定的动作

        Returns:
            _type_: 按钮组件
        """
        self._action = action_info
        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._action:
            data["action"] = self._action

        return data


class ImgComponent(Component):
    def __init__(
        self,
        resource_id: str,
    ) -> None:
        super().__init__(ComponentTag.Img)

        self.src = {"id": resource_id}
