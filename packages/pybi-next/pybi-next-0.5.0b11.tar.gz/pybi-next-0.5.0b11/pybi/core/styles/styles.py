from __future__ import annotations
from typing import TYPE_CHECKING, Union, List, Callable, Dict

if TYPE_CHECKING:
    from pybi.core.components.component import Component


class Style:
    def __init__(self) -> None:
        self._dict_fn: List[Callable] = []

    def _copyFrom(self, other: Style):
        self._dict_fn.extend(other._dict_fn)
        return self

    def __add__(self, other: Style):
        new = Style()
        new._copyFrom(self)
        new._copyFrom(other)
        return new

    def _get_styles_dict(self):
        data = {}
        for fn in self._dict_fn:
            data.update(fn())

        return data


class StyleBuilder(Style):
    def __init__(self, data_dict: Dict) -> None:
        super().__init__()

        def fn():
            return data_dict

        self._dict_fn.append(fn)


class width(Style):
    def __init__(self, value: Union[str, int]) -> None:
        super().__init__()

        def fn():
            return {"width": value}

        self._dict_fn.append(fn)


class border(Style):
    """https://developer.mozilla.org/zh-CN/docs/Web/CSS/border"""

    def __init__(self, value="1px solid #000") -> None:
        super().__init__()

        def fn():
            return {"border": value}

        self._dict_fn.append(fn)


class borderRadius(Style):
    """https://developer.mozilla.org/zh-CN/docs/Web/CSS/border-radius"""

    def __init__(self, value="0.25rem") -> None:
        super().__init__()

        def fn():
            return {"border-radius": value}

        self._dict_fn.append(fn)


class padding(Style):
    """https://developer.mozilla.org/zh-CN/docs/Web/CSS/padding"""

    def __init__(self, value="0.8em") -> None:
        super().__init__()

        def fn():
            return {"padding": value}

        self._dict_fn.append(fn)


class textAlign(Style):
    """https://developer.mozilla.org/zh-CN/docs/Web/CSS/text-align"""

    def __init__(self, value="left") -> None:
        super().__init__()

        def fn():
            return {"text-align": value}

        self._dict_fn.append(fn)


class background(Style):
    """https://developer.mozilla.org/zh-CN/docs/Web/CSS/background"""

    def __init__(self, value="inherit") -> None:
        super().__init__()

        def fn():
            return {"background": value}

        self._dict_fn.append(fn)


class color(Style):
    """https://developer.mozilla.org/zh-CN/docs/Web/CSS/color"""

    def __init__(self, value="inherit") -> None:
        super().__init__()

        def fn():
            return {"color": value}

        self._dict_fn.append(fn)


class fontWeight(Style):
    """https://developer.mozilla.org/zh-CN/docs/Web/CSS/font-weight"""

    def __init__(self, value="400") -> None:
        super().__init__()

        def fn():
            return {"font-weight": value}

        self._dict_fn.append(fn)


class fontSize(Style):
    """https://developer.mozilla.org/zh-CN/docs/Web/CSS/font-size"""

    def __init__(self, value="1rem") -> None:
        super().__init__()

        def fn():
            return {"font-size": value}

        self._dict_fn.append(fn)


class lineHeight(Style):
    """https://developer.mozilla.org/zh-CN/docs/Web/CSS/line-height"""

    def __init__(self, value="1.5rem") -> None:
        super().__init__()

        def fn():
            return {"line-height": value}

        self._dict_fn.append(fn)
