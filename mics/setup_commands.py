import asyncio

from aiogram import Dispatcher
from aiogram.types import BotCommand


def set_default_commands(dp: Dispatcher):
    from data.strings import CommandsS, CommandsAnnotationsS
    annotations = CommandsAnnotationsS.__dict__
    commands = []
    for key, value in CommandsS.__dict__.items():
        if '__' in key:
            continue
        commands.append(BotCommand(value, annotations[key]))


    asyncio.create_task(dp.bot.set_my_commands(
        commands
    ))