# commands/refresh_cmd.py
# /refresh slash command
# re-fetches sheet data and edits an existing embed message

import discord
from discord import app_commands

from bot import command_tree, client
from config import VGDCServerId
from workshops import (
	build_workshop_embed,
	parse_refresh_tag,
	get_week_start_date,
	week_has_started,
)


@command_tree.command(
	name="refresh",
	description="Re-fetch workshop data and update an existing embed message",
)
@app_commands.describe(
	message_id="The ID of the embed message to refresh",
	channel="The channel the message is in",
	year="The year (2023–2026). Defaults to the value in the embed.",
	quarter="The quarter. Defaults to the value in the embed.",
	week="The week number (1–10). Defaults to the value in the embed.",
)
@app_commands.choices(quarter=[
	app_commands.Choice(name="Fall", value="Fall"),
	app_commands.Choice(name="Winter", value="Winter"),
	app_commands.Choice(name="Spring", value="Spring"),
])
async def refresh(
		interaction: discord.Interaction,
		message_id: str,
		channel: discord.TextChannel,
		year: app_commands.Range[int, 2023, 2026] = None,
		quarter: app_commands.Choice[str] = None,
		week: app_commands.Range[int, 1, 10] = None,
):
	# Defer in case the Google Sheets call / message fetch takes a moment
	await interaction.response.defer(ephemeral=True)

	try:
		msg_id = int(message_id.strip())
	except (ValueError, AttributeError):
		await interaction.followup.send(
			"⚠️ That doesn't look like a valid message ID.", ephemeral=True
		)
		return

	# Require "Manage Messages" on the *target* channel. permissions_for()
	# accounts for the member's roles plus any channel-specific overwrites.
	member = channel.guild.get_member(interaction.user.id) or interaction.user
	if not channel.permissions_for(member).manage_messages:
		await interaction.followup.send(
			f"⛔ You need the **Manage Messages** permission in "
			f"{channel.mention} to refresh messages there.",
			ephemeral=True,
		)
		return

	# Fetch the message to refresh.
	try:
		message = await channel.fetch_message(msg_id)
	except discord.NotFound:
		await interaction.followup.send(
			f"⚠️ Couldn't find a message with ID `{msg_id}` in {channel.mention}.",
			ephemeral=True,
		)
		return
	except discord.Forbidden:
		await interaction.followup.send(
			f"⚠️ I don't have permission to read messages in {channel.mention}.",
			ephemeral=True,
		)
		return
	except discord.HTTPException as e:
		print(f"[refresh] fetch error: {e}")
		await interaction.followup.send(
			"⚠️ Something went wrong fetching that message. Please try again later.",
			ephemeral=True,
		)
		return

	# Make sure it's actually a message Bjorn sent.
	if message.author.id != client.user.id:
		await interaction.followup.send(
			"⚠️ I can only refresh messages that I sent myself.", ephemeral=True
		)
		return

	# Pull defaults out of the existing embed's footer tag.
	existing_embed = message.embeds[0] if message.embeds else None
	embed_year, embed_quarter, embed_week = parse_refresh_tag(existing_embed)

	# Any argument that's omitted falls back to the value from the embed.
	resolved_year = year if year is not None else embed_year
	resolved_quarter = quarter.value if quarter is not None else embed_quarter
	resolved_week = week if week is not None else embed_week

	if resolved_year is None or resolved_quarter is None or resolved_week is None:
		await interaction.followup.send(
			"⚠️ Couldn't read the year/quarter/week from that message's embed. "
			"Please pass `year`, `quarter`, and `week` explicitly.",
			ephemeral=True,
		)
		return

	# Block refreshing to a week that hasn't started yet. Leave the message
	# untouched so a future week can't clobber a currently-valid embed.
	if not week_has_started(resolved_year, resolved_quarter, resolved_week):
		monday = get_week_start_date(resolved_year, resolved_quarter, resolved_week)
		when = monday.strftime("%b %d, %Y") if monday else "its scheduled start date"
		await interaction.followup.send(
			f"⏳ Can't refresh to **{resolved_quarter} {resolved_year}, "
			f"Week {resolved_week}** yet because that week starts **Monday, {when}**. "
			f"The message was left unchanged.",
			ephemeral=True,
		)
		return

	# Rebuild the embed from fresh sheet data.
	try:
		guild = client.get_guild(VGDCServerId)
		embed = build_workshop_embed(
			resolved_year, resolved_quarter, resolved_week, guild=guild
		)
	except Exception as e:
		print(f"[refresh] sheet error: {e}")
		await interaction.followup.send(
			"⚠️ Something went wrong reading the workshop data. Please try again later.",
			ephemeral=True,
		)
		return

	# Edit the existing message in place.
	try:
		await message.edit(embed=embed)
	except discord.HTTPException as e:
		print(f"[refresh] edit error: {e}")
		await interaction.followup.send(
			"⚠️ Something went wrong updating the message. Please try again later.",
			ephemeral=True,
		)
		return

	await interaction.followup.send(
		f"✅ Refreshed workshops for **{resolved_quarter} {resolved_year}, "
		f"Week {resolved_week}** in {channel.mention}.",
		ephemeral=True,
	)
