from discord.ext import tasks, commands
from discord import app_commands
import os
import discord
import logging
import configparser
from typing import Literal
from typing import Optional

logger = logging.getLogger('bot')

class Roles_Manager_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# Load config
		self.config = configparser.ConfigParser()
		self.config.read(os.path.dirname(__file__)+os.path.sep+'..'+os.path.sep+'config.ini')
		logger.info('Loaded Role Manager')

	# Add/remove/toggle role
	@commands.hybrid_command(description='Add or remove roles from a member. Defaults to toggle unless an action is specified.')
	async def role_manager(self, context: commands.Context, target_member: discord.Member, perm_type: Literal['speak','name'], action: Optional[Literal['add','remove']]):
		# Mod role check
		mod_role = context.guild.get_role(self.config.getint('roles','mod_perm'))
		if mod_role not in context.author.roles:
			await context.send('You do not have permission to do this.', ephemeral=True)
			logger.debug('User {context.author.name} failed mod check to change roles on {target_member.name}.')
			return

		# Get role to change
		if perm_type == 'speak':
			target_role = context.guild.get_role(self.config.getint('roles','speak_perm'))
		elif perm_type == 'name':
			target_role = context.guild.get_role(self.config.getint('roles','name_perm'))
		else:
			await context.send('Something went wrong. Please contact server owner.', ephemeral=True)
			logger.debug('Asked to change perm type for a perm that does not exist')
			return

		# Ready toggle action
		if action == None:
			if target_role not in target_member.roles:
				action = 'add'
			else:
				action = 'remove'

		try:
			# Perform role change
			if action == 'add':
				await target_member.add_roles(target_role)
				await context.send(f'Added {perm_type} role to {target_member.display_name}.', ephemeral=True)
				logger.debug(f'{context.author.name} added {perm_type} to {target_member.display_name}')
			else:
				await target_member.remove_roles(target_role)
				await context.send(f'Removed {perm_type} role from {target_member.display_name}.', ephemeral=True)
				logger.debug(f'{context.author.name} removed {perm_type} from {target_member.display_name}')
		except Exception as err:
				await context.send('Error occurred while running command. Please contact server admin.', ephemeral=True)
				logger.debug(f'Error occurred while {context.author.name} did {action} action for {perm_type} perm on {target_member.name}. Error info:\n{err}')


	# Safeword
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, member):
		if reaction.emoji.name == 'safeword':
			speak_role = member.guild.get_role(self.config.getint('roles','speak_perm'))
			name_role = member.guild.get_role(self.config.getint('roles','name_perm'))

			# event roles
			rosaflatable_role = member.guild.get_role(1119393991721492550)


			await member.add_roles(speak_role)
			await member.add_roles(name_role)
			await member.remove_roles(rosaflatable_role)
			logger.debug(f'{member.name} safeworded')

		if reaction.emoji.name == 'Rosasmile':
			# event roles
			rosaflatable_role = member.guild.get_role(1119393991721492550)

			await member.add_roles(rosaflatable_role)
			logger.debug(f'{member.name} opted-in to being a rosaflatable')
