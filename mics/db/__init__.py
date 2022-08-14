from .databasebaseobject import DBBaseObject
from .proxies import Proxy, ProxyDB
from .sessions import Session, BotFileDB
from .groups import GroupsDB, FileGroup
from .messages import MessagesDB, MessageHandle
from .spam import SpamParamsDB, SpamHandle

def make_dbs(*args):
    for db in args:
        db.make_table()


def clean_dbs(*dbs):
    for db in dbs:
        db.clean()


def delete_dbs(*dbs):
    for db in dbs:
        db.delete()

