from discord.ext import tasks, commands
from discord import app_commands
import pickle
import re
import os
import discord
import time
import logging
from string import ascii_uppercase
#from random import randint
from random import choice
from random import randint
from typing import Literal
from settings import *
from helpers import *
#from typing import Optional

# Rosa ID
rosa_id = 153857426813222912
#rosa_id = 137655955876741120 # doll :3


# Thrall role ID: 1125452920301834250

mantra_file_location = os.path.dirname(__file__)+os.path.sep+'mantras.txt'
thrall_file_location = os.path.dirname(__file__)+os.path.sep+'thralls.pickle'

logger = logging.getLogger('bot')

class Mantras_Cog(commands.Cog):
	# List of mantras
	mantras = []
	# List of thralls
	thralls = {}

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded Mantras')
		# Load mantras
		if os.path.exists(mantra_file_location):
			with open(mantra_file_location, 'r') as mantra_file:
				self.mantras = mantra_file.readlines()
		#print(self.mantras)
		# Load thralls
		if os.path.exists(thrall_file_location):
			with open(thrall_file_location, 'rb') as thrall_infile:
				self.thralls = pickle.load(thrall_infile)
		# Start loop for clearing thralls
		self.clean_thralls.start()

	async def cog_load(self):
		target_guild = self.bot.get_guild(config.getint('guild','guild_id'))
		for webhook in await target_guild.webhooks():
			if webhook.name == 'rosa_bot':
				self.webhook = webhook
				# Track this separately since it seems to get lost
				config['runtime']['webhook_channel'] = str(webhook.channel_id)


	async def cog_unload(self):
		self.clean_thralls.unload()

	# Remove thralldom after a user's timer expires
	@tasks.loop(seconds=20)
	async def clean_thralls(self):
		thralls_copy = list(self.thralls.keys())
		for user_id in thralls_copy:
			# If X minutes have passed
			#print(user_id)
			#print(time.time() > (self.thralls[user_id] + (config.getint('numbers','thrall_duration')*60)))
			if time.time() > (self.thralls[user_id] + (config.getint('numbers','thrall_duration'))):
				await self.remove_thralldom(user_id)

	# Run message relay
	@commands.Cog.listener()
	async def on_message(self, message):
		# webhook check
		if type(message.author) == discord.User:
			return


		# Od exemption
		if message.author.id == 201821870255898625:
			return

		# Prevent rosa from self-thralling
		#if message.author.id == rosa_id:
		if await is_rosa(message.author.id):
			return

		# Prevent bot from thralling itself
		#if message.author.id == self.bot.user.id:
		if await is_bot(self.bot, message.author.id):
			return

		# See if Rosa was mentioned
		rosa_mentioned = rosa_id in [user.id for user in message.mentions]

		if message.reference is not None:
			if message.reference.cached_message is not None:
				if message.reference.cached_message.author.id == rosa_id:
					rosa_mentioned = True

		#print(message.author.id not in self.thralls)
		#print(f'{message.author.name} {rosa_mentioned}')

		# if not in list AND message mentions rosa
		if (message.author.id not in self.thralls.keys()) and rosa_mentioned:
			logger.info(f'{message.author.display_name} is now a thrall')
			# remove user from conflicting roles
			#feral_role = message.guild.get_role(config.getint('roles','feral_role'))
			#squeak_role = message.guild.get_role(config.getint('roles','toy_role'))
			#toy_role = message.guild.get_role(config.getint('roles','squeak_role'))
			#await message.author.remove_roles(feral_role, squeak_role, toy_role)
			await add_role(self.bot, config.getint('roles','thrall_role'), message.author)
			# add user to rosa-worship thralls
			self.thralls[message.author.id] = time.time()
			with open(thrall_file_location, 'wb') as thrall_outfile:
				pickle.dump(self.thralls, thrall_outfile)
			return

		# check if user not a thrall
		if message.author.id not in self.thralls.keys():
			return

		# Log original message
		logger.debug(f'{message.author.display_name}: {message.content}')

		# replace message w/ random mantra

		# Delete message
		await message.delete()

		# Squeak modififer
		if config.getint('runtime','webhook_channel') != message.channel.id:
			await self.webhook.edit(channel=message.channel)
			config['runtime']['webhook_channel'] = str(message.channel.id)

		wm_contents = self.get_mantra()
		wm_author = message.author.display_name
		wm_avatar_url = message.author.display_avatar.url
		await self.webhook.send(wm_contents, username=wm_author, avatar_url=wm_avatar_url, silent=True)


	# Modify messages
	def get_mantra(self):
		return choice(self.mantras)

	# Role safeword
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, member):
		if isinstance(reaction.emoji, str):
			return 

		# Avoid extra logging
		if member.id not in self.thralls.keys():
			return

		# Remove role - safeword
		if reaction.emoji.name == 'safeword':
			await self.remove_thralldom(member.id)

	# Remove user from thralls
	async def remove_thralldom(self, user_id):
		# Remove user from thrall tracking
		self.thralls.pop(user_id)
		with open(thrall_file_location, 'wb') as thrall_outfile:
			pickle.dump(self.thralls,thrall_outfile)
		# Remove role from user
		await remove_role(self.bot, config.getint('roles','thrall_role'), user_id)
		user_obj = await find_member(self.bot, user_id)
		logger.debug(f'{user_obj.display_name} was removed from thralldom')

