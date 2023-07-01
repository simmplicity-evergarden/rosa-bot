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
from settings import *
#from typing import Optional
import configparser

logger = logging.getLogger('bot')

class Smile_Enforcer_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Smile Enforcer')

	async def cog_load(self):
		target_guild = self.bot.get_guild(config.getint('guild','guild_id'))
		for webhook in await target_guild.webhooks():
			if webhook.name == 'rosa_bot':
				self.webhook = webhook
				# Track this separately since it seems to get lost
				config['runtime']['webhook_channel'] = str(webhook.channel_id)

	# Run message relay
	@commands.Cog.listener()
	async def on_message(self, message):

		# Webhook check
		if isinstance(message.author, discord.User):
			return

		# Toy role check
		toy_role = message.guild.get_role(config.getint('roles','toy_role'))
		if toy_role not in message.author.roles:
			return

		message_content = message.content
		print(message_content)

		# Allow Rosa sticker
		for sticker in message.stickers:
			if sticker.name == 'Rosaflatable':
				return


		if re.search(r"\*\*Smile(?:s)?!~\*\*",message_content) == None:
			# Tease on error, 5% chance
			display_tease = randint(0,9)
			if display_tease == 1:
				await message.reply("Someone forgot to **Smile!~**")
			await message.delete()

			# Squeak modififer
			if config.getint('runtime','webhook_channel') != message.channel.id:
				await self.webhook.edit(channel=message.channel)
				config['runtime']['webhook_channel'] = str(message.channel.id)

			wm_contents = self.squeak_modifier(message.content)
			wm_author = message.author.display_name
			wm_avatar_url = message.author.display_avatar.url
			await self.webhook.send(wm_contents, username=wm_author, avatar_url=wm_avatar_url, silent=True)


	# Run message relay
	@commands.Cog.listener()
	async def on_message_edit(self, message_old, message):

		# Webhook check
		if isinstance(message.author, discord.User):
			return

		# Toy role check
		toy_role = message.guild.get_role(config.getint('roles','toy_role'))
		if toy_role not in message.author.roles:
			return


		message_content = message.content
		print(message_content)

		# Allow Rosa sticker
		for sticker in message.stickers:
			if sticker.name == 'Rosaflatable':
				return

		if re.search(r"\*\*Smile(?:s)?!~\*\*",message_content) == None:
			await message.delete()
			#await message.reply("Don't forget to **Smile!~**")

	# Modify messages
	def squeak_modifier(self, message_content: str):
		new_message = re.sub(r"(?<![<:@])\b[\w']*\w*",self.squeak_length,message_content)
		return new_message

	def squeak_length(self, word):
		if len(word.group()) == 0:
			return '';
		elif len(word.group()) < 3:
			return 'sqk'
		elif len(word.group()) < 5:
			return 'SQUEAK'
		else:
			match randint(0,5):
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
					return 'Smile!'
