# commands/workshop_cmd.py
# /workshops slash command
import datetime

import discord
from discord import app_commands

from bot import command_tree, client
from config import VGDCServerId, pst, PREVIEW_OFFSET_WEEKS, PREVIEW_SAFE_OFFSET_WEEKS
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
	now = datetime.datetime.now(pst).date()
	as_of_date = now + datetime.timedelta(weeks=PREVIEW_OFFSET_WEEKS)

	will_be_blocked = not week_has_started(year, quarter.value, week, as_of_date)
	await interaction.response.defer(ephemeral=will_be_blocked)

	safe_as_of_date = now + datetime.timedelta(weeks=PREVIEW_SAFE_OFFSET_WEEKS)

	if not week_has_started(year, quarter.value, week, as_of_date):
		monday = get_week_start_date(year, quarter.value, week - PREVIEW_OFFSET_WEEKS)
		when = monday.strftime("%b %d, %Y") if monday else "its scheduled start date"
		await interaction.followup.send(
			f"⏳ The workshop schedule for **{quarter.value} {year}, Week {week}** isn't "
			f"available yet. It will be available by **Monday, {when}**.",
			ephemeral=True,
		)
		return

	tentative = not week_has_started(year, quarter.value, week, safe_as_of_date)

	try:
		guild = client.get_guild(VGDCServerId)
		embed = build_workshop_embed(year, quarter.value, week, guild=guild, tentative=tentative)
	except Exception as e:
		print(f"[workshops] sheet error: {e}")
		await interaction.followup.send(
			"⚠️ Something went wrong reading the workshop data. Please try again later."
		)
		return

	await interaction.followup.send(embed=embed)