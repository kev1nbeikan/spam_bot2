from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.strings import ChooseMachineS, menu
from keyboards.callbackdatas import show_proxy_data, delete_proxy_data, activate_proxy_data, deactivate_proxy_data
from loader import dp, db_proxies, current_machines


@dp.callback_query_handler(Text(ChooseMachineS.activate_proxy))
async def show_proxies(call: types.CallbackQuery):
    proxies = db_proxies.get_all()
    buttons = InlineKeyboardMarkup()
    for proxy in proxies:
        buttons.add(
            InlineKeyboardButton(text=proxy.hostname, callback_data=show_proxy_data.new(proxy.id_)),
            InlineKeyboardButton(ChooseMachineS.delete, callback_data=delete_proxy_data.new(id_=proxy.id_)),
                    )
    buttons.add(InlineKeyboardButton(text=menu, callback_data=menu))
    await call.message.edit_reply_markup(buttons)
    await call.answer()


@dp.callback_query_handler(show_proxy_data.filter())
async def show_proxy(call: types.CallbackQuery, callback_data: dict):
    proxy = db_proxies.get_one_by_id(callback_data['id_'])

    buttons = InlineKeyboardMarkup()
    buttons.row(
        InlineKeyboardButton(ChooseMachineS.activate, callback_data=activate_proxy_data.new(id_=proxy.id_)),
        InlineKeyboardButton(ChooseMachineS.deactivate, callback_data=deactivate_proxy_data.new(id_=proxy.id_))

    )

    buttons.add(InlineKeyboardButton(text=menu, callback_data=menu))

    await call.message.edit_text(ChooseMachineS.show_proxy.format(scheme=proxy.scheme,
                                                                  hostname=proxy.hostname,
                                                                  port=proxy.port,
                                                                  username=proxy.username,
                                                                  password=proxy.username),
                                 reply_markup=buttons, parse_mode='')


@dp.callback_query_handler(delete_proxy_data.filter())
async def delete_proxy(call: types.CallbackQuery, callback_data: dict):
    db_proxies.drop_one_by_id(callback_data['id_'])
    await show_proxies(call)
    await call.answer()


@dp.callback_query_handler(activate_proxy_data.filter())
async def setup_proxy(call: types.CallbackQuery, callback_data: dict):
    proxy = db_proxies.get_one_by_id(callback_data['id_'])

    current_machines.setup_proxy(proxy)

    await call.answer()


@dp.callback_query_handler(deactivate_proxy_data.filter())
async def deactivate_proxy(call: types.CallbackQuery, callback_data: dict):
    current_machines.unninstal_proxy()
    await call.answer()