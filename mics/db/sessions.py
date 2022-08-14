import dataclasses

from .databasebaseobject import DBBaseObject


@dataclasses.dataclass(init=False)
class Session:
    id_: int
    ban_info: str
    phone: str
    app_id: str
    app_hash: str
    password: str

    def __init__(self,
                 id_: int,
                 ban_info: str,
                 phone: str,
                 app_id: str,
                 app_hash: str,
                 password: str = None):
        self.id_ = id_
        self.ban_info = str(ban_info)
        self.phone = str(phone)
        self.app_id = str(app_id)
        self.app_hash: str = str(app_hash)
        self.password = str(password)



class BotFileDB(DBBaseObject):
    NAME_OF_TABLE = 'bots_files'
    ID_COLUMN = 'file_name'
    BAN_COLUMN = 'ban_info'
    PHONE_COLUMN = 'phone_number'
    APP_ID = 'app_id'
    APP_HASH = 'app_hash'
    PASSWORD = 'twostep_pass'

    def make_table(self):
        sessions_check = f'''
                CREATE TABLE IF NOT EXISTS {self.NAME_OF_TABLE}(
                {self.ID_COLUMN} INTEGER PRIMARY KEY,
                {self.BAN_COLUMN} STRING,
                {self.PHONE_COLUMN} STRING,
                {self.APP_ID} STRING,
                {self.APP_HASH} STRING,
                {self.PASSWORD} STRING);'''
        self.execute(sessions_check, commit=True)

    def get_all(self) -> list[Session]:
        command = f'''SELECT * FROM {self.NAME_OF_TABLE};'''
        f = self.execute(command, fetch_all=True)
        return list(map(lambda x: Session(*x), f))

    def get_one_by_id(self, id_: int) -> Session:
        command = f'''SELECT * FROM {self.NAME_OF_TABLE} WHERE {self.ID_COLUMN} = ?;'''
        f = self.execute(command, (id_,), fetch_one=True)
        return Session(*f) if f else None

    def add_one(self, ban: str = None, phone: str = None, app_id: str = None, app_hash: str = None,
                password: str = None):
        print(ban.__class__, phone.__class__, app_id.__class__, app_hash.__class__)
        command = f'''INSERT INTO {self.NAME_OF_TABLE} (
                {self.BAN_COLUMN},
                {self.PHONE_COLUMN},
                {self.APP_ID},
                {self.APP_HASH},
                {self.PASSWORD}) VALUES (?, ?, ?, ?, ?);'''

        self.execute(command, (ban, phone, app_id, app_hash, password), commit=True)

    def drop_one_by_id(self, id_: int):
        command = f'DELETE FROM {self.NAME_OF_TABLE} WHERE {self.ID_COLUMN} = ?;'
        self.execute(command, (id_,), commit=True)

    def update_ban_info(self, id_: int, ban: str = None):
        command = f'''UPDATE {self.NAME_OF_TABLE} SET {self.BAN_COLUMN} = ? WHERE {self.ID_COLUMN} = ?;'''
        self.execute(command, (id_, ban), commit=True)


if __name__ == '__main__':
    pass
