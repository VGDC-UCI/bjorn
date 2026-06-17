# commands/workshop_cmd.py
# /workshops slash command

import discord
from discord import app_commands

from bot import command_tree, client
from config import VGDCServerId
from workshops import build_workshop_embed, get_week_start_date, week_has_started


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

	# Block weeks that haven't started yet (before that week's Monday in PST).
	if not week_has_started(year, quarter.value, week):
		monday = get_week_start_date(year, quarter.value, week)
		when = monday.strftime("%b %d, %Y") if monday else "its scheduled start date"
		await interaction.response.send_message(
			f"⏳ The workshop schedule for **{quarter.value} {year}, Week {week}** isn't "
			f"available yet. It will be available by **Monday, {when}**.",
			ephemeral=True,
		)
		return

	# Defer in case the Google Sheets call takes a moment
	await interaction.response.defer()

	try:
		guild = client.get_guild(VGDCServerId)
		embed = build_workshop_embed(year, quarter.value, week, guild=guild)
	except Exception as e:
		print(f"[workshops] sheet error: {e}")
		await interaction.followup.send(
			"⚠️ Something went wrong reading the workshop data. Please try again later."
		)
		return

	await interaction.followup.send(embed=embed)
