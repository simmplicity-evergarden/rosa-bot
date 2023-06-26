from discord.ext import tasks, commands
#from discord import app_commands
import discord
#import petrify_logic
#import json
#import helpers
#import time
import logging
#from random import randint
#from random import choice
#from typing import Literal
from typing import Optional

logger = logging.getLogger('bot')

class Speak_as_Bot_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.hybrid_command(description='Speak through the bot')
	async def speak(self, context: commands.Context, *, message: str):
		if context.author.id not in [1053028780383424563,153857426813222912]:
			logger.debug(f'{context.author.display_name} failed /speak command auth with message: {message}')
			return

		logger.debug(f'{context.author.display_name} speaks as the bot: {message}')
		await context.channel.send(message)
		await context.send('confirmed',ephemeral=True,delete_after=0.1)
