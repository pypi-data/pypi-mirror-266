from pybi.utils.data_gen import Jsonable, get_global_id


from typing import Optional


class StyleTagInfo(Jsonable):
    def __init__(
        self, css: str, id: Optional[str] = None, media: Optional[str] = None
    ) -> None:
        self.css = css
        self._media = media
        self._id = id

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._media:
            data["media"] = self._media

        if self._id:
            data["id"] = self._id
        return data
