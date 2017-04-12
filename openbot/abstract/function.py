from abc import ABC, abstractmethod

import openbot.config
import openbot.logger


class FunctionBase(ABC):

  def __init__(self,
               function_name,
               simple_string,
               qualified_string,
               help_text,
               args_description=None,
               allowed_modifiers=None,
               allowed_args_length='0'):
    if args_description is None:
      args_description = []

    if allowed_modifiers is None:
      allowed_modifiers = {}

    self.function_name = function_name
    self.help_text = help_text
    self.allowed_args_length = allowed_args_length
    self.args_description = args_description
    self.allowed_modifiers = allowed_modifiers
    self.simple_string = simple_string
    self.qualified_string = qualified_string


  def load_test(self):
    """
    Loading Self Test.
    Implement this method to allow for more vigorous control over loading requirements.

    Returns:
      Dictionary with two keys:
        state: True if the function should be loaded
        msg: Detailed error message (Do not use logging here; It may not always work)
    """
    return {'state': True}

  @abstractmethod
  def call(self, **kwargs):
    pass


  def help_message(self):
    head = '{}. {}\n'.format(self.function_name, self.help_text)
    usage = 'Usage:\n  {}{} '.format(openbot.config.get_config('core.command_prefix'), self.function_name)

    if len(self.args_description) > 1:
      args = '[...]' + '\n ... '.join(self.args_description) + '\n\n'
    else:
      args = self.args_description[0] + '\n\n'

    if len(self.allowed_modifiers) > 0:
      mod = 'Modifiers:\n'

      for k, v in self.allowed_modifiers:
        mod += '  - {} {}\n'.format(k, v)
    else:
      mod = ''

    return head + usage + args + mod
