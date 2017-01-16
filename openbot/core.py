import os
import argparse
import importlib.util

from openbot.client import BotClient
from openbot.permissions import BotPerms
from openbot.config import ConfigStream
from openbot.logger import Logger


class BotCore:

  CORE_VERSION = "0.0.1"
  CORE_RELEASE_TYPE = "alpha"
  CORE_DESCRIPTION = "A simple, easily expandable, and well documented framework to add custom commands and interactions to Discord"

  def __init__(self, config_file, locale):
    self.logger = Logger(self, locale)
    self.server = BotClient(self)
    self.permissions = BotPerms()

    self.store, self.plugins = self.load_plugins()
    # self.tasks = self.load_tasks()
    self.functions = self.load_functions()
    self.server.run('***REMOVED***')


  def load_plugins(self):
    store = {}
    plugins = {}

    for plugin in os.listdir('plugins/'):
      try:
        plugin_name = plugin.split('.')[-1]
        spec = importlib.util.spec_from_file_location(plugin,"plugins/{}/{}.py".format(plugin, plugin_name))
        store[plugin_name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(store[plugin_name])
        plugins[plugin_name] = store[plugin_name].PluginBase()
      except Exception as e:
        self.logger.log(plugin,
                        parent="core.error.plugin_loading",
                        type=LogLevel.error,
                        error_point=e,
                        send_to_chat=False)

    """
    # Debug code for now
    for name, plugin in plugins.items():
      if name == plugin.get_definitions()['plugin_name'].split('.')[-1]:
        print("Successfully loaded plugin {}\n -> {}".format(name, plugin.get_definitions()['plugin_description']))
      else:
        self.logger.log(name,
                        parent="core.error.plugin_loading",
                        error_point="idk wtf this does",
                        send_to_chat=False)
        print("Error loading plugin: {}".format(name))
    """

    return store, plugins

  def load_tasks(self):
    pass

  def load_functions(self):
    functions = []
    for name, plugin in self.plugins.items():
      self.logger.log(name,
                      parent='core.debug.load_function_plugin_title',
                      type=LogLevel.debug,
                      send_to_chat=False)
      prefix = plugin.get_definitions()['plugin_prefix']
      for ftn in plugin.get_functions():
        functions.append("{command_prefix}{plugin_prefix}.{ftn}".format(command_prefix=command_prefix,
                                                                        plugin_prefix=prefix,
                                                                        ftn=ftn))
        self.logger.log(functions[-1],
                        parent="core.debug.load_function_success",
                        type=LogLevel.debug,
                        send_to_chat=False)
      functions.append(plugin.get_functions())

    return functions

  def fuck_you_bitch(self):
    return "No, fuck you"

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=BotCore.CORE_DESCRIPTION)
  parser.add_argument('-c', '--config', nargs=1, default='config/openbot.json',
                      help='location of config file')
  parser.add_argument('-l', '--locale', nargs=1, default='en_us',
                      help='language')
  args = parser.parse_args()

  BotCore(args.config, args.locale)
