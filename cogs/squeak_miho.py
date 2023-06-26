from discord.ext import tasks, commands
from discord import app_commands
import re
import os
import discord
import logging
from string import ascii_uppercase
#from random import randint
from random import choices
from random import randint
from typing import Literal
#from typing import Optional
import configparser

logger = logging.getLogger('bot')

class Squeak_Miho_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# Load config
		self.config = configparser.ConfigParser()
		self.config.read(os.path.dirname(__file__)+os.path.sep+'..'+os.path.sep+'config.ini')
		logger.info('Loaded Squeak Miho')

	async def cog_load(self):
		target_guild = self.bot.get_guild(self.config.getint('guild','guild_id'))
		for webhook in await target_guild.webhooks():
			if webhook.name == 'rosa_bot':
				self.webhook = webhook
				# Track this separately since it seems to get lost
				self.webhook_channel_id = webhook.channel_id

	# Run message relay
	@commands.Cog.listener()
	async def on_message(self, message):

		# Toy role check
		if message.author.id != 232281893696045056:
			return

		message_content = message.content
		print(message_content)

		# Allow Rosa sticker
		for sticker in message.stickers:
			if sticker.name == 'Rosaflatable':
				return

		dice_roll = randint(0,9)
		print(dice_roll)

		# ~10% chance to activate
		if dice_roll == 4:
			# Replace message
			await message.delete()

			# Squeak modififer
			if self.webhook_channel_id != message.channel.id:
				await self.webhook.edit(channel=message.channel)
				self.webhook_channel_id = message.channel.id

			wm_contents = self.squeak_modifier(message.content)
			wm_author = message.author.display_name
			wm_avatar_url = message.author.display_avatar.url
			await self.webhook.send(wm_contents, username=wm_author, avatar_url=wm_avatar_url, silent=True)


	# Modify messages
	def squeak_modifier(self, message_content: str):
		new_message = re.sub(r'[A-Za-z0-9\']+',self.squeak_length,message_content)
		return new_message

	def squeak_length(self, word):
		if len(word.group()) == 0:
			return '';
		elif len(word.group()) < 3:
			return 'sqk'
		elif len(word.group()) < 5:
			return 'SQUEAK'
		else:
			match randint(0,6):
				case 0:
					return 's'+str('q'*(len(word.group())-1))+'rk'
				case 1:
					return 'squ'+str('i'*(len(word.group())-1))+'rk'
				case 2:
					return 'squ'+str('i'*(len(word.group())-1))+'sh'
				case 3:
					return 'fw'+str('o'*(len(word.group())-1))+'mp'
				case 4:
					return 'fw'+str('w'*(len(word.group())-1))+'mp'
				case 5:
					return 'cr'+str('e'*(len(word.group())-1))+'ak'
				case 6:
					return '**Smile!**'
				case 7:
					return 'Rosa'