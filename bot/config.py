import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://backend:8000")
BOT_TOKEN = os.getenv("BOT_TOKEN")
