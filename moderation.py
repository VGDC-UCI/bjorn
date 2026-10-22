# moderation.py
# Message content moderation (scam detection handling)

import discord

from nltk.stem import PorterStemmer
import re

from bot import client
from config import SCAM_KEYWORDS, SCAM_THRESHOLD, ChannelBjornHammer, secret_lab_regex


async def handle_message(message):
	msg_lower = message.content.lower()
	stemmed_tokens = tokenize_and_stem(msg_lower)

	points:int = 0
	word_table = {}

	flags = set(SCAM_KEYWORDS)

	pos = 0
	for token in stemmed_tokens:
		if token in flags:
			word_table[token] = word_table[token] + [pos]
		pos += 1

	# perform some math
	# todo

	if points > SCAM_THRESHOLD:
		await message.delete()

	if secret_lab_regex.search(message.content) is not None:
		await message.reply("I think you mean \"Quiet Lab.\"")
		return


async def tokenize_and_stem(msg:str) -> list[str]:
	stripped = re.sub(r'[^\w\s]', '', msg)
	tokens = stripped.split()
	ps = PorterStemmer()
	return [ps.stem(token) for token in tokens]

