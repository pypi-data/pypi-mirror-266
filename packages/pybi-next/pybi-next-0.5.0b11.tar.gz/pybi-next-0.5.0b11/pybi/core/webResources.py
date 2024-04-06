import pybi.utils.data_gen as data_gen
from pathlib import Path
import simplejson as json

# TODO:
_pj_root = data_gen.get_project_root()
_static_path = _pj_root / "static"


def load_province_data():
    return json.loads(Path(_static_path / "province_map_full.json").read_bytes())


class WebResourceManager:
    def __init__(self) -> None:
        self.echarts_map_names = set()
        self.wrs = []

    def mark_echarts_map(self, map_name: str, online=False):
        if map_name in self.echarts_map_names:
            return

        base_wr = {
            "id": map_name,
            "type": "echarts-map",
        }

        if online:
            base_wr.update(
                **{
                    "input": None,
                    "actionPipe": [
                        {
                            "name": "fetch",
                            "args": {
                                "url": "https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json",
                                "options": {},
                            },
                        }
                    ],
                }
            )
            return

        base_wr.update(
            **{
                "input": load_province_data(),
            }
        )

        self.wrs.append(base_wr)
        self.echarts_map_names.add(map_name)

    def create_webResources(self):
        return self.wrs
