import sqlite3


class DBBaseObject:
    NAME_OF_TABLE = ''

    def __init__(self, path_db):
        self.path_db = path_db

    def make_table(self):
        pass

    @property
    def connection(self):
        return sqlite3.connect(self.path_db)

    def execute(self, command: str, params: tuple = (), fetch_one=False, fetch_all=False, commit=False) -> tuple | list[tuple]:

        connection = self.connection
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute(command, params)

        data = None

        if commit:
            connection.commit()
        if fetch_one:
            data = cursor.fetchone()
        if fetch_all:
            data = cursor.fetchall()

        connection.close()

        return data

    def delete(self):
        command = f'''DROP TABLE IF EXISTS {self.NAME_OF_TABLE}'''
        self.execute(command, commit=True)

    def clean(self):
        command = f'''DELETE FROM  {self.NAME_OF_TABLE}'''
        self.execute(command, commit=True)

