import itertools
import random
import string
from abc import ABC

import openbot
import openbot.logger


class PluginLoadingException(Exception):
  pass


class DisabledPluginError(Exception):
  pass


class PluginBase(ABC):
  def __init__(self, description=None, versioning=None, functions=None, user=None, config_template=None):
    if user is not None and not user.get('enabled', True):
      raise DisabledPluginError(description.get('plugin_name', self.__class__.__name__))

    description = self._validate_dict(description, 'description')
    versioning = self._validate_dict(versioning, 'versioning')
    config_template = self._validate_dict(config_template, 'config_template', optional=True)
    functions = self._validate_dict(functions, 'functions', optional=True)
    user = self._validate_dict(user, 'user', optional=True)

    self.description = description
    self.versioning = versioning
    self.user = user
    self.functions = functions
    self.config_template = config_template

    # Validate description keys
    self._validate_key('plugin_name', self.description, self.__class__.__name__)
    self._validate_key('domain_name', self.description, 'nodomain')
    self._validate_key('plugin_prefix', self.description, ''.join(random.choices(string.ascii_lowercase, k=3)))
    self._validate_key('plugin_description', self.description, 'No description.')
    self._validate_key('plugin_type',
                       self.description,
                       'standard',
                       optional=True,
                       valid_options=['standard', 'single-file'])

    # Validate versioning keys
    self._validate_key('plugin_version', self.versioning, '0.0.1-unknown')
    self._validate_key('requires', self.versioning, '*', optional=True)
    self._validate_key('update_repo', self.versioning, None, optional=True)
    self._validate_key('beta_update_repo', self.versioning, None, optional=True)

    # Validate user keys
    self._validate_key('enabled', self.user, True, optional=True)
    self._validate_key('auto_update', self.user, False, optional=True)
    self._validate_key('beta_testing', self.user, False, optional=True)


  @staticmethod
  def compare_versions(existing, other):
    """
    Compares version strings.

    Returns 0 if same version
            1 if other is greater
           -1 if existing is greater
    """
    if existing == other:
      return 0

    existing_array = existing.split('.')
    other_array = other.split('.')

    # Pad other to match existing length [1.4 -> 1.4.0]
    while len(existing_array) != len(other_array):
      if len(existing_array) > len(other_array):
        other_array.append(0)
      else:
        existing_array.append(0)

    for x, y in zip(existing_array, other_array):
      if x[0].isalpha(): y = '0' + y
      if y[0].isalpha(): y = '0' + y

      compare = PluginBase._compare_section(x, y)
      # print("ZIP: {} {} Comparison: {}".format(x, y, compare))
      if compare != 0: return compare

    return -2


  @staticmethod
  def _compare_section(existing, other):
    # Check if all numbers
    num = PluginBase._safe_compare_numbers(existing, other)
    if abs(num) == 1: return num

    # Alpha-numeric compare
    existing_split = [''.join(x) for _, x in itertools.groupby(existing, key=str.isdigit)]
    other_split = [''.join(x) for _, x in itertools.groupby(other, key=str.isdigit)]
    # print("EX: {} OTH: {}".format(existing_split, other_split))

    num = PluginBase._safe_compare_numbers(existing_split[0], other_split[0])
    if abs(num) == 1: return num

    for i in range(97, 123):
      # print("On letter {}".format(chr(i)))
      try:
        existing_index = existing_split.index(chr(i))
        letter_ext = existing_split[existing_index + 1]
      except ValueError:
        letter_ext = 0
      except IndexError:
        letter_ext = 1

      try:
        other_index = other_split.index(chr(i))
        letter_oth = other_split[other_index + 1]
      except ValueError:
        letter_oth = 0
      except IndexError:
        letter_oth = 1

      num = PluginBase._safe_compare_numbers(letter_ext, letter_oth)
      if abs(num) == 1: return num

    return 0


  def get_full_name(self):
    return self.description.get('domain_name').lower() + '_' + self.description.get('plugin_name').lower()


  @staticmethod
  def _safe_compare_numbers(x, y):
    # print("Comparing {} and {}".format(x, y))
    try:
      int_x = int(x)
      int_y = int(y)

      if int_x == int_y:
        return 0
      else:
        return 1 if int_x < int_y else -1

    except ValueError:
      return -2


  def _validate_dict(self, config_set, key_name, optional=False):
    if config_set is None:
      openbot.logger.log(type(self).__name__, key_name=key_name, sub_value='{}',
                         parent='core.debug.load_plugin_value_omitted_{}'.format('opt' if optional else 'req'),
                         send_to_chat=False)
      if optional or openbot.__release_level__ == 0:
        return {}
      else:
        error = openbot.logger.get_locale_string('core.error.load_plugin_value_invalid').format(key_name)
        raise PluginLoadingException(error.format(key_name=key_name))
    else:
      return config_set


  def _validate_key(self, key_name, config_set, sub_value, optional=False, valid_options=None):
    if key_name not in config_set:
      openbot.logger.log(type(self).__name__, key_name=key_name, sub_value=sub_value,
                         parent='core.debug.load_plugin_value_omitted_{}'.format('opt' if optional else 'req'),
                         send_to_chat=False)
      if optional or openbot.__release_level__ == 0:
        config_set[key_name] = sub_value
      else:
        error = openbot.logger.get_locale_string('core.error.load_plugin_value_omitted').format(key_name)
        raise PluginLoadingException(error.format(key_name=key_name))

    if valid_options is not None and config_set.get(key_name) not in valid_options:
      openbot.logger.log(type(self).__name__,
                         key_name=key_name,
                         sub_value=sub_value,
                         valid_options=' '.join(valid_options),
                         parent='core.debug.load_plugin_value_invalid_{}'.format('opt' if optional else 'req'),
                         send_to_chat=False)
      if optional or openbot.__release_level__ == 0:
        config_set[key_name] = sub_value
      else:
        error = openbot.logger.get_locale_string('core.error.load_plugin_value_invalid').format(key_name)
        raise PluginLoadingException(error.format(key_name=key_name))