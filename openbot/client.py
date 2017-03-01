import discord
import asyncio

import openbot.config
import openbot.logger


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


  def print_message(self, content, channel=None, delete_after=None):
    asyncio.ensure_future(self._print_message(content, channel, delete_after))


  @asyncio.coroutine
  def _print_message(self, content, channel=None, delete_after=None):

    if channel is None and self.bound_channel is not None:
      channel = self.bound_channel

    if channel is not None:
      self.send_typing(channel)
      yield from asyncio.sleep(3)
      message = yield from self.send_message(channel, content)
    else:
      print('Nope')
      return

    # Delete after timeout
    if openbot.config.get_config('chat.delete_messages_delay.enabled'):
      asyncio.ensure_future(self._delay_delete(message))
    elif type(delete_after) is int:
      asyncio.ensure_future(self._delay_delete(message, delete_after))


  async def _find_binding_channel(self):
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
    if wait_duration is None:
      if len(message.content) > 250:
        wait_duration = openbot.config.get_config('chat.delete_messages_delay.timeout_long')
      else:
        wait_duration = openbot.config.get_config('chat.delete_messages_delay.timeout_short')

    await asyncio.sleep(wait_duration)
    await self.delete_message(message)

