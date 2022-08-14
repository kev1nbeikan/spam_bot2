from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command

from data.strings import ChooseMachineS, CommandsS, menu
from keyboards.inline import main_keyboard
from loader import dp


# @dp.callback_query_handler(state='*')
# async def echo(call: types.CallbackQuery):
#     await call.answer('123213', show_alert=True)


@dp.callback_query_handler(Text(menu), state='*')
async def choose(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(ChooseMachineS.hello.format(username=call.from_user.first_name),
                                 reply_markup=main_keyboard)
    await state.finish()


@dp.message_handler(Command(CommandsS.START), state='*')
async def choose(message: types.Message, state: FSMContext):
    await message.answer(ChooseMachineS.hello.format(username=message.from_user.first_name),
                         reply_markup=main_keyboard)
    await state.finish()
