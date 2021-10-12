from __future__ import annotations

import typing as p
import uuid
from copy import deepcopy

from .buttons import Menu, Button, Submenu


class Settings:
    title: str
    row_width: int
    undo: bool

    parameters: "ParameterType"

    def __init__(self, title: str, row_width: int = 1, undo: bool = False):
        self.title = title
        self.row_width = row_width
        self.undo = undo

        self.parameters = []

    def menu(self,
             settings: "SettingsType",
             text: str | None = None,
             callback_data: str | None = None) -> Menu | Submenu:
        buttons: list[Button, Submenu] = []
        if text and callback_data:
            menu = Submenu(self.title, text, str(callback_data) + "@" + str(uuid.uuid4())[0:8], self.row_width,
                           undo=self.undo)
        else:
            menu = Menu(self.title, self.row_width, undo=self.undo)

        for param in self.parameters:  # Create buttons
            if isinstance(param, Button):
                buttons.append(param)
            elif isinstance(param, Elements):
                buttons += param.buttons(settings)
            elif isinstance(param, Property):
                if param.key not in settings:
                    settings[param.key] = deepcopy(param.default)
                buttons.append(param.menu(settings[param.key]))
            else:  # If type not supported
                continue

        menu.add(*buttons)  # add button
        menu.storage["property"] = self
        menu.storage["settings"] = settings
        return menu

    def add(self, *args):
        self.parameters += list(args)
        return self

    @property
    def copy(self):
        return deepcopy(self)


class Property(Settings):
    text: str
    key: str
    default: p.Any

    def __init__(self, title: str, text: str, key: str, row_width=3, undo: bool = True, default: p.Any = None):
        super().__init__(title=title, row_width=row_width, undo=undo)
        self.text = text
        self.key = key
        self.default = {} if default is None else default

    def menu(self, settings: "SettingsType", **kwargs) -> Submenu:
        return super().menu(settings, self.text, self.key)


class Elements:
    text_format: str
    callback_data_format: str

    def __init__(self, text_format: str, callback_data_format: str):
        """
        Format string:
            {value} {v} - value of settings dict or list
            {key} {k} - key of dict (None if list)
            {num} {n} - number of position in dict or list (start with 0)
            {num1} {n1} - same as {num}, but start with 1
        """

        self.callback_data_format = callback_data_format
        self.text_format = text_format

    def buttons(self, settings: "SettingsType") -> list[Button]:
        num = 0
        buttons: list[Button] = []
        for key in settings:
            if isinstance(settings, list):
                value = key
                key = None
            elif isinstance(settings, dict):
                value = settings[key]

            mapping = {
                "key": key, "value": value, "num": num, "num1": num + 1,
                "k": key, "v": value, "n": num, "n1": num + 1
            }

            text = self.text_format.format(
                **mapping
            )
            callback_data = self.callback_data_format.format(
                **mapping
            )

            button = Button(text, callback_data)
            buttons.append(button)

            num += 1

        return buttons


SettingsType = p.Union[dict[str, p.Any], list[p.Any], p.Any]

ParameterType = list[p.Union[Property, Elements, Button]]
