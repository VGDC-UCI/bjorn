# tasks.py
# Scheduled background tasks

import datetime

from discord.ext import tasks

import lab_state
from bot import client
from config import pst, ChannelLabStatus, ChannelWorkshops, VGDCServerId
from lab_state import set_lab_open
from workshops import get_current_quarter_and_week, get_workshops_for, build_workshop_embed


# Automatically close at midnight
@tasks.loop(time=datetime.time(hour=0, tzinfo=pst))
async def auto_close_lab():
	if not lab_state.is_lab_open:
		return
	await set_lab_open(False)
	channel = client.get_channel(ChannelLabStatus)
	await channel.send("Midnight: Game Lab automatically closed.")


@tasks.loop(time=datetime.time(hour=7, tzinfo=pst))
async def weekly_workshop_reminder():
	# Only run on Mondays
	if datetime.datetime.now(pst).weekday() != 0:
		return

	# Determine what quarter/week it currently is
	year, quarter, week = get_current_quarter_and_week()

	if not year or not quarter or not week:
		return

	# Get this week's workshops
	try:
		ws = get_workshops_for(year, quarter, week)
	except Exception as e:
		print(f"[weekly_workshop_reminder] Error reading sheet: {e}")
		return

	if not ws:
		return

	channel = client.get_channel(ChannelWorkshops)
	if not channel:
		return

	# Build and send the styled embed
	# Pass the VGDC guild so department custom emojis resolve correctly
	guild = client.get_guild(VGDCServerId)
	embed = build_workshop_embed(year, quarter, week, guild=guild)

	# Don't send a reminder if no workshops exist (eg: during summer)
	if len(embed.fields) <= 1:
		return

	await channel.send(embed=embed)
