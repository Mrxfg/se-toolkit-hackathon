"""
Sell flow handler
"""

import re
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from services.api import get_or_create_user, add_car, geocode_location
from keyboards.menus import brand_selection, location_keyboard, post_add_menu
from states import MAKE, MODEL, YEAR, PRICE, MILEAGE, DESC, LOCATION


async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start sell flow"""
    get_or_create_user(
        update.effective_user.id,
        update.effective_user.first_name
    )

    await update.message.reply_text(
        "Choose car brand:",
        reply_markup=brand_selection()
    )
    return MAKE


async def make(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle brand selection"""
    text = update.message.text

    # Check if we're waiting for custom brand input
    if context.user_data.get("waiting_for_custom_brand"):
        context.user_data["make"] = text
        context.user_data.pop("waiting_for_custom_brand")
        await update.message.reply_text(
            "Enter model (e.g., Camry):",
            reply_markup=ReplyKeyboardRemove()
        )
        return MODEL

    if text.lower() == "other":
        context.user_data["waiting_for_custom_brand"] = True
        await update.message.reply_text(
            "Enter car brand (e.g., Honda, Kia):",
            reply_markup=ReplyKeyboardRemove()
        )
        return MAKE

    context.user_data["make"] = text
    await update.message.reply_text(
        "Enter model (e.g., Camry):",
        reply_markup=ReplyKeyboardRemove()
    )
    return MODEL


async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle model input"""
    context.user_data["model"] = update.message.text
    await update.message.reply_text("Enter year (e.g., 2018):")
    return YEAR


async def year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle year input"""
    nums = re.findall(r"\d+", update.message.text)

    if not nums:
        await update.message.reply_text("Enter valid year (e.g., 2018)")
        return YEAR

    context.user_data["year"] = int(nums[0])
    await update.message.reply_text("Enter price (e.g., 15000):")
    return PRICE


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle price input"""
    nums = re.findall(r"\d+", update.message.text)

    if not nums:
        await update.message.reply_text("Enter valid price (e.g., 15000)")
        return PRICE

    context.user_data["price"] = int(nums[0])
    await update.message.reply_text("Enter mileage (e.g., 50000):")
    return MILEAGE


async def mileage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mileage input"""
    nums = re.findall(r"\d+", update.message.text)

    if not nums:
        await update.message.reply_text("Enter valid mileage (e.g., 50000)")
        return MILEAGE

    context.user_data["mileage"] = int(nums[0])
    await update.message.reply_text("Enter description (e.g., Good condition, no accidents):")
    return DESC


async def desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle description input"""
    context.user_data["description"] = update.message.text

    await update.message.reply_text(
        "Send location or type city:",
        reply_markup=location_keyboard()
    )
    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location input"""
    user_id = get_or_create_user(
        update.effective_user.id,
        update.effective_user.first_name
    )

    if not user_id:
        await update.message.reply_text("Error creating user ❌")
        return ConversationHandler.END

    try:
        if update.message.location:
            lat = update.message.location.latitude
            lon = update.message.location.longitude
        else:
            geo = geocode_location(update.message.text)

            if not geo:
                await update.message.reply_text("Location not found ❌")
                return LOCATION

            lat = float(geo[0]["lat"])
            lon = float(geo[0]["lon"])

        car = {
            **context.user_data,
            "latitude": lat,
            "longitude": lon,
            "user_id": user_id
        }

        add_car(car)

        await update.message.reply_text(
            "Car added successfully ✅\nWhat would you like to do next?",
            reply_markup=post_add_menu()
        )
        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text("Error adding car ❌")
        return LOCATION
