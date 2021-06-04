import sqlite3
from dataclasses import dataclass
from json import loads
from typing import *


@dataclass
class settings:
    __settings: dict

    @property
    def row(self):
        return self.__settings

    @property
    def sticker_alias(self) -> Dict[str, str]:
        if "sticker_alias" in self.__settings:
            return self.__settings["sticker_alias"]
        return {}

    @property
    def text_alias(self) -> Dict[str, str]:
        if "text_alias" in self.__settings:
            return self.__settings["text_alias"]
        return {}


@dataclass
class chat:
    id: int
    _settings: str
    owner: int

    @property
    def settings(self) -> settings:
        return settings(loads(self._settings))


@dataclass
class user:
    id: int
    settings: str
    permission: str


class Database:
    def __init__(self, path: str) -> None:
        self.connect = sqlite3.connect(path)
        self.cursor = self.connect.cursor()

    def add_user(self, id: int) -> user:
        self.run(f"INSERT INTO Users (id) VALUES ({id})")
        return self.get_user(id)

    def add_chat(self, id: int, owner: int) -> chat:
        self.run(f"INSERT INTO Chats (id,owner) VALUES ({id},{owner})")
        return self.get_chat(id)

    def get_user(self, id: int) -> user:
        result = self.run(f"SELECT * FROM Users WHERE id={id}", True)

        if not result:
            return

        return user(*result)

    def get_chat(self, id: int) -> chat:
        result = self.run(f"SELECT * FROM Chats WHERE id={id}", True)

        if not result:
            return

        return chat(*result)

    def get_users(self) -> List[user]:
        result = self.run("SELECT id FROM Users")
        result = [user(*i) for i in result]
        return result

    def get_chats(self) -> List[chat]:
        result = self.run("SELECT id FROM Chats")
        result = [chat(*i) for i in result]
        return result

    def delete_user(self, id: int) -> bool:
        self.run(f"DELETE FROM Uses WHERE id = {id}")

    def delete_chat(self, id: int) -> bool:
        self.run(f"DELETE FROM Chats WHERE id = {id}")

    def run(self, sql: str, one: bool = False) -> Union[Any, List]:
        with self.connect:
            result = self.cursor.execute(sql)
            if one:
                result = result.fetchone()
            else:
                result = result.fetchall()

            return result

    def get_owns(self, id: int) -> List[chat]:
        result = self.run(f"SELECT * FROM Chats WHERE owner={id}")
        return [chat(*i) for i in result]


if __name__ == "__main__":
    db = Database("data/database.db")
