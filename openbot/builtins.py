import openbot.config as config

from openbot.abstract.plugin import PluginBase
from openbot.abstract.function import FunctionBase

class Builtins(PluginBase):
  """
  Built-in Functions.
  This file will contain functions that are either too small or too vital to be included in the jhnhnck_coreftns plugin.
  These are fundamentally the same as any other function and could preform the same in a command, but is required to be
  loaded for the bot to work.

  Contents.
    chat_bind, chat_reload, chat_restart, chat_shutdown, chat_sleep
  """

  plugin = """\
  description:
    plugin_name: builtins
    domain_name: jhnhnck
    plugin_prefix: core
    plugin_description: Core functions included with discord-bot-core
  functions:
    chat_bind:
      function_name: bind
      help_text: Use to specify a chat channel for commands and responses
      allowed_modifiers:
        --append: promote this channel to an approved channel
    chat_reload:
      function_name: reload
      help_text: Reloads config and plugins from file
    chat_shutdown:
      function_name: shutdown
      help_text: Completely stops the bot
    chat_restart:
      function_name: restart
      help_text: Completely stops then starts the bot again
    chat_sleep:
      function_name: sleep
      help_text: Ignore commands and mute output for a certain amount of time
      allowed_args_length: '1'
      args_description:
      - '[seconds]'
  """
