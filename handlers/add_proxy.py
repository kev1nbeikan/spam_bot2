import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from data.strings import ChooseMachineS, AddProxyS, query_is_correct, success
from keyboards.inline import is_correct_keyboard
from loader import dp, db_proxies
from .states import AddProxyState


@dp.callback_query_handler(Text(ChooseMachineS.query_add_proxy))
async def first_state_handler(call: types.CallbackQuery):
    await AddProxyState.first()
    await call.message.answer(AddProxyState.asks[AddProxyState.wait_scheme.state])


@dp.callback_query_handler(Text(query_is_correct), state=AddProxyState.wait_password)
async def last_state_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        db_proxies.add_one(*data.values(), call.message.text)
    await call.message.answer(success)
    await call.answer()

@dp.callback_query_handler(Text([ChooseMachineS.query_add_proxy, query_is_correct]), state=AddProxyState.states)
async def ask_scheme(call: types.CallbackQuery, state: FSMContext):
    current = await state.get_state()

    async with state.proxy() as data:
        data[current] = call.message.text

    next = await AddProxyState.next()

    await call.message.answer(AddProxyState.asks[next])
    await call.answer()


@dp.message_handler(state=AddProxyState.states)
async def get_scheme(message: types.Message):
    await message.answer(message.text, reply_markup=is_correct_keyboard)


