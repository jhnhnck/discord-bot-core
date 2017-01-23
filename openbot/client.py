import discord
import asyncio


class BotClient(discord.Client):
  def __init__(self, core, logger):
    super().__init__()
    self.core = core
    self.logger = logger

  async def on_ready(self):
    self.logger.log("{} [{}]".format(self.user.name, self.user.id), parent='core.info.bot_logged')

  async def on_message(self, message):
    # Saved for later: self.core.config.get_config('core', 'command_prefix')
    if message.content.startswith('!stop'):
      await self.logout()
