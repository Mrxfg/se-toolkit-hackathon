"""
Conversation states for the bot
"""

# Sell flow states
MAKE, MODEL, YEAR, PRICE, MILEAGE, DESC, LOCATION, PHOTOS = range(8)

# Edit flow states
EDIT_FIELD_SELECT, EDIT_VALUE_INPUT = range(8, 10)

# Search flow state
SEARCH_INPUT = 10

# Message flow state
MESSAGE_INPUT = 11
