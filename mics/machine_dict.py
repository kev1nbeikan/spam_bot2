import logging

from client import SpamMachine
from mics.db import Session, Proxy


class MachineDict(dict):
    current_proxy: Proxy | None = None
    current_machine: SpamMachine = None

    def get_machine(self, bot: Session):
        if bot.id_ not in self:
            machine = SpamMachine(str(bot.id_),
                                  api_id=bot.app_id,
                                  api_hash=bot.app_hash,
                                  proxy=self.current_proxy.dict_repr if self.current_proxy else dict(),
                                  test_mode=False,
                                  phone_number=bot.phone,
                                  password=bot.password)
            machine.main_db_id = bot.id_
            self[bot.id_] = machine
            return machine
        else:
            return self[bot.id_]

    def setup_proxy(self, proxy: Proxy):
        self.current_proxy = proxy

    def unninstal_proxy(self):
        self.setup_proxy(None)

    def get_current_machine(self):
        return self.current_machine

    def setup_current_machine(self, bot):
        self.current_machine = self.get_machine(bot)

    def get_proxy(self):
        return self.current_proxy

    def __str__(self):
        return f'MachineDict: {self.items()}; current_machine: {self.current_machine}; current_proxy: {self.current_proxy}'
