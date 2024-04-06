# from .styles import *
from .tailwindStyles.textColor import TextColor
from .tailwindStyles.boxShadow import BoxShadow
from .tailwindStyles.textSize import TextSize
from .tailwindStyles.textAlign import TextAlign

from functools import lru_cache

__all__ = ["styles"]


class StylesMeta:
    @property
    @lru_cache(1)
    def textColor(self):
        return TextColor()

    @property
    @lru_cache(1)
    def boxShadow(self):
        return BoxShadow()

    @property
    @lru_cache(1)
    def textSize(self):
        return TextSize()

    @property
    @lru_cache(1)
    def textAlign(self):
        return TextAlign()


styles = StylesMeta()


# text_color = textColor
