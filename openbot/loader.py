import importlib
import json
import os
import sys
from datetime import datetime

import openbot.config as config
import openbot.logger as logger


# Add plugin directory to path
sys.path.insert(0, os.path.abspath('plugins'))


def self_test():
  pass


def load_plugins():
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
  'BotPlugin' that inherits 'PluginBase' from 'openbot.abstract.plugin'. This class does not have to implement any
  methods (you may simply put 'pass' in the body) but can override the other methods present in the abstract class for
  more customization such as changing the default versioning scheme or (see 'openbot/abstract/plugin.py' for more
  details).

  Internal Plugin Structure.
  Each plugin is loaded into a dictionary with the above keys and values with an additional key of 'store' for the
  loaded for the initialized plugin.
  """
  plugins = {}

  for plugin in os.listdir('plugins/'):
    if not os.path.isdir('plugins/{}'.format(plugin)):
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
      with open('plugins/{}/{}.json'.format(plugin, plugin_name), 'r') as file:
        plugins[plugin] = json.loads(file.read())

      # Test if disabled
      if not plugins[plugin].get('user').get('enabled'):
        logger.log(plugin,
                   parent='core.warn.disabled_plugin',
                   send_to_chat=False)
        del plugins[plugin]
        continue

      # Load python file dynamically
      plugins.get(plugin)['store'] = getattr(importlib.import_module('{}.{}'.format(plugin, plugin_name)), 'BotPlugin')()

    except Exception as e:
      logger.log(plugin,
                 parent='core.error.plugin_loading',
                 error_point=e,
                 send_to_chat=False)
      del plugins[plugin]

  return plugins


def load_functions(plugins):
  """
  Basic Function Structure.
  TODO: Create a structure for functions to be loaded
  """
  functions = {}

  for plugin_name, plugin in plugins.items():
    logger.log(plugin_name,
               parent='core.debug.load_function_plugin_title',
               send_to_chat=False)

    # Stores prefix for easy lookup later
    prefix = plugin.get('description')['plugin_prefix']

    for ftn_name, ftn in plugin.get('functions').items():
      ftn_path = 'plugins/{}/functions/{}.py'.format(plugin_name, ftn_name)

      if not _test_function_valid(plugin_name, ftn_name, ftn_path):
        continue

      # Name without prefix (can be called if no conflicts)
      simple_string = config.get_config('core.command_prefix') + ftn.get('function_name')

      # Name with prefix (can always be called, but must be used in case of name conflicts)
      qualified_string = '{}{}.{}'.format(config.get_config('core.command_prefix'), prefix, ftn.get('function_name'))

      try:
        function = {
          'store': getattr(importlib.import_module('{}.functions.{}'.format(plugin_name, ftn_name)), 'BotFunction')(),
          'simple_string': simple_string,
          'qualified_string': qualified_string,
          **ftn
        }
      except Exception as e:
        logger.log(logger.get_locale_string('core.segments.from').format(ftn_name, plugin_name),
                   parent='core.error.function_loading',
                   error_point=e)

      # Run load_test()
      load_test = function.get('store').load_test()
      if not load_test.get('state'):
        if 'msg' not in load_test:
          load_test['msg'] = 'Load Test Failed (NoErrorReturned)'
        logger.log(logger.get_locale_string('core.segments.from').format(ftn_name, plugin_name),
                   parent='core.error.function_loading',
                   error_point=load_test.get('msg'))
        continue

      # Adds function to dictionary
      functions[qualified_string] = function

      # Checks for simple name conflicts
      if simple_string not in functions:
        functions[simple_string] = {'link': qualified_string}
      else:
        functions[qualified_string] = function
        conflict = functions[simple_string.get('link')]

        # See if already conflicting
        if type(functions[simple_string]) is dict:
          functions[simple_string] = [conflict.get('qualified_string'), qualified_string]
        elif type(functions[simple_string]) is list:
          functions.get(simple_string).append(qualified_string)

        # Assign to qualified_string instead of simple_string
        # functions[conflict.get('qualified_string')] = conflict

        logger.log(simple_string,
                   parent='core.warn.conflict_function_name',
                   error_point=logger.get_locale_string('core.segments.two_length_or')
                   .format(qualified_string, conflict),
                   send_to_chat=False)
        continue

      logger.log(simple_string,
                 parent='core.debug.load_function_success',
                 error_point=ftn_name,
                 send_to_chat=False)

  return functions


def load_tasks():
  """
  Basic Task Structure.
  TODO: Create a structure for tasks to be loaded
  """
  pass


def _test_function_valid(plugin_name, ftn_name, path):
  if os.path.isfile(path):
    return True
  else:
    logger.log(ftn_name, parent='core.debug.gen_stub_function', send_to_chat=False)
    with open('plugins/{}/functions/{}.py'.format(plugin_name, ftn_name), 'w+') as f:
      f.write(logger.get_locale_string('core.segments.stub_function').format(plugin=plugin_name, function=ftn_name, date=datetime.now()))
    return False
