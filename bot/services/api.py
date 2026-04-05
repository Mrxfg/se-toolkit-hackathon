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
