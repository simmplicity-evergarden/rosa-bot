import os
import discord
import time
import logging
import settings
from typing import Optional
from random import randint

from discord.ext import tasks, commands
from discord import app_commands

# Cogs import
import cogs.common
import cogs.roles_manager
import cogs.smile_enforcer
import cogs.renamer
import cogs.speak_as_bot
import cogs.squeak_miho
import cogs.leashing
import cogs.woof_enforcer
#import cogs.webhook_manager

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!!', intents=intents)
logger = logging.getLogger('bot')

@bot.event
async def on_ready():
	logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
	logger.info('---------------------------------------------')
	await bot.add_cog(cogs.common.Common_Cog(bot))
	await bot.add_cog(cogs.roles_manager.Roles_Manager_Cog(bot))
	await bot.add_cog(cogs.smile_enforcer.Smile_Enforcer_Cog(bot))
	await bot.add_cog(cogs.renamer.Renamer_Cog(bot))
	await bot.add_cog(cogs.speak_as_bot.Speak_as_Bot_Cog(bot))
	await bot.add_cog(cogs.squeak_miho.Squeak_Miho_Cog(bot))
	await bot.add_cog(cogs.leashing.Leashing_Cog(bot))
	await bot.add_cog(cogs.woof_enforcer.WoofEnforcer_Cog(bot))
	# Webhook comes last
#	await bot.add_cog(cogs.webhook_manager.Webhook_Manager_Cog(bot))
