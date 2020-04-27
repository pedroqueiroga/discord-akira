import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = bool(os.getenv("DEBUG"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    raise Exception("DISCORD_TOKEN not found")
