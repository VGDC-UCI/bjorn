# BJORN
# A VGDC@UCI BOT

# Written by Diane Sparks
# Bjorn (the character) by Franny (fruttipie)

import discord
from discord import app_commands
from discord.ext import tasks

import re
import datetime

# //////////////////////////////////////////////////////////////////////////////

VgdcServerId = 228326116270538753
TestServerId = 1393079029589999739
ChannelLabStatus = 629369478462963722
ChannelTableLackers = 361379365134663691

TokenFile = "token.txt"

scam_keywords_start = ["give", "giving", "offering", "selling", "join our"]
scam_keywords = ["tutors", "macbook", "mac book", "charger", "tickets", "iphone", "apple"]

secret_lab_regex = re.compile(r"(?:[s$]\s*(?:[e3 ]\s*)+[ck]\s*[r4]\s*(?:[e3 i1]\s*)+[t7]\s*([e3 ]\s*)*\s*[l1]\s*[a@8 ]\s*[b8])", re.IGNORECASE)

# //////////////////////////////////////////////////////////////////////////////

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
command_tree = app_commands.CommandTree(client)

# //////////////////////////////////////////////////////////////////////////////

async def set_lab_open(is_open: bool):
	await client.change_presence(activity=discord.CustomActivity(name=f"{'✅' if is_open else '⛔'} Game Lab is {'OPEN' if is_open else 'CLOSED'}"))

@client.event
async def on_ready():
	await command_tree.sync(guild=discord.Object(id=VgdcServerId))
	await set_lab_open(False)
	auto_close_lab.start()
	print(f"Connected as {client.user.name}")

@client.event
async def on_message(message: discord.Message):
	if message.author.id == client.user.id:
		return

	if True:
		msg_lower = message.content.lower()
		if any(word in msg_lower for word in scam_keywords_start) and any(word in msg_lower for word in scam_keywords):
			#await message.reply(f"I just automatically removed a message that contained phrases we've recently seen in malicious messages. If this is a mistake, please DM one of the programming officers.\nMessage sent by: <@{message.author.id}>", mention_author=True)
			await message.delete()
			#await message.author.timeout(datetime.timedelta(seconds=15), reason="Suspected spam")
			table_channel = client.get_channel(ChannelTableLackers)
			await table_channel.send(f"I just automatically removed a suspected spam message from <@{message.author.id}> in <#{message.channel.id}>\nMessage: {message.content}")
			return

	if secret_lab_regex.search(message.content) != None:
		await message.reply("I think you mean \"Quiet Lab.\"")
		return

@command_tree.command(
	name="labopen",
	description="Set Game Lab status to open",
	guild=discord.Object(id=VgdcServerId)
)
async def labopen(interaction: discord.Interaction):
	await set_lab_open(True)
	await interaction.response.send_message("Game Lab is now open! ✅")

@command_tree.command(
	name="labclose",
	description="Set Game Lab status to closed",
	guild=discord.Object(id=VgdcServerId)
)
async def labclose(interaction: discord.Interaction):
	await set_lab_open(False)
	await interaction.response.send_message("Game Lab is now closed! ⛔")

@tasks.loop(time=datetime.time(hour=5))
async def auto_close_lab():
	await set_lab_open(False)

if __name__ == "__main__":
	token_file = open(TokenFile, "r")
	token = token_file.readline()
	token_file.close()

	client.run(token)
