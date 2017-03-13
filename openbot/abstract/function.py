from abc import ABC
from abc import abstractmethod


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
