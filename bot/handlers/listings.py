"""
Listings handler
"""

from telegram import Update
from telegram.ext import ContextTypes
from services.api import get_brands
from keyboards.inline import brand_list


async def listings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show car listings by brand"""
    try:
        brands = get_brands()

        await update.message.reply_text(
            "Choose brand:",
            reply_markup=brand_list(brands)
        )
    except Exception as e:
        await update.message.reply_text("Error loading brands ❌")
