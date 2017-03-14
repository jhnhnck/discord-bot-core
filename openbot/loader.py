import importlib
import json
import os
from datetime import datetime

import openbot
import openbot.config
import openbot.logger


def load_plugins():
  """
  Basic Plugin Structure.

  Naming.
  The plugin should be contained within a directory in the 'plugins/' directory named in the form 'domain_plugin'.
  The domain should be an identifier for the specific developer and/or developing group and the plugin be a somewhat
  unique plugin name. Domain name is only used if both plugin names and plugin prefixes conflict which "probably won't
  ever happen"^(tm).

  Plugin Structure.
  Plugins are defined based upon a json file located in the root of the plugin directory (see 'Naming.' above). You can
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
        openbot.logger.log(plugin,
                           error_point='nodomain',
                           parent='core.warn.plugin_domain_malformed')
        domain_name = 'nodomain'
        plugin_name = plugin

      # Loads the json plugin specifier
      with open('plugins/{}/{}.json'.format(plugin, plugin_name), 'r') as file:
        plugins[plugin] = json.loads(file.read())

      # Test if disabled
      if not plugins[plugin].get('user').get('enabled'):
        openbot.logger.log(plugin,
                           parent='core.warn.disabled_plugin',
                           send_to_chat=False)
        del plugins[plugin]
        continue

      # Load python file dynamically
      plugins.get(plugin)['store'] = getattr(importlib.import_module('{}.{}'.format(plugin, plugin_name)), 'BotPlugin')()

    except Exception as e:
      openbot.logger.log(plugin,
                         parent='core.error.plugin_loading',
                         error_point=e,
                         send_to_chat=False)
      try:
        del plugins[plugin]
      except:
        pass

  return plugins


def load_functions(plugins):
  """
  Basic Function Structure.

  Naming.
  The function should be contained within a directory in the 'plugins/domain_plugin/functions/' directory. The file name
  is not in a specific format but the recommended format is 'section_function.py'. This must be defined in the
  'pluginname.json' file (See 'Function Structure.' below)

  Function Structure.
  Functions are defined based upon the 'functions' section in the json file located in the root of the plugin directory.
  For more information on this file see 'Basic Plugin Structure. -> Plugin Structure.' above.

  Additionally, the function must also have a python file that contains a class 'BotFunction' that inherits
  'FunctionBase' from 'openbot.abstract.function'. This class must at least implement the 'call()' function and can
  override the other methods present in the abstract class for more customization such as providing more advanced
  loading requirements

  Internal Function Structure.
  Each plugin is loaded into a dictionary with all the keys for that function from the 'pluginname.json' file with three
  additional keys for 'store' which contains the initialized class for that function, 'simple_string' which contains the
  calling command in the form 'core.command_prefix + function_name', and 'qualified string' which contains the longer
  calling command with the plugin prefix included in the form 'core.command_prefix + plugin_prefix + function_name'.
  """
  functions = {}

  for plugin_name, plugin in plugins.items():
    openbot.logger.log(plugin_name,
                       parent='core.debug.load_function_plugin_title',
                       send_to_chat=False)

    for ftn_name, ftn in plugin.get('functions').items():
      # ftn_path = 'plugins/{}/functions/{}.py'.format(plugin_name, ftn_name)

      if not _test_function_valid(plugin_name, ftn_name):
        continue

      # Name without prefix (can be called if no conflicts)
      simple_string = '{}{}'.format(openbot.config.get_config('core.command_prefix'),
                                    ftn.get('function_name'))

      # Name with prefix (can always be called, but must be used in case of name conflicts)
      qualified_string = '{}{}.{}'.format(openbot.config.get_config('core.command_prefix'),
                                          plugin.get('description')['plugin_prefix'],
                                          ftn.get('function_name'))

      try:
        function_class = getattr(importlib.import_module('{}.functions.{}'.format(plugin_name, ftn_name)), 'BotFunction')
        function = function_class(**{'simple_string': simple_string, 'qualified_string': qualified_string, **ftn})
      except Exception as e:
        openbot.logger.log(openbot.logger.get_locale_string('core.segments.from').format(ftn_name, plugin_name),
                           parent='core.error.function_loading',
                           error_point=e,
                           send_to_chat=False)
        continue

      # Run load_test()
      load_test = function.load_test()
      if not load_test.get('state'):
        if 'msg' not in load_test:
          load_test['msg'] = 'Load Test Failed (NoErrorReturned)'
        openbot.logger.log(openbot.logger.get_locale_string('core.segments.from').format(ftn_name, plugin_name),
                           parent='core.error.function_loading',
                           error_point=load_test.get('msg'),
                           send_to_chat=False)
        continue

      # Adds function to dictionary
      functions[qualified_string] = function

      # Checks for simple name conflicts
      if simple_string not in functions:
        functions[simple_string] = {'link': qualified_string}
      else:
        functions[qualified_string] = function
        qualified_conflict = functions[functions.get(simple_string).get('link')].qualified_string

        # See if already conflicting
        if type(functions[simple_string]) is dict:
          functions[simple_string] = [qualified_conflict, qualified_string]
        elif type(functions[simple_string]) is list:
          functions.get(simple_string).append(qualified_string)

        # Assign to qualified_string instead of simple_string
        # functions[conflict.get('qualified_string')] = conflict

          openbot.logger.log(simple_string,
                             parent='core.warn.conflict_function_name',
                             error_point=openbot.logger.get_locale_string('core.segments.two_length_or')
                             .format(qualified_string, qualified_conflict),
                             send_to_chat=False)
        continue

      # TODO: Check for qualified name conflicts

      openbot.logger.log(simple_string,
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


def _test_function_valid(plugin_name, ftn_name):
  """
  Test Function Valid.
  Tests if the function is a valid file; If discord-bot-core is ran on a develop release it will generate stub files
  for all functions that are not found

  Args:
    plugin_name: Full plugin name with domain included
    ftn_name: Name of function python file

  Returns:
    True if the function is valid, false otherwise
  """
  path = 'plugins/{}/functions/{}.py'.format(plugin_name, ftn_name)

  if os.path.isfile(path):
    return True

  elif openbot.RELEASE_TYPE == 0:
    openbot.logger.log(ftn_name,
                       parent='core.debug.gen_stub_function',
                       send_to_chat=False)

    if not os.path.exists(os.path.dirname(path)):
      os.makedirs(os.path.dirname(path))

    with open(path, 'w+') as f:
      f.write(openbot.logger.get_locale_string('core.segments.stub_function')
              .format(plugin=plugin_name, function=ftn_name, date=datetime.now()))
    return False
  else:
    openbot.logger.log(ftn_name,
                       parent='core.error.function_loading',
                       send_to_chat=False,
                       error_point='FileNotExistsError')
