# config.py
# Constants, IDs, timezone, and regex patterns for Bjorn

import datetime
import re
import zoneinfo

# Timezone
pst = zoneinfo.ZoneInfo("America/Los_Angeles")

# Server & channel IDs
VGDCServerId = 228326116270538753
ChannelLabStatus = 629369478462963722
ChannelBjornHammer = 1420871723363991673
ChannelWorkshops = 363457813608923137
ModerationChannelWhitelist = [
	639931618051489792,     # announcements
	363457813608923137,     # workshops
	657357663574818836,     # promotions
	583438712445206555,     # meeting-slides
]

# Scam detection keywords
scam_keywords_start = ["give", "giving", "offering", "sell", "join our", "handing", "handling", "gift",
                       "for sale", "dm", "interested"]
scam_keywords = ["tutors", "macbook", "apple watch", "iphone", "i phone", "mac book", "charger", "tickets", "apple",
                 "camera", "honda", "car", "ps4", "ps5", "xbox", "nintendo"]
secret_lab_regex = re.compile(
	r"(?:[s$]\s*(?:[e3 ]\s*)+[ck]\s*[r4]\s*(?:[e3 i1]\s*)+[t7]\s*([e3 ]\s*)*\s*[l1]\s*[a@8 ]\s*[b8])", re.IGNORECASE)

# Day ordering for sorting workshops
DAY_ORDER = {
	"monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4,
	"friday": 5, "saturday": 6, "sunday": 7
}

# UCI quarter start dates (the Monday that begins Week 1).
# Add a new entry each academic year as the dates are published.
QUARTER_STARTS = {
	2023: {
		"Winter": datetime.date(2023, 1, 9),
		"Spring": datetime.date(2023, 4, 3),
		"Fall": datetime.date(2023, 10, 2),
	},
	2024: {
		"Winter": datetime.date(2024, 1, 8),
		"Spring": datetime.date(2024, 4, 1),
		"Fall": datetime.date(2024, 9, 30),
	},
	2025: {
		"Winter": datetime.date(2025, 1, 6),
		"Spring": datetime.date(2025, 3, 31),
		"Fall": datetime.date(2025, 9, 29),
	},
	2026: {
		"Winter": datetime.date(2026, 1, 5),
		"Spring": datetime.date(2026, 3, 30),
		"Fall": datetime.date(2026, 9, 28),
	},
	2027: {
		"Winter": datetime.date(2026, 1, 4),
		"Spring": datetime.date(2026, 3, 29),
		"Fall": datetime.date(2026, 9, 27),  # edit when this comes out
	},
}
