from discord.ext import tasks, commands
from discord import app_commands
import configparser
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
from settings import *
#from cogs.webhook_manager import *
#import webhook_manager

logger = logging.getLogger('bot')

class Feral_Filter_Cog(commands.Cog):
	message_saving_dict = {}

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded WoofEnforcer')
		self.clean_dict.start()

	async def cog_load(self):
		target_guild = self.bot.get_guild(config.getint('guild','guild_id'))
		for webhook in await target_guild.webhooks():
			if webhook.name == 'rosa_bot':
				self.webhook = webhook
				# Track this separately since it seems to get lost
				config['runtime']['webhook_channel'] = str(webhook.channel_id)


	async def cog_unload(self):
		self.clean_dict.unload()

	# Clean up messages to most recent 25
	# run every 20 minutes
	@tasks.loop(minutes=20)
	async def clean_dict(self):
		newest_messages = sorted(self.message_saving_dict.keys(), reverse=True)[:50]
		for message in list(self.message_saving_dict.keys()):
			if message not in newest_messages:
				self.message_saving_dict.pop(message)

	# Run message relay
	@commands.Cog.listener()
	async def on_message(self, message):
		# Webhook msg check
		if type(message.author) == discord.User:
			return

		feral_role = message.guild.get_role(config.getint('roles','feral_role'))
		if feral_role not in message.author.roles:
			return



		message_content = message.content
		print(message_content)
		self.last_message_text = message.content

		if config.getint('runtime','webhook_channel') != message.channel.id:
			await self.webhook.edit(channel=message.channel)
			config['runtime']['webhook_channel'] = str(message.channel.id)

		wm_name=message.author.display_name
		wm_icon_url=self.icon_modifier(message.author)

		await message.delete()
		last_message_webhook_msg = await self.webhook.send(self.message_modifier(message.content), username=wm_name, avatar_url=wm_icon_url, wait=True)
		await last_message_webhook_msg.add_reaction('🔓')

		# Save message contents
		# For contents of the last message
		self.message_saving_dict[last_message_webhook_msg.id] = message.content


	# Modify message, return string
	def message_modifier(self, message_content: str):
		if message_content.endswith('...'):
			message_content = "*whines*"
		elif message_content.endswith('!'):
			message_content = "***bark!***"
		else:
			message_content = re.sub(r"(?:(?<![<:@])\b[\w']*\w*|(?:<a?)?:\w+:(?:\d{18,19}>)?)",self.woof_length,message_content)
		return message_content

	def woof_length(self, word):
		if len(word.group()) == 0:
			return '';
		elif len(word.group()) < 3:
			match randint(0,1):
				case 0:
					return 'gr'
				case 1:
					return 'arf'
				case 2:
					return 'ru'
		elif len(word.group()) < 5:
			match randint(0,1):
				case 0:
					return 'ruff'
				case 1:
					return 'woof'
				case 2:
					return 'bark'
		else:
			match randint(0,7):
				case 0:
					return 'ba'+str('r'*(len(word.group())-1))+'k'
				case 1:
					return 'w'+str('o'*(len(word.group())-1))+'f'
				case 2:
					return 'ba'+str('r'*(len(word.group())-1))+'k'
				case 3:
					return 'b'+str('a'*(len(word.group())//2))+str('r'*(len(word.group())//2))+'k'
				case 4:
					return '*whimper*'
				case 5:
					return 'aww'+str('o'*(len(word.group())-1))
				case 6:
					return '*growl*'
				case 7:
					return '*pants*'


	# Modify user's name, return string
	def name_modifier(self, user: discord.User):
		return user.display_name

	# Modify user's icon, return url
	def icon_modifier(self, user: discord.User):
		return user.display_avatar.url



	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, member):
		feral_role = member.guild.get_role(config.getint('roles','feral_role'))
		mod_role = member.guild.get_role(config.getint('roles','mod_role'))
		admin_role = member.guild.get_role(config.getint('roles','admin_role'))

		# error prevention
		if not isinstance(reaction.emoji, str):
			# Safeword
			if reaction.emoji.name == 'safeword':
				await member.remove_roles(feral_role)
				logger.info(f'{member.name} safeworded')

		# ignore bot + affected user
		if member.id == self.bot.user.id:
			return

		# only affect last message
		if reaction.message.id not in self.message_saving_dict.keys():
			return


		# count unlock reactions
		user_count = 0
		for msg_reaction in reaction.message.reactions:
			# Track "score"
			# Points toward unlocking
			if (msg_reaction.emoji == '🔓'):
				async for reaction_user_raw in  msg_reaction.users():
					# get member obj
					reaction_user = member.guild.get_member(reaction_user_raw.id)
					# cache miss
					if reaction_user == None:
						reaction_user = await member.guild.fetch_member(reaction_user_raw.id)

					# skip bot
					#if reaction_user.id == 1053028780383424563:
					#	user_count += 100
					if reaction_user.id == self.bot.user.id:
						#print(f'Bot user {reaction_user.name}')
						continue
					# skip ferals
					elif feral_role in reaction_user.roles:
						#print('feral')
						user_count += config.getint('numbers','feral_vote_value')
						continue
					else:
						user_count += 1
					# insta-reveal for mods and admins
					if mod_role in reaction_user.roles:
						#print(f'moderator {reaction_user.display_name}')
						user_count += 100
					if admin_role in reaction_user.roles:
						#print(f'admin {reaction_user.display_name}')
						user_count += 100
				#print(f'User count is now {user_count}')
			# Points against unlocking
			elif (msg_reaction.emoji == '🔒'):
				async for reaction_user_raw in  msg_reaction.users():
					# get member obj
					reaction_user = member.guild.get_member(reaction_user_raw.id)
					# cache miss
					if reaction_user == None:
						reaction_user = await member.guild.fetch_member(reaction_user_raw.id)
					# Only work for admins
					if mod_role in reaction_user.roles:
						#print(f'moderator {reaction_user.display_name}')
						user_count -= 10000
					if admin_role in reaction_user.roles:
						#print(f'admin {reaction_user.display_name}')
						user_count -= 10000
				#print(f'User count is now {user_count}')


		# double-check this
		if reaction.message.id not in self.message_saving_dict.keys():
			return

		# restore message
		if user_count >= config.getint('numbers','feral_vote_requirement'):
			if config.getint('runtime','webhook_channel') != reaction.message.channel.id:
				await self.webhook.edit(channel=reaction.message.channel)
				config['runtime']['webhook_channel'] = str(reaction.message.channel.id)
			original_content = self.message_saving_dict[reaction.message.id]

			# Huff chance
			dice_roll = randint(0,100)
			if dice_roll < config.getint('numbers','paw_huff_chance'):
				original_content = "***HUFF HUFF HUFF HUFF*** **AWOOO~**"

			await self.webhook.edit_message(reaction.message.id, content=original_content)
			self.message_saving_dict.pop(reaction.message.id)



	
