import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import GROUPS_FILES_PATH
from data.strings import AddGroupsS, success
from loader import dp, db_groups
from .states import AddGroupsStates
from keyboards.callbackdatas import delete_group_data, choose_group_data
from mics.file_handler import LocalFileHandler


@dp.callback_query_handler(Text(AddGroupsS.show_groups_query))
async def show_groups(call: types.CallbackQuery, state: FSMContext):
    for group in db_groups.get_all():
        button = InlineKeyboardMarkup()
        button.row(InlineKeyboardButton(AddGroupsS.delete, callback_data=delete_group_data.new(id_=group.id_)))
        if not group.is_choose:
            button.insert(
                InlineKeyboardButton(AddGroupsS.choose, callback_data=choose_group_data.new(id_=group.id_)),
            )
            await call.message.answer(group.name, reply_markup=button)
        else:
            msg = await call.message.answer(group.name, reply_markup=button)
            await state.update_data(msg_id=msg.message_id)


    await call.answer()


@dp.callback_query_handler(choose_group_data.filter())
async def choose_group(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    group = db_groups.get_one_by_id(callback_data['id_'])
    db_groups.switch_all_choose_except_one(group.id_)
    db_groups.update_choose_column_by_id(group.id_, True)

    async with state.proxy() as data:
        msg_id = data['msg_id']

        button = InlineKeyboardMarkup()
        button.row(
            InlineKeyboardButton(AddGroupsS.delete, callback_data=delete_group_data.new(id_=group.id_)),
            InlineKeyboardButton(AddGroupsS.choose, callback_data=choose_group_data.new(id_=group.id_))
        )
        await dp.bot.edit_message_reply_markup(call.from_user.id, msg_id, reply_markup=button)

        data['msg_id'] = call.message.message_id

    button = InlineKeyboardMarkup()
    button.row(
        InlineKeyboardButton(AddGroupsS.delete, callback_data=delete_group_data.new(id_=group.id_))
    )

    await call.message.edit_reply_markup(button)
    await call.answer(success)


@dp.callback_query_handler(delete_group_data.filter())
async def delete_group(call: types.CallbackQuery, callback_data: dict):
    group = db_groups.get_one_by_id(callback_data['id_'])
    db_groups.drop_one_by_id(group.id_)
    LocalFileHandler.delete_file(f'{group.name}.txt')
    await call.message.delete()
    await call.answer(success)


@dp.callback_query_handler(Text(AddGroupsS.add_groups_query))
async def add_groups_handler(call: types.CallbackQuery):
    await call.message.answer(AddGroupsS.ask_name)
    await AddGroupsStates.wait_name.set()
    await call.answer()


@dp.message_handler(state=AddGroupsStates.wait_name)
async def ask_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(AddGroupsS.ask_files_txt)
    await AddGroupsStates.wait_file.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=AddGroupsStates.wait_file)
async def add_groups_handler(message: types.Message, state: FSMContext):

    document = message.document

    if 'txt' not in document.file_name:
        await message.answer(AddGroupsS.need_txt_format)
        return

    name = (await state.get_data())['name']
    db_groups.add_one(name, document.file_id)
    file_handle = db_groups.get_one_by_name(name)
    await document.download(f'{GROUPS_FILES_PATH}{file_handle.id_}.txt')
    await state.finish()
    await message.answer(success)


