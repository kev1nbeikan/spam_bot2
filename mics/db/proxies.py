from dataclasses import dataclass

from .databasebaseobject import DBBaseObject


@dataclass(init=False)
class Proxy:
    id_: int
    scheme: str  # "socks4", "socks5" and "http" are supported
    hostname: str
    port: int
    username: str
    password: str


    def __init__(self, id_: int = None,
                 scheme: str = None,  # "socks4", "socks5" and "http" are supported
                 hostname: str = None,
                 port: int = None,
                 username: str = None,
                 password: str = None, ):
        self.id_: int = id_
        self.scheme: str  = str(scheme) # "socks4", "socks5" and "http" are supported
        self.hostname: str = str(hostname)
        self.port: int = port
        self.username: str = str(username)
        self.password: str = str(password)

        self.dict_repr = {
            'scheme': self.scheme,
            'hostname': self.hostname,
            'port': self.port,
            'username': self.username,
            'password': self.password,
        }

    def get_dict(self):
        return {'scheme': self.scheme,
                'hostname': self.hostname,
                'port': self.port,
                'username': self.username,
                'password': self.password,
                }


# бд, где хранится информация о ботах
class ProxyDB(DBBaseObject):
    ID_COLUMN = 'id'
    SCHEME_COLUMN = "scheme"  # "socks4", "socks5" and "http" are supported
    HOSTNAME_COLUMN = "hostname"
    PORT_COLUMN = "port"
    USERNAME_COLUMN = "username"
    PASSWORD_COLUMN = "password"
    NAME_OF_TABLE = 'proxies'

    def make_table(self):
        sessions_check = f'''
                CREATE TABLE IF NOT EXISTS {self.NAME_OF_TABLE}( 
                {self.ID_COLUMN} INTEGER PRIMARY KEY,
                {self.SCHEME_COLUMN} STRING,
                {self.HOSTNAME_COLUMN} STRING,
                {self.PORT_COLUMN} INTEGER,
                {self.USERNAME_COLUMN} STRING,
                {self.PASSWORD_COLUMN} STRING);'''
        self.execute(sessions_check, commit=True)

    def get_all(self) -> list[Proxy]:
        command = f'''SELECT * FROM {self.NAME_OF_TABLE};'''
        f = self.execute(command, fetch_all=True)
        return list(map(lambda x: Proxy(*x), f))

    def get_one_by_id(self, id_: int) -> Proxy:
        command = f'''SELECT * FROM {self.NAME_OF_TABLE} WHERE {self.ID_COLUMN} = ?;'''
        f = self.execute(command, (id_,), fetch_one=True)
        for x in f:
            print(x.__class__, end=', ')
        return Proxy(*f)

    def add_one(self, scheme: str, hostname: str, port: int, username: str, password: str):
        command = f'''INSERT INTO {self.NAME_OF_TABLE} (
                {self.SCHEME_COLUMN},
                {self.HOSTNAME_COLUMN},
                {self.PORT_COLUMN},
                {self.USERNAME_COLUMN},
                {self.PASSWORD_COLUMN}) VALUES (?, ?, ?, ?, ?);'''

        self.execute(command, (scheme, hostname, port, username, password), commit=True)

    def drop_one_by_id(self, id_: int):
        command = f'DELETE FROM {self.NAME_OF_TABLE} WHERE {self.ID_COLUMN} = ?;'
        self.execute(command, (id_,), commit=True)


if __name__ == '__main__':
    pass
