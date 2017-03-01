import platform

import openbot.client
import openbot.config
import openbot.loader
import openbot.logger
import openbot.permissions


# Global Variables
permissions = None
plugins = None
functions = None
tasks = None
server = None


def startup(config_file, perm_file, locale):
  """
  Startup.
  Loading Order.
    1. Logger: In loaded in 'en_us' mode or provided locale mode first and reloaded if changed via config
    2. Config: The configuration is loaded from 'config/openbot.json' or the provided path
      - Logger is reloaded if loaded in 'en_us' mode and config has a differing locale
    3. Permissions: The permissions are loaded from 'config/perms.json' or the provided path
    4. Plugins, Functions, Tasks: These are loaded into separate dictionaries via the Loader class
  """
  openbot.logger.setup(locale)
  _log_system_info()

  if openbot.RELEASE_TYPE == 0:
    openbot.logger.self_test()

  openbot.config.setup(config_path=config_file)

  # Logger is reloaded if loaded in 'en_us' mode and config has a differing locale
  if locale == 'en_us' and openbot.config.get_config('core.locale') != 'en_us':
    openbot.logger.setup(openbot.config.get_config('core.locale'))

  global permissions
  permissions = openbot.permissions.BotPerms()

  global plugins
  plugins = openbot.loader.load_plugins()

  global functions
  functions = openbot.loader.load_functions(plugins)

  # global tasks
  # tasks = loader.load_tasks()


def run():
  # Client token: '***REMOVED***'
  global server
  server = openbot.client.BotClient()
  server.run(openbot.config.get_config('core.token'))


def call_function(function, params):
  # Test if function exists
  if function not in functions:
    return []

  ftn = functions.get(function)

  if type(ftn) is list:
    return ftn

  elif type(ftn) is dict:
    # Test for linked function
    if 'link' in ftn:
      return call_function(ftn.get('link'), params)
    else:
      args, mod = _parse_args(params, function)
      ftn.get('store').call(args, mod)
      return [ftn.get('qualified_string')]


def _parse_args(params, funct):
  args = []
  mod = {}

  return args, mod


def _log_system_info():
  sys_info = openbot.logger.get_locale_string('core.segments.sys_info').format(
    machine_type=platform.machine(),
    processor=platform.processor(),
    platform=platform.platform(),
    python_version=platform.python_version(),
    python_implementation=platform.python_implementation(),
    core_full_version=openbot.FULL_VERSION)

  openbot.logger.log(sys_info, log_type=openbot.logger.LogLevel.blank, send_to_chat=False)
  openbot.logger.newline()
