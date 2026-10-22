
# Trusted Roles - These will be skipped over by automod
TrustedRoleIds:set[int] = ()

# Trusted Channels - These will be skipped over by automod
TrustedChannelIds:set[int] = ()

# Scam detection keywords
SCAM_KEYWORDS:set[str] = ("just upgraded", "an upgrade", "give out", "giving out", "give away",
					   "giving away", "is free", "for free", "join our", "for sale",
					   "dm me", "you are interested", "you're interested", "tutors", "macbook"
                       "iphone", "tickets", "camera", "car", "ps5", "PC", "windows")

SCAM_PAIRS = []
SCAM_THRESHOLD:int = 25

# PENALTIES
NEWUSERPENALTY:int = 8
PINGPENALTY:int = 15
