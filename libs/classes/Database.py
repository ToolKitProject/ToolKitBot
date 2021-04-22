import sqlite3
from typing import *


class Database:
    def __init__(self, path: str) -> None:
        self.connect = sqlite3.connect(path)
        self.cursor = self.connect.cursor()

    def run(self, sql: str, one: bool = False) -> Union[Any, List]:
        with self.connect:
            result = self.cursor.execute(sql)
            if one:
                result = result.fetchone()
            else:
                result = result.fetchall()

            return result


if __name__ == "__main__":
    db = Database("data/database.db")
