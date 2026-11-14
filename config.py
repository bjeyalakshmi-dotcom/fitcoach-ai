import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = "gpt-4o"
DB_PATH = os.getenv("DB_PATH", "fitagent.db")
MAX_TOKENS = 4096

# Autonomy thresholds
HIGH_VALUE_INVOICE_THRESHOLD = 1200  # min safe kcal/day
MAX_LOAD_INCREASE_PCT = 20           # max % training load increase per week
MAX_DAILY_NOTIFICATIONS = 3
