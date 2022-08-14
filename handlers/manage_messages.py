import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import CantParseEntities

from data.strings import AddMessagesS, query_is_correct, success, yes_query
from handlers.states import AddMessagesStates
from keyboards.callbackdatas import delete_message_data, choose_message_data
from keyboards.inline import is_correct_keyboard, is_postbot_keyboard
from loader import dp, db_messages


@dp.callback_query_handler(Text(AddMessagesS.show_messages_query))
async def show_messages(call: types.CallbackQuery, state: FSMContext):
    messages = db_messages.get_all()

    for msg in messages:
        button = InlineKeyboardMarkup()

        button.row(InlineKeyboardButton(AddMessagesS.delete, callback_data=delete_message_data.new(id_=msg.id_)))
        if not msg.is_choose:
            button.insert(
                InlineKeyboardButton(AddMessagesS.choose, callback_data=choose_message_data.new(id_=msg.id_)),
            )
            await call.message.answer(text=msg.text, reply_markup=button)

        else:
            msg = await call.message.answer(text=msg.text, reply_markup=button)
            await state.update_data(msg_id=msg.message_id)

    await call.answer()


@dp.callback_query_handler(Text(AddMessagesS.add_messages_query))
async def ask_message(call: types.CallbackQuery):
    await call.message.answer(AddMessagesS.ask_text)
    await AddMessagesStates.wait_text.set()
    await call.answer()


@dp.message_handler(state=AddMessagesStates.wait_text)
async def get_text(message: types.Message, state: FSMContext):
    try:
        await message.answer(message.text, reply_markup=is_correct_keyboard)
        await state.update_data(text=message.text)
    except CantParseEntities:
        await message.answer(AddMessagesS.wrong_tags)


@dp.callback_query_handler(Text(query_is_correct), state=AddMessagesStates.wait_text)
async def save_message_and_ask_is_postbot(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(AddMessagesS.is_postbot, reply_markup=is_postbot_keyboard)
    await AddMessagesStates.wait_is_postbot.set()
    await call.answer(success)


@dp.callback_query_handler(state=AddMessagesStates.wait_is_postbot)
async def is_postbot(call: types.CallbackQuery, state: FSMContext):
    cmd = call.data
    data = await state.get_data()
    logging.info(yes_query == cmd)
    db_messages.add_one(data['text'], yes_query == cmd)
    await state.finish()
    await call.answer(success)




@dp.callback_query_handler(choose_message_data.filter())
async def choose_message(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    msg = db_messages.get_one_by_id(callback_data['id_'])
    db_messages.switch_all_choose_except_one(msg.id_)
    db_messages.update_choose_column_by_id(msg.id_, True)

    async with state.proxy() as data:
        msg_id = data['msg_id']

        button = InlineKeyboardMarkup()
        button.row(
            InlineKeyboardButton(AddMessagesS.delete, callback_data=delete_message_data.new(id_=msg.id_)),
            InlineKeyboardButton(AddMessagesS.choose, callback_data=choose_message_data.new(id_=msg.id_))
        )
        await dp.bot.edit_message_reply_markup(call.from_user.id, msg_id, reply_markup=button)

        data['msg_id'] = call.message.message_id

    button = InlineKeyboardMarkup()
    button.row(
        InlineKeyboardButton(AddMessagesS.delete, callback_data=delete_message_data.new(id_=msg.id_))
    )

    await call.message.edit_reply_markup(button)
    await call.answer(success)


@dp.callback_query_handler(delete_message_data.filter())
async def delete_msg(call: types.CallbackQuery, callback_data: dict):
    db_messages.drop_one_by_id(callback_data['id_'])
    await call.message.delete()
    await call.answer(success)





