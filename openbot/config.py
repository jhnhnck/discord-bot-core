import json
import os

import openbot
import openbot.logger


config_file = ""            # Path to the config file
_config = {}                 # Dictionary of the config values TODO: Convert this to _config
state = False               # Should config be unloaded


def setup(config_path):
  """
  Setup.
  Preforms the actions to load and initialize the configuration options

  Args:
    config_path: (:type: str) Path to the config file
  """
  global config_file, _config, state

  config_file = config_path

  try:
    with open(config_file) as file:
      _config = json.load(file)

    # Test if config should be upgraded
    if openbot.VERSION != _config.get('core').get('version'):
      _config = _match_keys(_config, get_default_config())
      _config['core']['version'] = openbot.VERSION
      state = True

  # Make a new config if doesn't exist
  except FileNotFoundError:
    openbot.logger.log(config_file, parent='core.info.gen_new_config')
    _config = get_default_config()
    state = True
  # Make a new config if another error occurs - Probably will fail later
  except Exception as e:
    openbot.logger.log(config_file,
                       parent='core.warn.config_loading_exception',
                       error_point=e)
    _config = get_default_config()
    state = True

  # Save the file (This handles change detection)
  _unload()


def _unload(force=False):
  """
  Unload.
  Unloads the config to the path indicated at config_path in json format if

  Args:
    force: (:type: bool) Unload even without changes
  """
  if not changed and not force and len(_config) > 0:
    return

  try:
    if not os.path.exists(os.path.dirname(config_file)):
      os.makedirs(os.path.dirname(config_file))

    with open(config_file, 'w+') as file:
      json.dump(_config, file, sort_keys=True, indent=2)
  except:
    openbot.logger.log(config_file,
                       parent='core.fatal.unload_config_error',
                       error_point=_config,
                       pad_newlines=False)


def _match_keys(old, new):
  """
  Match Keys.
  Merges the changes from a new config with an old config with the new config taking priority

  Args:
    old: (:type: dict) Old config
    new: (:type: dict) New config

  Returns:
    A new config dictionary
  """
  matched_set = {}

  for key, value in new:
    if key in old:
      if value.isinstance(type(old[key])):
        if key.isinstance(dict):
          matched_set[key] = _match_keys(old[key], value)
        else:
          # TODO: Match string keys
          pass
    else:
      # TODO: Add new keys
      pass
  return matched_set


# Unpacks config value from '.' separated keys
def get_config(key, safe_mode=True):
  """
  Get Config.
  Gets the value of the key value in the config dictionary
  Args:
    key: (:type: dict) Dot-separated keys
    safe_mode: (:type: bool) Prevent ending on dictionary values

  Returns:
    Value from the config
  """
  # Checks for config loaded already
  if len(_config) == 0:
    openbot.logger.log(key,
                       parent='core.warn.config_before_load',
                       send_to_chat=False)
    return None

  # Make a copy of the config
  store = _config

  try:
    for branch in key.split('.'):
      store = store[branch]
  except KeyError:
    openbot.logger.log(key,
                       parent='core.warn.config_key_error',
                       send_to_chat=False)
    return None

  # TODO: Handle safe_mode
  if safe_mode and type(store) is dict:
    pass

  return store


def set_config(key, value, safe_mode=True):
  """
  Set Config.
  Change a value within the config

  Args:
    key: (:type: str) Dot-separated keys
    value: Value to replace in config
    safe_mode: Prevent dictionaries from being overridden
  """
  # TODO: Get config from package and key
  pass


def get_default_config():
  """
  Get Default Config
  Generate a new configuration dictionary from the default values

  Returns:
    Default configuration values
  """
  config = {
    'core': {
      'token': None,
      'owner_id': None,
      'command_prefix': '//',
      'debug_mode': 'False',
      'version': openbot.VERSION,
      'locale': 'en_us',
    },
    'chat': {
      'bind_text_channels': {
        'enabled': False,
        'channels': [],
      },
      'delete_messages_delay': {
        'enabled': True,
        'timeout_short': 30,  # Messages under 250 characters
        'timeout_long': 60,  # Messages over 250 characters
      },
      'delete_commands': {
        'enabled': True,
        'delay': 5,
      }
    }
  }

  return config
