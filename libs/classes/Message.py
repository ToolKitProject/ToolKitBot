from typing import *
from aiogram import types


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
        self.storage: Dict[types.Message, Data] = {}

    async def __call__(self, msg: types.Message) -> Data:
        """ 
        Создает или возвращает данные
        """
        if msg.message_id in self.storage:
            return await self.get(msg)
        else:
            return await self.new(msg)

    async def delete(self, msg: types.Message):
        """
        Удаляет данные и сообщение 
        """
        await self.remove(msg.message_id)
        await msg.delete()

    async def remove(self, msg: types.Message):
        """
        Удаляет данные
        """
        self.storage.pop(msg.message_id)

    async def close(self):
        """
        Удаляет ВСЕ данные и ВСЕ сообщение 
        """
        for msg in self.storage:
            try:
                await self.delete(msg)
            except:
                pass

    async def new(self, msg: types.Message) -> Data:
        """
        Добавляет данные к сообщению 
        """
        self.storage[msg.message_id] = Data(msg)
        return self.storage[msg.message_id]

    async def get(self, msg: types.Message) -> Data:
        """
        Возвращает данные 
        """
        return self.storage[msg.message_id]
