import itertools
import random
import string
from abc import ABC
import os

import openbot
import openbot.logger


class PluginLoadingException(Exception):
  pass


class DisabledPluginError(Exception):
  pass


class PluginBase(ABC):
  def __init__(self, description=None, versioning=None, functions=None, user=None, config_template=None):
    if description is None:
      openbot.logger.log(type(self).__name__, key_name='description', sub_value='{}', optional='required',
                         parent='core.debug.load_plugin_value_omitted',
                         send_to_chat=False)
      description = {}
    if versioning is None:
      openbot.logger.log(type(self).__name__, key_name='versioning', sub_value='{}', optional='required',
                         parent='core.debug.load_plugin_value_omitted',
                         send_to_chat=False)
      versioning = {}
    if config_template is None:
      openbot.logger.log(type(self).__name__, key_name='config_template', sub_value='{}', optional='optional',
                         parent='core.debug.load_plugin_value_omitted',
                         send_to_chat=False)
      config_template = {}
    if functions is None:
      openbot.logger.log(type(self).__name__, key_name='functions', sub_value='{}', optional='optional',
                         parent='core.debug.load_plugin_value_omitted',
                         send_to_chat=False)
      functions = {}
    if user is None:
      openbot.logger.log(type(self).__name__, key_name='user', sub_value='{}', optional='optional',
                         parent='core.debug.load_plugin_value_omitted',
                         send_to_chat=False)
      user = {}

    self.description = description
    self.versioning = versioning
    self.user = user
    self.functions = functions
    self.config_template = config_template

    # Validate description keys
    self._validate_key('plugin_name', self.description, os.path.basename(__file__))
    self._validate_key('domain_name', self.description, 'nodomain')
    self._validate_key('plugin_prefix', self.description, ''.join(random.choices(string.ascii_lowercase, k=3)))
    self._validate_key('plugin_description', self.description, 'No description.')
    self._validate_key('plugin_type', self.description, 'standard', optional=True)

    if not user.get('enabled', True):
      raise DisabledPluginError(self.description.get('plugin_name'))

    # Validate versioning keys
    self._validate_key('plugin_version', self.versioning, '0.0.1a')
    self._validate_key('requires', self.versioning, '*', optional=True)
    self._validate_key('update_repo', self.versioning, None, optional=True)
    self._validate_key('beta_update_repo', self.versioning, None, optional=True)

    # Validate user keys
    self._validate_key('enabled', self.user, True, optional=True)
    self._validate_key('auto_update', self.user, False, optional=True)
    self._validate_key('beta_testing', self.user, False, optional=True)



  def load_test(self):
    """
    Loading Self Test.

    The plugin will only load if this returns true. Override this method to allow for more vigorous control over loading
    requirements.

    NOTE: BotCore will already check for dependencies and version incompatibilities from pluginname.json. This is for
    other checks that are more fine tuned for your plugin  and functions
    """
    return True


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


  def _validate_key(self, key_name, config_set, sub_value, optional=False):
    if key_name not in config_set:
        if openbot.RELEASE_TYPE == 0:
          openbot.logger.log(type(self).__name__,
                             key_name=key_name,
                             sub_value=sub_value,
                             optional='optional' if optional else 'required',
                             parent='core.debug.load_plugin_value_omitted',
                             send_to_chat=False)
          config_set[key_name] = sub_value
        elif optional:
          config_set[key_name] = sub_value
        else:
          error = openbot.logger.get_locale_string('core.error.load_plugin_value_omitted')
          raise PluginLoadingException(error.format(key_name=key_name))