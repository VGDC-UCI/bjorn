# moderation.py
# Message content moderation (scam detection handling)

import discord

from nltk.stem import PorterStemmer
import re
from datetime import datetime, timedelta, date

from bot import client
from config import ChannelBjornHammer, secret_lab_regex
from moderation_config import SCAM_KEYWORDS, SCAM_THRESHOLD, NEWUSERPENALTY, TrustedRoleIds, TrustedChannelIds


async def handle_message(message):

	# Skip messages in trusted channels
	if message.channel.id in TrustedChannelIds:
		return
	
	# Skip messages sent by trusted users
	for role in message.author.roles:
		if role.id in TrustedRoleIds:
			return

	# Process message
	msg_lower = message.content.lower()
	stemmed_tokens = tokenize_and_stem(msg_lower)

	# Initialize point system
	points:int = 0

	# If the user is new, add negative penalty
	dayssincejoin = message.author.joined_at.date() - date.today()
	if dayssincejoin.days < 2:
		points += NEWUSERPENALTY

	# Intialize index
	word_table = {}

	# Retrieve scam keywords
	flags = set(SCAM_KEYWORDS)

	# Build token index of flagged scam words
	pos = 0
	for token in stemmed_tokens:
		if token in flags:
			word_table[token] = word_table[token] + [pos]
		elif token in ("everyone", "here"): #penalty for mentions
			points += 15
		pos += 1

	# perform some math
	# todo

	for key in word_table.keys():
		points += len(word_table[key][1])


	# Handle message based on points vs threshold
	if points > SCAM_THRESHOLD:
		await message.delete()
		automated_scam_response(message.created_at, message.author.id, message.channel.id, points, message.content[:1024] if message.content else None)
		return
	elif points/SCAM_THRESHOLD > 0.8:
		automated_scam_warn(message.created_at, message.author.id, message.channel.id, points/SCAM_THRESHOLD, message.content[:1024] if message.content else None)
		return

	# Quiet Lab
	if secret_lab_regex.search(message.content) is not None:
			await message.reply("I think you mean \"Quiet Lab.\"")
			return


async def tokenize_and_stem(msg:str) -> list[str]:
	stripped = re.sub(r'[^\w\s]', '', msg)
	tokens = stripped.split()
	# ps = PorterStemmer()
	# return [ps.stem(token) for token in tokens]
	return tokens

async def automated_scam_response(time:datetime, author, location,score:int, quote):
	table_channel = client.get_channel(ChannelBjornHammer)
	if table_channel:
		embed = discord.Embed(
			title="🛡️ Spam Message Removed",
			description="A suspected spam message was automatically detected and deleted.",
			color=0xE74C3C,
			timestamp=time
		)
		embed.add_field(
			name="Author",
			value=f"<@{author}>",
			inline=True
		)
		embed.add_field(
			name="Channel",
			value=f"<#{location}>",
			inline=True
		)
		embed.add_field(
			name="Reason",
			value=f"Message met spam likely threshold with a score of {score}.",
			inline=False
		)
		embed.add_field(
			name="Message Content",
			value=quote if quote!=None else "*(no text content)*",
			inline=False
		)
		embed.set_footer(text="Automated Moderation")

		await table_channel.send(
			embed=embed,
			allowed_mentions=discord.AllowedMentions.none()
		)
	return

async def automated_scam_warn(time:datetime,author,location,score:float,quote):
	table_channel = client.get_channel(ChannelBjornHammer)
	if table_channel:
		embed = discord.Embed(
			title="🛡️ Spam Message Likely",
			description="Suspected spam message found. Review requested.",
			color=0xE74C3C,
			timestamp=time
		)
		embed.add_field(
			name="Author",
			value=f"<@{author}>",
			inline=True
		)
		embed.add_field(
			name="Channel",
			value=f"<#{location}>",
			inline=True
		)
		embed.add_field(
			name="Reason",
			value=f"{score}% confident message is spam.",
			inline=False
		)
		embed.add_field(
			name="Message Content",
			value=quote if quote!=None else "*(no text content)*",
			inline=False
		)
		embed.set_footer(text="Automated Moderation")

		await table_channel.send(
			embed=embed,
			allowed_mentions=discord.AllowedMentions.none()
		)
	return


