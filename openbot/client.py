import asyncio

import discord

import openbot.logger


class BotClient(discord.Client):

  def __init__(self):
    super().__init__()

  async def on_ready(self):
    openbot.logger.log('{} [{}]'.format(self.user.name, self.user.id),
                       parent='core.info.bot_logged',
                       send_to_chat=False)

    if openbot.RELEASE_TYPE == 0:
      openbot.logger.self_test(send_to_chat=True)

  async def on_message(self, message):
    # Saved for later: self.core.config.get_config('core', 'command_prefix')
    if message.content.startswith('!stop'):
      await self.logout()
