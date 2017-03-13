from abc import ABC
from abc import abstractmethod

import openbot.config

class FunctionBase(ABC):

  def __init__(self, function_name, help_text, allowed_args_length, args_description, allowed_modifiers):
    self.function_name = function_name
    self.help_text = help_text
    self.allowed_args_length = allowed_args_length
    self.args_description = args_description
    self.allowed_modifiers = allowed_modifiers


  def load_test(self):
    """
    Loading Self Test.

    This function will only load if this returns true. Override this method to allow for more vigorous control over
    loading requirements.

    NOTE: BotCore will already check for dependencies and version incompatibilities from pluginname.json. This is for
    other checks that are more fine tuned for your plugin and functions
    """
    return True


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
