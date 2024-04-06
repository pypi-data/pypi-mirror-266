import base64
from pathlib import Path


class ImgManager:
    def __init__(self) -> None:
        self.__id_number = 0
        self._mapping = {}
        self._img_bs64_to_id = {}

    def _create_id(self):
        id = f"img_{self.__id_number}"
        self.__id_number = self.__id_number + 1
        return id

    def mark_img(self, file_path: Path) -> str:
        b64_str = base64.b64encode(file_path.read_bytes()).decode("utf-8")

        id = self._img_bs64_to_id.get(b64_str, None)

        if id is None:
            id = self._create_id()

            img_b64 = f"data:image/png;base64,{b64_str}"
            self._mapping[id] = img_b64

            self._img_bs64_to_id[b64_str] = id

        return id

    def create_resource(self):
        return [{"id": key, "bs64": value} for key, value in self._mapping.items()]
