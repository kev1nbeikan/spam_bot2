import asyncio
from contextlib import suppress

from aiogram.dispatcher import Dispatcher
from pyrogram.errors import SessionPasswordNeeded

from client.client_init import SpamMachine, Switch
from mics.setup_commands import set_default_commands
from loader import current_machines, db_spam, db_bots, db_groups, db_proxies, db_messages
from data.config import loggi

async def stop_spam(spam: SpamMachine):
    # await asyncio.sleep(2)
    # print('Пауза', await spam.switch_task(Switch.OFF))
    # await asyncio.sleep(4)
    # print('Продолжаем', spam.continue_current_task())
    # await asyncio.sleep(4)
    # print('Остановка')
    # await spam.switch_task(Switch.OFF)
    # await spam.finish_task()
    pass


async def main():
    bot = db_bots.get_one_by_id(3)
    machine = current_machines.get_machine(bot)

    await machine.connect()
    print(machine.password)
    sentcode = await machine.send_code(bot.phone)
    print(sentcode)
    try:
        await machine.sign_in(phone_code_hash=sentcode.phone_code_hash, phone_number=bot.phone, phone_code=input())

    except SessionPasswordNeeded as e:
        print(await machine.check_password(machine.password))

    user = await machine.get_me()
    print(user.first_name)
    m = await machine.send_message('learn_for_shaida_bot', text='123123')
    print(m)
    # await m.delete()
    # await machine.connect()
#





    pass


async def on_startup(dp: Dispatcher):
    # import filters
    # import middlewares
    # filters.setup(dp)
    # middlewares.setup(dp)

    # from utils.notify_admins import on_startup_notify
    # await on_startup_notify(dp)
    set_default_commands(dp)
    pass


if __name__ == '__main__':
    from aiogram import executor, Dispatcher
    from handlers import dp

    # asyncio.run(main())
    executor.start_polling(dp, on_startup=on_startup)
