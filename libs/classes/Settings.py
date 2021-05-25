from aiogram import types as t
import typing as p
from .Buttons import Button, MenuButton

ElementType = p.Union[str, bool]
ListType = p.List[ElementType]
DictType = p.Dict[str, ElementType]
SettingType = p.Dict[str, p.Union[ListType, DictType]]


class _Settings:
    def __init__(self, title: str, text: str, key: str, *elements, undo: int = False, row: int = 1):
        ParametersType = p.List[p.Union[ListSettings, DictSettings, Element]]

        self.title = title
        self.text = text
        self.key = key
        self.undo = undo
        self.row = row
        self.elements: ParametersType = list(elements)

    def add(self, *elements) -> object:
        self.elements += elements
        return self

    def menu(self, settings):
        menu = MenuButton(self.text, self.title, self.key)
        for elem in self.elements:
            if isinstance(elem, Element):
                button = elem
            else:
                button = elem.menu(settings)

            menu.add(
                button
            )
        return menu


class Element(Button):
    def __init__(self, text: str, key: str):
        super().__init__(text, data=key)

class ListSettings(_Settings):
    def __init__(self, title: str, text: str, key: str):
        super().__init__(title, text, key)


class DictSettings(_Settings):
    def __init__(self, title: str, text: str, key: str):
        super().__init__(title, text, key)


class Settings(_Settings):
    def __init__(self, title: str, text: str, key: str, *elements):
        super().__init__(title, text, key, *elements)
