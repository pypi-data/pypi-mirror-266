class IconManager:
    def __init__(self) -> None:
        self.__id_number = 0
        self.__mapping_svg_id = {}

    def _create_id(self):
        id = f"icon_{self.__id_number}"
        self.__id_number = self.__id_number + 1
        return id

    def make_icon(self, svg_content: str):
        if not svg_content in self.__mapping_svg_id:
            self.__mapping_svg_id[svg_content] = self._create_id()

        return self.__mapping_svg_id[svg_content]

    def get_infos(self):
        infos = [{"id": id, "svg": svg} for svg, id in self.__mapping_svg_id.items()]

        return infos


__singleton = IconManager()


def get_singleton():
    return __singleton
