import itertools
from abc import ABC


class PluginBase(ABC):
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
