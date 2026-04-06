"""
Reply keyboard markups for the bot
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    """Main menu keyboard"""
    keyboard = [
        ["Sell 🚗", "Listings 📋"],
        ["Search 🔍", "My Cars 👤"],
        ["Inbox 📬"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def brand_selection():
    """Brand selection keyboard"""
    keyboard = [
        ["Toyota", "BMW"],
        ["Mercedes", "Opel"],
        ["Other"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def location_keyboard():
    """Location request keyboard"""
    button = KeyboardButton("Send location 📍", request_location=True)
    keyboard = [[button]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def post_add_menu():
    """Menu shown after adding a car"""
    keyboard = [
        ["➕ Add another car"],
        ["📋 View listings", "👤 My cars"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def post_edit_menu():
    """Menu shown after editing a car"""
    keyboard = [
        ["📋 View listings", "👤 My cars"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
