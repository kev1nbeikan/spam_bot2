# add_messages bot handlers
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from data.strings import ChooseMachineS, query_is_correct
from handlers.states import AddBotState
from keyboards.inline import is_correct_keyboard
from loader import dp, db_bots



@dp.callback_query_handler(Text(ChooseMachineS.query_add_bot))
async def ask_app_id(call: types.CallbackQuery):
    await call.message.answer(ChooseMachineS.ASK_API_ID)
    await AddBotState.wait_api_id.set()
    await call.answer()


@dp.message_handler(state=AddBotState.wait_api_id)
async def add_app_id(message: types.Message, state: FSMContext):
    await message.answer(message.text, reply_markup=is_correct_keyboard)


@dp.callback_query_handler(Text(query_is_correct), state=AddBotState.wait_api_id)
async def save_app_id_ask_app_hash(call: types.CallbackQuery, state: FSMContext):
    app_id = call.message.text
    await state.update_data(app_id=app_id)
    await call.answer()
    await call.message.answer(ChooseMachineS.ASK_API_HASH)
    await AddBotState.wait_api_hash.set()


@dp.message_handler(state=AddBotState.wait_api_hash)
async def add_app_hash(message: types.Message, state: FSMContext):
    await message.answer(message.text, reply_markup=is_correct_keyboard)


@dp.callback_query_handler(Text(query_is_correct), state=AddBotState.wait_api_hash)
async def save_app_hash_ask_phone(call: types.CallbackQuery, state: FSMContext):
    app_hash = call.message.text
    await state.update_data(app_hash=app_hash)

    await call.answer()
    await call.message.answer(ChooseMachineS.ASK_PHONE)
    await AddBotState.wait_phone.set()


@dp.message_handler(state=AddBotState.wait_phone)
async def add_phone(message: types.Message, state: FSMContext):
    await message.answer(message.text, reply_markup=is_correct_keyboard)


@dp.callback_query_handler(Text(query_is_correct), state=AddBotState.wait_phone)
async def save_phone_ask_password(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(phone=call.message.text.replace(' ', ''))
    await call.answer()
    await call.message.answer(ChooseMachineS.ASK_PASSWORD)
    await AddBotState.wait_password.set()


@dp.message_handler(state=AddBotState.wait_password)
async def add_password(message: types.Message, state: FSMContext):
    await message.answer(message.text, reply_markup=is_correct_keyboard)


@dp.callback_query_handler(Text(query_is_correct), state=AddBotState.wait_password)
async def save_password_add_bot(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    db_bots.add_one(phone=data['phone'], app_id=data['app_id'], app_hash=data['app_hash'], password=call.message.text)
    await call.message.answer(ChooseMachineS.BOT_HAS_BEEN_ADDED)
    await state.finish()
    await call.answer()
