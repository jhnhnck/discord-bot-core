from abc import ABC, abstractmethod, abstractproperty


class BotPlugin(ABC):

  plugin_name = None
  plugin_prefix = None
  plugin_description = None

  def __init__(self, core):
    self.core = core

  @abstractmethod
  def load(self):
    pass

  @abstractmethod
  def get_functions(self):
    pass

  @abstractmethod
  def get_default_config(self):
    """
      This should be in the form of a dictionary
    """
    pass

  def get_definitions(self):
    return {
      'plugin_name': self.plugin_name,
      'plugin_prefix': self.plugin_prefix,
      'plugin_description': self.plugin_description,
    }
