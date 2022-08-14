import dataclasses

from .databasebaseobject import DBBaseObject


@dataclasses.dataclass
class FileGroup:
    id_: int = None
    name: str = None
    tg_id: str = None
    is_choose: bool = None


class GroupsDB(DBBaseObject):
    NAME_OF_TABLE = 'groups'

    ID_COLUMN = 'id'
    NAME_COLUMN = 'name'
    TELEGRAM_SERVER_FILE_ID_COLUMN = 'telegram_server_file_id'
    IS_CHOOSE_COLUMN = 'is_choose'

    def __init__(self, path_db):
        super().__init__(path_db)

    def make_table(self):
        sessions_check = f'''
                CREATE TABLE IF NOT EXISTS {self.NAME_OF_TABLE}( 
                {self.ID_COLUMN} INTEGER PRIMARY KEY,
                {self.NAME_COLUMN} STRING,
                {self.TELEGRAM_SERVER_FILE_ID_COLUMN} STRING,
                {self.IS_CHOOSE_COLUMN} BOOL);'''
        self.execute(sessions_check, commit=True)

    def get_all(self) -> list[FileGroup]:
        command = f'''SELECT * FROM {self.NAME_OF_TABLE};'''
        f = self.execute(command, fetch_all=True)
        return list(map(lambda x: FileGroup(*x), f))

    def get_one_by_id(self, id_: int) -> FileGroup:
        command = f'''SELECT * FROM {self.NAME_OF_TABLE} WHERE {self.ID_COLUMN} = ?;'''
        f = self.execute(command, (id_,), fetch_one=True)
        return FileGroup(*f) if f else None

    def add_one(self, name: str, tg_id: str):
        command = f'INSERT INTO {self.NAME_OF_TABLE} ({self.NAME_COLUMN}, {self.TELEGRAM_SERVER_FILE_ID_COLUMN}, {self.IS_CHOOSE_COLUMN}) ' \
                  f'VALUES (?, ?, {not self.get_one_where_choose_is_true()});'

        self.execute(command, (name, tg_id), commit=True)

    def drop_one_by_id(self, id_: int):
        group = self.get_one_by_id(id_)
        command = f'DELETE FROM {self.NAME_OF_TABLE} WHERE {self.ID_COLUMN} = ?;'
        self.execute(command, (id_,), commit=True)
        lst_id = self.get_last_id()
        if group.is_choose and lst_id:
            self.update_choose_column_by_id(lst_id, True)

    def get_last_id(self):
        command = f'SELECT {self.ID_COLUMN} FROM {self.NAME_OF_TABLE} ORDER BY {self.ID_COLUMN} DESC'
        f = self.execute(command, fetch_one=True)
        return f[0] if f else None

    def get_one_by_name(self, name: str):
        command = f'SELECT * FROM {self.NAME_OF_TABLE} WHERE {self.NAME_COLUMN} = ?'
        return FileGroup(*self.execute(command, (name,), fetch_one=True))

    def switch_all_choose_except_one(self, id_: int, state: bool = False):
        """
        :param id_: id of one element which will not be changed
        :return:
        """
        command = f'UPDATE {self.NAME_OF_TABLE} SET {self.IS_CHOOSE_COLUMN} = ? WHERE {self.ID_COLUMN} <> ?;'

        self.execute(command, (state, id_,), commit=True)

    def switch_one_true_and_false_other(self, id_):
        self.update_choose_column_by_id(id_, True)
        self.switch_all_choose_except_one(id_)

    def get_one_where_choose_is_true(self):
        command = f'SELECT * FROM {self.NAME_OF_TABLE} WHERE {self.IS_CHOOSE_COLUMN} = TRUE;'
        f = self.execute(command, fetch_one=True)
        return FileGroup(*f) if f else None

    def update_choose_column_by_id(self, id_: int, state: bool):
        command = f'UPDATE {self.NAME_OF_TABLE} SET {self.IS_CHOOSE_COLUMN} = ? WHERE {self.ID_COLUMN} = ?;'
        self.execute(command, (state, id_), commit=True)
