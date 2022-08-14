# choose bot handlers
import asyncio
import logging
from contextlib import suppress

from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, UserDeactivated
from pyrogram.errors import AuthKeyUnregistered, RPCError

from data.strings import ChooseMachineS, menu, success, auth_require
from data.config import SESSION_FILES_PATH
from keyboards.callbackdatas import show_bots_data, delete_bot_data, auth_bot_data, activate_bot_data, \
    reconnectbot_data, delete_file_session_data
from loader import db_bots, dp, current_machines
from mics.file_handler import LocalFileHandler
from mics.help_funcs import get_error_explanation


@dp.callback_query_handler(Text(ChooseMachineS.query_choose_bot))
async def show_bots(call: types.CallbackQuery):
    bots = db_bots.get_all()
    buttons = InlineKeyboardMarkup()
    for bot in bots:
        buttons.row(
            InlineKeyboardButton(text=bot.phone, callback_data=show_bots_data.new(bot.id_)),
            InlineKeyboardButton(text=ChooseMachineS.delete, callback_data=delete_bot_data.new(bot.id_))
        )
    buttons.add(InlineKeyboardButton(text=menu, callback_data=menu))
    await call.message.edit_reply_markup(buttons)
    await call.answer()


@dp.callback_query_handler(show_bots_data.filter())
async def show_bot(call: types.CallbackQuery, callback_data: dict):
    await call.answer('ожидание 10 сек')
    bot = db_bots.get_one_by_id(callback_data['id_'])
    buttons = InlineKeyboardMarkup()
    buttons.row(
        InlineKeyboardButton(text=ChooseMachineS.activate, callback_data=activate_bot_data.new(bot.id_)),
        InlineKeyboardButton(text=ChooseMachineS.update, callback_data=show_bots_data.new(bot.id_))
    )
    buttons.row(
        InlineKeyboardButton(text=ChooseMachineS.auth, callback_data=auth_bot_data.new(bot.id_)),
        InlineKeyboardButton(text=ChooseMachineS.delete_session, callback_data=delete_file_session_data.new(bot.id_)),
    )

    machine = current_machines.get_machine(bot)
    # logging.info(f'{machine.proxy}; {current_machines.get_proxy()}')
    # if current_machines.get_proxy() != machine.proxy:
    #     if machine.is_initialized:
    #         await machine.stop()
    #     current_machines.pop(bot.id_)
    #     machine = current_machines.get_machine(bot)
    try:
        if not machine.is_initialized or not machine.is_connected:
            await asyncio.wait_for(machine.connect(), timeout=10)
            await machine.get_me()
            await machine.disconnect()
            await machine.start()
        mute = await machine.get_ban_info()
    except AttributeError as ex:
        await call.message.answer('Ошибка, попробуйте поменять или отключить прокси/бота.\n ' + str(ex))
        return

    except RPCError as ex:
        explain = get_error_explanation(ex)
        if explain:
            mute = explain
        else:
            await call.message.answer('Ошибка, попробуйте еще раз или добавить бота заново.\n ' + str(ex))
            return

    except asyncio.exceptions.TimeoutError as ex:
        await call.message.answer('Долгое ожидание подключения, возможно: нерабочий прокси, проблемы с соединением на хосте.\n ' + str(ex))
        return

    if machine.is_initialized:
        buttons.insert(
            InlineKeyboardButton(text=ChooseMachineS.recconnect, callback_data=reconnectbot_data.new(bot.id_)))

    buttons.add(InlineKeyboardButton(text=menu, callback_data=menu))

    with suppress(MessageNotModified):
        await call.message.edit_text(
            ChooseMachineS.show_bot.format(number=bot.phone, app_id=bot.app_id, app_hash=bot.app_hash, mute=mute, password=bot.password if bot.password else 'нет'),
            reply_markup=buttons)
    await call.answer()


@dp.callback_query_handler(reconnectbot_data.filter())
async def reconnect_bot(call: types.CallbackQuery, callback_data: dict):
    bot = db_bots.get_one_by_id(callback_data['id_'])
    machine = current_machines.get_machine(bot)
    if machine.is_busy():
        return
    if machine.is_initialized:
        await machine.stop()
    current_machines.pop(bot.id_)
    await show_bot(call, callback_data)



@dp.callback_query_handler(delete_bot_data.filter())
async def delete_bot(call: types.CallbackQuery, callback_data: dict):
    db_bots.drop_one_by_id(callback_data['id_'])
    await show_bots(call)


@dp.callback_query_handler(activate_bot_data.filter())
async def activate_bot(call: types.CallbackQuery, callback_data: dict):
    bot = db_bots.get_one_by_id(callback_data['id_'])
    machine = current_machines.get_machine(bot)
    if not machine.is_initialized:
        await call.answer(auth_require)
        return
    current_machines.setup_current_machine(bot)
    await call.answer(success)


@dp.callback_query_handler(delete_file_session_data.filter())
async def delete_session_file(call: types.CallbackQuery, callback_data: dict):
    bot = db_bots.get_one_by_id(callback_data['id_'])
    machine = current_machines.get_machine(bot)
    file_handler = LocalFileHandler()
    if machine.is_initialized:
        await machine.stop()
    if machine.is_connected:
        await machine.disconnect()
    await machine.storage.close()
    file_handler.delete_file(SESSION_FILES_PATH + f'{bot.id_}' + '.session')
    await call.answer(success)

