import dataclasses
import logging

from .databasebaseobject import DBBaseObject


@dataclasses.dataclass
class MessageHandle:
    id_: int = None
    text: str = None
    is_choose: bool = None
    is_postobt: bool = None


class MessagesDB(DBBaseObject):
    NAME_OF_TABLE = 'messages'

    ID_COLUMN = 'id'
    TEXT_COLUMN = 'text'
    IS_CHOOSE_COLUMN = 'is_choose'
    IS_POSTBOT_COLUMN = 'is_postbot'

    def make_table(self):
        sessions_check = f'''
                CREATE TABLE IF NOT EXISTS {self.NAME_OF_TABLE}( 
                {self.ID_COLUMN} INTEGER PRIMARY KEY,
                {self.TEXT_COLUMN} STRING,
                {self.IS_CHOOSE_COLUMN} BOOL,
                {self.IS_POSTBOT_COLUMN} BOOL);'''

        self.execute(sessions_check, commit=True)

    def get_all(self) -> list[MessageHandle]:
        command = f'''SELECT * FROM {self.NAME_OF_TABLE};'''
        f = self.execute(command, fetch_all=True)
        return list(map(lambda x: MessageHandle(*x), f))

    def get_one_by_id(self, id_: int) -> MessageHandle:
        command = f'''SELECT * FROM {self.NAME_OF_TABLE} WHERE {self.ID_COLUMN} = ?;'''
        f = self.execute(command, (id_,), fetch_one=True)
        return MessageHandle(*f)

    def add_one(self, text: str, postbot: bool):

        command = f'INSERT INTO {self.NAME_OF_TABLE} ({self.TEXT_COLUMN}, {self.IS_CHOOSE_COLUMN}, {self.IS_POSTBOT_COLUMN}) ' \
                  f'VALUES (?, {not self.get_one_where_choose_is_true()}, ?);'
        logging.info(postbot)
        self.execute(command, (text, postbot), commit=True)

    def drop_one_by_id(self, id_: int):
        msg = self.get_one_by_id(id_)
        command = f'DELETE FROM {self.NAME_OF_TABLE} WHERE {self.ID_COLUMN} = ?;'
        self.execute(command, (id_,), commit=True)
        lst_id = self.get_last_id()
        if msg.is_choose and lst_id:
            self.update_choose_column_by_id(lst_id, True)

    def update_choose_column_by_id(self, id_: int, state: bool):
        command = f'UPDATE {self.NAME_OF_TABLE} SET {self.IS_CHOOSE_COLUMN} = ? WHERE {self.ID_COLUMN} = ?;'
        self.execute(command, (state, id_), commit=True)

    def switch_all_choose_except_one(self, id_: int, state: bool = False):
        """
        :param id_: id of one element which will not be changed
        :return:
        """
        command = f'UPDATE {self.NAME_OF_TABLE} SET {self.IS_CHOOSE_COLUMN} = ? WHERE {self.ID_COLUMN} <> ?;'

        self.execute(command, (state, id_,), commit=True)

    def get_one_where_choose_is_true(self):
        command = f'SELECT * FROM {self.NAME_OF_TABLE} WHERE {self.IS_CHOOSE_COLUMN} = TRUE;'
        f = self.execute(command, fetch_one=True)
        return MessageHandle(*f) if f else None

    def switch_one_true_and_false_other(self, id_):
        self.update_choose_column_by_id(id_, True)
        self.switch_all_choose_except_one(id_)

    def get_last_id(self):
        command = f'SELECT {self.ID_COLUMN} FROM {self.NAME_OF_TABLE} ORDER BY {self.ID_COLUMN} DESC'

        return self.execute(command, fetch_one=True)[0]

    def update_postbot_column_by_id(self, id_: int,  postbot: bool):
        command = f'UPDATE {self.NAME_OF_TABLE} SET {self.IS_POSTBOT_COLUMN} = ? WHERE {self.ID_COLUMN} = ?;'

        self.execute(command, (postbot, id_, ), commit=True)
