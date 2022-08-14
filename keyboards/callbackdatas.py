from aiogram.utils.callback_data import CallbackData

show_bots_data = CallbackData('show_bot', 'id_')
get_mut_bot_data = CallbackData('bot_mute', 'id_')
activate_bot_data = CallbackData('bot_activate', 'id_')
delete_bot_data = CallbackData('delete_bot', 'id_')
auth_bot_data = CallbackData('auth_bot', 'id_')
reconnectbot_data = CallbackData('reconnectbot', 'id_')


show_proxy_data = CallbackData('show_proxy', 'id_')
delete_proxy_data = CallbackData('delete_proxy', 'id_')
activate_proxy_data = CallbackData('activate_proxy', 'id_')
deactivate_proxy_data = CallbackData('deactivate_proxy', 'id_')

delete_file_session_data = CallbackData('delete_session', 'id_')

delete_message_data = CallbackData('delete_message_data', 'id_')
choose_message_data = CallbackData('choose_message_data', 'id_')

delete_group_data = CallbackData('delete_group_data', 'id_')
choose_group_data = CallbackData('choose_group_data', 'id_')


load_savedspam_data = CallbackData('delete_savedspam_data', 'id_')
delete_savedspam_data = CallbackData('laod_savedspam_data', 'id_')
