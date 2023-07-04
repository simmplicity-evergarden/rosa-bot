from discord.ext import tasks, commands
from discord import app_commands
import re
import os
import discord
import logging
import pickle
#from random import randint
from random import choice
from random import randint
from typing import Literal
#from typing import Optional
from settings import *
from helpers import *
#from cogs.webhook_manager import *
#import webhook_manager

logger = logging.getLogger('bot')

message_pickle_file = os.path.dirname(__file__)+os.path.sep+'feral_messages.pickle'

class Feral_Filter_Cog(commands.Cog):
	# Maps message ID to tuple(author_user_ID, original_message) 
	message_saving_dict = {}

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded WoofEnforcer')
		if os.path.exists(message_pickle_file):
			with open(message_pickle_file, 'rb') as pickle_infile:
				self.message_saving_dict = pickle.load(pickle_infile)
		self.clean_dict.start()
		self.save_messages.start()

	async def cog_load(self):
		target_guild = self.bot.get_guild(config.getint('guild','guild_id'))
		for webhook in await target_guild.webhooks():
			if webhook.name == 'rosa_bot':
				self.webhook = webhook
				# Track this separately since it seems to get lost
				config['runtime']['webhook_channel'] = str(webhook.channel_id)


	async def cog_unload(self):
		self.clean_dict.unload()
		self.save_messages.unload()

	# Clean up messages to most recent 25
	# run every 20 minutes
	@tasks.loop(minutes=20)
	async def clean_dict(self):
		newest_messages = sorted(self.message_saving_dict.keys(), reverse=True)[:50]
		for message in list(self.message_saving_dict.keys()):
			if message not in newest_messages:
				self.message_saving_dict.pop(message)

	# Save messages to file
	@tasks.loop(minutes=1)
	async def save_messages(self):
		with open(message_pickle_file, 'wb') as pickle_outfile:
			pickle.dump(self.message_saving_dict, pickle_outfile)


	# Run message relay
	@commands.Cog.listener()
	async def on_message(self, message):
		# Webhook msg check
		if type(message.author) == discord.User:
			return

		# If not a feral
		if not await has_role(self.bot, config.getint('roles','feral_role'), message.author):
			return

		# Skip if thralled
		if await has_role(self.bot, config.getint('roles','thrall_role'), message.author):
			return

		# Save message content
		message_content = message.content
		logger.debug(f'{message.author.display_name}: {message_content}')

		# Move webhook if needed
		if config.getint('runtime','webhook_channel') != message.channel.id:
			await self.webhook.edit(channel=message.channel)
			config['runtime']['webhook_channel'] = str(message.channel.id)

		wm_name=message.author.display_name
		wm_icon_url=self.icon_modifier(message.author)

		await message.delete()
		last_message_webhook_msg = await self.webhook.send(self.message_modifier(message.content), username=wm_name, avatar_url=wm_icon_url, wait=True)
		await last_message_webhook_msg.add_reaction('🔓')
		await last_message_webhook_msg.add_reaction('🔒')
		await last_message_webhook_msg.add_reaction('🐾')

		# Save author ID and message content
		self.message_saving_dict[last_message_webhook_msg.id] = (message.author.id, message.content)


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
		elif len(word.group()) > 10:
			return 'aw'+str('o'*(len(word.group())))
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
		# error prevention
		if not isinstance(reaction.emoji, str):
			# Safeword
			if reaction.emoji.name == 'safeword':
				await remove_role(self.bot, config.getint('roles','feral_role'), member)
				#await member.remove_roles(config.getint('roles','feral_role'))
				logger.info(f'{member.name} safeworded')

		# ignore bot votes
		if member.id == self.bot.user.id:
			return

		# only affect messages in dict
		if reaction.message.id not in self.message_saving_dict.keys():
			return


		# count lock/unlock votes
		vote_score = 0
		extra_huff = 0
		for msg_reaction in reaction.message.reactions:
			# Points toward unlocking w/ unlock
			if (msg_reaction.emoji == '🔓'):
				async for reaction_user in msg_reaction.users():
					# Check for bot
					if reaction_user.id == self.bot.user.id:
						continue
					# Check for ferals
					elif await has_role(self.bot, config.getint('roles','feral_role'), reaction_user.id):
						vote_score += config.getint('numbers','feral_vote_value')
					else:
						vote_score += 1
			# Points against unlocking w/ lock
			elif (msg_reaction.emoji == '🔒'):
				async for reaction_user in  msg_reaction.users():
					# Check for bot
					if reaction_user.id == self.bot.user.id:
						continue
					# Check for ferals
					elif await has_role(self.bot, config.getint('roles','feral_role'), reaction_user.id):
						vote_score -= 1
						# Prevent admin ferals from double-counting
						continue
					# Admins fully lock
					elif await is_privileged(self.bot, reaction_user.id):
						vote_score -= 10000
					else:
						vote_score -= 1
			# Increase huff chance w/ paws
			elif (msg_reaction.emoji == '🐾'):
				async for reaction_user in  msg_reaction.users():
					# Check for bot
					if reaction_user.id == self.bot.user.id:
						continue
					# Check for ferals - votes worth double
					elif await has_role(self.bot, config.getint('roles','feral_role'), reaction_user.id):
						extra_huff += int(config.getint('numbers','paw_huff_vote_value')*2)
					# Else 
						extra_huff += config.getint('numbers','paw_huff_vote_value')
			# Insta-unlock w/ key
			elif (msg_reaction.emoji == '🔑'):
				async for reaction_user in  msg_reaction.users():
					# Admins insta-unlock and 
					if await is_privileged(self.bot, reaction_user.id):
						vote_score += 100
						extra_huff = -200


		# double-check this
		if reaction.message.id not in self.message_saving_dict.keys():
			return

		(original_author_id, original_content) = self.message_saving_dict[reaction.message.id]

		if await is_simm(original_author_id) or original_author_id == 233769716198539264:
			vote_requirement = config.getint('numbers','simm_vote_requirement')
			base_huff_chance = config.getint('numbers','simm_huff_base_chance')
		else:
			vote_requirement = config.getint('numbers','feral_vote_requirement')
			base_huff_chance = config.getint('numbers','paw_huff_base_chance')

		#print(vote_score)
		#print(vote_requirement)

		# restore message
		if vote_score >= vote_requirement:
			# Fix webhook location
			if config.getint('runtime','webhook_channel') != reaction.message.channel.id:
				await self.webhook.edit(channel=reaction.message.channel)
				config['runtime']['webhook_channel'] = str(reaction.message.channel.id)

			# Huff chance
			dice_roll = randint(0,100)
			if dice_roll < base_huff_chance + extra_huff:
				original_content = "***HUFF HUFF HUFF HUFF*** **AWOOO~**"

			# triple-check this because I think it's fucking with the API limits
			if reaction.message.id not in self.message_saving_dict.keys():
				return

			await self.webhook.edit_message(reaction.message.id, content=original_content)
			self.message_saving_dict.pop(reaction.message.id)


	
