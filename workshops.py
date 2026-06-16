# workshops.py
# Quarter/week logic, sorting, and embed building

import datetime

import discord

from config import pst, DAY_ORDER
from sheets import get_workshops


def get_current_quarter_and_week():
	"""
	Returns (year, quarter_name, week_number) based on today's date.
	Update the start dates each year as needed.
	"""
	now = datetime.datetime.now(pst)
	year = now.year

	# First Monday of each UCI quarter
	quarter_starts = {
		"Winter": datetime.date(year, 1, 4),
		"Spring": datetime.date(year, 3, 24),
		"Fall": datetime.date(year, 9, 28),
	}

	today = now.date()
	sorted_quarters = sorted(quarter_starts.items(), key=lambda x: x[1])

	for i, (name, start) in enumerate(sorted_quarters):
		next_start = sorted_quarters[i + 1][1] if i + 1 < len(sorted_quarters) else datetime.date(year, 12, 31)
		if start <= today < next_start:
			week_number = (today - start).days // 7 + 1
			return year, name, week_number

	return None, None, None  # between quarters / outside known range


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
		title=f"📅 Workshops — {quarter} {year}, Week {week}",
		color=0x2E5E8C,
	)
	if not matches:
		embed.description = f"No workshops found for {quarter} {year}, Week {week}."
		return embed

	embed.description = f"There are {len(matches)} workshops found for {quarter} {year}, Week {week}:"
	for w in matches:
		dept = str(w.get("Dept", "")).strip()
		emoji = get_dept_emoji(guild, dept)
		title = w.get("Workshop", "Untitled")
		value = f"🗓️ **{w.get('Day', '')}** at **{w.get('Time', '')}** · 📍 {w.get('Location', '')}\n{emoji} {dept}"
		link = str(w.get("Public Link", "")).strip()
		if link and link.lower() not in ("", "n/a", "tbd", "no slides provided"):
			value += f"\n🔗 [Slides / Link]({link})"
		embed.add_field(name=f"{title}", value=value, inline=False)

	embed.set_footer(text="VGDC at UCI")
	return embed
