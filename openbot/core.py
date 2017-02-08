import argparse
import platform

import openbot.client
import openbot.config as config
import openbot.loader
import openbot.logger as logger
import openbot.permissions
from openbot.logger import LogLevel

# Global Variables
permissions = None
plugins = None
functions = None
tasks = None


def startup(config_file, perm_file, locale):
  """ Init.
  Loading Order.
    1. Logger: In loaded in 'en_us' mode or provided locale mode first and reloaded if changed via config
    2. Config: The configuration is loaded from 'config/openbot.json' or the provided path
      - Logger is reloaded if loaded in 'en_us' mode and config has a differing locale
    3. Permissions: The permissions are loaded from 'config/perms.json' or the provided path
    4. Plugins, Functions, Tasks: These are loaded into separate dictionaries via the Loader class
  """
  logger.setup(locale)
  _log_system_info()
  logger.self_test()

  config.setup(config_path=config_file)

  # Logger is reloaded if loaded in 'en_us' mode and config has a differing locale
  if locale == 'en_us' and config.get_config('core.locale') != 'en_us':
    logger.setup(config.get_config('core.locale'))

  global permissions
  permissions = openbot.permissions.BotPerms()

  # loader = openbot.loader.Loader(config)
  openbot.loader.self_test()

  global plugins
  plugins = openbot.loader.load_plugins()

  global functions
  functions = openbot.loader.load_functions(plugins)

  # global tasks
  # tasks = loader.load_tasks()


def run():
  # Client token: '***REMOVED***'
  server = openbot.client.BotClient()
  server.run(config.get_config("core.token"))


def _log_system_info():
  logger.log("Printing Version Info:",
             log_type=LogLevel.blank)
  logger.log("machine-type: {}".format(platform.machine()),
             log_type=LogLevel.blank)
  logger.log("machine-processor: {}".format(platform.processor()),
             log_type=LogLevel.blank)
  logger.log("machine-platform: {}".format(platform.platform()),
             log_type=LogLevel.blank)
  logger.log("python-version: {}".format(platform.python_version()),
             log_type=LogLevel.blank)
  logger.log("python-implementation: {}".format(platform.python_implementation()),
             log_type=LogLevel.blank)
  logger.log("python-version: {}".format(platform.python_version()),
             log_type=LogLevel.blank)
  logger.log("bot-core-version: {}-{}".format(openbot.CORE_VERSION, openbot.CORE_RELEASE_TYPE),
             log_type=LogLevel.blank)

  logger.newline()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=openbot.CORE_DESCRIPTION)
  parser.add_argument('-c', '--config', nargs=1, default='config/openbot.json',
                      help='location of config file')
  parser.add_argument('-l', '--locale', nargs=1, default='en_us',
                      help='language')
  parser.add_argument('-p', '--perms', nargs=1, default='config/permissions.json',
                      help='location of permissions file')
  parser.add_argument('--testing', default=False, action="store_true",
                      help='disables server connection')
  args = parser.parse_args()

  startup(args.config, args.perms, args.locale)
  if not args.testing:
    run()
