import asyncio
import logging
from asyncio import Future
from dataclasses import dataclass
from inspect import iscoroutinefunction

import pyrogram.types
from pyrogram import Client, types, filters
from pyrogram.handlers import MessageHandler

from data.config import SESSION_FILES_PATH
from .enum_classes import Switch


class MachineIsBusy(Exception):

    def __str__(self):
        return 'Machine is busy. Use is_busy() to check before calling funcs'


@dataclass()
class SpamResult:
    username: str | None = None
    is_done: bool | None = None
    msg: Exception | None = None
    circle: int | None = None
    task: str = None


class SpamMachine(Client):
    turn_task: Switch = Switch.OFF

    # used in is_busy
    is_busy_state: bool = False

    _future = None

    _future_turn_task = None

    _is_pause_future = None

    handler = None

    main_db_id = None


    SEND_MESSAGES = 'send_messages'
    JOIN_TO_GROUP = 'join_to_group'

    def __init__(self, name, *args, **kwargs):
        logging.info(SESSION_FILES_PATH + name)
        super().__init__(name=SESSION_FILES_PATH + name, *args, **kwargs)

        self._future = Future()

    async def connect(
            self: "pyrogram.Client",
    ) -> bool:
        if not self.is_connected:
            return await super().connect()

    async def start(
            self
    ):
        await super().start()

    async def check_restrictions(self) -> None | tuple:
        me = await self.get_me()
        return me.restrictions

    def setup_handler(self, chat_id=178220800):
        """
        используется в get_ban_info
        :param chat_id:
        :return:
        """

        async def spam_handler(client, message: types.Message):
            self._future.set_result(message.text)

        self.handler = self.add_handler(MessageHandler(spam_handler, filters=filters.chat(chat_id)))

    def refresh_future(self):
        self._future = Future()

    async def get_ban_info(self):
        self.refresh_future()
        self.setup_handler()
        await self.send_message('@SpamBot', text='/start')
        await self._future
        self.remove_handler(*self.handler)
        return self._future.result()

    def is_busy(self) -> bool:
        """
        Проверка: выполняет ли бот другие задачи. true: current_machines is busy
        :return: bool
        """
        return self.is_busy_state

    async def do_spam_task(self, data: list, func, repeat=1):
        if not iscoroutinefunction(func):
            raise TypeError(f'{func.__name__} must be coroutine function')
        if self.is_busy():
            raise MachineIsBusy()

        if data:
            # записываем в переменную, что отправка включена
            await self.switch_task(Switch.ON)
            self.is_busy_state = True
        for _ in range(repeat):
            for chat in data:
                if not self.turn_task:
                    # записываем в переменную, что бот остановился(это сделано на случай, если между вступлениями есть сон)
                    self.is_busy_state = False
                    yield None
                    return
                try:
                    await func(self, chat)
                    yield SpamResult(
                        username=chat,
                        is_done=True,
                    )
                except TypeError:
                    raise
                except Exception as ex:
                    yield SpamResult(
                        username=chat,
                        is_done=False,
                        msg=ex
                    )

            # записываем в переменную, что бот остановился(это сделано на случай, если между отправками есть сон)
            self.is_busy_state = False
            self.turn_task = Switch.OFF
            yield None

    async def join_to_groups(self, groups: list):
        """
        Итератор, при каждом вызове добавляется в чат из массива. Если группы закончились, возвращает None.

        :param groups:
        :return:
        """
        if self.is_busy():
            raise MachineIsBusy()

        if groups:
            # записываем в переменную, что отправка включена
            await self._activate_machine()

        for chat in groups:
            if not self.turn_task:
                self._is_pause_future.set_result(True)
                if await self._future_turn_task:
                    self.is_busy_state = False
                    yield None
                    return
                await self._activate_machine()

            try:
                await self.join_chat(chat)
                yield SpamResult(
                    username=chat,
                    is_done=True,
                )
            except Exception as ex:
                yield SpamResult(
                    username=chat,
                    is_done=False,
                    msg=ex
                )

        # записываем в переменную, что бот остановился(это сделано на случай, если между отправками есть сон)
        self.is_busy_state = False
        self.turn_task = Switch.OFF
        yield None

    def finish_task(self):
        if self.is_busy():
            self._future_turn_task.set_result(True)

    def continue_current_task(self):
        if self.is_busy():
            self._future_turn_task.set_result(False)

    def switch_joining_groups(self, state: Switch):
        """
        :param state: Switch.OFF or Switch.ON
        """
        self.turn_task = state

    def switch_send_messages(self, state: Switch):
        """
        :param state: Switch.OFF or Switch.ON
        """
        self.turn_task = state

    async def switch_task(self, state: Switch):

        self.turn_task = state
        if state:
            self._is_pause_future = self.loop.create_future()
            return None
        else:
            return await self._is_pause_future

    async def _activate_machine(self):
        await self.switch_task(Switch.ON)
        self._future_turn_task = self.loop.create_future()
        self.is_busy_state = True

    async def send_messages(self, chats: list, text, repeat_count=1, is_postbot=False):
        """
        Итератор, при каждом вызове отправляет сообщение в чат из массива. Если отправка окончена возвращает None

        :param groups:
            :return:
        """

        if is_postbot:
            POST_BOT = '@PostBot'
            bot_results = await self.get_inline_bot_results(POST_BOT, text)
            async def task_func(chat):
                await self.send_inline_bot_result(
                    chat, bot_results.query_id,
                    bot_results.results[0].id)

        else:
            async def task_func(chat):
                await self.send_message(chat, text)


        if self.is_busy():
            raise MachineIsBusy()

        # записываем в переменную, что отправка включена
        if chats:
            await self._activate_machine()

        for i in range(repeat_count):
            for chat in chats:
                if not self.turn_task:
                    self._is_pause_future.set_result(True)
                    if await self._future_turn_task:
                        self.is_busy_state = False
                        yield None
                        return
                    await self._activate_machine()

                try:
                    await task_func(chat)
                    yield SpamResult(
                        username=chat,
                        is_done=True,
                        circle=i,
                    )

                except Exception as ex:
                    yield SpamResult(
                        username=chat,
                        is_done=False,
                        msg=ex,
                        circle=i,
                    )

        # записываем в переменную, что бот остановился(это сделано на случай, если между отправками есть сон)
        self.is_busy_state = False
        self.turn_task = Switch.OFF
        yield None

    async def send_via_postbot(self, chats: list, code: str, repeat=1):
        """
        Итератор, при каждом вызове отправляет сообщение в чат из массива используя @PostBot. Если отправка окончена возвращает None
        :param code - код сообщения, получать при создании поста в @PostBot
        """
        POST_BOT = '@PostBot'
        if self.is_busy():
            raise MachineIsBusy()
        bot_results = await self.get_inline_bot_results(POST_BOT, code)

        # записываем в переменную, что отправка включена
        if chats:
            await self._activate_machine()

        for i in range(repeat):
            for chat in chats:
                if not self.turn_task:
                    self._is_pause_future.set_result(True)
                    if await self._future_turn_task:
                        self.is_busy_state = False
                        yield None
                        return
                    await self._activate_machine()
                try:

                    await self.send_inline_bot_result(
                        chat, bot_results.query_id,
                        bot_results.results[0].id)
                    yield SpamResult(
                        username=chat,
                        is_done=True,
                        circle=i
                    )
                except Exception as ex:
                    yield SpamResult(
                        username=chat,
                        is_done=False,
                        msg=ex,
                        circle=i,

                    )

            # записываем в переменную, что бот остановился(это сделано на случай, если между отправками есть сон)
        self.is_busy_state = False
        self.turn_task = Switch.OFF
        yield None




    async def join_and_send_messages(self, chats: list, text, repeat_count=1, is_postbot=False):
        """
        Итератор, при каждом вызове отправляет сообщение в чат из массива. Если отправка окончена возвращает None

        :param groups:
            :return:
        """

        if self.is_busy():
            raise MachineIsBusy()

        if is_postbot:
            POST_BOT = '@PostBot'
            bot_results = await self.get_inline_bot_results(POST_BOT, text)

            async def task_func(chat):
                await self.send_inline_bot_result(
                    chat, bot_results.query_id,
                    bot_results.results[0].id)
        else:
            async def task_func(chat):
                await self.send_message(chat, text)

        # записываем в переменную, что отправка включена
        if chats:
            await self._activate_machine()


        for chat in chats:
            if not self.turn_task:
                self._is_pause_future.set_result(True)
                if await self._future_turn_task:
                    self.is_busy_state = False
                    yield None
                    return
                await self._activate_machine()

            try:
                await self.join_chat(chat_id=chat)
                yield SpamResult(
                    username=chat,
                    is_done=True,
                    task=self.JOIN_TO_GROUP,
                    circle=0,
                )

            except Exception as ex:
                yield SpamResult(
                    username=chat,
                    is_done=False,
                    msg=ex,
                    task=self.JOIN_TO_GROUP,
                    circle=0,

                )


        for i in range(repeat_count):
            for chat in chats:
                if not self.turn_task:
                    self._is_pause_future.set_result(True)
                    if await self._future_turn_task:
                        self.is_busy_state = False
                        yield None
                        return
                    await self._activate_machine()

                try:
                    await task_func(chat)
                    yield SpamResult(
                        username=chat,
                        is_done=True,
                        circle=i,
                        task=self.SEND_MESSAGES,
                    )

                except Exception as ex:
                    yield SpamResult(
                        username=chat,
                        is_done=False,
                        msg=ex,
                        circle=i,
                        task=self.SEND_MESSAGES,
                    )

        # записываем в переменную, что бот остановился(это сделано на случай, если между отправками есть сон)
        self.is_busy_state = False
        self.turn_task = Switch.OFF
        yield None



if __name__ == '__main__':
    pass
