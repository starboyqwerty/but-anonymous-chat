import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set. Copy .env.example to .env and put your "
        "token from @BotFather there."
    )

ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
]

DATABASE_FILE = os.getenv("DATABASE_FILE", "db.db")
