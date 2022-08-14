from os import remove
from os.path import exists


class FileHandler:
    @classmethod
    def delete_file(cls, file):
        pass


class LocalFileHandler(FileHandler):
    @classmethod
    def delete_file(cls, file):
        if exists(file):
            remove(file)


