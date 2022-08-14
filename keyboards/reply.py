from aiogram.types import ReplyKeyboardMarkup

from data.strings import AddMessagesS

add_message_markup = ReplyKeyboardMarkup(resize_keyboard=True)
add_message_markup.row(AddMessagesS.add_messages)
