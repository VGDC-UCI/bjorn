# workshops.py
# Quarter/week logic, sorting, and embed building

import datetime

import discord

from config import pst, DAY_ORDER, QUARTER_STARTS
from sheets import get_workshops

# ---------------------------------------------------------------------------
# Hidden refresh tag
#
# The footer needs to stash the year/quarter/week so /refresh can recover them
# regardless of how the human-facing footer is worded. Rather than show a
# technical token to members, the data is encoded in a refresh tag in zero-width
# characters that is invisible in Discord but easy to decode here.
# ---------------------------------------------------------------------------

_ZW_PREFIX = "\u2060"  # word joiner        -> "payload starts here"
_ZW_ZERO = "\u200b"  # zero-width space     -> bit 0
_ZW_ONE = "\u200c"  # zero-width non-joiner -> bit 1


def _encode_refresh_tag(year, quarter, week) -> str:
	"""Encode (year, quarter, week) into an invisible zero-width string."""
	payload = f"{year}|{quarter}|{week}"
	bits = "".join(format(byte, "08b") for byte in payload.encode("utf-8"))
	encoded = "".join(_ZW_ONE if bit == "1" else _ZW_ZERO for bit in bits)
	return _ZW_PREFIX + encoded


def parse_refresh_tag(embed: discord.Embed):
	"""
	Recover (year, quarter, week) from a workshop embed's footer tag.
	Returns (None, None, None) if the tag can't be found/parsed.
	"""
	if not embed or not embed.footer or not embed.footer.text:
		return None, None, None

	text = embed.footer.text
	start = text.find(_ZW_PREFIX)
	if start == -1:
		return None, None, None

	bits = []
	for ch in text[start + 1:]:
		if ch == _ZW_ZERO:
			bits.append("0")
		elif ch == _ZW_ONE:
			bits.append("1")
		else:
			break  # ran off the end of the payload

	if not bits or len(bits) % 8 != 0:
		return None, None, None

	try:
		byte_values = [
			int("".join(bits[i:i + 8]), 2) for i in range(0, len(bits), 8)
		]
		payload = bytes(byte_values).decode("utf-8")
		year_str, quarter, week_str = payload.split("|")
		return int(year_str), quarter.capitalize(), int(week_str)
	except (ValueError, UnicodeDecodeError):
		return None, None, None


def get_week_start_date(year: int, quarter: str, week):
	"""
	Return the Monday that begins the given (year, quarter, week),
	or None if the quarter name isn't recognized.
	"""
	starts = QUARTER_STARTS.get(int(year))
	if not starts:
		return None
	start = starts.get(quarter.strip().capitalize())
	if start is None:
		return None
	return start + datetime.timedelta(weeks=int(float(week)) - 1)


def week_has_started(year, quarter, week) -> bool:
	"""True only if today (PST) is on or after that week's Monday.
	If the year/quarter isn't in the table, fail open (return True)."""
	monday = get_week_start_date(year, quarter, week)
	if monday is None:
		return True
	return datetime.datetime.now(pst).date() >= monday


def get_current_quarter_and_week():
	now = datetime.datetime.now(pst)
	year = now.year

	quarter_starts = QUARTER_STARTS.get(year)
	if not quarter_starts:
		return None, None, None  # year not configured yet

	today = now.date()
	sorted_quarters = sorted(quarter_starts.items(), key=lambda x: x[1])

	for i, (name, start) in enumerate(sorted_quarters):
		next_start = (sorted_quarters[i + 1][1]
		              if i + 1 < len(sorted_quarters)
		              else datetime.date(year, 12, 31))
		if start <= today < next_start:
			week_number = (today - start).days // 7 + 1
			return year, name, week_number

	return None, None, None


def _normalize_week(value):
	"""Return the week as a float if it's numeric, otherwise a stripped string."""
	try:
		return float(value)
	except (ValueError, TypeError):
		return str(value).strip()


def get_workshops_for(year: int, quarter: str, week):
	ws = get_workshops()
	matches = []

	target_week = _normalize_week(week)

	acceptable = {target_week}
	if isinstance(target_week, float) and target_week.is_integer():
		acceptable.add(target_week + 0.5)

	for w in ws:
		# Skip empty or incomplete rows (blank Year or Wk)
		if not str(w.get('Year', '')).strip() or not str(w.get('Wk', '')).strip():
			continue

		# Convert the year
		try:
			row_year = int(float(w['Year']))
		except (ValueError, TypeError):
			continue

		row_week = _normalize_week(w['Wk'])

		if (row_year == int(year)
				and str(w['Qtr']).strip().lower() == quarter.strip().lower()
				and row_week in acceptable):
			matches.append(w)

	return matches


def parse_time(time_str):
	"""Convert '1:00 PM' into a sortable (hour, minute) tuple. Unknown times sort last."""
	try:
		t = datetime.datetime.strptime(str(time_str).strip(), "%I:%M %p")
		return t.hour, t.minute
	except (ValueError, TypeError):
		return 99, 99  # TBD / blank times go to the end


def sort_workshops(ws):
	return sorted(
		ws,
		key=lambda w: (
			DAY_ORDER.get(str(w.get("Day", "")).strip().lower(), 99),
			parse_time(w.get("Time", ""))
		)
	)


def get_dept_emoji(guild: discord.Guild, dept: str) -> str:
	# Map each department to its corresponding mascot
	custom_names = {
		"Design": "Bongo",
		"Programming": "Syntax",
		"Production": "Kanban_Cool",
		"Writing": "Shelley",
		"Art 3D": "Stylus",
		"Art 2D": "Stylus",
		"Audio": "Plop",
		"UI/UX": "Uli",
		"Strike": "Bjorn",
	}
	# Fallback Unicode emojis if mascot is not found
	fallback = {
		"Design": "⚙️", "Programming": "💻", "Production": "📈",
		"Writing": "✍️", "Art 3D": "🧊", "Art 2D": "🖌️",
		"Audio": "🎵", "UI/UX": "📱", "Strike": "🐸",
	}

	name = custom_names.get(dept)
	if name and guild:
		emoji = discord.utils.get(guild.emojis, name=name)
		if emoji:
			return str(emoji)  # renders as <:name:id> automatically

	return fallback.get(dept, "📌")


def build_workshop_embed(year, quarter, week, guild=None):
	matches = sort_workshops(get_workshops_for(year, quarter, week))
	embed = discord.Embed(
		title=f"📅 Workshops for {quarter} {year}, Week {week}",
		color=0xD2FF5E,
	)

	# User-friendly, readable footer. The refresh data is appended as an
	# invisible zero-width tag that /refresh can still decode.
	now = datetime.datetime.now(pst)
	updated = now.strftime("%b %d, %Y at ") + now.strftime("%I:%M %p").lstrip("0")
	footer_text = (
		f"VGDC at UCI \u00A0•\u00A0 Last updated {updated}"
		f"{_encode_refresh_tag(year, quarter, week)}"
	)

	if not matches:
		embed.description = f"No workshops found for {quarter} {year}, Week {week}."
		embed.set_footer(text=footer_text)
		return embed

	embed.description = f"Bjorn found {len(matches)} workshops:"
	for w in matches:
		dept = str(w.get("Dept", "")).strip()
		emoji = get_dept_emoji(guild, dept)
		title = w.get("Workshop", "Untitled")
		value = f"🗓️ **{w.get('Day', '')}** at **{w.get('Time', '')}** \u00A0•📍 {w.get('Location', '')}\n{emoji} {dept}"
		link = str(w.get("Public Link", "")).strip()
		if link and link.lower() not in ("", "n/a", "tbd", "no slides provided"):
			value += f"\n🔗 [Slides / Link]({link})"
		embed.add_field(name=f"{title}", value=value, inline=False)

	embed.set_footer(text=footer_text)
	return embed
