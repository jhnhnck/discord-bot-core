import discord
import asyncio
import inspect

import openbot.core
import openbot.config
import openbot.logger

from openbot.abstract.function import FunctionBase

class BotSyncedWrapper:

  def __init__(self):
    # Does this cause a error?
    self.client = BotClient()


  def run(self, *args, **kwargs):
    """
    Run.
    Pass-through for BotClient.run()
    """
    self.client.run(*args, **kwargs)


  def print_message(self, content, channel=None, delete_after=None):
    """
    Print Message.
    Ensures that a message will be sent to the server

    Args:
      content: String value of the message
      channel: (Optional) Channel to send the message to
      delete_after: (Optional) Seconds to delete message after; -1 to disable; defaults to config value
    """
    asyncio.ensure_future(self.client.print_message(content, channel, delete_after))


class BotClient(discord.Client):

  bound_channel = None

  def __init__(self):
    super().__init__()

  async def on_ready(self):
    openbot.logger.log('{} [{}]'.format(self.user.name, self.user.id),
                       parent='core.info.bot_logged',
                       send_to_chat=False)

    # Tries to match a binding channel
    self.bound_channel = await self._find_binding_channel()
    # openbot.core.server = self

    # if openbot.RELEASE_TYPE == 0:
    #   openbot.logger.self_test(send_to_chat=True)


  async def on_message(self, message):
    await self.wait_until_ready()

    content = message.content.strip()

    if content.startswith(openbot.config.get_config('core.command_prefix')):
      asyncio.ensure_future(self.call_function(message))


  @asyncio.coroutine
  def print_message(self, content, channel=None, delete_after=None):
    """
    Print Message.
    Ensures that a message will be sent to the server

    Args:
      content: String value of the message
      channel: (Optional) Channel to send the message to
      delete_after: (Optional) Seconds to delete message after; -1 to disable; defaults to config value
    """
    if channel is None and self.bound_channel is not None:
      channel = self.bound_channel

    if channel is not None:
      yield from self.send_typing(channel)
      message = yield from self.send_message(channel, content)
    else:
      openbot.logger.log(content[:20], parent='core.error.channel_none', send_to_chat=False)
      return

    # Delete after timeout
    if delete_after == -1:
      return
    elif type(delete_after) is int:
      asyncio.ensure_future(self._delay_delete(message, delete_after))
    elif openbot.config.get_config('chat.delete_messages_delay.enabled'):
      asyncio.ensure_future(self._delay_delete(message))


  async def _find_binding_channel(self):
    """
    Find Binding Channel.
    Finds the chat channel that messages should default to

    Returns:
      A discord.Channel object of the binded channel
    """
    if openbot.config.get_config('chat.bind_text_channels.enabled'):
      for channel in openbot.config.get_config('chat.bind_text_channels.channels'):
        try:
          # Checks for channel ids
          if channel.isdigit():
            attempt_channel = self.get_channel(channel)

            if attempt_channel is not None:
              openbot.logger.log(attempt_channel, parent='core.info.bound_channel', send_to_chat=False)
              return attempt_channel

          # Checks for channel names
          else:
            for attempt_channel in self.get_all_channels():
              if attempt_channel.name.lower() == channel:
                openbot.logger.log(attempt_channel, parent='core.info.bound_channel', send_to_chat=False)
                return attempt_channel

          openbot.logger.log(channel, parent='core.warn.bound_channel', send_to_chat=False)
        except Exception as e:
          openbot.logger.log(channel,
                             error_point=e,
                             parent='core.error.bound_channel',
                             send_to_chat=False)

    # If can't match channel or disabled
    for attempt_channel in self.get_all_channels():
      if attempt_channel.name.lower() == 'general':
        openbot.logger.log(attempt_channel, parent='core.info.bound_channel', send_to_chat=False)
        return attempt_channel

    # if all else fails
    attempt_channel = self.get_all_channels()[0]
    openbot.logger.log(attempt_channel, parent='core.info.bound_channel', send_to_chat=False)
    return attempt_channel
        

  async def _delay_delete(self, message, wait_duration=None):
    """
    Delayed Delete.
    Async task to delete messages after a delay
    Args:
      message: message object to delete
      wait_duration: delay in seconds
    """
    if wait_duration is None:
      if len(message.content) > 250:
        wait_duration = openbot.config.get_config('chat.delete_messages_delay.timeout_long')
      else:
        wait_duration = openbot.config.get_config('chat.delete_messages_delay.timeout_short')

    await asyncio.sleep(wait_duration)
    await self.delete_message(message)


  @asyncio.coroutine
  def call_function(self, message):
    call = message.content.split()

    ftn = self._get_function(call[0])

    # Function is not found
    if ftn is None:
      asyncio.ensure_future(self._delay_delete(message, wait_duration=120))

      # Check for close commands
      import difflib
      close_matches = difflib.get_close_matches(call, ftn)

      if len(close_matches) > 0:
        openbot.logger.log('\n - ' + '\n - '.join(close_matches),
                           error_point=call[0],
                           parent='core.error.command_error_suggest')
      else:
        openbot.logger.log(call[0],
                           parent='core.error.command_not_found',
                           delete_after=120)
      return

    # Function is not specific enough
    elif type(ftn) is list:
      openbot.logger.log('\n - ' + '\n - '.join(ftn),
                         parent='core.error.command_specifics',
                         delete_after=120)
      asyncio.ensure_future(self._delay_delete(message, wait_duration=120))
      return

    # Valid Function
    elif isinstance(ftn, FunctionBase):
      args = self._make_call_args(message, call, ftn)

      # Handle invalid length
      if 'invalid_length' in args:
        openbot.logger.log(ftn.help_message(),
                           error_point=call[0],
                           parent='core.error.args_length',
                           delete_after=120)
        asyncio.ensure_future(self._delay_delete(message, wait_duration=120))
        return

      ftn.call(**args)


  def _get_function(self, name):
    # Test if function exists
    if name not in openbot.core.functions:
      return None

    ftn = openbot.core.functions.get(name)

    # Recurse on link
    if type(ftn) is dict:
      return self._get_function(ftn.get('link'))

    # Either a list or actual ftn object
    else:
      return ftn


  def _make_call_args(self, message, call, ftn):
    args = {
      'client': openbot.core.server.client,
      'message': message,
      **self._parse_args(call, ftn)
    }

    req = inspect.signature(ftn.call).parameters.keys()
    for key in list(args):
      if key not in req:
        del args[key]
    return args


  @staticmethod
  def _parse_args(call, ftn):
    args = []
    mod = {}

    for i in range(1, len(call)):
      # Tests if modifier
      if call[i].startswith('-'):
        # Tests if in expected modifiers
        if call[i] in ftn.allowed_modifiers:
          # Tests if provides a value
          if call[i].endswith('='):
            new_mod = call[i].split('=')
            mod[new_mod[0]] = new_mod[1]
          else:
            mod[call[i]] = True

        # Tests for split between calls
        elif call[i] + '=' in ftn.allowed_modifiers:
          mod[call[i]] = call[i+1]
          i += 1
      else:
        args.append(call[i])

    # Valid args length
    valids = ftn.allowed_args_length.split(',')
    is_valid = False

    for valid in valids:
      if valid == '*':
        is_valid = True
        break
      elif valid.startswith('>'):
        if len(args) > int(valid[1:]):
          is_valid = True
          break
      elif valid.startswith('<'):
        if len(args) < int(valid[1:]):
          is_valid = True
          break
      elif valid.startswith('!'):
        if not len(args) == int(valid[1:]):
          is_valid = True
      elif len(args) < int(valid):
          is_valid = True
          break

    # Handle invalid args length
    if not is_valid:
      return {'invalid_length': len(args)}

    # Set false for missing mods
    for a_mod in ftn.allowed_modifiers:
      if '=' not in a_mod and a_mod not in mod:
        mod[a_mod] = False

    return {
      'args': args,
      'mod': mod
      }
