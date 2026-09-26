# lab_state.py
# Shared lab-status helper (used by both commands and tasks)

import discord

from bot import client

is_lab_open = False

async def set_lab_open(is_open: bool):
	global is_lab_open
	is_lab_open = is_open
	await client.change_presence(activity=discord.CustomActivity(
		name="✅ Game Lab is OPEN" if is_open else "⛔ Game Lab is CLOSED"))
