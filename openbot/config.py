import json
import os

import openbot.core as core
import openbot.logger as logger

from openbot.logger import LogLevel


# TODO: Async things
class ConfigStream:

  def __init__(self, config_file):
    self.config_file = config_file
    self.changed = False
    self.config = self._load()


  def _load(self):
    try:
      with open(self.config_file, "r") as file:
        config = json.loads(file.read())

      if core.CORE_VERSION != config.get('core').get('version'):
        config = self._match_keys(config, self.gen_new_config())
        config['core']['version'] = core.CORE_VERSION
        self.changed = True

    except:
      logger.log(self.config_file,
                 parent='core.info.gen_new_config',
                 type=LogLevel.info)
      config = self.gen_new_config()
      self.changed = True

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

    self._unload()
    return config


  def _unload(self):
    if not self.changed:
      return

    for i in range(0, 10):
      try:
        with open(self.config_file, 'w+') as file:
          json.dump(self.config, file, sort_keys=True, indent=2)
      except FileNotFoundError:
        os.makedirs(os.path.dirname(self.config_file))
    logger.log(self.config_file,
               parent='core.fatal.unload_config_error',
               error_point=self.config,
               type=LogLevel.fatal)


  def _match_keys(self, old, new):
    matched_set = {}

    for key, value in new:
      if key in old:
        if value.isinstance(type(old[key])):
          if key.isinstance(dict):
            matched_set[key] = self._match_keys(old[key], value)
          else:
            # TODO: Match string keys
            pass
      else:
        # TODO: Add new keys
        pass
    return matched_set


  # Unpacks config value from '.' separated keys
  def get_config(self, key):
    store = self.config

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


  def set_config(self, key, value):
    # TODO: Get config from package and key
    pass


  def gen_new_config(self):
    config = {
      'core': {
        'token': None,
        'owner_id': None,
        'command_prefix': '//',
        'debug_mode': 'False',
        'version': core.CORE_VERSION,
        'locale': 'en_us',
      },
      'chat': {
        'restrict_text_channels': {
          'enabled': False,
          'channels': [],
        },
        'delete_messages_delay': {
          'enabled': True,
          'timeout_short': 30,      # Messages under 250 characters
          'timeout_long': 60,       # Messages over 250 characters
        },
        'delete_commands': {
          'enabled': True,
          'delay': 5,
        }
      }
    }

    return config
