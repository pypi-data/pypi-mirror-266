from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Union, List, Optional
from typing_extensions import Literal

from pybi.core.sql import ForeachRowInfo
from pybi.core.actions import ActionInfo


from .componentTag import ComponentTag
from .component import Component
from pybi.icons.iconManager import get_singleton as get_iconManager

if TYPE_CHECKING:
    from pybi.app import App
    from pybi.core.sql import SqlInfo


class ContainerComponent(Component):
    def __init__(
        self,
        tag: ComponentTag,
        appHost: Optional[App] = None,
        childredHook: Optional[ContainerComponent] = None,
    ) -> None:
        super().__init__(tag, appHost=appHost)

        self._childredHook = childredHook
        self.children: List[Component] = []

    def _add_children(self, stat: Component):
        if self._childredHook:
            self._childredHook._add_children(stat)
        else:
            self.children.append(stat)
        return self

    def __enter__(self):
        if self._appHost:
            self._appHost._with_temp_host_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self._appHost:
            self._appHost._with_temp_host_stack.pop()


class BoxComponent(ContainerComponent):
    m_align_mapping = {
        "left": "flex-start",
        "center": "center",
        "right": "flex-end",
        "stretch": "stretch",
    }

    m_vertical_align_mapping = {
        "top": "flex-start",
        "center": "center",
        "bottom": "flex-end",
        "between": "space-between",
        "around": "space-around",
    }

    def __init__(
        self,
        align: Optional[str] = None,
        vertical_align: Optional[str] = None,
        appHost: Optional[App] = None,
    ) -> None:
        """
        Args:
            align (Optional[str], optional): 'left' | 'center' | 'right'. Defaults to None.
            vertical_align (Optional[str], optional): 'top' | 'center' | 'bottom'. Defaults to None.
        """
        super().__init__(ComponentTag.Box, appHost)
        self._align = align
        self._vertical_align = vertical_align

    def _to_json_dict(self):
        data = super()._to_json_dict()
        if self._align:
            data["align"] = self.m_align_mapping[self._align]

        if self._vertical_align:
            data["verticalAlign"] = self.m_vertical_align_mapping[self._vertical_align]

        return data


class FlowBoxComponent(ContainerComponent):
    m_align_mapping = {
        "left": "flex-start",
        "center": "center",
        "right": "flex-end",
        "between": "space-between",
        "around": "space-around",
        "evenly": "space-evenly",
        "stretch": "stretch",
    }

    def __init__(
        self, align: Optional[str] = None, appHost: Optional[App] = None
    ) -> None:
        """
        Args:
            align (Optional[str], optional): 'left' | 'center' | 'right'. Defaults to None.
        """
        super().__init__(ComponentTag.FlowBox, appHost)
        self._align = align

    def __get_item__(self, idx: int):
        return self.children[idx]

    def _to_json_dict(self):
        data = super()._to_json_dict()
        if self._align:
            data["align"] = self.m_align_mapping[self._align]

        return data


class GridBoxComponent(ContainerComponent):
    m_align_mapping = {
        "left": "flex-start",
        "center": "center",
        "right": "flex-end",
        "stretch": "stretch",
    }

    m_vertical_align_mapping = {
        "top": "flex-start",
        "center": "center",
        "bottom": "flex-end",
        "between": "space-between",
        "around": "space-around",
    }

    def __init__(
        self,
        areas: Optional[List[List[str]]] = None,
        align: Optional[str] = None,
        vertical_align: Optional[str] = None,
        appHost: Optional[App] = None,
    ) -> None:
        super().__init__(ComponentTag.GridBox, appHost)
        self.__areas = areas
        self.__columns_sizes: List[str] = []
        self.__rows_sizes: List[str] = []
        self.__gridTemplateColumns = None

        self._align = align
        self._vertical_align = vertical_align

    def set_columns_sizes(self, sizes: List[Union[str, int]]):
        """
        >>> set_columns_sizes([1,2,2])
        >>> set_columns_sizes(['150px','1fr','2fr'])
        >>> set_columns_sizes(['150px','1fr','minmax(100px, 1fr)'])
        """
        self.__columns_sizes = [f"{s}fr" if isinstance(s, int) else s for s in sizes]
        return self

    def set_rows_sizes(self, sizes: List[Union[str, int]]):
        """
        >>> set_rows_sizes([1,2,2])
        >>> set_rows_sizes(['150px','1fr','2fr'])
        >>> set_rows_sizes(['150px','1fr','minmax(100px, 1fr)'])
        """
        self.__rows_sizes = [f"{s}fr" if isinstance(s, int) else s for s in sizes]
        return self

    def __get_item__(self, idx: int):
        return self.children[idx]

    def auto_fill_by_width(self, width="15em"):
        """动态调整每行组件数量，每个组件固定宽度为指定 `width`。
        当设置有效 grid areas 时，此设置无效

        Args:
            width (str, optional): 每个组件固定宽度. Defaults to "15em".

        """

        width_value = f"minmax(0, {width})"
        self.__gridTemplateColumns = f"repeat(auto-fill, {width_value})"
        self.set_style("justify-content: space-between")
        return self

    def auto_fill_by_num(self, num=3):
        """自动调整每行组件宽度，每行组件数量为 `num`。
        当设置有效 grid areas 时，此设置无效

        Args:
            num (int, optional): 每行组件数量. Defaults to 3.

        """
        self.__gridTemplateColumns = f"repeat({num}, 1fr)"
        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self.__areas:
            data["areas"] = GridBoxComponent.areas_array2str(self.__areas)

            areas_cols_len = max(map(len, self.__areas))
            cols_size = GridBoxComponent.padded_grid_template(
                self.__columns_sizes, areas_cols_len, "1fr"
            )

            areas_rows_len = len(self.__areas)
            rows_size = GridBoxComponent.padded_grid_template(
                self.__rows_sizes, areas_rows_len
            )

            data["gridTemplateColumns"] = " ".join(cols_size)
            data["gridTemplateRows"] = " ".join(rows_size)
        else:
            if self.__gridTemplateColumns:
                data["gridTemplateColumns"] = self.__gridTemplateColumns

        if self._align:
            data["align"] = self.m_align_mapping[self._align]

        if self._vertical_align:
            data["verticalAlign"] = self.m_vertical_align_mapping[self._vertical_align]

        return data

    @staticmethod
    def padded_grid_template(sizes: List[str], real_size: int, pad="auto"):
        """
        >>> sizes = ['1fr']
        >>> real_size = 3
        >>> padded_grid_template(sizes,real_size)
        >>> ['1fr','auto','auto']
        """
        diff_len = real_size - len(sizes)
        sizes = sizes.copy()

        if diff_len > 0:
            sizes.extend([pad] * diff_len)
        return sizes

    @staticmethod
    def areas_array2str(areas_array: List[List[str]]):
        """
        >>> input = [
            ["sc1", "sc2"],
            ["sc3"],
            ["table"] * 4
        ]
        >>> areas_array2str(input)
        >>> '"sc1 sc2 . ." "sc3 . . ." "table table table table"'
        """
        max_len = max(map(len, areas_array))

        fix_empty = (
            [*line, *(["."] * (max_len - len(line)))] if len(line) < max_len else line
            for line in areas_array
        )

        line2str = (f'"{" ".join(line)}"' for line in fix_empty)
        return " ".join(line2str)

    @staticmethod
    def areas_str2array(areas: str) -> List[List[str]]:
        """
        >>> input='''
            sc1 sc2
            sc3
            table table table table
        '''
        >>> areas_str2array(input)
        >>> [
            ["sc1", "sc2"],
            ["sc3"],
            ["table", "table", "table", "table"]
        ]
        """
        pass

        lines = (line.strip() for line in areas.splitlines())
        remove_empty_rows = (line for line in lines if len(line) > 0)
        splie_space = (line.split() for line in remove_empty_rows)
        return list(splie_space)


class TabsComponent(ContainerComponent):
    def __init__(self, names: List[str], appHost: Optional[App] = None) -> None:
        """
        mode: 'fullWidth' | 'narrowing'
        """
        super().__init__(ComponentTag.Tabs, appHost)
        if len(names) > len(set(names)):
            raise Exception("names cannot be duplicated")
        self.names = names
        self.__icons = []
        self.tabsProps = {}
        self.panelsProps = {}
        self.tabsClasses: List[str] = []
        self.panelsClasses: List[str] = []

        self.__name2idx = {name: idx for idx, name in enumerate(self.names)}

        for _ in range(len(self.names)):
            self._add_children(BoxComponent(appHost=appHost))

    def __getitem__(self, idx: Union[int, str]):
        if isinstance(idx, str):
            if idx not in self.__name2idx:
                raise Exception(f"tab name[{idx}] not found")
            idx = self.__name2idx[idx]

        res = self.children[idx]
        assert isinstance(res, ContainerComponent)
        return res

    def set_icons(self, icons: List[str]):
        self.__icons = icons

        self.set_tabsProps({"inline-label": len(icons) > 0})
        return self

    def set_tabsProps(self, props: Dict):
        self.tabsProps.update(props)
        return self

    def set_panelsProps(self, props: Dict):
        self.panelsProps.update(props)
        return self

    def set_tabsClasses(self, value: str):
        """
        set_tabsClasses('text-primary bg-positive')
        """
        values = (v for v in value.split(" ") if v)
        self.tabsClasses.extend(values)
        return self

    def set_panelsClasses(self, value: str):
        """
        set_panelsClasses('text-primary bg-positive')
        """
        values = (v for v in value.split(" ") if v)
        self.panelsClasses.extend(values)
        return self

    def set_tab_position(self, position: _T_TAB_POSITION):
        self.__tab_position = position
        return self

    def set_props(self, props: Dict):
        return self.set_tabsProps(props)

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["tabsClasses"] = list(dict.fromkeys(data["tabsClasses"]).keys())
        data["panelsClasses"] = list(dict.fromkeys(data["panelsClasses"]).keys())

        icon_ids = []
        for icon in self.__icons:
            icon_id = get_iconManager().make_icon(icon)
            icon_ids.append(icon_id)

        data["iconIds"] = icon_ids

        return data


_T_TAB_POSITION = Literal["left", "right", "top", "bottom"]


class QsTabsComponent(ContainerComponent):
    def __init__(self, names: List[str], appHost: Optional[App] = None) -> None:
        """ """
        super().__init__(ComponentTag.QsTabs, appHost)
        if len(names) > len(set(names)):
            raise Exception("names cannot be duplicated")
        self.names = names
        self.__icons = []
        self.tabsProps = {}
        self.panelsProps = {}
        self.tabsClasses: List[str] = []
        self.panelsClasses: List[str] = []
        self.tabsStyles = {}
        self.panelsStyles = {}
        self.__tab_position: Optional[_T_TAB_POSITION] = None

        self.__name2idx = {name: idx for idx, name in enumerate(self.names)}

        for _ in range(len(self.names)):
            self._add_children(BoxComponent(appHost=appHost))

    def __getitem__(self, idx: Union[int, str]):
        if isinstance(idx, str):
            if idx not in self.__name2idx:
                raise Exception(f"tab name[{idx}] not found")
            idx = self.__name2idx[idx]

        res = self.children[idx]
        assert isinstance(res, ContainerComponent)
        return res

    def set_tab_position(self, position: _T_TAB_POSITION):
        self.__tab_position = position
        return self

    def set_icons(self, icons: List[str]):
        self.__icons = icons
        return self

    def set_tabsProps(self, props: Dict):
        self.tabsProps.update(props)
        return self

    def set_tabsStyles(self, styles: Dict):
        self.tabsStyles.update(styles)
        return self

    def set_panelsStyles(self, styles: Dict):
        self.panelsStyles.update(styles)
        return self

    def set_panelsProps(self, props: Dict):
        self.panelsProps.update(props)
        return self

    def set_tabsClasses(self, value: str):
        """
        set_tabsClasses('text-primary bg-positive')
        """
        values = (v for v in value.split(" ") if v)
        self.tabsClasses.extend(values)
        return self

    def set_panelsClasses(self, value: str):
        """
        set_panelsClasses('text-primary bg-positive')
        """
        values = (v for v in value.split(" ") if v)
        self.panelsClasses.extend(values)
        return self

    def set_props(self, props: Dict):
        return self.set_tabsProps(props)

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["tabsClasses"] = list(dict.fromkeys(data["tabsClasses"]).keys())
        data["panelsClasses"] = list(dict.fromkeys(data["panelsClasses"]).keys())

        data["icons"] = self.__icons

        if self.__tab_position:
            data["tabPosition"] = self.__tab_position

        return data


class AffixComponent(ContainerComponent):
    def __init__(self, appHost: Optional[App] = None) -> None:
        super().__init__(ComponentTag.Affix, appHost)
        box = BoxComponent(appHost=appHost)
        self._add_children(box)
        self._childredHook = box


class DynamicBoxComponent:
    def __init__(self, grid_box: GridBoxComponent) -> None:
        self.__grid_box = grid_box

    def set_each_row_num(self, num: int):
        pass

    def set_each_width(self, width: str):
        pass


class ForeachBoxComponent(ContainerComponent):
    def __init__(self, sql: SqlInfo, appHost: Optional[App] = None) -> None:
        super().__init__(ComponentTag.Foreach, appHost)
        self.sql = sql

    def __getitem__(self, field: str):
        return ForeachRowInfo(field)


class SizebarComponent(ContainerComponent):
    def __init__(self, appHost: Optional[App] = None) -> None:
        super().__init__(ComponentTag.Sizebar, appHost)


class DrawerActions:
    def __init__(self, drawer: QsDrawerComponent) -> None:
        self._drawer = drawer

    @property
    def switch_show(self):
        return ActionInfo(self._drawer.id, "switch_show")


class QsDrawerComponent(ContainerComponent):
    def __init__(self, appHost: Optional[App] = None, value: bool = False) -> None:
        super().__init__(ComponentTag.Drawer, appHost)
        self._value = value

    @property
    def actions(self):
        return DrawerActions(self)

    def _to_json_dict(self):
        data = super()._to_json_dict()

        data.update({"value": self._value})
        return data
