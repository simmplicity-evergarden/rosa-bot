from discord.ext import tasks, commands
from discord import app_commands
import os
import discord
import logging
import configparser
from typing import Literal
from typing import Optional

logger = logging.getLogger('bot')

class Renamer_Cog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# Load config
		self.config = configparser.ConfigParser()
		self.config.read(os.path.dirname(__file__)+os.path.sep+'..'+os.path.sep+'config.ini')
		logger.info('Loaded Renamer')

	# Add/remove/toggle role
	@commands.hybrid_command(description='Change a member\'s nickname.')
	async def rename(self, context: commands.Context, target_member: discord.Member, nickname: str):
		# Mod role check
		mod_role = context.guild.get_role(self.config.getint('roles','mod_perm'))
		if mod_role not in context.author.roles:
			await context.send('You do not have permission to do this.', ephemeral=True)
			logger.info(f'User {context.author.name} failed mod check to change roles on {target_member.name}.')
			return

		if len(nickname) > 32:
			await context.send('Nicknames can only be a maximum of 32 characters', ephemeral=True)
			logger.info(f'Nickname {nickname} is too long.')
			return

		await target_member.edit(nick=nickname)
		await context.send('Success!', ephemeral=True)
		logger.info(f'Changed {target_member.display_name}\'s nickname to {nickname}.')
		return

