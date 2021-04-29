from typing import *
from aiogram import types
from copy import copy


class MessageConstructor:
    pass


class Data:
    """
    Содержит пользовательские данные о сообщении 
    """

    def __init__(self, msg: types.Message) -> None:
        self.msg = msg

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __setattr__(self, name: str, value: Any):
        self.__dict__[name] = value

    def __getattr__(self, name: str) -> Any:
        return self.__dict__[name]

    def __setitem__(self, name: str, value: Any):
        self.__dict__[name] = value

    def __getitem__(self, name: str) -> Any:
        return self.__dict__[name]

    def __iter__(self):
        for key in self.__dict__:
            yield key

    @property
    def values(self):
        """
        Итерирует значения
        """
        for key in self:
            yield self[key]

    def get(self, key: str) -> object:
        """
        Возвращает данные
        """
        return self.__dict__[key]

    def set(self, key: str, value: str) -> object:
        """
        Добавляет или изменяет данные
        """
        self.__dict__[key] = value
        return self.__dict__(key)


class MessageData:
    """
    Иструмент для получения данных от каждого сообщения
    """

    def __init__(self):
        self.storage: Dict[int, Dict[int, Data]] = {}

    async def __call__(self, msg: types.Message) -> Data:
        """ 
        Создает или возвращает данные
        """
        if msg.chat.id in self.storage and msg.message_id in self.storage[msg.chat.id]:
            return await self.get(msg)
        else:
            return await self.new(msg)

    async def delete(self, msg: types.Message, markup: bool = True):
        """
        Удаляет данные и сообщение 
        """
        await self.remove(msg)
        if markup:
            await msg.delete_reply_markup()
        else:
            await msg.delete()

    async def remove(self, msg: types.Message):
        """
        Удаляет данные
        """
        self.storage[msg.chat.id].pop(msg.message_id)
        if not self.storage[msg.chat.id]:
            self.storage.pop(msg.chat.id)

    async def close(self, markup: bool = True):
        """
        Удаляет ВСЕ данные и ВСЕ сообщение 
        """
        for chat_id in self.storage:
            storage = copy(self.storage[chat_id])
            for id in storage:
                data = await self.get_id(chat_id, id)
                try:
                    if markup:
                        await data.msg.delete_reply_markup()
                    else:
                        await data.msg.delete()
                except:
                    pass

    async def new(self, msg: types.Message) -> Data:
        """
        Добавляет данные к сообщению 
        """
        if msg.chat.id not in self.storage:
            self.storage[msg.chat.id] = {}
        data = Data(msg)
        self.storage[msg.chat.id][msg.message_id] = data
        return data

    async def get(self, msg: types.Message) -> Data:
        """
        Возвращает данные 
        """
        return self.storage[msg.chat.id][msg.message_id]

    async def get_id(self, chat_id: int, message_id: int):
        """
        Возвращает данные 
        """
        return self.storage[chat_id][message_id]
