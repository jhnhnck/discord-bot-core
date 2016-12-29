import os
import asyncio

from openbot.permissions import BotPerms
from openbot.config import ConfigStream

class BotCore(config_file='config/openbot.json'):

  def __init__(self):
    self.config = ConfigStream()
    self.server = None
    self.permissions = BotPerms()

    self.plugins = self.load_plugins()
    self.tasks = self.load_tasks()
    self.functions = self.load_functions()

  async def load_plugins(self):

    pass

  async def load_tasks(self):
    pass

  async def load_functions(self):
    pass

  async def fuck_you_bitch(self):
    return "No, fuck you"