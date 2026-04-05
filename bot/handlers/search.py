"""
Search handler
"""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from services.api import search_cars
from keyboards.inline import search_pagination_buttons
from states import SEARCH_INPUT


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command"""
    if not context.args:
        await update.message.reply_text("Usage: /search toyota")
        return

    q = " ".join(context.args)
    try:
        cars = search_cars(q, limit=5, offset=0)

        if not cars:
            await update.message.reply_text("No results ❌")
            return

        text = "\n\n".join([
            f"🚗 {c['make']} {c['model']}\n💰 ${c['price']}"
            for c in cars
        ])

        # Pagination buttons
        keyboard = search_pagination_buttons(q, 0, len(cars) == 5)

        if keyboard:
            await update.message.reply_text(text, reply_markup=keyboard)
        else:
            await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text("Error searching cars ❌")


async def search_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search input from conversation"""
    q = update.message.text

    try:
        cars = search_cars(q, limit=5, offset=0)

        if not cars:
            await update.message.reply_text("No results ❌")
            return ConversationHandler.END

        text = "\n\n".join([
            f"🚗 {c['make']} {c['model']}\n💰 ${c['price']}"
            for c in cars
        ])

        # Pagination buttons
        keyboard = search_pagination_buttons(q, 0, len(cars) == 5)

        if keyboard:
            await update.message.reply_text(text, reply_markup=keyboard)
        else:
            await update.message.reply_text(text)

        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text("Error searching cars ❌")
        return ConversationHandler.END
