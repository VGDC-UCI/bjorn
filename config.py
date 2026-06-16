# config.py
# Constants, IDs, timezone, and regex patterns for Bjorn

import zoneinfo

# Timezone
pst = zoneinfo.ZoneInfo("America/Los_Angeles")

# Server & channel IDs
VGDCServerId = 228326116270538753
ChannelLabStatus = 629369478462963722
ChannelBjornHammer = 1420871723363991673
ChannelWorkshops = 363457813608923137

# Scam detection keywords
scam_keywords_start = ["give", "giving", "offering", "sell", "selling", "join our", "handing", "handling", "gifting",
                       "for sale"]
scam_keywords = ["tutors", "macbook", "apple watch", "iphone", "i phone", "mac book", "charger", "tickets", "apple",
                 "camera", "for sale", "honda", "car", "ps4", "ps5", "xbox", "nintendo", "dm", "interested"]
# secret_lab_regex = re.compile(
# 	r"(?:[s$]\s*(?:[e3 ]\s*)+[ck]\s*[r4]\s*(?:[e3 i1]\s*)+[t7]\s*([e3 ]\s*)*\s*[l1]\s*[a@8 ]\s*[b8])", re.IGNORECASE)

# Day ordering for sorting workshops
DAY_ORDER = {
	"monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4,
	"friday": 5, "saturday": 6, "sunday": 7
}
