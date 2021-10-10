import logging
import typing as p
from copy import copy
from datetime import datetime, timedelta
from time import time

from aiogram.utils.json import loads, dumps
from pymysql import connect

import config

JSON_DEFAULT = {}


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


def format_delta(column: str, delta: timedelta, contain: bool = True):
    from_date = datetime.now()
    to_date = from_date - delta

    if contain:
        result = f"{column}<={format_value(from_date)} AND {column}>={format_value(to_date)}"
    else:
        result = f"{column}<{format_value(from_date)} AND {column}>{format_value(to_date)}"

    return result


def format_value(value: p.Any) -> str:
    if isinstance(value, dict):
        value = dumps(clear_dict(value))
    elif isinstance(value, list):
        value = dumps(clear_list(value))
    elif isinstance(value, datetime):
        value = value.isoformat(" ", "seconds")

    if isinstance(value, str):
        value = repr(value)
    else:
        value = str(value)

    return value


def format_where(**selectors):
    where = []

    for k, v in selectors.items():
        if v is not None:
            if isinstance(v, timedelta):
                where.append(format_delta(k, v))
            else:
                where.append(f"{k}={format_value(v)}")

    return f"WHERE {' AND '.join(where)}"


def format_select(table: str, **selectors):
    return f"SELECT * FROM {table} {format_where(**selectors)}"


def format_delete(table: str, **selectors):
    return f"DELETE FROM {table} {format_where(**selectors)}"


def format_insert(table: str, **values):
    val = []
    col = []

    for k, v in values.items():
        if v is not None:
            v = format_value(v)
            col.append(k)
            val.append(v)

    val = ",".join(val)
    col = ",".join(col)

    return f"INSERT INTO {table}({col}) VALUES ({val})"


def objects(l: p.List[p.Tuple], o: p.Type) -> p.List[object]:
    return [o(*i) for i in l]


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

    @classmethod
    def all(cls):
        return list(cls.__dict__.values())

    @classmethod
    def my(cls):
        return [cls.REPORT]

    @classmethod
    def telegram(cls):
        return [
            cls.ADD_MEMBER,
            cls.REMOVE_MEMBER,
            cls.PROMOTE_ADMIN,
            cls.RESTRICT_ADMIN,
            cls.PROMOTE_MEMBER,
            cls.RESTRICT_MEMBER
        ]


class _link_obj:
    _init: bool = False

    _table: str
    _links: p.List[str]

    def __init__(self, table: str, *links: str):
        self._table = table
        self._links = links

        self._init = True

    def get(self, name: str):
        return

    def set(self, name: str, value: p.Any):
        from src.instances import Database as db

        where = {}
        for l in self._links:
            where[l] = self.__dict__[l]

        if name in self.__dict__:
            self.__dict__[name] = value

        sql = f"UPDATE {self._table} SET {name}={format_value(value)} {format_where(**where)}"

        db.update(sql)

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

    def __str__(self):
        result = f"{self.__class__.__name__}:\n"
        for col, val in self.__dict__.items():
            if "_" not in col:
                result += f"    {col}={format_value(val)}\n"

        return result


class userOBJ(_link_obj):
    id: int
    settings: p.Dict
    permission: p.Dict

    def __init__(self, id: int, settings: str, permission: str):
        self.id = id
        self.settings = loads(settings)
        self.permission = loads(permission)

        super().__init__("Users", "id")


class chatOBJ(_link_obj):
    id: int
    settings: p.Dict
    owner_id: p.Dict

    def __init__(self, id: str, settings: str, owner_id: int):
        self.id = id
        self.settings = loads(settings)
        self.owner_id = owner_id

        super().__init__("Chats", "id")


class messageOBJ(_link_obj):
    user_id: int
    chat_id: int
    message_id: str
    reply_message_id: p.Optional[int]
    message: p.Optional[str]
    type: str
    data: str

    def __init__(self,
                 user_id: int,
                 chat_id: int,
                 message_id: int,
                 reply_message_id: p.Optional[int],
                 message: p.Optional[str],
                 type: str,
                 date: datetime):
        self.user_id = user_id
        self.chat_id = chat_id
        self.message_id = message_id
        self.reply_message_id = reply_message_id
        self.message = message
        self.type = type
        self.date = date

        super().__init__("Messages", "chat_id", "user_id", "message_id")


class logOBJ(_link_obj):
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

        super().__init__("Logs", "log_id")


class Database:
    connect: connect
    autocommit: bool

    def __init__(self, user: str, password: str, host: str, database: str, autocommit: bool = True):
        self.autocommit = autocommit
        self.connect = connect(
            user=user,
            password=password,
            host=host,
            database=database
        )

    # SETTERS
    def add_user(self, id: int) -> userOBJ:
        self.update(
            format_insert(
                "Users",
                id=id,
                settings=JSON_DEFAULT,
                permissions=JSON_DEFAULT
            )
        )
        return self.get_last_user()

    def add_chat(self, id: int, owner_id: int) -> chatOBJ:
        self.update(
            format_insert(
                "Chats",
                id=id,
                settings=JSON_DEFAULT,
                owner_id=owner_id
            )
        )
        return self.get_last_chat()

    def add_message(self,
                    user_id: int,
                    chat_id: int,
                    message_id: int,
                    reply_message_id: p.Optional[int] = None,
                    message: p.Optional[str] = None,
                    type: p.Optional[str] = None,
                    date: p.Optional[datetime] = None) -> messageOBJ:
        self.update(
            format_insert(
                "Messages",
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                reply_message_id=reply_message_id,
                message=message,
                type=type,
                date=date
            )
        )
        return self.get_last_message()

    def add_log(self,
                chat_id: int,
                executor_id: int,
                target_id: int,
                type: str,
                date: datetime) -> logOBJ:
        self.update(
            format_insert(
                "Logs",
                chat_id=chat_id,
                executor_id=executor_id,
                target_id=target_id,
                type=type,
                date=date
            )
        )
        return self.get_last_log()

    # ONE GETTER
    def get_user(self, id: int) -> userOBJ:
        result = self.get(
            format_select(
                "Users",
                id=id
            ),
            True
        )
        if not result:
            return self.add_user(id)

        return userOBJ(*result)

    def get_chat(self, id: id, owner_id: p.Optional[int] = None) -> chatOBJ:
        result = self.get(
            format_select(
                "Chats",
                id=id
            ),
            True
        )
        if not result:
            if id is not None and owner_id is not None:
                return self.add_chat(id, owner_id)
            return

        return chatOBJ(*result)

    def get_message(self,
                    user_id: p.Optional[int] = None,
                    chat_id: p.Optional[int] = None,
                    message_id: p.Optional[int] = None,
                    reply_message_id: p.Optional[int] = None,
                    message: p.Optional[str] = None,
                    type: p.Optional[str] = None,
                    delta: p.Optional[timedelta] = None) -> messageOBJ:
        if message_id is None:
            raise ValueError("message_id is required")
        if chat_id is None:
            raise ValueError("chat_id is required")

        result = self.get(
            format_select(
                "Messages",
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                reply_message_id=reply_message_id,
                message=message,
                type=type,
                date=delta
            ),
            True
        )
        return messageOBJ(*result)

    def get_log(self,
                log_id: int,
                chat_id: p.Optional[int] = None,
                executor_id: p.Optional[int] = None,
                target_id: p.Optional[int] = None,
                type: p.Optional[str] = None,
                delta: p.Optional[timedelta] = None) -> logOBJ:
        result = self.get(
            format_select(
                "Logs",
                log_id=log_id,
                chat_id=chat_id,
                executor_id=executor_id,
                target_id=target_id,
                type=type,
                delta=delta
            ),
            True
        )
        return logOBJ(*result)

    # MANY GETTER
    def get_users(self,
                  id: p.Optional[int] = None,
                  settings: p.Optional[dict] = None,
                  permissions: p.Optional[dict] = None) -> p.List[userOBJ]:
        result = self.get(
            format_select(
                "Users",
                id=id,
                settings=settings,
                permissions=permissions
            )
        )

        return objects(result, userOBJ)

    def get_chats(self,
                  id: p.Optional[int] = None,
                  settings: p.Optional[dict] = None,
                  owner_id: p.Optional[int] = None) -> p.List[chatOBJ]:
        result = self.get(
            format_select(
                "Chats",
                id=id,
                settings=settings,
                owner_id=owner_id
            )
        )

        return objects(result, chatOBJ)

    def get_messages(self,
                     user_id: p.Optional[int] = None,
                     chat_id: p.Optional[int] = None,
                     message_id: p.Optional[int] = None,
                     reply_message_id: p.Optional[int] = None,
                     message: p.Optional[str] = None,
                     type: p.Optional[str] = None,
                     delta: p.Optional[timedelta] = None) -> p.List[messageOBJ]:
        result = self.get(
            format_select(
                "Messages",
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                reply_message_id=reply_message_id,
                message=message,
                type=type,
                date=delta
            )
        )

        return objects(result, messageOBJ)

    def get_logs(self,
                 log_id: p.Optional[int] = None,
                 chat_id: p.Optional[int] = None,
                 executor_id: p.Optional[int] = None,
                 target_id: p.Optional[int] = None,
                 type: p.Optional[str] = None,
                 delta: p.Optional[timedelta] = None) -> p.List[logOBJ]:
        result = self.get(
            format_select(
                "Logs",
                log_id=log_id,
                chat_id=chat_id,
                executor_id=executor_id,
                target_id=target_id,
                type=type,
                date=delta
            )
        )

        return objects(result, logOBJ)

    # ALL GETTER
    def get_all_users(self, size: p.Optional[int] = None) -> p.List[userOBJ]:
        return objects(self.get("SELECT * FROM Users", size=size), userOBJ)

    def get_all_chats(self, size: p.Optional[int] = None) -> p.List[chatOBJ]:
        return objects(self.get("SELECT * FROM Chats", size=size), chatOBJ)

    def get_all_messages(self, size: p.Optional[int] = None) -> p.List[messageOBJ]:
        return objects(self.get("SELECT * FROM Messages", size=size), messageOBJ)

    def get_all_logs(self, size: p.Optional[int] = None) -> p.List[logOBJ]:
        return objects(self.get("SELECT * FROM Logs", size=size), logOBJ)

    # DELETER
    def delete_users(self,
                     id: p.Optional[int] = None,
                     settings: p.Optional[dict] = None,
                     permissions: p.Optional[dict] = None):
        self.update(
            format_delete(
                "Users",
                id=id,
                settings=settings,
                permissions=permissions
            )
        )

    def delete_chats(self,
                     id: p.Optional[int] = None,
                     settings: p.Optional[dict] = None,
                     owner_id: p.Optional[int] = None):
        self.update(
            format_delete(
                "Chats",
                id=id,
                settings=settings,
                owner_id=owner_id
            )
        )

    def delete_messages(self,
                        user_id: p.Optional[int] = None,
                        chat_id: p.Optional[int] = None,
                        message_id: p.Optional[int] = None,
                        reply_message_id: p.Optional[int] = None,
                        message: p.Optional[str] = None,
                        type: p.Optional[str] = None,
                        delta: p.Optional[timedelta] = None):
        self.update(
            format_delete(
                "Messages",
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                reply_message_id=reply_message_id,
                message=message,
                type=type,
                date=delta,
            )
        )

    def delete_logs(self,
                    log_id: p.Optional[int] = None,
                    chat_id: p.Optional[int] = None,
                    executor_id: p.Optional[int] = None,
                    target_id: p.Optional[int] = None,
                    type: p.Optional[str] = None,
                    delta: p.Optional[timedelta] = None):
        self.update(
            format_delete(
                "Logs",
                log_id=log_id,
                chat_id=chat_id,
                executor_id=executor_id,
                target_id=target_id,
                type=type,
                date=delta,
            )
        )

    # GET LAST
    def get_last_user(self) -> userOBJ:
        return userOBJ(*self.get("SELECT * FROM Users ORDER BY id DESC LIMIT 1", True))

    def get_last_chat(self) -> chatOBJ:
        return chatOBJ(*self.get("SELECT * FROM Chats ORDER BY id DESC LIMIT 1", True))

    def get_last_message(self) -> messageOBJ:
        return messageOBJ(*self.get("SELECT * FROM Messages ORDER BY message_id DESC LIMIT 1", True))

    def get_last_log(self) -> logOBJ:
        return logOBJ(*self.get("SELECT * FROM Logs ORDER BY log_id DESC LIMIT 1", True))

    # LOW LEVEL GETTER
    def get(self, sql: str, one: bool = False, size: int = None) -> p.Union[p.List[p.Tuple], p.Tuple]:
        logging.debug(f"Getting from database:\n    {sql}")
        with self.connect.cursor() as cursor:
            cursor.execute(sql)
            if one:
                return cursor.fetchone()
            else:
                if size:
                    return cursor.fetchmany(size)
                else:
                    return cursor.fetchall()

    def update(self, sql: str):
        logging.debug(f"Updating database:\n    {sql}")
        with self.connect.cursor() as cursor:
            cursor.execute(sql)

        if self.autocommit:
            self.commit()

    def commit(self):
        self.connect.commit()

    # ANY

    def disable_autocommit(self):
        self.commit()
        self.autocommit = False

    def enable_autocommit(self):
        self.commit()
        self.autocommit = True
