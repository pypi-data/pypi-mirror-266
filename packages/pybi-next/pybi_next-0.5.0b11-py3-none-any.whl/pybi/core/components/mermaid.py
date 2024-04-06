from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Union, Dict
from pybi.core.components.component import Component


from pybi.utils.data_gen import Jsonable, get_global_id
from .componentTag import ComponentTag


class Mermaid(Component):
    def __init__(self, graph: str, name) -> None:
        super().__init__(ComponentTag.Mermaid)
        # self.graph = graph
        self.__graph_infos = [{"graph": graph, "name": name}]
        self.__relationships = []

    def add_graph(self, graph: str, name: str):
        self.__graph_infos.append({"graph": graph, "name": name})
        return self

    def set_relationship(self, rel_str: str):
        '''
        例子：
        ```python
        mm = pbi.add_mermaid(
            """
        graph TB
        FullFirstSquad-->StripedFirstSquad
        """,'main')

        mm.add_graph(
            """
            flowchart LR
        A[Hard] -->|Text| B(Round)
        B --> C{Decision}
        C -->|One| D[Result 1]
        C -->|Two| E[Result 2]
        """
            "g2",
        )

        # main 流程图的节点 FullFirstSquad，点击后跳转到 g2 流程图
        mm.set_relationship("main.FullFirstSquad>g2")
        ```


        '''
        # parent = 'g1'
        # other = 'g>g2'
        parent, other = rel_str.split(".")
        node, child = other.split(">")

        return self.__set_relationship(parent, node, child)

    def __set_relationship(
        self, parent_graph_name: str, node_name: str, child_graph_name: str
    ):
        self.__relationships.append(
            {"parent": parent_graph_name, "node": node_name, "child": child_graph_name}
        )
        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["graphInfos"] = self.__graph_infos

        data["relationships"] = self.__relationships

        return data
