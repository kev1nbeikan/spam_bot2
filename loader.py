from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from client.client_init import SpamMachine
from data import BOT
from data.config import DB_PATH
from mics.db import make_dbs, clean_dbs, delete_dbs, \
    BotFileDB, ProxyDB, GroupsDB, MessagesDB, SpamParamsDB
import logging





db_bots = BotFileDB(DB_PATH)
db_proxies = ProxyDB(DB_PATH)
db_groups = GroupsDB(DB_PATH)
db_messages = MessagesDB(DB_PATH)
db_spam = SpamParamsDB(db_bots, db_proxies, db_groups, db_messages, DB_PATH)
make_dbs(db_bots, db_proxies, db_groups, db_messages, db_spam)



logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    # level=logging.DEBUG,
                    )


from mics.machine_dict import MachineDict

current_machines: MachineDict[SpamMachine] = MachineDict()


bot = Bot(token=BOT, parse_mode=types.ParseMode.HTML)
# storage = RedisStorage2()
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

