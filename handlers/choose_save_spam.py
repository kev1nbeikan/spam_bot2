import logging

from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.callbackdatas import load_savedspam_data, delete_savedspam_data
from client import SpamMachine
from data.strings import SaveSpamParamsS, ManageBotS, success, delete, turn
from loader import dp, db_spam, db_messages, db_groups, current_machines
from .choose_bot import show_bot

@dp.callback_query_handler(Text(SaveSpamParamsS.save_spam_query))
async def save_spam_params(call: types.CallbackQuery):
    machine: SpamMachine = current_machines.get_current_machine()
    if machine is None:
        await call.message.answer(ManageBotS.bot_not_started)
        return

    group = db_groups.get_one_where_choose_is_true()
    choosen_msg = db_messages.get_one_where_choose_is_true()
    db_spam.add_one(machine.main_db_id, choosen_msg.id_, group.id_)
    await call.answer(success)


@dp.callback_query_handler(Text(SaveSpamParamsS.show_saved_spam_query))
async def show_savedspams(call: types.CallbackQuery):
    for saved_spam in db_spam.get_all():
        button = InlineKeyboardMarkup()
        button.row(
            InlineKeyboardButton(text=delete, callback_data=delete_savedspam_data.new(saved_spam.id_)),
            InlineKeyboardButton(text=turn, callback_data=load_savedspam_data.new(saved_spam.id_))

        )
        await call.message.answer(SaveSpamParamsS.info.format(
            number=saved_spam.bot.phone,
            file_name=saved_spam.file.name,
            hostname=saved_spam.proxy.hostname if saved_spam.proxy else 'нет',
            msg_text=saved_spam.msg.text
        ), reply_markup=button)




@dp.callback_query_handler(delete_savedspam_data.filter())
async def delete_savedspam(call: types.CallbackQuery, callback_data: dict):
    db_spam.drop_one_by_id(callback_data['id_'])
    await call.answer(success)


@dp.callback_query_handler(load_savedspam_data.filter())
async def load_savedspam(call: types.CallbackQuery, callback_data: dict):
    saved_spam = db_spam.get_one_by_id(callback_data['id_'])
    db_messages.switch_one_true_and_false_other(saved_spam.msg.id_)
    db_groups.switch_one_true_and_false_other(saved_spam.file.id_)
    if saved_spam.proxy:
        current_machines.setup_proxy(saved_spam.proxy)
    else:
        current_machines.unninstal_proxy()
    current_machines.setup_current_machine(saved_spam.bot)
    await show_bot(call, {'id_': saved_spam.bot.id_})
    await call.answer(success)


