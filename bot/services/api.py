"""
API service for making requests to the backend
"""

import requests
from config import API_URL


def get_or_create_user(telegram_id, name):
    """Get or create a user in the database"""
    try:
        res = requests.post(
            f"{API_URL}/users",
            json={
                "telegram_id": telegram_id,
                "name": name
            },
            timeout=5
        )
        res.raise_for_status()
        return res.json().get("id")
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


def get_user_cars(telegram_id):
    """Get all cars for a user"""
    res = requests.get(f"{API_URL}/cars/user/{telegram_id}", timeout=5)
    res.raise_for_status()
    return res.json()


def get_brands():
    """Get all car brands"""
    res = requests.get(f"{API_URL}/cars/brands", timeout=5)
    res.raise_for_status()
    return res.json()


def search_cars(query, limit=5, offset=0):
    """Search for cars"""
    res = requests.get(
        f"{API_URL}/cars/search",
        params={"q": query, "limit": limit, "offset": offset},
        timeout=5
    )
    res.raise_for_status()
    return res.json()


def add_car(car_data):
    """Add a new car"""
    res = requests.post(f"{API_URL}/cars", json=car_data, timeout=5)
    res.raise_for_status()
    return res.json()


def update_car(car_id, car_data):
    """Update a car"""
    res = requests.put(f"{API_URL}/cars/{car_id}", json=car_data, timeout=5)
    return res


def delete_car(car_id, telegram_id):
    """Delete a car"""
    res = requests.delete(
        f"{API_URL}/cars/{car_id}",
        params={"telegram_id": telegram_id},
        timeout=5
    )
    res.raise_for_status()
    return res.json()


def geocode_location(location_text):
    """Convert location text to coordinates"""
    res = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": location_text, "format": "json"},
        headers={"User-Agent": "carbot"},
        timeout=5
    )
    return res.json()

def upload_car_image(car_id, telegram_id, image_file):
    """Upload an image for a car"""
    files = {"file": image_file}
    res = requests.post(
        f"{API_URL}/cars/{car_id}/images",
        params={"telegram_id": telegram_id},
        files=files,
        timeout=10
    )
    return res


def get_car_images(car_id):
    """Get all images for a car"""
    res = requests.get(f"{API_URL}/cars/{car_id}/images", timeout=5)
    res.raise_for_status()
    return res.json()


def delete_car_image(car_id, image_id, telegram_id):
    """Delete a car image"""
    res = requests.delete(
        f"{API_URL}/cars/{car_id}/images/{image_id}",
        params={"telegram_id": telegram_id},
        timeout=5
    )
    res.raise_for_status()
    return res.json()


def get_seller_info(car_id):
    """Get seller information for a car"""
    res = requests.get(f"{API_URL}/cars/{car_id}/seller", timeout=5)
    res.raise_for_status()
    return res.json()


def send_message(car_id, from_telegram_id, to_telegram_id, message_text):
    """Send a message to a seller"""
    res = requests.post(
        f"{API_URL}/messages",
        json={
            "car_id": car_id,
            "from_telegram_id": from_telegram_id,
            "to_telegram_id": to_telegram_id,
            "message_text": message_text
        },
        timeout=5
    )
    res.raise_for_status()
    return res.json()


def get_inbox(telegram_id, unread_only=False):
    """Get messages for a user"""
    res = requests.get(
        f"{API_URL}/messages/inbox/{telegram_id}",
        params={"unread_only": unread_only},
        timeout=5
    )
    res.raise_for_status()
    return res.json()


def mark_message_read(message_id, telegram_id):
    """Mark a message as read"""
    res = requests.put(
        f"{API_URL}/messages/{message_id}/read",
        params={"telegram_id": telegram_id},
        timeout=5
    )
    res.raise_for_status()
    return res.json()


def get_seller_info(car_id):
    """Get seller information for a car"""
    res = requests.get(f"{API_URL}/cars/{car_id}/seller", timeout=5)
    res.raise_for_status()
    return res.json()
