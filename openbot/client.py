import discord
import asyncio

import openbot.config
import openbot.logger


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

    if openbot.RELEASE_TYPE == 0:
      openbot.logger.self_test(send_to_chat=True)


  async def on_message(self, message):
    # Saved for later: core.config.get_config('core', 'command_prefix')
    if message.content.startswith('!stop'):
      await self.logout()


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

