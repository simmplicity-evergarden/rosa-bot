from discord.ext import tasks, commands
from discord import SyncWebhook
from discord import app_commands
import configparser
import re
import os
import discord
import logging
from string import ascii_uppercase
#from random import randint
from random import choices
from typing import Literal
#from typing import Optional

logger = logging.getLogger('bot')

woof_enforced_path = os.path.dirname(__file__)+os.path.sep+'woof_enforced.txt'

class Leashing_Cog(commands.Cog):

	leash_mapping = {}

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded leashing')

	# Leashing command
	@commands.hybrid_command(description='Add or remove leashing (toggle).')
	async def leash(self, context: commands.Context, target_member: discord.Member):
		# Permissions check
		if context.author.id not in [1053028780383424563]:
			return
		logger.info(f'{context.author.name} attempts to leash {target_member.name}')

		for leasher in self.leash_mapping.keys():
			if target_member.id in self.leash_mapping[leasher] and context.author.id != leasher:
				await context.send('This user is already leashed by someone else!')
				return
			elif target_member.id in self.leash_mapping[leasher] and context.author.id == leasher:
				await self.remove_from_leashing(target_member)
				await context.send('Unleashed user')
				return

		if context.author.id in self.leash_mapping.keys():
			self.leash_mapping[context.author.id].append(target_member.id)
		else:
			self.leash_mapping[context.author.id] = [target_member.id]
		await context.send(f'Successfully leashed {target_member.display_name}.')

		# Permission overwrite that deny viewing a channel
		no_perms = discord.PermissionOverwrite()
		no_perms.view_channel = False

		for channel in context.guild.channels:
			# Ignore important channels
			if channel.category == None:
				continue
			if channel.category_id != 1047483311703998486:
				continue

			# Allow only the channel that 
			if channel.id == context.channel.id:
				await channel.set_permissions(target_member, overwrite = None)
			else:
				await channel.set_permissions(target_member, overwrite = no_perms)
		logger.info('Leashing successful!')

	# Leashing command
	@commands.hybrid_command(description='Add or remove leashing (toggle).')
	async def leash_debug(self, context: commands.Context, target_member: discord.Member):
		# Permissions check
		if context.author.id not in [1053028780383424563]:
			return

		await self.remove_from_leashing(target_member)


	# Run message relay
	@commands.Cog.listener()
	async def on_message(self, message):
		# Check for leasher's ID
		if message.author.id not in self.leash_mapping.keys():
			return

		# Permission overwrite that deny viewing a channel
		no_perms = discord.PermissionOverwrite()
		no_perms.view_channel = False

		# Edit leashee's perms
		for leashee_id in self.leash_mapping[message.author.id]:
			leashee = message.guild.get_member(leashee_id)
			# cache miss
			if leashee == None:
				leashee = await message.guild.fetch_member(leashee_id)
			for channel in message.guild.channels:
				# Ignore important channels
				if channel.category == None:
					continue
				if channel.category_id != 1047483311703998486:
					continue

				# Allow only the channel that 
				if channel.id == message.channel.id:
					await channel.set_permissions(leashee, overwrite = None)
				else:
					await channel.set_permissions(leashee, overwrite = no_perms)

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, member: discord.Member):
		# Error check
		if isinstance(reaction.emoji, str):
			return

		# safeword
		if reaction.emoji.name == 'safeword':
			await self.remove_from_leashing(member)

	# Remove user from lists + clear channel restrictions
	async def remove_from_leashing(self, member: discord.Member):
		# Remove user from list
		for leasher in self.leash_mapping.keys():
			if member.id in self.leash_mapping[leasher]:
				self.leash_mapping[leasher].remove(member.id)

		# Clear all user-specific channel restrictions
		for channel in member.guild.channels:
			# Ignore important channels
			if channel.category == None:
				continue
			if channel.category_id != 1047483311703998486:
				continue

			await channel.set_permissions(member, overwrite = None)



