from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from data.strings import ChooseMachineS, is_correct, query_is_correct, AddGroupsS, AddMessagesS, SaveSpamParamsS, yes, \
    yes_query, no_query, no

main_keyboard = InlineKeyboardMarkup()
main_keyboard.row(InlineKeyboardButton(ChooseMachineS.choose_bot, callback_data=ChooseMachineS.query_choose_bot),
                  InlineKeyboardButton(ChooseMachineS.add_bot, callback_data=ChooseMachineS.query_add_bot))
main_keyboard.row(
    InlineKeyboardButton(ChooseMachineS.activate_proxy, callback_data=ChooseMachineS.activate_proxy),
    InlineKeyboardButton(ChooseMachineS.add_proxy, callback_data=ChooseMachineS.query_add_proxy)
)
main_keyboard.row(
    InlineKeyboardButton(AddMessagesS.add_messages, callback_data=AddMessagesS.add_messages_query),
    InlineKeyboardButton(AddMessagesS.show_messages, callback_data=AddMessagesS.show_messages_query)
)
main_keyboard.row(
    InlineKeyboardButton(AddGroupsS.add_groups, callback_data=AddGroupsS.add_groups_query),
    InlineKeyboardButton(AddGroupsS.show_groups, callback_data=AddGroupsS.show_groups_query)
)
main_keyboard.row(
    InlineKeyboardButton(SaveSpamParamsS.show_saved_spam, callback_data=SaveSpamParamsS.show_saved_spam_query),
    InlineKeyboardButton(SaveSpamParamsS.save_spam, callback_data=SaveSpamParamsS.save_spam_query)
)


is_correct_keyboard =  InlineKeyboardMarkup()
is_correct_keyboard.row(InlineKeyboardButton(is_correct, callback_data=query_is_correct))


is_postbot_keyboard = InlineKeyboardMarkup()
is_postbot_keyboard.row(
    InlineKeyboardButton(yes, callback_data=yes_query),
    InlineKeyboardButton(no, callback_data=no_query)

)

