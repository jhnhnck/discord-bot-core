import discord
import asyncio


class BotClient(discord.Client):
  def __init__(self, core):
    super().__init__()
    self.core = core

  async def on_ready(self):
    self.core.logger.log("{} [{}]".format(self.user.name, self.user.id), parent='core.info.bot_logged')

  async def on_message(self, message):
    if message.content.startswith('!test'):
      counter = 0
      tmp = await self.send_message(message.channel, 'Calculating messages...')
      async for log in self.lpogs_from(message.channel, limit=100):
        if log.author == message.author:
          counter += 1

      await self.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!sleep'):
      await asyncio.sleep(5)
      await self.send_message(message.channel, 'Done sleeping')

    elif message.content.startswith('!stop'):
      await self.logout()