"""
My Cars handler
"""

from telegram import Update
from telegram.ext import ContextTypes
from services.api import get_user_cars
from keyboards.inline import car_actions


async def mycars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's cars"""
    tid = update.effective_user.id

    try:
        cars = get_user_cars(tid)

        if not cars:
            await update.message.reply_text("No cars ❌")
            return

        for car in cars:
            text = f"🚗 {car['make']} {car['model']} ({car['year']})\n💰 ${car['price']}\n📏 {car['mileage']} km\n📝 {car['description']}"

            await update.message.reply_text(
                text,
                reply_markup=car_actions(car['id'])
            )
    except Exception as e:
        await update.message.reply_text("Error loading cars ❌")
