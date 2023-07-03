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

logger = logging.getLogger('bot')

class Squeak_Role_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# Load config
		logger.info('Loaded Squeak Role')

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
		# webhook check
		if type(message.author) == discord.User:
			return


		# Role ID check
		if config.getint('roles','squeak_role') not in [role.id for role in message.author.roles]:
			return

		# Allow Rosa sticker
		for sticker in message.stickers:
			if sticker.name == 'Rosaflatable':
				return
		message_content = message.content

		# Squeak-toy synergy - multi-track brainrot
		if re.search(r"\*\*Smile(?:s)?!~\*\*",message_content) == None and \
			config.getint('roles','toy_role') in [role.id for role in message.author.roles]:
			# Quit if toy_role will pick up on it
			return


		dice_roll = randint(0,100)
		#logger.debug(dice_roll)
		logger.debug(f'{message.author.display_name} {dice_roll}: {message_content}')

		# ~10% chance to activate
		if dice_roll < config.getint('numbers','role_squeak_chance'):
			# Replace message
			await message.delete()

			# Squeak modififer
			if config.getint('runtime','webhook_channel') != message.channel.id:
				await self.webhook.edit(channel=message.channel)
				config['runtime']['webhook_channel'] = str(message.channel.id)

			wm_contents = self.squeak_modifier(message.content)
			wm_author = message.author.display_name
			wm_avatar_url = message.author.display_avatar.url
			await self.webhook.send(wm_contents, username=wm_author, avatar_url=wm_avatar_url, silent=True)


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

	# Role safeword
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, member):
		# Add role
		if reaction.emoji == '🎈':
			squeak_role = member.guild.get_role(config.getint('roles','squeak_role'))
			await member.add_roles(squeak_role)
			logger.debug(f'{member.name} added themselves to the squeak role')

		if isinstance(reaction.emoji, str):
			return 

		# Avoid extra logging
		if config.getint('roles','squeak_role') not in [role.id for role in member.roles]:
			return

		# Remove role - safeword
		if reaction.emoji.name == 'safeword':
			squeak_role = member.guild.get_role(config.getint('roles','squeak_role'))
			await member.remove_roles(squeak_role)
			logger.debug(f'{member.name} safeworded')
