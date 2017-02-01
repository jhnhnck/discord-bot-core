import argparse

import openbot.logger as logger
import openbot.client
import openbot.permissions
import openbot.config
import openbot.loader

# Global Definitions
CORE_VERSION = "0.0.1"
CORE_RELEASE_TYPE = "alpha"
CORE_DESCRIPTION = "A simple, easily expandable, and well documented framework to add custom commands and \
                    interactions to Discord"

# Global Variables
config = None
permissions = None
plugins = None
functions = None
tasks = None

"""
Init.

Loading Order.
  1. Logger: In loaded in 'en_us' mode or provided locale mode first and reloaded if changed via config
  2. Config: The configuration is loaded from 'config/openbot.json' or the provided path
    - Logger is reloaded if loaded in 'en_us' mode and config has a differing locale
  3. Permissions: The permissions are loaded from 'config/perms.json'
  4. Plugins, Functions, Tasks: These are loaded into separate dictionaries via the Loader class
"""
def startup(config_file, locale):
  logger.setup(locale)
  logger.self_test()

  global config
  config = openbot.config.ConfigStream(config_file=config_file)

  # Logger is reloaded if loaded in 'en_us' mode and config has a differing locale
  if locale == 'en_us' and config.get_config('core.locale') != 'en_us':
    logger.setup(config.get_config('core.locale'))

  # TODO: Make permissions movable
  global permissions
  permissions = openbot.permissions.BotPerms()

  loader = openbot.loader.Loader(config)
  loader.self_test()

  global plugins
  plugins = loader.load_plugins()

  global functions
  functions = loader.load_functions(plugins)

  # global tasks
  # tasks = loader.load_tasks()


def run():
  # Client token: '***REMOVED***'
  server = openbot.client.BotClient()
  server.run(config.get_config("core.token"))


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=CORE_DESCRIPTION)
  parser.add_argument('-c', '--config', nargs=1, default='config/openbot.json',
                      help='location of config file')
  parser.add_argument('-l', '--locale', nargs=1, default='en_us',
                      help='language')
  parser.add_argument('--testing', default=False, action="store_true",
                      help='disables server connection')
  args = parser.parse_args()

  startup(args.config, args.locale)
  if not args.testing:
    run()
