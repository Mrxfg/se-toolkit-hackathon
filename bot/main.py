"""
Main bot application
"""

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters
)

from config import BOT_TOKEN
from states import *
from handlers.start import start
from handlers.sell import sell, make, model, year, price, mileage, desc, location
from handlers.search import search_command, search_input
from handlers.listings import listings
from handlers.mycars import mycars
from handlers.edit import start_edit, edit_field_select, edit_value_input
from services.api import search_cars, delete_car
from keyboards.inline import (
    delete_confirmation, pagination_buttons, search_pagination_buttons
)


# ======================
# MENU HANDLER
# ======================
async def menu_handler(update: Update, context):
    """Handle main menu button presses"""
    text = update.message.text.lower()

    if "sell" in text or "add another" in text:
        await update.message.reply_text("Use /sell command to start selling")

    elif "listings" in text or "view listings" in text:
        return await listings(update, context)

    elif "search" in text:
        await update.message.reply_text("Enter car name (e.g., Toyota):")
        return SEARCH_INPUT

    elif "my cars" in text:
        return await mycars(update, context)


# ======================
# CALLBACK HANDLER
# ======================
async def handle_button(update: Update, context):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        await query.edit_message_text("Use menu below ⬇")
        return

    # Handle delete
    if query.data.startswith("delete_"):
        car_id = query.data.split("_")[1]
        context.user_data["delete_car_id"] = car_id

        await query.edit_message_text(
            "Are you sure you want to delete this car?",
            reply_markup=delete_confirmation(car_id)
        )
        return

    # Handle delete confirmation
    if query.data.startswith("confirm_delete_"):
        car_id = query.data.split("_")[2]
        tid = update.effective_user.id

        try:
            delete_car(car_id, tid)
            await query.edit_message_text("Car deleted successfully ✅")
        except Exception as e:
            await query.edit_message_text("Error deleting car ❌")
        return

    # Handle cancel delete
    if query.data == "cancel_delete":
        await query.edit_message_text("Deletion cancelled")
        return

    # Handle brand pagination
    if query.data.startswith("page_"):
        parts = query.data.split("_")
        brand = parts[1]
        page = int(parts[2])

        try:
            offset = page * 5
            cars = search_cars(brand, limit=5, offset=offset)

            if not cars:
                await query.edit_message_text("No more cars ❌")
                return

            text = "\n\n".join([
                f"🚗 {c['make']} {c['model']}\n💰 ${c['price']}"
                for c in cars
            ])

            keyboard = pagination_buttons(brand, page, len(cars) == 5)
            if keyboard:
                keyboard.inline_keyboard.append(
                    [{"text": "⬅ Back", "callback_data": "back"}]
                )

            await query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            await query.edit_message_text("Error loading cars ❌")
        return

    # Handle search pagination
    if query.data.startswith("search_page_"):
        parts = query.data.split("_", 3)
        search_query = parts[2]
        page = int(parts[3])

        try:
            offset = page * 5
            cars = search_cars(search_query, limit=5, offset=offset)

            if not cars:
                await query.edit_message_text("No more cars ❌")
                return

            text = "\n\n".join([
                f"🚗 {c['make']} {c['model']}\n💰 ${c['price']}"
                for c in cars
            ])

            keyboard = search_pagination_buttons(search_query, page, len(cars) == 5)
            await query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            await query.edit_message_text("Error loading cars ❌")
        return

    # Handle brand search
    if query.data.startswith("brand_"):
        brand = query.data.split("_", 1)[1]

        try:
            cars = search_cars(brand, limit=5, offset=0)

            if not cars:
                await query.edit_message_text("No cars ❌")
                return

            text = "\n\n".join([
                f"🚗 {c['make']} {c['model']}\n💰 ${c['price']}"
                for c in cars
            ])

            keyboard = pagination_buttons(brand, 0, len(cars) == 5)
            if keyboard:
                keyboard.inline_keyboard.append(
                    [{"text": "⬅ Back", "callback_data": "back"}]
                )

            await query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            await query.edit_message_text("Error loading cars ❌")
        return


# ======================
# CONVERSATION HANDLERS
# ======================
sell_conv = ConversationHandler(
    entry_points=[CommandHandler("sell", sell)],
    states={
        MAKE: [MessageHandler(filters.TEXT, make)],
        MODEL: [MessageHandler(filters.TEXT, model)],
        YEAR: [MessageHandler(filters.TEXT, year)],
        PRICE: [MessageHandler(filters.TEXT, price)],
        MILEAGE: [MessageHandler(filters.TEXT, mileage)],
        DESC: [MessageHandler(filters.TEXT, desc)],
        LOCATION: [MessageHandler(filters.TEXT | filters.LOCATION, location)],
    },
    fallbacks=[]
)

edit_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_edit, pattern="^edit_\\d+$")],
    states={
        EDIT_FIELD_SELECT: [CallbackQueryHandler(edit_field_select)],
        EDIT_VALUE_INPUT: [MessageHandler(filters.TEXT | filters.LOCATION, edit_value_input)],
    },
    fallbacks=[CallbackQueryHandler(edit_field_select, pattern="^editcancel$")],
    per_chat=True,
    per_user=True,
    per_message=False
)

search_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(r"(?i)search"), menu_handler)],
    states={
        SEARCH_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_input)],
    },
    fallbacks=[]
)


# ======================
# MAIN
# ======================
def main():
    """Start the bot"""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("listings", listings))
    app.add_handler(CommandHandler("mycars", mycars))

    # Conversation handlers
    app.add_handler(sell_conv)
    app.add_handler(edit_conv)
    app.add_handler(search_conv)

    # Callback handler
    app.add_handler(CallbackQueryHandler(handle_button))

    # Menu handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
