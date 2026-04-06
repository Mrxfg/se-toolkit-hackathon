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
from handlers.sell import sell, make, model, year, price, mileage, desc, location, photos
from handlers.search import search_command, search_input
from handlers.listings import listings
from handlers.mycars import mycars
from handlers.edit import start_edit, edit_field_select, edit_value_input
from services.api import search_cars, delete_car, get_car_images, get_seller_info, send_message, get_inbox
from keyboards.inline import (
    delete_confirmation, pagination_buttons, search_pagination_buttons
)
from helpers.display import send_car_with_photos
import base64
import io


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

    elif "inbox" in text:
        return await inbox(update, context)


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

        await query.answer()

        # Send new message instead of editing (works for both text and photo messages)
        await query.message.reply_text(
            "Are you sure you want to delete this car?",
            reply_markup=delete_confirmation(car_id)
        )
        return

    # Handle delete confirmation
    if query.data.startswith("confirm_delete_"):
        car_id = query.data.split("_")[2]
        tid = update.effective_user.id

        await query.answer()

        try:
            delete_car(car_id, tid)
            await query.message.reply_text("Car deleted successfully ✅")
        except Exception as e:
            await query.message.reply_text(f"Error deleting car ❌\n{str(e)}")
        return

    # Handle cancel delete
    if query.data == "cancel_delete":
        await query.answer()
        await query.message.reply_text("Deletion cancelled")
        return

    # Handle contact seller
    if query.data.startswith("contact_"):
        car_id = query.data.split("_")[1]

        try:
            seller = get_seller_info(car_id)

            # Build contact message
            contact_msg = "📞 Seller Contact Information:\n\n"
            contact_msg += f"👤 Name: {seller['name']}\n\n"
            contact_msg += "💬 Click the button below to send a message to the seller:"

            # Create inline keyboard with "Send Message" button
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton("💬 Send Message", callback_data=f"sendmsg_{car_id}_{seller['telegram_id']}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.answer()
            await query.message.reply_text(contact_msg, reply_markup=reply_markup)
        except Exception as e:
            await query.answer("Error getting seller info ❌", show_alert=True)
        return

    # Handle send message button
    if query.data.startswith("sendmsg_"):
        parts = query.data.split("_")
        car_id = parts[1]
        seller_telegram_id = parts[2]

        # Store in context for message input
        context.user_data["message_car_id"] = car_id
        context.user_data["message_to_telegram_id"] = seller_telegram_id

        await query.answer()
        await query.message.reply_text(
            "✍️ Type your message to the seller:\n\n"
            "(e.g., 'Hello, is this car still available?')"
        )
        return MESSAGE_INPUT

    # Handle reply button
    if query.data.startswith("reply_"):
        parts = query.data.split("_")
        message_id = parts[1]
        buyer_telegram_id = parts[2]
        car_id = parts[3]

        # Store in context for reply input
        context.user_data["message_car_id"] = car_id
        context.user_data["message_to_telegram_id"] = buyer_telegram_id
        context.user_data["reply_to_message_id"] = message_id

        await query.answer()
        await query.message.reply_text(
            "✍️ Type your reply:\n\n"
            "(The buyer will receive your message)"
        )
        return MESSAGE_INPUT

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

            await query.answer()

            # Send each car with photos and contact button
            for car in cars:
                await send_car_with_photos(query, car, show_contact=True)

        except Exception as e:
            await query.edit_message_text("Error loading cars ❌")
        return


# ======================
# MESSAGE HANDLER
# ======================
async def handle_message_input(update: Update, context):
    """Handle message input for contacting seller"""
    message_text = update.message.text
    car_id = context.user_data.get("message_car_id")
    to_telegram_id = context.user_data.get("message_to_telegram_id")
    from_telegram_id = update.effective_user.id
    is_reply = context.user_data.get("reply_to_message_id") is not None

    if not car_id or not to_telegram_id:
        await update.message.reply_text("Error: Session expired. Please try again.")
        return ConversationHandler.END

    try:
        # Send message via API
        result = send_message(car_id, from_telegram_id, int(to_telegram_id), message_text)

        # Notify sender
        if is_reply:
            await update.message.reply_text(
                "✅ Reply sent successfully!\n\n"
                "The buyer will receive your message."
            )
        else:
            await update.message.reply_text(
                "✅ Message sent successfully!\n\n"
                "The seller will receive your message and can reply to you."
            )

        # Notify recipient
        try:
            from telegram import Bot
            bot = Bot(token=BOT_TOKEN)

            # Get car info for context
            from services.api import search_cars
            cars = search_cars("", limit=1000)  # Get all cars
            car = next((c for c in cars if c['id'] == int(car_id)), None)

            if is_reply:
                notification = (
                    f"📩 Reply from seller:\n\n"
                    f"🚗 Car: {car['make']} {car['model']} ({car['year']})\n"
                    f"👤 From: {update.effective_user.first_name}\n"
                    f"💬 Message: {message_text}\n\n"
                    f"Use /inbox to see all messages or reply directly."
                )
            else:
                notification = (
                    f"📩 New message about your car:\n\n"
                    f"🚗 Car: {car['make']} {car['model']} ({car['year']})\n"
                    f"👤 From: {update.effective_user.first_name}\n"
                    f"💬 Message: {message_text}\n\n"
                    f"Use /inbox to reply."
                )

            await bot.send_message(chat_id=int(to_telegram_id), text=notification)
        except Exception as e:
            print(f"Failed to notify recipient: {e}")

        # Clear context
        context.user_data.pop("message_car_id", None)
        context.user_data.pop("message_to_telegram_id", None)
        context.user_data.pop("reply_to_message_id", None)

        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(f"❌ Error sending message: {str(e)}")
        return ConversationHandler.END


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
        PHOTOS: [MessageHandler(filters.PHOTO | filters.TEXT, photos)],
    },
    fallbacks=[]
)

edit_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_edit, pattern="^edit_\\d+$")],
    states={
        EDIT_FIELD_SELECT: [CallbackQueryHandler(edit_field_select)],
        EDIT_VALUE_INPUT: [MessageHandler(filters.TEXT | filters.LOCATION | filters.PHOTO, edit_value_input)],
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

message_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(handle_button, pattern="^sendmsg_"),
        CallbackQueryHandler(handle_button, pattern="^reply_")
    ],
    states={
        MESSAGE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_input)],
    },
    fallbacks=[],
    per_chat=True,
    per_user=True
)


# ======================
# INBOX COMMAND
# ======================
async def inbox(update: Update, context):
    """Show user's inbox"""
    tid = update.effective_user.id

    try:
        messages = get_inbox(tid)

        if not messages:
            await update.message.reply_text("📭 No messages yet.")
            return

        await update.message.reply_text(f"📬 You have {len(messages)} message(s):")

        # Send each message separately with Reply button
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        for msg in messages[:10]:  # Show last 10 messages
            read_icon = "✅" if msg['is_read'] else "🆕"

            msg_text = (
                f"{read_icon} Message from {msg['sender_name']}\n\n"
                f"🚗 About: {msg['car_make']} {msg['car_model']}\n"
                f"💬 Message:\n{msg['message_text']}\n\n"
                f"📅 {msg['created_at'][:16]}"
            )

            # Add Reply button
            keyboard = [[InlineKeyboardButton("↩️ Reply", callback_data=f"reply_{msg['id']}_{msg['sender_telegram_id']}_{msg['car_id']}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(msg_text, reply_markup=reply_markup)

            # Mark as read
            try:
                mark_message_read(msg['id'], tid)
            except:
                pass

    except Exception as e:
        await update.message.reply_text(f"Error loading inbox ❌\n{str(e)}")


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
    app.add_handler(CommandHandler("inbox", inbox))

    # Conversation handlers
    app.add_handler(sell_conv)
    app.add_handler(edit_conv)
    app.add_handler(message_conv)
    app.add_handler(search_conv)

    # Callback handler
    app.add_handler(CallbackQueryHandler(handle_button))

    # Menu handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
