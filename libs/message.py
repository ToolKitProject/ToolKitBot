import typing as p

from aiogram import types as t


class Data:
    msg: t.Message

    def __init__(self, msg: t.Message, **kwargs) -> None:
        self.msg = msg
        self.__dict__.update(kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __setattr__(self, name: str, value: p.Any):
        self.set(name, value)

    def __getattr__(self, name: str) -> p.Any:
        return self.get(name)

    def __setitem__(self, name: str, value: p.Any):
        self.set(name, value)

    def __getitem__(self, name: str) -> p.Any:
        return self.get(name)

    def __iter__(self):
        return self.__dict__

    @property
    def storage(self):
        return self.__dict__

    @property
    def values(self):
        for key in self:
            yield self[key]

    def get(self, key: str) -> object:
        return self.__dict__[key] if key in self.__dict__ else None

    def set(self, key: str, value: str) -> object:
        self.__dict__[key] = value
        return value

    async def close(self, markup: bool = True):
        try:
            if markup:
                await self.msg.delete_reply_markup()
            else:
                await self.msg.delete()
        except Exception:
            pass

    async def auto_close(self, time: int):
        pass


class MessageData:
    storage: p.Dict[int, p.Dict[int, Data]]
    poll_storage: p.Dict[str, t.Message]

    def __init__(self):
        self.storage = {}
        self.poll_storage = {}

    def data(self, msg: t.Message = None) -> Data:
        if not msg:
            if t.Message.get_current():
                msg = t.Message.get_current()
            elif t.CallbackQuery.get_current():
                msg = t.CallbackQuery.get_current().message
            elif t.Poll.get_current():
                poll = t.Poll.get_current()
                if poll.id in self.poll_storage:
                    msg = self.poll_storage[poll.id]

        if t.Poll.get_current() is None and msg.poll:
            self.poll_storage[msg.poll.id] = msg

        if msg.chat.id in self.storage and msg.message_id in self.storage[msg.chat.id]:
            return self.get(msg)
        else:
            return self.new(msg)

    def new(self, msg: t.Message) -> Data:
        if msg.chat.id not in self.storage:
            self.storage[msg.chat.id] = {}
        data = Data(msg=msg)
        self.storage[msg.chat.id][msg.message_id] = data
        return data

    def get(self, msg: t.Message) -> Data:
        return self.storage[msg.chat.id][msg.message_id]

    def remove(self, msg: t.Message) -> p.Optional[Data]:
        try:
            data = self.storage[msg.chat.id].pop(msg.message_id)
            if not self.storage[msg.chat.id]:
                self.storage.pop(msg.chat.id)

            return data
        except Exception:
            pass

    async def close(self, markup: bool = True):
        for storage in self.storage.values():
            for data in storage.values():
                await data.close(markup)
        self.poll_storage = {}

    async def move(self, from_msg: t.Message, to_msg: t.Message) -> Data:
        data = self.get(from_msg)
        await data.close(True)
        data.msg = to_msg
        self.storage[to_msg.chat.id][to_msg.message_id] = data
        return data

    async def delete(self, msg: t.Message, markup: bool = True):
        data = self.remove(msg)

        if data:
            if markup:
                await msg.delete_reply_markup()
            else:
                await msg.delete()

        return data
