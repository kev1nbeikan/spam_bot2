import asyncio

from aiogram.dispatcher.filters.state import StatesGroup, State

from data.strings import AddProxyS


class AddBotState(StatesGroup):
    wait_phone = State()
    wait_api_hash = State()
    wait_api_id = State()
    wait_password = State()


class AuthBotState(StatesGroup):
    wait_phone_code = State()


class AddProxyState(StatesGroup):
    wait_scheme = State('scheme', 'AddProxyState')
    wait_hostmane = State('hostmane', 'AddProxyState')
    wait_port = State('port', 'AddProxyState')
    wait_username = State('username', 'AddProxyState')
    wait_password = State('password', 'AddProxyState')




    asks = {
        wait_scheme.state: AddProxyS.ask_scheme,
        wait_hostmane.state: AddProxyS.ask_hostmane,
        wait_port.state: AddProxyS.ask_port,
        wait_username.state: AddProxyS.ask_username,
        wait_password.state: AddProxyS.ask_password
    }


class AddGroupsStates(StatesGroup):
    wait_name = State()
    wait_file = State()



class AddMessagesStates(StatesGroup):
    wait_text = State()
    wait_is_postbot = State()


if __name__ == '__main__':
    print(AddProxyState.asks)


