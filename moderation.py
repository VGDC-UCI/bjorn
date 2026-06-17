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

		# Capture the first matched word from each list
		matched_start = next((word for word in scam_keywords_start if word in msg_lower), None)
		matched_keyword = next((word for word in scam_keywords if word in msg_lower), None)
		matched_mention = "@everyone" if "everyone" in msg_lower else "@here"

		table_channel = client.get_channel(ChannelBjornHammer)
		if table_channel:
			embed = discord.Embed(
				title="🛡️ Spam Message Removed",
				description="A suspected spam message was automatically detected and deleted.",
				color=0xE74C3C,
				timestamp=message.created_at
			)
			embed.add_field(
				name="Author",
				value=f"<@{message.author.id}>",
				inline=True
			)
			embed.add_field(
				name="Channel",
				value=f"<#{message.channel.id}>",
				inline=True
			)
			embed.add_field(
				name="Reason",
				value=(
					f"Mention: `{matched_mention}`\n"
					f"Start keyword: `{matched_start}`\n"
					f"Scam keyword: `{matched_keyword}`"
				),
				inline=False
			)
			embed.add_field(
				name="Message Content",
				value=message.content[:1024] if message.content else "*(no text content)*",
				inline=False
			)
			embed.set_footer(text="Automated Moderation")

			await table_channel.send(
				embed=embed,
				allowed_mentions=discord.AllowedMentions.none()
			)
		return

# if secret_lab_regex.search(message.content) is not None:
# 	await message.reply("I think you mean \"Quiet Lab.\"")
# 	return
