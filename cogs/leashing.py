from discord.ext import tasks, commands
from discord import SyncWebhook
from discord import app_commands
import configparser
import pickle
import re
import os
import discord
import logging
from string import ascii_uppercase
#from random import randint
from random import choices
from typing import Literal
#from typing import Optional
from settings import *

logger = logging.getLogger('bot')

leash_pickle_file = os.path.dirname(__file__)+os.path.sep+'leashing.pickle'

class Leashing_Cog(commands.Cog):
	# Maps leasher to list of leashees
	leash_mapping = {}
	# Maps leasher to lsat channel spoken in
	channel_mapping = {}

	def __init__(self, bot):
		self.bot = bot
		logger.info('Loaded leashing')
		if os.path.exists(leash_pickle_file):
			with open(leash_pickle_file, 'rb') as pickle_infile:
				self.leash_mapping = pickle.load(pickle_infile)

	# Leashing command
	@commands.hybrid_command(description='Add or remove leashing (toggle).')
	async def leash(self, context: commands.Context, target_member: discord.Member):

		# Prevent leashing the bot
		if target_member.id == self.bot.user.id:
			await context.send('*limit-breaks so hard it crashes your game*')
			return


		# Permissions check
		#if context.author.id not in [1053028780383424563]:
		#	return
		if config.getint('roles','meanie_role') not in [role.id for role in context.author.roles]:
			return

		logger.info(f'{context.author.name} attempts to leash {target_member.name}')

		for leasher in self.leash_mapping.keys():
			if target_member.id in self.leash_mapping[leasher] and context.author.id != leasher:
				await context.send('This user is already leashed by someone else!')
				return
			elif target_member.id in self.leash_mapping[leasher] and context.author.id == leasher:
				await self.remove_from_leashing(target_member)
				await context.send(f'Unleashed {target_member.display_name}')
				return

		if context.author.id in self.leash_mapping.keys():
			self.leash_mapping[context.author.id].append(target_member.id)
		else:
			self.leash_mapping[context.author.id] = [target_member.id]
		await context.send(f'Successfully leashed {target_member.display_name}.')

		# Save file
		with open(leash_pickle_file, 'wb') as pickle_outfile:
			pickle.dump(self.leash_mapping, pickle_outfile)

		# Permission overwrite that deny viewing a channel
		no_perms = discord.PermissionOverwrite()
		no_perms.view_channel = False

		self.channel_mapping[context.author.id] = context.channel.id

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
	@commands.hybrid_command(description='Release all leashes you are currently holding.')
	async def unleash_all(self, context: commands.Context):
		# Check for leasher's ID
		if context.author.id not in self.leash_mapping.keys():
			await context.send(f'No users to unleash', ephemeral=True)
			return

		total_leashees = len(self.leash_mapping[context.author.id])
		# Make copy to avoid issues of leashing
		leashee_id_list = self.leash_mapping[context.author.id].copy()
		# Edit leashee's perms
		for leashee_id in leashee_id_list:
			member_obj = context.guild.get_member(leashee_id)
			# cache miss
			if member_obj == None:
				member_obj = await context.guild.fetch_member(leashee_id)
			await self.remove_from_leashing(member_obj)

		await context.send(f'Removed leash from {total_leashees} user(s)')


	# Leashing command
	@commands.hybrid_command(description='Print users you have leashed.')
	async def print_leashees(self, context: commands.Context):
		# Check for leasher's ID
		if context.author.id not in self.leash_mapping.keys():
			await context.send(f'No users currently leashed', ephemeral=True)
			return

		if len(self.leash_mapping[context.author.id]) == 0:
			await context.send(f'No users currently leashed', ephemeral=True)
			return

		leashed_users = 'Currently leashed users:\n'
		# Edit leashee's perms
		for leashee_id in self.leash_mapping[context.author.id]:
			member_obj = context.guild.get_member(leashee_id)
			# cache miss
			if member_obj == None:
				member_obj = await context.guild.fetch_member(leashee_id)
			# Append to list
			leashed_users += f'- {member_obj.display_name}\n'

		await context.send(leashed_users)


	# Run message relay
	@commands.Cog.listener()
	async def on_message(self, message):
		# Check for leasher's ID
		if message.author.id not in self.leash_mapping.keys():
			return

		# Limit API calls
		# Check for non-existent key
		if message.author.id not in self.channel_mapping.keys():
			self.channel_mapping[message.author.id] = message.channel.id
		# Check for mismatched channel
		elif message.channel.id != self.channel_mapping[message.author.id]:
			self.channel_mapping[message.author.id] = message.channel.id
		# Avoid updating perms if channel matches last channel
		else:
			return


		# DEBUG
		print('Updating channel perms')


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

		# Save file
		with open(leash_pickle_file, 'wb') as pickle_outfile:
			pickle.dump(self.leash_mapping, pickle_outfile)


		# Clear all user-specific channel restrictions
		for channel in member.guild.channels:
			# Ignore important channels
			if channel.category == None:
				continue
			if channel.category_id != 1047483311703998486:
				continue

			await channel.set_permissions(member, overwrite = None)




