from pybi.utils.data_gen import Jsonable


class ActionInfo(Jsonable):
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
