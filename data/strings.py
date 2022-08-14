is_correct = 'верно'
query_is_correct = 'correct'
menu = 'меню'
success = 'успешно'
auth_require = 'требует авторизации'
delete = 'удалить'
turn = 'включить'
yes_query = 'yes'
no_query = 'no'
yes = 'да'
no = 'нет'


NOT_BAN_MSG_FROM_SPAM_BOT = ['Good news, no limits are currently applied to your account. You’re free as a bird!',
                             'Ваш аккаунт свободен от каких-либо ограничений.']


class ChooseMachineS:
    ASK_PASSWORD = 'введите парль для двухфакторной аутентификации'
    deactivate = 'отключить'
    delete_session = 'удалить файл сессии'
    recconnect = 'переподключить'
    auth = 'авторизоваться'
    delete = 'удалить'
    BOT_HAS_BEEN_ADDED = 'Бот добавлен'
    ASK_PHONE = 'Введите номер телефона(пр. +799999999)'
    ASK_API_HASH = 'Введите APP_HASH'
    ASK_API_ID = 'Введите APP_ID'
    hello = 'Привет, {username}. Выбери или добавь нового бота'
    choose_bot = 'выбрать бота'
    add_bot = 'добавить бота'
    query_choose_bot = 'choose_bot'
    query_add_bot = 'add_bot'
    show_bot = '<b>номер</b> {number}\n' \
               '<b>app_id</b> {app_id}\n' \
               '<b>app_hash</b> {app_hash}\n' \
               '<b>двухфакторка</b> {password}\n' \
               '<b>мут инфо(@SpamBot)</b>: {mute}'

    show_proxy = '<b>протокол</b>: {scheme}\n' \
                 '<b>имя хоста</b>{hostname}\n' \
                 '<b>порт</b>{port}\n' \
                 '<b>логин</b>{username}\n' \
                 '<b>пароль</b>{password}'

    update = 'обновить'
    activate = 'включить'
    ask_sent_code = 'введите код'
    activate_proxy = 'proxy'
    add_proxy = 'добавить proxy'
    query_add_proxy = 'add_proxy'

    app_type_sent = 'Код отправлен через приложение'
    phone_type_sent = 'Код отправлен через смс'
    call_type_sent = 'Код отправлен через звонок на телефон'


class AddProxyS:
    ask_scheme = 'введите протокол ("socks4", "socks5", "http" доступны)'
    ask_hostmane = 'введите имя узла(hostname)'
    ask_port = 'введите порт'
    ask_username = 'введите имя пользователя'
    ask_password = 'введите пароль'


class AuthBotS:
    wrong_phone_code = 'Неверный код'


class CommandsS:
    START = 'start'
    JOIN_TO_CHATS = 'join_to_chats'
    JOIN_AND_SENDING = 'join_and_sending'
    GO = 'go'
    CURRENT_PARAMS = 'current'
    STOP_SPAM = 'stop'
    CONTINUE = 'c'
    PAUSE_SPAM = 'p'
    RESTRICTIONS = 'r'


class CommandsAnnotationsS:
    START = 'меню'
    RESTRICTIONS = 'ограничения'
    JOIN_TO_CHATS = '{пауза в секундах}'
    GO = '{после круга} {после отправки} {круги}'
    CURRENT_PARAMS = 'текущие параметры'
    STOP_SPAM = 'закончить спам'
    CONTINUE = 'продолжить спам'
    PAUSE_SPAM = 'приостановить спам'
    JOIN_AND_SENDING = '{после вступления} {после отправки} {после круга} {круги}'


class ManageBotS:
    paused = 'спам приостановлен'
    bot_need_recconnect = 'переподключите бота'
    bot_not_started = 'бот не запущен'
    restrictions_is_none = 'ограничений нет'


class AddGroupsS:
    show_groups = 'файлы'
    choose = 'выбрать'
    delete = 'удалить'
    need_txt_format = 'загрузите файл в txt формате'
    add_groups_query = 'add_groups'
    show_groups_query = 'show_groups'
    ask_name = 'ввевидте название базы'
    add_groups = 'добавить базу'
    ask_files_txt = 'загрузите документов файл .txt'


class AddMessagesS:
    is_postbot = 'это код постбота'
    choose = 'выбрать'
    ask_text = 'введите текст или код сообщения от пост бота'
    add_messages = 'добавить сообщение'
    add_messages_query = 'add_message'
    show_messages = 'сообщения'
    show_messages_query = 'messages'
    delete = "удалить"
    wrong_tags = 'неправильные теги'


class SaveSpamParamsS:
    show_saved_spam = 'спамы'
    save_spam = 'сохранить спам'
    show_saved_spam_query = 'show_save_spam'
    save_spam_query = 'save_spam'
    info = '<b>бот</b>: {number}\n' \
           '<b>база</b>: {file_name}\n' \
           '<b>прокси</b>: {hostname}\n' \
           '<b>сообщение</b>: {msg_text}\n'
