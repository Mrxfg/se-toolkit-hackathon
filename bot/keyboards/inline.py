"""
Inline keyboard markups for the bot
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def brand_list(brands):
    """Create inline keyboard for brand selection"""
    keyboard = [[InlineKeyboardButton(b, callback_data=f"brand_{b}")] for b in brands]
    keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)


def car_actions(car_id):
    """Create inline keyboard for car actions (edit/delete)"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{car_id}"),
            InlineKeyboardButton("❌ Delete", callback_data=f"delete_{car_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def delete_confirmation(car_id):
    """Create inline keyboard for delete confirmation"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, delete", callback_data=f"confirm_delete_{car_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def edit_menu():
    """Create inline keyboard for edit field selection"""
    keyboard = [
        [InlineKeyboardButton("🚗 Brand", callback_data="editfield_make")],
        [InlineKeyboardButton("📝 Model", callback_data="editfield_model")],
        [InlineKeyboardButton("📅 Year", callback_data="editfield_year")],
        [InlineKeyboardButton("💰 Price", callback_data="editfield_price")],
        [InlineKeyboardButton("📏 Mileage", callback_data="editfield_mileage")],
        [InlineKeyboardButton("📄 Description", callback_data="editfield_description")],
        [InlineKeyboardButton("📍 Location", callback_data="editfield_location")],
        [InlineKeyboardButton("✅ Save Changes", callback_data="editsave")],
        [InlineKeyboardButton("❌ Cancel", callback_data="editcancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def pagination_buttons(query, page, has_more):
    """Create pagination buttons"""
    keyboard = []
    nav_buttons = []

    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page_{query}_{page-1}"))

    if has_more:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{query}_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard) if keyboard else None


def search_pagination_buttons(query, page, has_more):
    """Create pagination buttons for search results"""
    keyboard = []
    nav_buttons = []

    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"search_page_{query}_{page-1}"))

    if has_more:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"search_page_{query}_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard) if keyboard else None
