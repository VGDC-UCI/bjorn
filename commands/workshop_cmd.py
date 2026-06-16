# commands/workshop_cmd.py
# /workshops slash command

import discord
from discord import app_commands

from bot import command_tree, client
from config import VGDCServerId
from workshops import build_workshop_embed


@command_tree.command(
	name="workshops",
	description="Show workshops for a given year, quarter, and week",
)
@app_commands.describe(
	year="The year (2023–2026)",
	quarter="The quarter",
	week="The week number (1–10)"
)
@app_commands.choices(quarter=[
	app_commands.Choice(name="Fall", value="Fall"),
	app_commands.Choice(name="Winter", value="Winter"),
	app_commands.Choice(name="Spring", value="Spring"),
])
async def workshops(
		interaction: discord.Interaction,
		year: app_commands.Range[int, 2023, 2026],
		quarter: app_commands.Choice[str],
		week: app_commands.Range[int, 1, 10]
):
	# Defer in case the Google Sheets call takes a moment
	await interaction.response.defer()

	try:
		guild = client.get_guild(VGDCServerId)
		embed = build_workshop_embed(year, quarter.value, week, guild=guild)
	except Exception as e:
		print(f"[workshops] sheet error: {e}")  # full detail in your logs
		# await interaction.followup.send("⚠️ Something went wrong reading the workshop data. Please try again later.")
		return

	await interaction.followup.send(embed=embed)
