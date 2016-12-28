from openbot.config import ConfigStream

class BotCore(config_file='config/openbot.json'):
  def __init__(self):
    config = ConfigStream()
    plugins = self.load_plugins()
    pass

  def load_plugins(self):