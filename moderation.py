# moderation.py
# Message content moderation (scam detection handling)

import discord

from bot import client
from config import scam_keywords_start, scam_keywords, ChannelBjornHammer


async def handle_message(message):
	msg_lower = message.content.lower()
	if ("everyone" in msg_lower or "here" in msg_lower) and any(
			word in msg_lower for word in scam_keywords_start) and any(word in msg_lower for word in scam_keywords):
		await message.delete()
		table_channel = client.get_channel(ChannelBjornHammer)
		if table_channel:
			await table_channel.send(
				f"I just automatically removed a suspected spam message from <@{message.author.id}> in <#{message.channel.id}>\nMessage: {message.content}",
				allowed_mentions=discord.AllowedMentions.none())
		return

# if secret_lab_regex.search(message.content) is not None:
# 	await message.reply("I think you mean \"Quiet Lab.\"")
# 	return
