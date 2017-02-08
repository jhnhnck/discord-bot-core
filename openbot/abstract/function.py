from abc import ABC, abstractmethod

class BotFunction(ABC):

  fnc_help_test = None
  fnc_name = None
  fnc_allowed_args_length = "0"
  fnc_allowed_modifiers = None


  def load_test(self):
    """
    Loading Self Test.

    This function will only load if this returns true. Override this method to allow for more vigorous control over
    loading requirements.

    NOTE: BotCore will already check for dependencies and version incompatibilities from pluginname.json. This is for
    other checks that are more fine tuned for your plugin and functions
    """
    return True


  def __init__(self, core):
    self.core = core


  @abstractmethod
  def call(self, args, mod):
    pass
