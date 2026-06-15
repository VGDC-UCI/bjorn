# BJORN
# A VGDC@UCI BOT

# Written by Diane Sparks
# Bjorn (the character) by Franny (fruttipie)

import os
import discord
from discord import app_commands
from discord.ext import tasks

import re
import datetime
import zoneinfo


# //////////////////////////////////////////////////////////////////////////////

pst = zoneinfo.ZoneInfo("America/Los_Angeles")

VGDCServerId = 228326116270538753
TestServerId = 1393079029589999739
ChannelLabStatus = 629369478462963722
ChannelBjornHammer = 1420871723363991673

scam_keywords_start = ["give", "giving", "offering", "sell", "selling", "join our", "handing", "handling", "gifting",
                       "for sale"]
scam_keywords = ["tutors", "macbook", "apple watch", "iphone", "i phone", "mac book", "charger", "tickets", "apple",
                 "camera", "for sale", "honda", "car", "ps4", "ps5", "xbox", "nintendo", "dm", "interested"]

secret_lab_regex = re.compile(
	r"(?:[s$]\s*(?:[e3 ]\s*)+[ck]\s*[r4]\s*(?:[e3 i1]\s*)+[t7]\s*([e3 ]\s*)*\s*[l1]\s*[a@8 ]\s*[b8])", re.IGNORECASE)

# //////////////////////////////////////////////////////////////////////////////

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
command_tree = app_commands.CommandTree(client)


# //////////////////////////////////////////////////////////////////////////////

async def set_lab_open(is_open: bool):
	await client.change_presence(activity=discord.CustomActivity(
		name="✅ Game Lab is OPEN" if is_open else "⛔ Game Lab is CLOSED"))


@client.event
async def on_ready():
	await command_tree.sync(guild=discord.Object(id=VGDCServerId))
	await set_lab_open(False)
	auto_close_lab.start()
	print(f"Connected as {client.user.name}")


@client.event
async def on_message(message: discord.Message):
	if message.author.id == client.user.id:
		return

	msg_lower = message.content.lower()
	if ("everyone" in msg_lower or "here" in msg_lower) and any(
			word in msg_lower for word in scam_keywords_start) and any(word in msg_lower for word in scam_keywords):
		#await message.reply(f"I just automatically removed a message that contained phrases we've recently seen in malicious messages. If this is a mistake, please DM one of the programming officers.\nMessage sent by: <@{message.author.id}>", mention_author=True)
		await message.delete()
		#await message.author.timeout(datetime.timedelta(seconds=15), reason="Suspected spam")
		table_channel = client.get_channel(ChannelBjornHammer)
		if table_channel:
			await table_channel.send(
				f"I just automatically removed a suspected spam message from <@{message.author.id}> in <#{message.channel.id}>\nMessage: {message.content.replace('everyone', '/everyone').replace('here', '/here')}")
		return

	if secret_lab_regex.search(message.content) is not None:
		await message.reply("I think you mean \"Quiet Lab.\"")
		return


def is_in_lab_status(interaction: discord.Interaction) -> bool:
	return interaction.channel.id == ChannelLabStatus


@command_tree.command(
	name="labopen",
	description="Set Game Lab status to open",
	guild=discord.Object(id=VGDCServerId)
)
@app_commands.check(is_in_lab_status)
async def labopen(interaction: discord.Interaction):
	await set_lab_open(True)
	await interaction.response.send_message("Game Lab is now open! ✅")


@command_tree.command(
	name="labclose",
	description="Set Game Lab status to closed",
	guild=discord.Object(id=VGDCServerId)
)
@app_commands.check(is_in_lab_status)
async def labclose(interaction: discord.Interaction):
	await set_lab_open(False)
	await interaction.response.send_message("Game Lab is now closed! ⛔")


# Automatically close at 21:00 (9 PM)
@tasks.loop(time=datetime.time(hour=21, tzinfo=pst))
async def auto_close_lab():
	await set_lab_open(False)
	channel = client.get_channel(ChannelLabStatus)
	await channel.send("9PM: Game Lab automatically closed.")


if __name__ == "__main__":
	token = os.getenv('DISCORD_TOKEN')
	if token is None:
		raise ValueError("DISCORD_TOKEN environment variable not set")

	client.run(token)
