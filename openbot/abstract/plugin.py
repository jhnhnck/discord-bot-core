from abc import ABC, abstractmethod

class BotPlugin(ABC, locale='en_us'):

  @abstractmethod
  def __init__(self):
    # String with a unique name of your plugin in inverted domain format
    # Last section
    self.plugin_name = None
    self.plugin_prefix = None
    self.plugin_description = None

  @abstractmethod
  def load(self, core):
    pass

  @abstractmethod
  def get_functions(self):
    pass

  def get_definitions(self):
    return {
      'plugin_name': self.plugin_name,
      'plugin_prefix': self.plugin_prefix,
      'plugin_description': self.plugin_description,
    }

