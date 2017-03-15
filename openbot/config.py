import json
import os

import openbot
import openbot.logger


config_file = ""            # Path to the config file
config = {}                 # Dictionary of the config values TODO: Convert this to _config
changed = False             # Should config be unloaded


def setup(config_path):
  """
  Setup.
  Preforms the actions to load and initialize the configuration options

  Args:
    config_path: (:type: str) Path to the config file
  """
  global config_file
  global changed
  global config

  config_file = config_path

  try:
    with open(config_file) as file:
      config = json.load(file)

    # Test if config should be upgraded
    if openbot.VERSION != config.get('core').get('version'):
      config = _match_keys(config, gen_new_config())
      config['core']['version'] = openbot.VERSION
      changed = True

  # Make a new config if doesn't exist
  except FileNotFoundError:
    openbot.logger.log(config_file, parent='core.info.gen_new_config')
    config = gen_new_config()
    changed = True
  # Make a new config if another error occurs - Probably will fail later
  except Exception as e:
    openbot.logger.log(config_file,
                       parent='core.warn.config_loading_exception',
                       error_point=e)
    config = gen_new_config()
    changed = True

  # Save the file (This handles change detection)
  _unload()


def _unload(force=False):
  """
  Unload.
  Unloads the config to the path indicated at config_path in json format if

  Args:
    force: (:type: bool) Unload even without changes
  """
  if not changed:
  if not changed and not force and len(config) > 0:
    return

  try:
    if not os.path.exists(os.path.dirname(config_file)):
      os.makedirs(os.path.dirname(config_file))

    with open(config_file, 'w+') as file:
      json.dump(config, file, sort_keys=True, indent=2)
  except:
    openbot.logger.log(config_file,
                       parent='core.fatal.unload_config_error',
                       error_point=config,
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
def get_config(key):
  """
  Get Config.
  Gets the value of the key value in the config dictionary
  Args:
    key: (:type: dict) Dot-separated keys

  Returns:
    Value from the config
  """
  # Make a copy of the config
  store = config

  try:
    for branch in key.split('.'):
      store = store[branch]
    if isinstance(store, dict):
      # TODO: Handle endpoint on dict (or don't)
      pass
  except KeyError:
    # TODO: Handle invalid keys
    pass

  return store


def set_config(key, value):
  """
  Set Config.
  Change a value within the config

  Args:
    key: (:type: str) Dot-separated keys
    value: Value to replace in config
  """
  # TODO: Get config from package and key
  pass


def gen_new_config():
  """
  Generate New Config.
  Generate a new configuration dictionary from the default values

  Returns:
    A new config
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
