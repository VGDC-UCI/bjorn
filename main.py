# main.py
# BJORN
# A VGDC@UCI BOT
#
# Written by Diane Sparks and Justin Li
# Bjorn (the character) by Franny (fruttipie)
#
# Entry point: wires everything together and runs the bot.

import os

from dotenv import load_dotenv

load_dotenv()

from bot import client, command_tree
import moderation
import tasks
from lab_state import set_lab_open

import commands  # noqa: F401


@client.event
async def on_ready():
	await command_tree.sync()

	await set_lab_open(False)
	if not tasks.auto_close_lab.is_running():
		tasks.auto_close_lab.start()
	if not tasks.weekly_workshop_reminder.is_running():
		tasks.weekly_workshop_reminder.start()
	print(f"Connected as {client.user.name}")


@client.event
async def on_message(message):
	if message.author.id == client.user.id:
		return
	await moderation.handle_message(message)


if __name__ == "__main__":
	token = os.getenv('DISCORD_TOKEN')
	if token is None:
		raise ValueError("DISCORD_TOKEN environment variable not set")

	client.run(token)
