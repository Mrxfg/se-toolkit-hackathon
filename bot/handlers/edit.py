"""
Edit flow handler
"""

import re
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from services.api import get_user_cars, update_car, geocode_location
from keyboards.inline import edit_menu
from keyboards.menus import post_edit_menu
from states import EDIT_FIELD_SELECT, EDIT_VALUE_INPUT


async def start_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for edit conversation"""
    query = update.callback_query
    await query.answer()

    car_id = query.data.split("_")[1]
    tid = update.effective_user.id

    try:
        # Get car details
        cars = get_user_cars(tid)
        car = next((c for c in cars if c['id'] == int(car_id)), None)

        if not car:
            await query.edit_message_text("Car not found ❌")
            return ConversationHandler.END

        # Store car data for editing
        context.user_data["edit_car_id"] = car_id
        context.user_data["edit_car_data"] = {
            "make": car['make'],
            "model": car['model'],
            "year": car['year'],
            "price": car['price'],
            "mileage": car['mileage'],
            "description": car['description'],
            "latitude": car['latitude'],
            "longitude": car['longitude']
        }

        car_info = f"🚗 {car['make']} {car['model']} ({car['year']})\n💰 ${car['price']}\n📏 {car['mileage']} km\n\nSelect field to edit:"

        await query.edit_message_text(
            car_info,
            reply_markup=edit_menu()
        )
        return EDIT_FIELD_SELECT

    except Exception as e:
        await query.edit_message_text(f"Error loading car: {str(e)}")
        return ConversationHandler.END


async def edit_field_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle field selection in edit menu"""
    query = update.callback_query
    await query.answer()

    # Handle save
    if query.data == "editsave":
        car_id = context.user_data["edit_car_id"]
        tid = update.effective_user.id

        try:
            # Ensure all fields are properly typed
            car_data = {
                "make": str(context.user_data["edit_car_data"]["make"]),
                "model": str(context.user_data["edit_car_data"]["model"]),
                "year": int(context.user_data["edit_car_data"]["year"]),
                "price": int(context.user_data["edit_car_data"]["price"]),
                "mileage": int(context.user_data["edit_car_data"]["mileage"]),
                "description": str(context.user_data["edit_car_data"]["description"]),
                "latitude": float(context.user_data["edit_car_data"]["latitude"]) if context.user_data["edit_car_data"]["latitude"] else None,
                "longitude": float(context.user_data["edit_car_data"]["longitude"]) if context.user_data["edit_car_data"]["longitude"] else None,
                "telegram_id": int(tid)
            }

            res = update_car(car_id, car_data)

            if res.status_code == 403:
                await query.edit_message_text("❌ Not authorized to edit this car")
                return ConversationHandler.END
            elif res.status_code == 404:
                await query.edit_message_text("❌ Car not found")
                return ConversationHandler.END

            res.raise_for_status()
            await query.edit_message_text("✅ Car updated successfully!")
            return ConversationHandler.END

        except Exception as e:
            error_detail = str(e)
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                pass
            await query.edit_message_text(f"❌ Error: {error_detail}")
            return ConversationHandler.END

    # Handle cancel
    if query.data == "editcancel":
        await query.edit_message_text("Edit cancelled")
        return ConversationHandler.END

    # Handle field selection
    if query.data.startswith("editfield_"):
        field = query.data.replace("editfield_", "")
        context.user_data["edit_field"] = field

        field_names = {
            "make": "brand (e.g., Toyota)",
            "model": "model (e.g., Camry)",
            "year": "year (e.g., 2018)",
            "price": "price (e.g., 15000)",
            "mileage": "mileage (e.g., 50000)",
            "description": "description",
            "location": "location (city name or send GPS)"
        }

        current_value = context.user_data["edit_car_data"].get(field, "")

        await query.edit_message_text(
            f"Current {field}: {current_value}\n\nEnter new {field_names.get(field, field)}:"
        )
        return EDIT_VALUE_INPUT

    return EDIT_FIELD_SELECT


async def edit_value_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle value input for selected field"""
    field = context.user_data.get("edit_field")
    value = update.message.text

    try:
        # Handle location separately
        if field == "location":
            if update.message.location:
                context.user_data["edit_car_data"]["latitude"] = update.message.location.latitude
                context.user_data["edit_car_data"]["longitude"] = update.message.location.longitude
            else:
                geo = geocode_location(value)

                if not geo:
                    await update.message.reply_text("Location not found ❌\nTry again:")
                    return EDIT_VALUE_INPUT

                context.user_data["edit_car_data"]["latitude"] = float(geo[0]["lat"])
                context.user_data["edit_car_data"]["longitude"] = float(geo[0]["lon"])
 
        # Handle numeric fields
        elif field in ["year", "price", "mileage"]:
            nums = re.findall(r"\d+", value)
            if not nums:
                await update.message.reply_text(f"Invalid {field}. Enter a valid number:")
                return EDIT_VALUE_INPUT

            num_value = int(nums[0])

            # Validate ranges
            if field == "year" and (num_value < 1900 or num_value > 2100):
                await update.message.reply_text("Year must be between 1900 and 2100:")
                return EDIT_VALUE_INPUT
            elif field == "price" and num_value <= 0:
                await update.message.reply_text("Price must be greater than 0:")
                return EDIT_VALUE_INPUT
            elif field == "mileage" and num_value < 0:
                await update.message.reply_text("Mileage must be 0 or greater:")
                return EDIT_VALUE_INPUT

            context.user_data["edit_car_data"][field] = num_value

        # Handle text fields
        else:
            if len(value) == 0:
                await update.message.reply_text(f"{field.capitalize()} cannot be empty:")
                return EDIT_VALUE_INPUT
            context.user_data["edit_car_data"][field] = value

        # Show updated menu
        car_data = context.user_data["edit_car_data"]
        car_info = f"🚗 {car_data['make']} {car_data['model']} ({car_data['year']})\n💰 ${car_data['price']}\n📏 {car_data['mileage']} km\n\n✅ {field.capitalize()} updated!\n\nSelect another field or save:"

        await update.message.reply_text(
            car_info,
            reply_markup=edit_menu()
        )
        return EDIT_FIELD_SELECT

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}\nTry again:")
        return EDIT_VALUE_INPUT
