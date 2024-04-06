from __future__ import annotations
from typing import Dict, Callable
import pybi.utils.data_gen as data_gen
import jinja2
from pathlib import Path

# TODO:
_pj_root = data_gen.get_project_root()
_static_path = _pj_root / "static"


def _get_file_path_from_static(file_name: str):
    return str(_static_path / file_name)


def js_online_resource(src: str):
    def fn():
        return f'<script src="{src}"></script>'

    return fn


def js_offline_resource(path: str, id=""):
    def fn():
        return f'<script id="{id}">{Path(path).read_text("utf8")}</script>'

    return fn


def css_online_resource(href: str):
    def fn():
        return f'<link rel="stylesheet" type="text/css" href="{href}">'

    return fn


def css_offline_resource(path: str, id=""):
    def fn():
        return f'<style id="{id}">{Path(path).read_text("utf8")}</style>'

    return fn


def empty_resource():
    def fn():
        return ""

    return fn


TResource = Callable


_system_resources: Dict[str, TResource] = {
    "sysApp": js_offline_resource(
        _get_file_path_from_static("sysApp.iife.js"), id="sysApp"
    ),
    "sysApp-css": css_offline_resource(
        _get_file_path_from_static("sysApp-style.css"), id="sysApp-css"
    ),
    "vue-js": js_offline_resource(
        _get_file_path_from_static("vue.global.prod.min.js"), id="vue-js"
    ),
    "echarts-js": js_offline_resource(
        _get_file_path_from_static("echarts.min.js"), id="echarts-js"
    ),
}


_env = jinja2.Environment(loader=jinja2.PackageLoader("pybi", "template"))
_html_template = _env.get_template("index.html")


class ResourceManager:
    def __init__(self):
        pass
        # self.system_resources =
        self.sysApp_css = _system_resources["sysApp-css"]
        self.sysApp_js = _system_resources["sysApp"]
        self.vue_js = _system_resources["vue-js"]

        self.echarts_core_js = empty_resource()
        self.echarts_cps_js = empty_resource()
        self.echarts_cps_css = empty_resource()

        self.element_cps_js = empty_resource()
        self.element_cps_css = empty_resource()

        self.material_icons_css = empty_resource()

        self.quasar_cps_js = empty_resource()
        self.quasar_cps_css = empty_resource()
        self.quasar_core_js = empty_resource()
        self.quasar_core_css = empty_resource()
        self.quasar_lang_zh_js = empty_resource()

        self.mermaid_cps_js = empty_resource()
        self.mermaid_cps_css = empty_resource()

        self.experimental_cps_js = empty_resource()

        self.zip_js = None

    def register_echarts(self):
        self.echarts_cps_js = js_offline_resource(
            _get_file_path_from_static("echartsCps.iife.js"), id="echartsCps-js"
        )
        self.echarts_cps_css = css_offline_resource(
            _get_file_path_from_static("echartsCps-style.css"), id="echartsCps-style"
        )
        self.echarts_core_js = js_offline_resource(
            _get_file_path_from_static("echarts.min.js"), id="echarts-js"
        )
        return self

    def register_material_icons(self):
        self.material_icons_css = css_offline_resource(
            _get_file_path_from_static("material_icons.css"), id="material_icons-style"
        )

    def register_quasar_cps(self):
        self.quasar_cps_js = js_offline_resource(
            _get_file_path_from_static("quasarCps.iife.js"), id="quasarCps-js"
        )
        self.quasar_cps_css = css_offline_resource(
            _get_file_path_from_static("quasarCps-style.css"), id="quasarCps-style"
        )
        self.quasar_core_js = js_offline_resource(
            _get_file_path_from_static("quasar.umd.prod.js"), id="quasar-js"
        )
        self.quasar_core_css = css_offline_resource(
            _get_file_path_from_static("quasar.prod.css"), id="quasar-css"
        )
        self.register_material_icons()
        self.quasar_lang_zh_js = js_offline_resource(
            _get_file_path_from_static("quasar.lang.zh-CN.umd.prod.js"),
            id="quasar.lang.zh-CN.umd.prod.js",
        )
        return self

    def register_element_cps(self):
        self.element_cps_js = js_offline_resource(
            _get_file_path_from_static("elementCps.iife.js"), id="elementCps-js"
        )
        self.element_cps_css = css_offline_resource(
            _get_file_path_from_static("elementCps-style.css"), id="elementCps-style"
        )
        return self

    def register_experimental_cps(self):
        self.experimental_cps_js = js_offline_resource(
            _get_file_path_from_static("experimentalCps.iife.js"),
            id="experimentalCps-js",
        )
        # self.experimental_cps_css = css_offline_resource(
        #     _get_file_path_from_static("experimentalCps-style.css"),
        #     id="experimentalCps-style",
        # )
        return self

    def register_mermaid_cps(self):
        self.mermaid_cps_js = js_offline_resource(
            _get_file_path_from_static("mermaidCps.iife.js"), id="mermaidCps-js"
        )

        self.mermaid_cps_css = css_offline_resource(
            _get_file_path_from_static("mermaidCps-style.css"), id="mermaidCps-style"
        )

        return self

    def build_html(self, appConfig: str) -> str:
        res = _html_template.render(app_config=appConfig, resources=self)
        assert isinstance(res, str)
        return res
