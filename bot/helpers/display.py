"""
Helper functions for displaying cars with photos
"""

from telegram import Update, InputMediaPhoto
from services.api import get_car_images
import io
import base64


async def send_car_with_photos(update, car, reply_markup=None, show_contact=False):
    """Send a car listing with photos if available

    Args:
        update: Telegram update object
        car: Car data dictionary
        reply_markup: Optional inline keyboard
        show_contact: If True, adds contact seller button
    """
    from keyboards.inline import car_view_actions

    text = f"🚗 {car['make']} {car['model']} ({car['year']})\n💰 ${car['price']}\n📏 {car['mileage']} km\n📝 {car['description']}"

    # Use contact button if requested and no other markup provided
    if show_contact and reply_markup is None:
        reply_markup = car_view_actions(car['id'])

    try:
        images = get_car_images(car['id'])

        if images and len(images) > 0:
            # Decode first image
            first_img_bytes = base64.b64decode(images[0]['image_data'])

            # Send first image with caption
            await update.message.reply_photo(
                photo=io.BytesIO(first_img_bytes),
                caption=text,
                reply_markup=reply_markup
            )

            # Send remaining images if any
            if len(images) > 1:
                media_group = [
                    InputMediaPhoto(media=io.BytesIO(base64.b64decode(img['image_data'])))
                    for img in images[1:]
                ]
                await update.message.reply_media_group(media=media_group)
        else:
            # No images, send text only
            await update.message.reply_text(text, reply_markup=reply_markup)
    except:
        # Error getting images, send text only
        await update.message.reply_text(text, reply_markup=reply_markup)
