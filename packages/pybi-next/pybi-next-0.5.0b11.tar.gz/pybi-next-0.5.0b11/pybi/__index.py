from pybi.core.components.reactiveComponent.echarts import EChartJsCode
from .app import App, Quasar, ElementUi
from typing_extensions import Literal

# import pybi.core.styles as styles
from pybi.core.styles import *
from pybi.easyEcharts import *


app = App()
quasar_ui = Quasar(app)
element_ui = ElementUi(app)


__all__ = [
    "actions",
    "preset_ui",
    "quasar_ui",
    "element_ui",
    "set_source",
    "add_slicer",
    "add_table",
    "add_echart",
    "add_text",
    "colBox",
    "flowBox",
    "gridBox",
    "box",
    "app",
    "styles",
    "easy_echarts",
    "echartJsCode",
    "to_json",
    "sql",
    "set_dataView",
    "to_html",
    "clear_all_data",
    "add_upload",
    "_save_db",
    "meta",
    "save_zip_db",
    "add_tabs",
    "add_markdown",
    "add_icon",
    "affix",
    "add_mermaid",
    "add_input",
    "add_numberSlider",
    "space",
    "foreach",
    "drawer",
    "add_checkbox",
    "add_button",
    "add_img",
]

PRESET_UI = Literal["element-plus", "quasar"]


def preset_ui(ui: PRESET_UI):
    import pybi

    if ui == "element-plus":
        pybi.add_slicer = element_ui.add_slicer
        pybi.add_table = element_ui.add_table
        pybi.add_tabs = element_ui.add_tabs
        # pybi.sidebar = element_ui.sidebar
        pybi.affix = element_ui.affix
        pybi.add_input = element_ui.add_input
        pybi.add_numberSlider = element_ui.add_numberSlider

    if ui == "quasar":
        pybi.add_slicer = quasar_ui.add_slicer
        pybi.add_table = quasar_ui.add_table
        pybi.add_input = quasar_ui.add_input
        pybi.add_tabs = quasar_ui.add_tabs
        pybi.drawer = quasar_ui.drawer
        # pybi.affix = quasar_ui.affix
        # pybi.add_numberSlider = quasar_ui.add_numberSlider


add_tabs = quasar_ui.add_tabs
meta = app.meta
actions = app.actions
gridBox = app.gridBox
set_source = app.set_source
add_upload = app.add_upload
add_text = app.add_text
add_slicer = quasar_ui.add_slicer
add_table = quasar_ui.add_table
add_button = quasar_ui.add_button
add_img = quasar_ui.add_img
add_echart = app.add_echart
colBox = app.colBox
flowBox = app.flowBox
echartJsCode = EChartJsCode
box = app.box
to_json = app.to_json
set_dataView = app.set_dataView
sql = app.sql
clear_all_data = app.clear_all_data
_save_db = app.save_db
save_zip_db = app.save_zip_db

to_html = app.to_html
add_markdown = app.add_markdown
add_icon = quasar_ui.add_icon
affix = element_ui.affix
add_mermaid = app.add_mermaid
add_input = quasar_ui.add_input
add_numberSlider = element_ui.add_numberSlider
space = app.space

foreach = app.foreach
drawer = quasar_ui.drawer
add_checkbox = app.add_checkbox
