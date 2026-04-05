"""
Start command handler
"""

from telegram import Update
from telegram.ext import ContextTypes
from services.api import get_or_create_user
from keyboards.menus import main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    get_or_create_user(
        update.effective_user.id,
        update.effective_user.first_name
    )

    await update.message.reply_text(
        "Welcome to CarBot 🚗\nChoose option:",
        reply_markup=main_menu()
    )
