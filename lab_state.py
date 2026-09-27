# lab_state.py
# Shared lab-status helper (used by both commands and tasks)

import discord

from bot import client
from config import ChannelLabOpenVC

is_lab_open = False

async def set_lab_open(is_open: bool):
	global is_lab_open
	is_lab_open = is_open

	new_status = "✅ Game Lab is OPEN" if is_open else "⛔ Game Lab is CLOSED"
	await client.change_presence(activity=discord.CustomActivity(name=new_status))

	lab_open_channel = client.get_channel(ChannelLabOpenVC)
	if lab_open_channel.name != new_status:
		await lab_open_channel.edit(name=new_status)