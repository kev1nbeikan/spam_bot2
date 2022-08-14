import asyncio
import logging

from aiogram import types
from aiogram.dispatcher.filters import Command
from pyrogram.errors import UserDeactivated, UserDeactivatedBan, UserRestricted, Unauthorized
from client.client_init import SpamMachine
from client.enum_classes import Switch
from data.config import GROUPS_FILES_PATH, loggi, PAUSE_AFTER_JOIN_TO_CHAT
from data.strings import CommandsS, ManageBotS, SaveSpamParamsS
from loader import dp, current_machines, db_groups, db_messages, db_spam, db_bots, db_proxies
from mics.check_commands import check_args_in_command_go, check_args_in_command_join_and_sending
from mics.help_funcs import is_mean_ban_spambot_msg


@dp.message_handler(Command(CommandsS.RESTRICTIONS))
async def restrictions_handler(message: types.Message):
    machine: SpamMachine = current_machines.get_current_machine()
    if machine is None:
        await message.answer(ManageBotS.bot_not_started)
        return
    if not machine.is_initialized:
        await message.answer(ManageBotS.bot_not_started)
        return

    r = await machine.check_restrictions()
    if r is None:
        await message.answer(ManageBotS.restrictions_is_none)
        return
    await message.answer('\n'.join(r))


@dp.message_handler(Command(CommandsS.CURRENT_PARAMS))
async def show_current_params(message: types.Message):
    machine: SpamMachine = current_machines.get_current_machine()
    if machine is None:
        await message.answer(ManageBotS.bot_not_started)
        return

    await message.answer(SaveSpamParamsS.info.format(
        number=db_bots.get_one_by_id(machine.main_db_id).phone,
        file_name=db_groups.get_one_where_choose_is_true().name,
        hostname=current_machines.get_proxy().hostname
        if current_machines.current_proxy
        else 'нет',
        msg_text=db_messages.get_one_where_choose_is_true().text
    ))


@dp.message_handler(Command(CommandsS.PAUSE_SPAM))
async def pause_c_spam(message: types.Message):
    machine = current_machines.get_current_machine()
    if machine is None:
        await message.answer(ManageBotS.bot_not_started)
        return

    if not machine.is_busy():
        return

    if await machine.switch_task(Switch.OFF):
        await message.answer(ManageBotS.paused)


@dp.message_handler(Command(CommandsS.CONTINUE))
async def continue_spam(message: types.Message):
    machine = current_machines.get_current_machine()
    if machine is None:
        await message.answer(ManageBotS.bot_not_started)
        return

    if not machine.is_busy():
        return

    machine.continue_current_task()


@dp.message_handler(Command(CommandsS.STOP_SPAM))
async def stop_spam(message: types.Message):
    machine = current_machines.get_current_machine()
    if machine is None:
        await message.answer(ManageBotS.bot_not_started)
        return

    if not machine.is_busy():
        return
    await machine.switch_task(Switch.OFF)
    machine.finish_task()


@dp.message_handler(Command(CommandsS.JOIN_TO_CHATS))
async def join_to_chats(message: types.Message):
    machine: SpamMachine = current_machines.get_current_machine()

    if machine is None:
        await message.answer(ManageBotS.bot_not_started)
        return

    if not machine.is_connected:
        await message.answer(ManageBotS.bot_need_recconnect)
        return

    if machine.is_busy():
        await message.answer("На данный момент бот занят")
        return

    usernames = []

    args = message.get_args()
    pause = PAUSE_AFTER_JOIN_TO_CHAT
    if args:
        if args[0].isdigit():
            pause = int(args[0])

    group = db_groups.get_one_where_choose_is_true()
    try:
        with open(f'{GROUPS_FILES_PATH}{group.id_}.txt', "r", encoding="utf-8") as file:

            users = file.read().split("\n")

    except FileNotFoundError:
        await message.answer(f"Файла {group.id_}.txt не существует")
        return

    for line in users:
        usernames.append(line.replace('\feff', '').replace('\n', '').replace('@', ''))
    async for result in machine.join_to_groups(usernames):

        if result is None:
            break

        if result.is_done:
            await dp.bot.send_message(loggi, f"{machine.phone_number}: Аккаунт успешно зашел в {result.username}")
        else:

            await dp.bot.send_message(loggi,
                                      f"{machine.phone_number}: Не удалось зайти в {result.username}\n Код ошибки: <i>{str(result.msg)}</i>")

            if isinstance(result.msg, UserDeactivated | UserDeactivatedBan | UserRestricted | Unauthorized):
                await restrictions_handler(message)
                break

        await asyncio.sleep(pause)

    await dp.bot.send_message(loggi, f"{machine.phone_number}: вступил во все группы")


@dp.message_handler(Command(CommandsS.GO))
async def start_sending_messages(message: types.Message):
    machine: SpamMachine = current_machines.get_current_machine()
    logging.info('121312')
    if machine is None:
        await message.answer(ManageBotS.bot_not_started)
        return

    if not machine.is_connected:
        await message.answer(ManageBotS.bot_need_recconnect)
        return

    if machine.is_busy():
        await message.answer("На данный момент бот занят")
        return

    usernames = []

    args = message.get_args().split()
    if res := check_args_in_command_go(args):
        await message.answer(res)
        return

    group = db_groups.get_one_where_choose_is_true()
    try:
        with open(f'{GROUPS_FILES_PATH}{group.id_}.txt', "r", encoding="utf-8") as file:

            users = file.read().split("\n")

    except FileNotFoundError:
        await message.answer(f"Файла {group.id_}.txt не существует")
        return

    pause_after_sending_all_messages = int(args[0]) * 60
    pause_after_sending_one_message = int(args[1])
    repeat_count = int(args[2]) if len(args) >= 3 else 1

    choosen_msg = db_messages.get_one_where_choose_is_true()

    for line in users:
        usernames.append(line.replace('\feff', '').replace('\n', '').replace('@', ''))
    last = 0

    async for result in machine.send_messages(usernames, choosen_msg.text, repeat_count, choosen_msg.is_postobt):
        if result is None:
            break
        if last != result.circle:
            await dp.bot.send_message(loggi, f"{machine.phone_number}: Круг {last} завершен. Сон {args[0]} минут(ы/а)")
            await asyncio.sleep(pause_after_sending_all_messages)
            mute = await machine.get_ban_info()

            await message.answer(mute)
            last = result.circle

        if result.is_done:
            await dp.bot.send_message(loggi, f"{machine.phone_number}:  Отправилось сообщение в {result.username}")
        else:

            await dp.bot.send_message(loggi,
                                      f"{machine.phone_number}: Не удалось отправить сообщение в {result.username}\n Код ошибки: <i>{str(result.msg)}</i>")

            if isinstance(result.msg, UserDeactivated | UserDeactivatedBan | UserRestricted | Unauthorized):
                await message.answer(f'{machine.phone_number}: аккаунт забанен')
                break

        await asyncio.sleep(pause_after_sending_one_message)

    await dp.bot.send_message(loggi, f"{machine.phone_number}: Рассылка завершена")


@dp.message_handler(Command(CommandsS.JOIN_AND_SENDING))
async def join_and_sending(message: types.Message):
    machine: SpamMachine = current_machines.get_current_machine()

    if machine is None:
        await message.answer(ManageBotS.bot_not_started)
        return

    if not machine.is_connected:
        await message.answer(ManageBotS.bot_need_recconnect)
        return

    if machine.is_busy():
        await message.answer("На данный момент бот занят")
        return

    usernames = []

    args = message.get_args().split()
    if res := check_args_in_command_join_and_sending(args):
        await message.answer(res)
        return

    group = db_groups.get_one_where_choose_is_true()
    try:
        with open(f'{GROUPS_FILES_PATH}{group.id_}.txt', "r", encoding="utf-8") as file:

            users = file.read().split("\n")

    except FileNotFoundError:
        await message.answer(f"Файла {group.id_}.txt не существует")
        return

    pause_after_join_group = int(args[0])
    pause_after_sending_all_messages = int(args[1]) * 60
    pause_after_sending_one_message = int(args[2])
    repeat_count = int(args[3]) if len(args) >= 4 else 1

    choosen_msg = db_messages.get_one_where_choose_is_true()



    for line in users:
        usernames.append(line.replace('\feff', '').replace('\n', '').replace('@', ''))


    success_result_msgs = {machine.JOIN_TO_GROUP: '{machine}: Аккаунт успешно зашел в {username}',
                          machine.SEND_MESSAGES: '{machine}: Отправилось сообщение в {username}'}

    error_result_msgs =  {machine.JOIN_TO_GROUP: "{machine}: Не удалось вступить в {username}\n Код ошибки: <i>{msg}</i>",
                          machine.SEND_MESSAGES: "{machine}: Не удалось отправить сообщение в {username}\n Код ошибки: <i>{msg}</i>"}


    last = 0

    async for result in machine.join_and_send_messages(usernames, choosen_msg.text, repeat_count, choosen_msg.is_postobt):
        if result is None:
            break
        logging.info(result.circle)
        if last != result.circle:
            await dp.bot.send_message(loggi, f"{machine.phone_number}: Круг {last} завершен. Сон {args[0]} минут(ы/а)")
            await asyncio.sleep(pause_after_sending_all_messages)
            mute = await machine.get_ban_info()
            await message.answer(mute)
            last = result.circle

        if result.is_done:
            await dp.bot.send_message(loggi, success_result_msgs[result.task].format(machine=machine.phone_number, username=result.username))
        else:

            await dp.bot.send_message(loggi,
                                      error_result_msgs[result.task].format(machine=machine.phone_number, username=result.username, msg=str(result.msg)))

            if isinstance(result.msg, UserDeactivated | UserDeactivatedBan | UserRestricted | Unauthorized):
                await message.answer(f'{machine.phone_number}: аккаунт забанен')
                break
        if result.task == machine.JOIN_TO_GROUP:
            await asyncio.sleep(pause_after_join_group)
        else:
            await asyncio.sleep(pause_after_sending_one_message)

    await dp.bot.send_message(loggi, f"{machine.phone_number}: Рассылка завершена")


