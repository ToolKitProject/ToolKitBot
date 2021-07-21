from aiogram import types as t


class UserText:
    def __init__(self):
        import lang_conf
        user = t.User.get_current()
        lang = user.language_code

        if user.id == 486680241:
            lang = "other"

        if lang in lang_conf.lang_map:
            self.lang = lang
        else:
            self.lang = "other"

        self.src = lang_conf.lang_map[self.lang]
        self.text = self.src.text
        self.buttons = self.src.buttons
        self.any = self.src.any
