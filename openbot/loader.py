import os
import importlib.util

from openbot.logger import LogLevel


class Loader:
  def __init__(self, logger, config):
    self.logger = logger
    self.config = config


  def self_test(self):
    pass


  """
  Basic Plugin Structure.

  Naming.
    The plugin should be contained within a directory in the 'plugins/' directory named in the form 'domain_plugin'.
    The domain should be an identifier for the specific developer and/or developing group and the plugin be a somewhat
    unique plugin name. Domain name is only used if both plugin names and plugin prefixes conflict which "probably won't
    ever happen"^(tm).

  Plugin Structure.
    Plugins are defined based upon a json file located in the root of the plugin directory (see Naming. above). You can
    make a copy of the 'plugin.json' file within the 'resources/' directory commented example as a starting point. Note
    that this format and its fields may change with development without notice. The file may not always be up to date.
    As always the best example of plugin structure can be found in the 'jhnhnck_coreftns' plugin located at
    'https://github.com/jhnhnck/discord-bot-coreftns'

    Additionally, the plugin must also have a python file named in the form 'plugin_name.py' that contains a class
    'PluginBase' that inherits 'openbot.abstract.plugin'. This class does not have to implement any methods (you may
    simply put 'pass' in the body) but can override the other methods present in the abstract class for more
    customization such as changing the default versioning scheme or (see 'openbot/abstract/plugin.py' for more details).

  Internal Plugin Structure.
    Each plugin is loaded into a dictionary with the above keys and values with an additional key of 'store' for the
    loaded for the initialized plugin.
  """


  def load_plugins(self):
    store = {}
    plugins = {}

    # TODO: This doesn't actually load with the proper form correctly
    for plugin in os.listdir('plugins/'):
      try:
        # Splits fully-qualified plugin name into plugin domain/group name and plugin name.
        if plugin.find('_') != -1:
          split = plugin.split('_')
          plugin_name = split[:-1]
          domain_name = split[0]
        else:
          self.logger.log(plugin, error_point='nodomain', parent='core.warn.plugin_domain_malformed')
          domain_name = 'nodomain'
          plugin_name = plugin

        spec = importlib.util.spec_from_file_location(plugin, "plugins/{}/{}.py".format(plugin, plugin_name))
        store[plugin_name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(store[plugin_name])
        plugins[plugin_name] = store[plugin_name].PluginBase(self)
      except Exception as e:
        self.logger.log(plugin,
                        parent="core.error.plugin_loading",
                        type=LogLevel.error,
                        error_point=e,
                        send_to_chat=False)

    return store, plugins


  """
  Basic Function Structure.
  TODO: Create a structure for functions to be loaded
  """


  def load_functions(self, plugins):
    functions = []

    # TODO: This doesn't actually load with the proper form correctly
    for name, plugin in plugins.items():
      self.logger.log(name,
                      parent='core.debug.load_function_plugin_title',
                      type=LogLevel.debug,
                      send_to_chat=False)
      prefix = plugin.get_definitions()['plugin_prefix']
      for ftn in plugin.get_functions():
        functions.append("{command_prefix}{plugin_prefix}.{ftn}"
                         .format(command_prefix=self.config.get_config('core.command_prefix'),
                                 plugin_prefix=prefix,
                                 ftn=ftn))
        self.logger.log(functions[-1],
                        parent="core.debug.load_function_success",
                        type=LogLevel.debug,
                        send_to_chat=False)
      functions.append(plugin.get_functions())

    return functions


  """
  Basic Task Structure.
  TODO: Create a structure for tasks to be loaded
  """


  def load_tasks(self):
    pass
