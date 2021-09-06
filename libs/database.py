import typing as p
from copy import copy
from datetime import datetime
from aiogram.utils.json import loads, dumps

from pymysql import connect

JSON_DEFAULT = "{}"


def clear_dict(d: dict):
    for k, v in copy(d).items():
        if v is None or v == "" or v == [] or v == {}:
            d.pop(k)
        elif isinstance(v, dict):
            clear_dict(v)
        elif isinstance(v, list):
            clear_list(v)
    return d


def clear_list(l: list):
    for n, v in enumerate(copy(l)):
        if v is None or v == "" or v == [] or v == {}:
            l.pop(n)
        elif isinstance(v, dict):
            clear_dict(v)
        elif isinstance(v, list):
            clear_list(v)
    return l


class LogType:
    ADD_MEMBER = "add_member"
    REMOVE_MEMBER = "removed_member"
    PROMOTE_ADMIN = "promote_admin"
    RESTRICT_ADMIN = "restrict_admin"
    PROMOTE_MEMBER = "promote_member"
    RESTRICT_MEMBER = "restrict_member"
    REPORT = "report"

    def __contains__(self, item):
        return item in list(self.__dict__.values())

    @property
    def my(self):
        return [self.REPORT]

    @property
    def telegram(self):
        return [
            self.ADD_MEMBER,
            self.REMOVE_MEMBER,
            self.PROMOTE_ADMIN,
            self.RESTRICT_ADMIN,
            self.PROMOTE_MEMBER,
            self.RESTRICT_MEMBER
        ]


class _link_obj:
    _init: bool = False

    _table: str
    _id: int

    def __init__(self, table: str, id: str):
        self._table = table
        self._id = id

        self._init = True

    def get(self, name: str):
        return

    def set(self, name: str, value: p.Any):
        from src.instances import Database

        if name in self.__dict__:
            self.__dict__[name] = value

        if name in ["settings", "permission"]:
            value = dumps(clear_dict(value))

        Database.update(f"UPDATE {self._table} SET {name}='{value}' WHERE id={self._id};")

    def __getattr__(self, name: str):
        name = str(name)
        if self._init:
            return self.get(name)

    def __getitem__(self, name: str):
        name = str(name)
        if name in self.__dict__:
            return self.__dict__[name]
        elif self._init:
            return self.get(name)

    def __setattr__(self, key: str, value: p.Any):
        key = str(key)
        if self._init:
            self.set(key, value)
        else:
            self.__dict__[key] = value

    def __setitem__(self, key: str, value: p.Any):
        key = str(key)
        if self._init:
            self.set(key, value)
        else:
            self.__dict__[key] = value


class userOBJ(_link_obj):
    id: int
    settings: p.Dict
    permission: p.Dict

    def __init__(self, id: int, settings: str, permission: str):
        self.id = id
        self.settings = loads(settings)
        self.permission = loads(permission)

        super().__init__("Users", id)


class chatOBJ(_link_obj):
    id: int
    settings: p.Dict
    owner_id: p.Dict

    def __init__(self, id: str, settings: str, owner_id: int):
        self.id = id
        self.settings = loads(settings)
        self.owner_id = owner_id

        super().__init__("Chats", id)


class messageOBJ:
    user_id: int
    chat_id: int
    message_id: str
    message: p.Optional[str]
    type: str
    data: str

    def __init__(self,
                 user_id: int,
                 chat_id: int,
                 message_id: int,
                 message: p.Optional[str],
                 type: str,
                 date: datetime):
        self.user_id = user_id
        self.chat_id = chat_id
        self.message_id = message_id
        self.message = message
        self.type = type
        self.date = date


class logOBJ:
    log_id: int
    chat_id: int
    executor_id: int
    target_id: int
    type: str
    date: datetime

    def __init__(self,
                 log_id: int,
                 chat_id: int,
                 executor_id: int,
                 target_id: int,
                 type: str,
                 date: datetime):
        self.log_id = log_id
        self.chat_id = chat_id
        self.executor_id = executor_id
        self.target_id = target_id
        self.type = type
        self.date = date


class Database:
    def __init__(self, host: str, user: str, password: str, database: str) -> None:
        self.connect = connect(
            user=user,
            password=password,
            host=host,
            database=database
        )

    def add_user(self, id: int) -> userOBJ:
        self.update(f"INSERT INTO Users VALUES ({id},{JSON_DEFAULT!r},{JSON_DEFAULT!r},{JSON_DEFAULT!r})")
        return self.get_user(id)

    def add_chat(self, id: int, owner_id: int) -> chatOBJ:
        self.update(f"INSERT INTO Chats VALUES ({id},{JSON_DEFAULT!r},{owner_id})")
        return self.get_chat(id)

    def add_message(self,
                    user_id: int,
                    chat_id: int,
                    message_id: int,
                    message: p.Optional[str] = None,
                    type: p.Optional[str] = None,
                    date: p.Optional[datetime] = None) -> messageOBJ:
        sql = self._optionals_sql(
            "INSERT INTO Messages({columns}) VALUES ({values})", mode="INSERT",
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            message=message,
            type=type,
            date=date
        )
        self.update(sql)

        return self.get_message(chat_id, message_id)

    def add_log(self,
                chat_id: int,
                executor_id: int,
                target_id: int,
                type: str,
                date: datetime):
        sql = self._optionals_sql(
            "INSERT INTO Logs({columns}) VALUES ({values})", mode="INSERT",
            chat_id=chat_id,
            executor_id=executor_id,
            target_id=target_id,
            type=type,
            date=date
        )
        self.update(sql)

    def get_user(self, id: int) -> userOBJ:
        result = self.get(f"SELECT * FROM Users WHERE id={id}", True)

        if not result:
            return self.add_user(id)

        return userOBJ(*result)

    def get_chat(self, id: int, owner_id: p.Optional[int] = None) -> p.Optional[chatOBJ]:
        result = self.get(f"SELECT * FROM Chats WHERE id={id}", True)

        if not result:
            if owner_id is not None:
                return self.add_chat(id, owner_id)
            return

        return chatOBJ(*result)

    def get_message(self, chat_id: int, message_id: int) -> messageOBJ:
        result = self.get(
            f"SELECT * FROM Messages WHERE chat_id={chat_id} AND message_id={message_id}",
            one=True
        )
        return messageOBJ(*result)

    def get_messages(self,
                     user_id: p.Optional[int] = None,
                     chat_id: p.Optional[int] = None,
                     type: p.Optional[str] = None) -> p.List[messageOBJ]:
        sql = self._optionals_sql(
            "SELECT * FROM Messages WHERE {where}", mode="where",
            user_id=user_id,
            chat_id=chat_id,
            type=type,
        )
        return self._create_list_of_objects(self.get(sql), messageOBJ)

    def get_messages_by_date(self,
                             from_date: datetime,
                             to_date: p.Optional[datetime] = None,
                             contain: bool = True
                             ) -> p.List[messageOBJ]:
        sql = "SELECT * FROM Messages WHERE "

        fd = repr(from_date.isoformat(" "))

        if from_date and to_date:
            td = repr(to_date.isoformat(" "))
            if contain:
                sql += f"date >= {fd} AND date <= {td}"
            else:
                sql += f"date > {fd} AND date < {td}"
        elif from_date:
            sql += f"date = {fd}"

        result = self.get(sql)
        if result:
            result = self._create_list_of_objects(result, messageOBJ)
        return result

    def get_messages_id(self,
                        user_id: int,
                        chat_id: int,
                        from_date: p.Optional[datetime] = None,
                        to_date: p.Optional[datetime] = None,
                        contain: bool = True) -> p.List[int]:
        sql = f"SELECT message_id FROM Messages WHERE user_id={user_id} AND chat_id={chat_id}"

        if from_date and to_date:
            sql += " AND "
            td = repr(to_date.isoformat(" "))
            fd = repr(from_date.isoformat(" "))

            if contain:
                sql += f"date >= {fd} AND date <= {td}"
            else:
                sql += f"date > {fd} AND date < {td}"

        return self.get(sql, size=1000)

    def get_all_messages(self) -> p.List[messageOBJ]:
        return self._create_list_of_objects(self.get("SELECT * FROM Messages"), messageOBJ)

    def get_logs(self,
                 chat_id: p.Optional[int] = None,
                 executor_id: p.Optional[int] = None,
                 target_id: p.Optional[int] = None,
                 type: p.Optional[str] = None) -> p.List[logOBJ]:
        sql = self._optionals_sql(
            "SELECT * FROM Logs WHERE {where}", mode="where",
            chat_id=chat_id,
            executor_id=executor_id,
            target_id=target_id,
            type=type
        )
        return self._create_list_of_objects(self.get(sql), logOBJ)

    def get_logs_by_date(self,
                         from_date: datetime,
                         to_date: p.Optional[datetime] = None,
                         contain: bool = True
                         ) -> p.List[logOBJ]:
        sql = "SELECT * FROM Logs WHERE "

        fd = repr(from_date.isoformat(" "))

        if from_date and to_date:
            td = repr(to_date.isoformat(" "))
            if contain:
                sql += f"date >= {fd} AND date <= {td}"
            else:
                sql += f"date > {fd} AND date < {td}"
        elif from_date:
            sql += f"date = {fd}"

        return self._create_list_of_objects(self.get(sql), logOBJ)

    def get_all_logs(self) -> p.List[logOBJ]:
        return self._create_list_of_objects(self.get("SELECT * FROM Logs"), logOBJ)

    def get_users(self) -> p.List[userOBJ]:
        result = self.get("SELECT * FROM Users")
        return self._create_list_of_objects(result, userOBJ)

    def get_chats(self) -> p.List[chatOBJ]:
        result = self.get("SELECT * FROM Chats")
        return self._create_list_of_objects(result, chatOBJ)

    def get_owns(self, id: int) -> p.List[chatOBJ]:
        result = self.get(f"SELECT * FROM Chats WHERE owner_id={id}")
        return self._create_list_of_objects(result, chatOBJ)

    def delete_user(self, id: int):
        self.update(f"DELETE FROM Messages WHERE user_id={id}")
        self.update(f"DELETE FROM Messages WHERE target_id={id} OR executor_id={id}")
        self.update(f"DELETE FROM Chats WHERE owner_id = {id}")
        self.update(f"DELETE FROM Uses WHERE id = {id}")

    def delete_chat(self, id: int):
        self.update(f"DELETE FROM Messages WHERE chat_id={id}")
        self.update(f"DELETE FROM Logs WHERE chat_id={id}")
        self.update(f"DELETE FROM Chats WHERE id = {id}")

    def delete_messages(self, chat_id: int, ids: p.Union[int, p.List[int]]):
        if isinstance(ids, int):
            ids = [ids]

        for id in ids:
            self.update(f"DELETE FROM Messages WHERE chat_id={chat_id} AND message_id={id}")

    def get(self, sql: str, one: bool = False, size: int = None) -> p.Union[p.Any, p.List]:
        with self.connect.cursor() as cursor:
            cursor.execute(sql)
            if one:
                result = cursor.fetchone()
            else:
                if size:
                    result = cursor.fetchmany(size)
                else:
                    result = cursor.fetchall()
        return result

    def update(self, sql: str):
        with self.connect.cursor() as cursor:
            cursor.execute(sql)

        self.connect.commit()

    @staticmethod
    def _create_list_of_objects(l: p.List[p.Tuple[p.Any]], o: p.Any):
        return [o(*i) for i in l]

    @staticmethod
    def _optionals_sql(sql: str, mode: str, **opts) -> str:
        mode = mode.lower()
        columns = []
        values = []

        for c, v in opts.items():
            if v is not None:
                if isinstance(v, str):
                    v = repr(v)
                elif isinstance(v, datetime):
                    v = repr(v.isoformat(" "))
                elif isinstance(v, list) or isinstance(v, dict):
                    v = repr(dumps(v))
                else:
                    v = str(v)

                columns.append(c)
                values.append(v)
        if not (columns or values):
            raise ValueError("Selectors required")

        if mode == "insert":
            columns = ",".join(columns)
            values = ",".join(values)

            return sql.format(columns=columns, values=values)
        elif mode == "where":
            where = []
            for c, v in zip(columns, values):
                where.append(f"{c}={v}")
            where = " AND ".join(where)

            return sql.format(where=where)


if __name__ == "__main__":
    pass
