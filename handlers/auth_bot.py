import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from pyrogram.enums import SentCodeType
from pyrogram.errors import FloodWait, PhoneCodeInvalid, SessionPasswordNeeded

from handlers.states import AuthBotState
from keyboards.callbackdatas import auth_bot_data
from loader import dp, db_bots, current_machines
from data.strings import  ChooseMachineS, AuthBotS, success


@dp.callback_query_handler(auth_bot_data.filter())
async def auth_bot(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    bot = db_bots.get_one_by_id(callback_data['id_'])
    bot.phone = bot.phone.__str__()
    machine = current_machines.get_machine(bot)
    try:
        sent_code = await machine.send_code(phone_number=bot.phone)
    except Exception as ex:
        error_text = ex.__str__()
        if isinstance(ex, FloodWait):
            db_bots.update_ban_info(bot.id_, ban=error_text)
        await call.message.answer(error_text)
        await state.finish()
        return
    await AuthBotState.wait_phone_code.set()
    await state.update_data(phone_code_hash=sent_code.phone_code_hash, phone=bot.phone.__str__(), id_=bot.id_)
    match sent_code.type:
        case SentCodeType.APP:
            await call.answer(ChooseMachineS.app_type_sent)
        case SentCodeType.SMS:
            await call.answer(ChooseMachineS.phone_type_sent)
        case _:
            await call.answer(ChooseMachineS.call_type_sent)


    await call.message.answer(ChooseMachineS.ask_sent_code)


@dp.message_handler(state=AuthBotState.wait_phone_code)
async def sign_in_bot(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        phone_code_hash = data['phone_code_hash']
        id_ = data['id_']
        phone = data['phone']
    bot = db_bots.get_one_by_id(id_)
    machine = current_machines.get_machine(bot)
    try:
        await machine.sign_in(phone, phone_code_hash, message.text)

        # logging.info(await machine.get_me())
        await message.answer(success)
        await state.finish()
    except PhoneCodeInvalid:
        await message.answer(AuthBotS.wrong_phone_code)
    except SessionPasswordNeeded:
        await machine.check_password(machine.password)
        await message.answer(success)




