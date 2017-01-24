import argparse

from openbot.client import BotClient
from openbot.permissions import BotPerms
from openbot.config import ConfigStream
from openbot.logger import Logger, LogLevel
from openbot.loader import Loader


class BotCore:

  CORE_VERSION = "0.0.1"
  CORE_RELEASE_TYPE = "alpha"
  CORE_DESCRIPTION = "A simple, easily expandable, and well documented framework to add custom commands and \
                      interactions to Discord"

  def __init__(self, config_file, locale):
    self.logger = Logger(BotCore.CORE_VERSION, BotCore.CORE_RELEASE_TYPE, locale)
    self.logger.self_test()

    self.config = ConfigStream(self, self.logger, config_file=config_file)
    self.server = BotClient(self, self.logger)
    self.permissions = BotPerms()

    loader = Loader(self.logger, self.config)
    loader.self_test()

    self.store, self.plugins = loader.load_plugins()
    self.functions = loader.load_functions(self.plugins)
    # self.tasks = loader.load_tasks()


  def run(self):
    # Client token: '***REMOVED***'
    self.server.run(self.config.get_config("core.token"))


  def _register_configs(self):
      for name, plugin in self.plugins.items():
        # TODO: Log level=Debug "Config given to plugins [{}]" (array of registered plugins)
        pass
        

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=BotCore.CORE_DESCRIPTION)
  parser.add_argument('-c', '--config', nargs=1, default='config/openbot.json',
                      help='location of config file')
  parser.add_argument('-l', '--locale', nargs=1, default='en_us',
                      help='language')
  args = parser.parse_args()

  core = BotCore(args.config, args.locale)
  core.run()
