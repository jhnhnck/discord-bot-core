import argparse

import openbot.logger as logger
from openbot.client import BotClient
from openbot.permissions import BotPerms
from openbot.config import ConfigStream
from openbot.loader import Loader


class BotCore:

  CORE_VERSION = "0.0.1"
  CORE_RELEASE_TYPE = "alpha"
  CORE_DESCRIPTION = "A simple, easily expandable, and well documented framework to add custom commands and \
                      interactions to Discord"

  """
  Init.

  Loading Order.
    1. Logger: In loaded in 'en_us' mode or provided locale mode first and reloaded if changed via config
    2. Config: The configuration is loaded from 'config/openbot.json' or the provided path
      - Logger is reloaded if loaded in 'en_us' mode and config has a differing locale
    3. Permissions: The permissions are loaded from 'config/perms.json'
    4. Plugins, Functions, Tasks: These are loaded into separate dictionaries via the Loader class
  """
  def __init__(self, config_file, locale):
    logger.setup(locale, BotCore.CORE_VERSION, BotCore.CORE_RELEASE_TYPE)
    logger.self_test()

    self.config = ConfigStream(self, config_file=config_file)

    # Logger is reloaded if loaded in 'en_us' mode and config has a differing locale
    if locale == 'en_us' and self.config.get_config('core.locale') != 'en_us':
      logger.setup(self.config.get_config('core.locale'),
                   BotCore.CORE_VERSION,
                   BotCore.CORE_RELEASE_TYPE)

    # TODO: Make permissions movable
    self.permissions = BotPerms()

    loader = Loader(self.config)
    loader.self_test()

    self.store, self.plugins = loader.load_plugins()
    self.functions = loader.load_functions(self.plugins)
    # self.tasks = loader.load_tasks()

    # Provides each plugin with the
    self._register_postinit()

    self.server = None


  def run(self):
    # Client token: '***REMOVED***'
    self.server = BotClient(self)
    self.server.run(self.config.get_config("core.token"))


  def _register_postinit(self):
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
