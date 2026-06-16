# commands/lab.py
# /labopen and /labclose slash commands

import discord
from discord import app_commands

from bot import command_tree
from config import VGDCServerId
from lab_state import set_lab_open


@command_tree.command(
	name="labopen",
	description="Set Game Lab status to open",
	guild=discord.Object(id=VGDCServerId)
)
@app_commands.checks.has_permissions(manage_messages=True)
async def labopen(interaction: discord.Interaction):
	await set_lab_open(True)
	await interaction.response.send_message("Game Lab is now open! ✅")


@command_tree.command(
	name="labclose",
	description="Set Game Lab status to closed",
	guild=discord.Object(id=VGDCServerId)
)
@app_commands.checks.has_permissions(manage_messages=True)
async def labclose(interaction: discord.Interaction):
	await set_lab_open(False)
	await interaction.response.send_message("Game Lab is now closed! ⛔")
