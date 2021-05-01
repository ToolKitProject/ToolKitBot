import config
from libs import src
from libs.src import other as _src_type


class UserText:
    def __init__(self, lang: str) -> None:
        if lang in config.lang_encode:
            self.lang = lang
        else:
            self.lang = "other"

        self.src: _src_type = getattr(src, self.lang)
        self.text = self.src.text
        self.buttons = self.src.buttons

    @property
    def encode_lang(self) -> str:
        return config.lang_encode[self.lang]
