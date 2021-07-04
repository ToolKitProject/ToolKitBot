import random
import sqlite3
from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass
from json import loads, dumps
import typing as p


def clear_dict(d: dict):
    for k, v in copy(d).items():
        if v is None or v == "":
            d.pop(k)
        elif isinstance(v, dict):
            clear_dict(v)
    return d


class _link_obj(ABC):
    _init: bool = False

    _table: str
    _id: int

    def __init__(self, table: str, id: str):
        self._table = table
        self._id = id

        self._init = True

    @abstractmethod
    def get(self, name: str):
        pass

    @abstractmethod
    def set(self, name: str, value: p.Any):
        pass

    def __getattr__(self, name: str):
        if self._init:
            return self.get(name)

    def __getitem__(self, name: str):
        if name in self.__dict__:
            return self.__dict__[name]
        elif self._init:
            return self.get(name)

    def __setattr__(self, key: str, value: p.Any):
        if self._init:
            self.set(key, value)
        else:
            self.__dict__[key] = value

    def __setitem__(self, key: str, value: p.Any):
        if self._init:
            self.set(key, value)
        else:
            self.__dict__[key] = value


class settingsOBJ(_link_obj):
    _data: dict

    def __init__(self, settings: str, table: str, id: str):
        self._data = loads(settings)
        super().__init__(table, id)

    def get(self, name):
        if name in self._data:
            return self._data[name]

    def set(self, name: str, value: p.Any):
        from libs.objects import Database
        self._data[name] = value
        Database.run(f"UPDATE {self._table} SET settings='{dumps(clear_dict(self.row))}' WHERE id={self._id};")

    @property
    def row(self):
        return self._data


class permissionOBJ(settingsOBJ):
    def __init__(self, settings: str, id: str):
        super().__init__(settings, "Users", id)

    def set(self, name: str, value: p.Any):
        from libs.objects import Database
        self._data[name] = value
        Database.run(f"UPDATE {self._table} SET permission='{dumps(clear_dict(self.row))}' WHERE id={self._id};")


class userOBJ(_link_obj):
    id: int
    settings: settingsOBJ
    permission: permissionOBJ

    def __init__(self, id: int, settings: str, permission: str):
        self.id = id
        self.settings = settingsOBJ(settings, "Users", self.id)
        self.permission = permissionOBJ(permission, self.id)
        super().__init__("Users", id)

    def get(self, name: str):
        return None

    def set(self, name: str, value: p.Any):
        from libs.objects import Database

        if name in self.__dict__:
            self.__dict__[name] = value

        if name in ["settings", "permission"]:
            value = dumps(value)

        Database.run(f"UPDATE {self._table} SET {name}='{value}' WHERE id={self._id};")


class chatOBJ(_link_obj):
    id: int
    settings: settingsOBJ
    owner: userOBJ

    def __init__(self, id: str, settings: str, owner: int):
        from libs.objects import Database

        self.id = id
        self.settings = settingsOBJ(settings, "Chats", self.id)
        self.owner = Database.get_user(owner)

        super().__init__("Chats", id)

    def get(self, name: str):
        return None

    def set(self, name: str, value: p.Any):
        from libs.objects import Database

        if name in self.__dict__:
            self.__dict__[name] = value

        if name == "settings":
            value = dumps(value)
        Database.run(f"UPDATE {self._table} SET {name}='{value}' WHERE id={self._id};")


class Database:
    def __init__(self, path: str) -> None:
        self.connect = sqlite3.connect(path)
        self.cursor = self.connect.cursor()

    def add_user(self, id: int) -> userOBJ:
        self.run(f"INSERT INTO Users (id) VALUES ({id})")
        return self.get_user(id)

    def add_chat(self, id: int, owner: int) -> chatOBJ:
        self.run(f"INSERT INTO Chats (id,owner) VALUES ({id},{owner})")
        return self.get_chat(id)

    def get_user(self, id: int) -> userOBJ:
        result = self.run(f"SELECT * FROM Users WHERE id={id}", True)

        if not result:
            return

        return userOBJ(*result)

    def get_chat(self, id: int) -> chatOBJ:
        result = self.run(f"SELECT * FROM Chats WHERE id={id}", True)

        if not result:
            return

        return chatOBJ(*result)

    def get_users(self) -> p.List[userOBJ]:
        result = self.run("SELECT * FROM Users")
        result = [userOBJ(*i) for i in result]
        return result

    def get_chats(self) -> p.List[chatOBJ]:
        result = self.run("SELECT * FROM Chats")
        result = [chatOBJ(*i) for i in result]
        return result

    def delete_user(self, id: int) -> bool:
        self.run(f"DELETE FROM Uses WHERE id = {id}")

    def delete_chat(self, id: int) -> bool:
        self.run(f"DELETE FROM Chats WHERE id = {id}")

    def run(self, sql: str, one: bool = False) -> p.Union[p.Any, p.List]:
        with self.connect:
            result = self.cursor.execute(sql)
            if one:
                result = result.fetchone()
            else:
                result = result.fetchall()

            return result

    def get_owns(self, id: int) -> p.List[chatOBJ]:
        result = self.run(f"SELECT * FROM Chats WHERE owner={id}")
        return [chatOBJ(*i) for i in result]


if __name__ == "__main__":
    pass
