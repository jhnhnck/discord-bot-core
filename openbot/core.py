import platform

import openbot.client
import openbot.config
import openbot.loader
import openbot.logger


# Global Variables
plugins = None
functions = None
tasks = None
server = None


def startup(config_file, locale):
  """
  Startup.
  Loading Order.
    1. Logger: In loaded in 'en_us' mode or provided locale mode
    2. Config: The configuration is loaded from 'config/openbot.yml' or the provided path
      - Logger is reloaded if loaded in 'en_us' mode and config has a differing locale
    3. Plugins, Functions, Tasks: These are loaded into separate dictionaries via the Loader class
  """
  openbot.logger.setup(locale)
  _log_system_info()

  openbot.config.setup(config_file)

  # Logger is reloaded if loaded in 'en_us' mode and config has a differing locale
  if locale == 'en_us' and openbot.config.get_config('core.locale') != 'en_us':
    openbot.logger.setup(openbot.config.get_config('core.locale'))

  if openbot.RELEASE_TYPE == 0:
    openbot.logger.self_test()

  global plugins
  plugins = openbot.loader.load_plugins()

  global functions
  # TODO: Change front-end name to commands
  functions = openbot.loader.load_functions(plugins)

  # global tasks
  # tasks = loader.load_tasks()


def run():
  # Client token: '***REMOVED***'
  global server
  server = openbot.client.BotSyncedWrapper()
  server.run(openbot.config.get_config('core.token'))


def _log_system_info():
  sys_info = {
    'machine_type': platform.machine(),
    'processor': platform.processor(),
    'platform': platform.platform(),
    'python_version': platform.python_version(),
    'python_implementation': platform.python_implementation(),
    'core_full_version': openbot.FULL_VERSION,
    'core_git_version': openbot.GIT_VERSION
  }

  openbot.logger.log(sys_info,
                     parent='core.debug.sys_info',
                     log_type=openbot.logger.LogLevel.blank,
                     send_to_chat=False)
  openbot.logger.newline()
