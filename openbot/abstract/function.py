from abc import ABC
from abc import abstractmethod


class FunctionBase(ABC):

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
