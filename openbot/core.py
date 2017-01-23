import os
import argparse
import importlib.util

from openbot.client import BotClient
from openbot.permissions import BotPerms
from openbot.config import ConfigStream
from openbot.logger import Logger, LogLevel


class BotCore:

  CORE_VERSION = "0.0.1"
  CORE_RELEASE_TYPE = "alpha"
  CORE_DESCRIPTION = "A simple, easily expandable, and well documented framework to add custom commands and \
                      interactions to Discord"

  def __init__(self, config_file, locale):
    self.logger = Logger(self, locale)
    self.logger.self_test()

    self.store, self.plugins = self._load_plugins()

    self.config = ConfigStream(self, self.logger, config_file=config_file)
    self.server = BotClient(self, self.logger)
    self.permissions = BotPerms()

    # self.tasks = self.load_tasks()
    self.functions = self._load_functions()
    self._register_configs()

  def run(self):
    # Client token: '***REMOVED***'
    self.server.run(self.config.get_config("core.token"))


  """
  Basic Plugin Structure.

  Naming.
    The plugin should be contained within a directory in the 'plugins/' directory named in the form 'domain_plugin'.
    The domain should be an identifier for the specific developer and/or developing group and the plugin be a somewhat
    unique plugin name. Domain name is only used if both plugin names and plugin prefixes conflict which "probably won't
    ever happen"^(tm).

  Plugin Structure.
    Plugins are defined based upon a json file located in the root of the plugin directory (see Naming. above). You can
    use the following commented example as a starting point or make a copy of the 'plugin.json' file within the
    'resources/' directory. Note that this format and its fields may change with development without notice. The file
    and the below example may not always be up to date. As always the best example of plugin structure can be found in
    the 'jhnhnck_coreftns' plugin located at 'https://github.com/jhnhnck/discord-bot-coreftns'

    Example:
    {
      "description": {                          -> SECTION: Appearance of the plugin
        "plugin_name": "coreftns",               -> name of plugin (should match directory name)
        "domain_name": "jhnhnck",                -> developer identifier
        "plugin_prefix": "core",                 -> used in case of function name conflicts
        "plugin_description":                    -> provided to the end user via the help function
          "Core functions included with discord-bot-core"
      },
      "versioning": {                           -> SECTION: Handles compatibility and updating
        "plugin_version": "1.0.0r0",             -> plugin version: defaults to major.minor.patch with optional revision
                                                    for beta versions; if you wish to use a different form, you must
                                                    override the '_compare_versions' function in your 'plugin_name.py'
        "release_type": "stable",                -> valid options are stable, preview, beta, alpha, and internal
        "requires": "[*]",                       -> bot-core compatible versions; available symbols are "[]()<>=!,*"
        "update_check_url": "",                  -> url to json formatted update description (see update.json)
        "beta_update_check_url": "",             -> same as above
      },
      "user": {                                 -> SECTION: User options (leave at default settings)
        "enabled": true,                         -> if enabled, plugin will load
        "auto_update": true,                     -> if enabled, check update url on start
        "beta_testing": false                    -> if enabled, download beta releases if provided
      },
      "config_template": {},                    -> SECTION: Default config that will be copied to master config upon
                                                   first load or update
      "functions": {                            -> SECTION: Each function definition
        "example": {                             -> internal name of function
          "help_test": "provides an example",     -> provided to the end user via the help function
          "function_name": "example",               -> name of function as it will be called
          "allowed_args_length": "[0,>7,<9]",       -> number of space-delimited or comma-delimited arguments to allow;
                                                       available symbols are "[]()<>=!,*"
          "allowed_modifiers": {                    -> modifiers that do not count toward arguments; key should contain
            "-a=": "file to use",                      actual modifier (trailing equals allows for '-a=myfile.txt' or
            "--list": "list available files"           '-a myfile.txt') and value should be a brief description
          }
        }
      }
    }

    Additionally, the plugin must also have a python file named in the form 'plugin_name.py' that contains a class
    'PluginBase' that inherits 'openbot.abstract.plugin'. This class does not have to implement any methods (you may
    simply put 'pass' in the body) but can override the other methods present in the abstract class for more
    customization such as changing the default versioning scheme or (see 'openbot/abstract/plugin.py' for more details).

  Internal Plugin Structure.
    Each plugin is loaded into a dictionary with the above keys and values with an additional key of 'store' for the
    loaded class and 'plugin' for the initialized plugin.
  """
  def _load_plugins(self):
    store = {}
    plugins = {}

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

        spec = importlib.util.spec_from_file_location(plugin,"plugins/{}/{}.py".format(plugin, plugin_name))
        store[plugin_name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(store[plugin_name])
        plugins[plugin_name] = store[plugin_name].PluginBase(self)
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

  def _load_tasks(self):
    pass

  def _load_functions(self):
    functions = []
    for name, plugin in self.plugins.items():
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

  def _register_configs(self):
      for name, plugin in self.plugins.items():
        # TODO: Log level=Debug "Config given to plugins [{}]" (array of registered plugins)
        pass
        


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=BotCore.CORE_DESCRIPTION)
  parser.add_argument('-c', '--config', nargs=1, default='config/openbot.json',
                      help='location of config file')
  parser.add_argument('-l', '--locale', nargs=1, default='en_us',
                      help='language')
  args = parser.parse_args()

  core = BotCore(args.config, args.locale)
  core.run()
