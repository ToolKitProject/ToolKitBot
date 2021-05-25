import lang_conf


class UserText:
    def __init__(self, lang: str):
        if lang in lang_conf.lang_map:
            self.lang = lang
        else:
            self.lang = "other"

        self.src = lang_conf.lang_map[self.lang]
        self.text = self.src.text
        self.buttons = self.src.buttons

    @property
    def encode_lang(self) -> str:
        return lang_conf.lang_map[self.lang]
