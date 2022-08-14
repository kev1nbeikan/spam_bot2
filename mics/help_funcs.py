from pyrogram.errors import UserDeactivated, UserDeactivatedBan, UserRestricted, Unauthorized, RPCError
from data.strings import NOT_BAN_MSG_FROM_SPAM_BOT

def get_error_explanation(error: RPCError):
    if isinstance(error, UserDeactivated | UserDeactivatedBan):
        return 'невозможно зайти в аккаунт, бот забанен'

    if error.ID.startswith('AUTH_TOKEN') or isinstance(error, Unauthorized):
        return 'требует авторизации'

    if isinstance(error, UserRestricted):
        return 'мут'

    return None


def is_mean_ban_spambot_msg(msg: str):
    return msg not in NOT_BAN_MSG_FROM_SPAM_BOT







