# Manages the webhook used by other cogs
from discord.ext import tasks, commands
from discord import app_commands
import discord
import re
import os
import logging
from settings import *

logger = logging.getLogger('bot')

webhook = 'string'

# Webhook object to use, assigned in cog_load
class Webhook_Manager_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded Webhook_Manager')

	# Get the webhook obj and the location of the webhook
	async def cog_load(self):
		target_guild = self.bot.get_guild(config.getint('guild','guild_id'))
		for webhook_obj in await target_guild.webhooks():
			if webhook_obj.name == config.get('guild','webhook_name'):
				webhook = webhook_obj
				# Track this separately since it seems to get lost
				config['runtime'] = str(webhook.channel_id)

