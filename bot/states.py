"""
Conversation states for the bot
"""

# Sell flow states
MAKE, MODEL, YEAR, PRICE, MILEAGE, DESC, LOCATION = range(7)

# Edit flow states
EDIT_FIELD_SELECT, EDIT_VALUE_INPUT = range(7, 9)

# Search flow state
SEARCH_INPUT = 9
