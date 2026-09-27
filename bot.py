# bot.py
# Shared client and command tree instances

import discord
from discord import app_commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
command_tree = app_commands.CommandTree(client)
