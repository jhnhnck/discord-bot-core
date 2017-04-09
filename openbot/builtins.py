import ruamel.yaml as yaml

import openbot.config
from openbot.abstract.function import FunctionBase
from openbot.abstract.plugin import PluginBase


class Builtins(PluginBase):
  """
  Built-in Functions.
  This file will contain functions that are either too small or too vital to be included in the jhnhnck_coreftns plugin.
  These are fundamentally the same as any other function and could preform the same in a command, but is required to be
  loaded for the bot to work.

  Contents.
    chat_bind, chat_reload, chat_restart, chat_shutdown, chat_sleep
  """
  def __init__(self):
    plugin = """\
    description:
      plugin_name: Builtins
      domain_name: jhnhnck
      plugin_prefix: core
      plugin_description: Core functions included with discord-bot-core
      plugin_type: single-file
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
    config = yaml.load(plugin)
    super().__init__(**config)


class CommandBind(FunctionBase):

  def load_test(self):
    """
    Loading Self Test.
    Implement this method to allow for more vigorous control over loading requirements.

    Returns:
      Dictionary with two keys:
        state: True if the function should be loaded
        msg: Detailed error message (Do not use logging here; It may not always work)
    """
    return {'state': True}


  def call(self, client, message, mod):
    """
    Call.
    Binds the discord bot to a specific channel
    """
    # has_permission will handle no permissions
    if openbot.config.has_perm(message.owner, 'admin.set_channel_bindings'):
      if mod.get('--append'):
        channel_ids = openbot.config.get_config('chant.channels.bind_text_channels')
        channel_ids = channel_ids.append(message.channel.id)
      else:
        channel_ids = [message.channel.id]

        openbot.config.set_config('chat.channels.bind_text_channels', channel_ids)