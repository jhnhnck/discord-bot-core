import asyncio

import discord

import openbot.logger as logger


class BotClient(discord.Client):

  def __init__(self):
    super().__init__()

  async def on_ready(self):
    logger.log('{} [{}]'.format(self.user.name, self.user.id), parent='core.info.bot_logged')

  async def on_message(self, message):
    # Saved for later: self.core.config.get_config('core', 'command_prefix')
    if message.content.startswith('!stop'):
      await self.logout()
