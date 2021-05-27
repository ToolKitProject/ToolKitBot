from aiogram import types as t
import typing as p

from .Buttons import Button, MenuButton

ElementType = p.Union[str, bool]
ListType = p.List[ElementType]
DictType = p.Dict[str, ElementType]
SettingType = p.Dict[str, p.Union[ListType, DictType]]


class _Settings:
    def __init__(self, title: str, text: str, key: str, *elements, undo: bool = False, row: int = 1):
        ParametersType = p.List[p.Union[ListSettings, DictSettings, Elements]]

        self.title = title
        self.text = text
        self.key = key
        self.undo = undo
        self.row = row
        self.elements: ParametersType = list(elements)

        self.settings = None

    def add(self, *elements):
        self.elements += elements
        return self

    def menu(self, settings: SettingType, title: str = None, text: str = None, key: str = None):
        self.settings = settings

        self.title = title or self.title
        self.text = text or self.text
        self.key = key or self.key

        menu = MenuButton(self.text, self.title, self.key, undo=self.undo, row=self.row, unique=False)

        if isinstance(self, Settings):
            values = settings
        elif self.key not in settings:
            settings[self.key] = {}
            values = settings[self.key]
        else:
            values = settings[self.key]
        buttons = []

        for elem in self.elements:
            if isinstance(elem, Elements):
                buttons += elem.buttons(values)
                continue
            elif isinstance(elem, Button):
                button = elem
            elif isinstance(elem, _Settings):
                button = elem.menu(values)
            else:
                continue
            buttons.append(button)

        menu.add(
            *buttons
        )
        return menu


class Elements:
    def __init__(self, text: str, data: str):
        """
        text и data "{num} {key} {value}"
        """
        self.text = text
        self.data = data

    def buttons(self, values: p.Union[DictType, ListType]):
        buttons = []

        if isinstance(values, list):
            key = ""
            for num, value in enumerate(values):
                text = self.format_text(num, key, value)
                data = self.format_data(num, key, value)
                buttons.append(
                    Button(text, data)
                )

        elif isinstance(values, dict):
            num = 0
            for key, value in values.items():
                text = self.format_text(num, key, value)
                data = self.format_data(num, key, value)
                buttons.append(
                    Button(text, data)
                )

                num += 1

        return buttons

    def format_data(self, num: int, key: str, value: ElementType):
        return self.data.format(
            num=num,
            key=key,
            value=value
        )

    def format_text(self, num: int, key: str, value: ElementType):
        return self.text.format(
            num=num,
            key=key,
            value=value
        )


class ListSettings(_Settings):
    def __init__(self, title: str, text: str, key: str, *elements, undo: bool = True, row: int = 1):
        super().__init__(title, text, key, *elements, undo=undo, row=row)


class DictSettings(_Settings):
    def __init__(self, title: str, text: str, key: str, *elements, undo: bool = True, row: int = 1):
        super().__init__(title, text, key, *elements, undo=undo, row=row)


class Settings(_Settings):

    def __init__(self, title: str, text: str, key: str, *elements, undo: bool = True, row: int = 1):
        super().__init__(title, text, key, *elements, undo=undo, row=row)

    def save(self, chat):
        chat.settings = self.settings
