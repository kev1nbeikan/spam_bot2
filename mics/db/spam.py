import dataclasses

from .databasebaseobject import DBBaseObject
from .groups import GroupsDB, FileGroup
from .messages import MessagesDB, MessageHandle
from .proxies import Proxy, ProxyDB
from .sessions import Session, BotFileDB


@dataclasses.dataclass
class SpamHandle:
    id_: int = None
    bot: Session = None
    proxy: Proxy = None
    msg: MessageHandle = None
    file: FileGroup = None


class SpamParamsDB(DBBaseObject):
    NAME_OF_TABLE = 'spam_params'

    ID_COLUMN = 'id'
    BOT_COLUMN = 'bot'
    PROXY_COLUMN = 'proxy'
    MSG_COLUMN = 'message'
    FILE_COLUMN = 'file'

    db_bots: BotFileDB
    db_proxies: ProxyDB
    db_groups: GroupsDB
    db_messages: MessagesDB

    def __init__(self, db_bots: BotFileDB,
                 db_proxies: ProxyDB,
                 db_groups: GroupsDB,
                 db_messages: MessagesDB, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db_bots = db_bots
        self.db_proxies = db_proxies
        self.db_groups = db_groups
        self.db_messages = db_messages

    def _load_from_dbs(self, bot_id: int | None,
                       proxy: int | None,
                       msg: int | None,
                       file_id: int | None) -> tuple:
        return self.db_bots.get_one_by_id(bot_id), \
               self.db_proxies.get_one_by_id(proxy) if proxy else None, \
               self.db_messages.get_one_by_id(msg), \
               self.db_groups.get_one_by_id(file_id), \

    def _pack_data_to_spamhandler(self, x: tuple):
        return SpamHandle(x[0], *self._load_from_dbs(*x[1:]))

    def make_table(self):
        table = f'CREATE TABLE IF NOT EXISTS {self.NAME_OF_TABLE}' \
                f'({self.ID_COLUMN} INTEGER PRIMARY KEY,\n' \
                f'{self.BOT_COLUMN} INTEGER,\n' \
                f'{self.PROXY_COLUMN} INTEGER,\n' \
                f'{self.MSG_COLUMN} INTEGER,\n' \
                f'{self.FILE_COLUMN} INTEGER,\n' \
                f'FOREIGN KEY ({self.BOT_COLUMN}) REFERENCES {BotFileDB.NAME_OF_TABLE} ({BotFileDB.ID_COLUMN}) ON DELETE CASCADE,' \
                f'FOREIGN KEY ({self.PROXY_COLUMN}) REFERENCES {ProxyDB.NAME_OF_TABLE} ({ProxyDB.ID_COLUMN}),' \
                f'FOREIGN KEY ({self.MSG_COLUMN}) REFERENCES {MessagesDB.NAME_OF_TABLE} ({MessagesDB.ID_COLUMN}) ON DELETE CASCADE,' \
                f'FOREIGN KEY ({self.FILE_COLUMN}) REFERENCES {GroupsDB.NAME_OF_TABLE} ({GroupsDB.ID_COLUMN}) ON DELETE CASCADE);'

        self.execute(table, commit=True)

    def get_all(self) -> list[SpamHandle]:
        command = f'''SELECT * FROM {self.NAME_OF_TABLE};'''
        f = self.execute(command, fetch_all=True)
        return list(map(self._pack_data_to_spamhandler, f))

    def get_one_by_id(self, id_: int) -> SpamHandle:
        command = f'''SELECT * FROM {self.NAME_OF_TABLE} WHERE {self.ID_COLUMN} = ?;'''
        f = self.execute(command, (id_,), fetch_one=True)
        return self._pack_data_to_spamhandler(f)

    def add_one(self, bot_id: int,
                msg: int,
                file_id: int,
                proxy: int = None, ):
        command = f'INSERT INTO {self.NAME_OF_TABLE} ' \
                  f'({self.BOT_COLUMN}, ' \
                  f'{self.MSG_COLUMN}, ' \
                  f'{self.FILE_COLUMN},' \
                  f'{self.PROXY_COLUMN})' \
                  f'VALUES (?, ?, ?, ?);'

        self.execute(command, (bot_id, msg, file_id, proxy), commit=True)

    def drop_one_by_id(self, id_: int):
        command = f'DELETE FROM {self.NAME_OF_TABLE} WHERE {self.ID_COLUMN} = ?;'
        self.execute(command, (id_,), commit=True)

    def get_last_id(self):
        command = f'SELECT {self.ID_COLUMN} FROM {self.NAME_OF_TABLE} ORDER BY {self.ID_COLUMN} DESC'
        f = self.execute(command, fetch_one=True)
        return f[0] if f else None
