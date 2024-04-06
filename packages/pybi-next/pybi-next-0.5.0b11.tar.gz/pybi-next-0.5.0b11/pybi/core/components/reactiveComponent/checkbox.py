from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict


from pybi.core.components import ComponentTag
from .base import SingleReactiveComponent


if TYPE_CHECKING:
    from pybi.core.sql import SqlInfo


class Checkbox(SingleReactiveComponent):
    def __init__(self, sql: SqlInfo) -> None:
        super().__init__(ComponentTag.Checkbox, sql)
        self.title = ""
        self.mode = "tile"
        self.multiple = True
        self.itemDirection = "row"
        self.__hidden_title = None

    def set_itemDirection(self, value="row"):
        """选项排列方向

        Args:
            value (str, optional): 'row' | 'column' . Defaults to "row".
        """
        self.itemDirection = value
        return self

    def set_width(self, value: str):
        """设置宽度

        Args:
            value (str): css width的可能值.[参考文档](https://developer.mozilla.org/zh-CN/docs/Web/CSS/width)

        ## 示例
        ```python
        # 200px , 20em, 20vw
        pbi.add_checkbox(data["name"]).set_width('200px')
        ```
        """
        self.set_style(f"width:{value}")
        return self

    def set_height(self, value: str):
        """设置高度

        Args:
            value (str): css width的可能值.[参考文档](https://developer.mozilla.org/zh-CN/docs/Web/CSS/height)

        ## 示例
        ```python
        # 200px , 20em, 20vh
        pbi.add_checkbox(data["name"]).set_height('200px')
        ```

        """
        self.set_style(f"height:{value}")
        return self

    def set_mode(self, mode="tile"):
        """选项显示模式

        Args:
            mode (str, optional): 'tile' | 'list'. Defaults to 'tile'.
            'tile':磁贴模式,选项以磁贴方式显示
            'list':普通checkbox方式

        """
        self.mode = mode
        return self

    def set_hiddenTitle(self, value=True):
        """
        不显示标题
        """
        self.__hidden_title = value
        return self

    def set_title(self, title: str):
        self.title = title
        return self

    def set_multiple(self, multiple: bool):
        self.multiple = multiple
        return self

    def set_props(self, props: Dict):
        """
        [checkbox props](https://element-plus.org/zh-CN/component/checkbox.html#checkboxgroup-attributes)
        e.g
        >>> .add_checkbox(...).set_props({'min':2})
        """
        return super().set_props(props)

    def _to_json_dict(self):
        data = super()._to_json_dict()
        if self.__hidden_title:
            data["hiddenTitle"] = self.__hidden_title

        return data
