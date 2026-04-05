"""
My Cars handler
"""

from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from services.api import get_user_cars, get_car_images
from keyboards.inline import car_actions
import io


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

            # Try to get images
            try:
                images = get_car_images(car['id'])

                if images and len(images) > 0:
                    # Send first image with caption
                    first_img = images[0]
                    await update.message.reply_photo(
                        photo=io.BytesIO(first_img['image_data']),
                        caption=text,
                        reply_markup=car_actions(car['id'])
                    )

                    # Send remaining images as media group if any
                    if len(images) > 1:
                        media_group = [
                            InputMediaPhoto(media=io.BytesIO(img['image_data']))
                            for img in images[1:]
                        ]
                        await update.message.reply_media_group(media=media_group)
                else:
                    # No images, send text only
                    await update.message.reply_text(
                        text,
                        reply_markup=car_actions(car['id'])
                    )
            except:
                # Error getting images, send text only
                await update.message.reply_text(
                    text,
                    reply_markup=car_actions(car['id'])
                )
    except Exception as e:
        await update.message.reply_text("Error loading cars ❌")
