import logging

from aiogram import types

from loader import dp


@dp.errors_handler()
async def parse_tags_handler(update: types.Update, exception):
    logging.info(exception)
