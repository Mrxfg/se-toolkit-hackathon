"""
Sell flow handler
"""

import re
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from services.api import get_or_create_user, add_car, geocode_location, upload_car_image
from keyboards.menus import brand_selection, location_keyboard, post_add_menu
from states import MAKE, MODEL, YEAR, PRICE, MILEAGE, DESC, LOCATION, PHOTOS


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

        context.user_data["latitude"] = lat
        context.user_data["longitude"] = lon

        await update.message.reply_text(
            "📸 Send up to 5 photos of your car (or type 'skip' to finish):",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["photos"] = []
        return PHOTOS

    except Exception as e:
        await update.message.reply_text("Error processing location ❌")
        return LOCATION


async def photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads"""
    user_id = get_or_create_user(
        update.effective_user.id,
        update.effective_user.first_name
    )

    # Check if user wants to skip or finish
    if update.message.text and update.message.text.lower() in ['skip', 'done', 'finish']:
        # Save car without photos or with collected photos
        try:
            car = {
                "make": context.user_data["make"],
                "model": context.user_data["model"],
                "year": context.user_data["year"],
                "price": context.user_data["price"],
                "mileage": context.user_data["mileage"],
                "description": context.user_data["description"],
                "latitude": context.user_data["latitude"],
                "longitude": context.user_data["longitude"],
                "user_id": user_id
            }

            result = add_car(car)
            car_id = result.get("id")

            # Upload collected photos
            photos = context.user_data.get("photos", [])
            for photo_file in photos:
                upload_car_image(car_id, update.effective_user.id, photo_file)

            await update.message.reply_text(
                f"Car added successfully ✅\n{len(photos)} photo(s) uploaded\n\nWhat would you like to do next?",
                reply_markup=post_add_menu()
            )
            return ConversationHandler.END

        except Exception as e:
            await update.message.reply_text(f"Error adding car ❌")
            return ConversationHandler.END

    # Handle photo upload
    if update.message.photo:
        photos = context.user_data.get("photos", [])

        if len(photos) >= 5:
            await update.message.reply_text("Maximum 5 photos reached. Type 'done' to finish.")
            return PHOTOS

        # Get the largest photo
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        photos.append(("image.jpg", photo_bytes, "image/jpeg"))
        context.user_data["photos"] = photos

        remaining = 5 - len(photos)
        await update.message.reply_text(
            f"✅ Photo {len(photos)}/5 added\n"
            f"Send {remaining} more photo(s) or type 'done' to finish"
        )
        return PHOTOS

    await update.message.reply_text("Please send a photo or type 'skip' to finish")
    return PHOTOS
