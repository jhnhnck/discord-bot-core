import os
import importlib.util
import json

import openbot.logger as logger
import openbot.config as config


def self_test():
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
  make a copy of the 'coreftns.json' file within the 'resources/' directory commented example as a starting point. Note
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
def load_plugins():
  store = {}
  plugins = {}

  for plugin in os.listdir('plugins/'):
    if not os.path.isdir('plugins/{}'.format(plugin)):
      logger.log(plugin,
                 parent='core.error.plugin_loading',
                 error_point='invalid plugin',
                 send_to_chat=False)
      continue

    try:
      # Splits fully-qualified plugin name into plugin domain/group name and plugin name.
      if plugin.find('_') != -1:
        split = plugin.split('_')
        plugin_name = split[-1]
        domain_name = split[0]
      else:
        logger.log(plugin, error_point='nodomain', parent='core.warn.plugin_domain_malformed')
        domain_name = 'nodomain'
        plugin_name = plugin

      # Loads the json plugin specifier
      with open('plugins/{}/{}.json'.format(plugin, plugin_name), "r") as file:
        plugins[plugin_name] = json.loads(file.read())

      # Load python file dynamically
      spec = importlib.util.spec_from_file_location(plugin, "plugins/{}/{}.py".format(plugin, plugin_name))
      store[plugin_name] = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(store[plugin_name])
      plugins.get(plugin_name)['store'] = store[plugin_name].PluginBase()
    except Exception as e:
      logger.log(plugin,
                 parent="core.error.plugin_loading",
                 error_point=e,
                 send_to_chat=False)

  return plugins


"""
Basic Function Structure.
TODO: Create a structure for functions to be loaded
"""
def load_functions(plugins):
  functions = {}


  for name, plugin in plugins.items():
    logger.log(name,
               parent='core.debug.load_function_plugin_title',
               send_to_chat=False)
    prefix = plugin.get('description')['plugin_prefix']
    for ftn_name, ftn in plugin.get('functions').items():
      simple_string = config.get_config('core.command_prefix') + ftn.get('function_name')
      qualified_string = '{}{}.{}'.format(config.get_config('core.command_prefix'), prefix, ftn.get('function_name'))

      if simple_string not in functions:
        functions[simple_string] = qualified_string
      else:
        functions[qualified_string] = qualified_string
        conflict = functions[simple_string]
        del functions[simple_string]
        functions[conflict] = conflict
        logger.log(simple_string,
                   parent='core.warn.conflict_function_name',
                   # TODO: Fix this later...
                   error_point='"{}" or "{}"'.format(qualified_string, conflict),
                   send_to_chat=False)

      logger.log(simple_string,
                 parent="core.debug.load_function_success",
                 error_point=ftn_name,
                 send_to_chat=False)

  return functions


"""
Basic Task Structure.
TODO: Create a structure for tasks to be loaded
"""
def load_tasks():
  pass
