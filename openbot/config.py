import json
import os

import openbot
import openbot.logger


config_file = None
config = None
changed = False


# TODO: Async things
def setup(config_path):
  global config_file
  global changed
  global config

  config_file = config_path

  try:
    with open(config_file, 'r') as file:
      config = json.loads(file.read())

    if openbot.VERSION != config.get('core').get('version'):
      config = _match_keys(config, gen_new_config())
      config['core']['version'] = openbot.VERSION
      changed = True

  except FileNotFoundError:
    openbot.logger.log(config_file, parent='core.info.gen_new_config')
    config = gen_new_config()
    changed = True
  except Exception as e:
    openbot.logger.log(config_file,
                       parent='core.warn.config_loading_exception',
                       error_point=e)
    config = gen_new_config()
    changed = True

  """
  for name, plugin in self.core.plugins.items():
    try:
      if config.get(name).get('version') != plugin.plugin_version:
        config[name] = self._match_keys(config.get(name), plugin.get_default_config())
        config[name]['version'] = plugin.plugin_version
        changed = True
    except:
      # TODO: Logger error here
      config[name] = plugin.get_default_config()
      changed = True
  """

  _unload()


def _unload():
  if not changed:
    return

  try:
    if not os.path.exists(os.path.dirname(config_file)):
      os.makedirs(os.path.dirname(config_file))

    # noinspection PyTypeChecker
    with open(config_file, 'w+') as file:
      json.dump(config, file, sort_keys=True, indent=2)
  except:
    openbot.logger.log(config_file,
                       parent='core.fatal.unload_config_error',
                       error_point=config,
                       pad_newlines=False)


def _match_keys(old, new):
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
  # TODO: Get config from package and key
  pass


def gen_new_config():
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
      'restrict_text_channels': {
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
