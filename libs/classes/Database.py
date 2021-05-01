import sqlite3
from typing import *


class Database:
    def __init__(self, path: str) -> None:
        self.connect = sqlite3.connect(path)
        self.cursor = self.connect.cursor()

    def add_user(self, id: int):
        self.run(f"INSERT INTO Users (id) VALUES ({id})")

    def add_chat(self, id: int, owner: int):
        self.run(f"INSERT INTO Chats (id,owner) VALUES ({id},{owner})")

    def get_user(self, id: int) -> Tuple[int, str, str]:
        result = self.run(f"SELECT * FROM Users WHERE id={id}", True)
        return result

    def get_chat(self, id: int) -> Tuple[int, str, int]:
        result = self.run(f"SELECT * FROM Chats WHERE id={id}", True)
        return result

    def get_users(self) -> List[int]:
        result = self.run("SELECT id FROM Users")
        result = [i[0] for i in result]
        return result

    def get_chats(self) -> List[int]:
        result = self.run("SELECT id FROM Chats")
        result = [i[0] for i in result]
        return result

    def run(self, sql: str, one: bool = False) -> Union[Any, List]:
        with self.connect:
            result = self.cursor.execute(sql)
            if one:
                result = result.fetchone()
            else:
                result = result.fetchall()

            return result

    def get_owns(self, id: int) -> List[int]:
        result = self.run(f"SELECT id FROM Chats WHERE owner={id}")
        return [i[0] for i in result]


if __name__ == "__main__":
    db = Database("data/database.db")
