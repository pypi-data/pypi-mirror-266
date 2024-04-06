from __future__ import annotations


from .base import BaseChart
import pybi as pbi
import pybi.utils.sql as sqlUtils


from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from pybi.core.dataSource import DataSourceTable


class OptionsDictChart(BaseChart):
    def __init__(self, options_dict: Dict):
        super().__init__()
        self.options_dict = options_dict

    def _create_options_ex(self):
        return self.options_dict, self._updateInfos, []
