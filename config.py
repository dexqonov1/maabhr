# config.py
import os
from dotenv import load_dotenv

# .env dan o'qish
load_dotenv()

# Telegram bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "").strip() or None
CHANNEL_ID_ENV = os.getenv("CHANNEL_ID", "").strip()
CHANNEL_ID = int(CHANNEL_ID_ENV) if CHANNEL_ID_ENV else None

# Barcha fayl yo'llari
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

USERS_JSON = os.path.join(DATA_DIR, "users.json")
PASSWORDS_CSV = os.path.join(DATA_DIR, "passwords.csv")
JOBS_CSV = os.path.join(DATA_DIR, "jobs.csv")
HH_CSV = os.path.join(DATA_DIR, "hh.csv")
LINKEDIN_CSV = os.path.join(DATA_DIR, "linkedin.csv")
OLX_CSV = os.path.join(DATA_DIR, "olx.csv")
ISHUZ_CSV = os.path.join(DATA_DIR, "ishuz.csv")

# Savat limiti
CART_LIMIT = 2000


def ensure_data_files():
    """Kerakli fayllarni yaratib chiqadi (agar yo'q bo'lsa)."""
    import csv, json
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(USERS_JSON):
        with open(USERS_JSON, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

    if not os.path.exists(PASSWORDS_CSV):
        with open(PASSWORDS_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["password"])
            writer.writerow(["MAAB-2025"])

    if not os.path.exists(JOBS_CSV):
        with open(JOBS_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["job_id", "name", "company", "location", "skills", "description_html", "link"])
            writer.writerow([
                1, "Data Scientist", "BI-Group", "Uzbekistan, Tashkent",
                "Python;SQL;Power BI;Excel",
                "<p><strong>Looking to take your first serious step?</strong></p>",
                "https://uz.linkedin.com/jobs/view/123"
            ])

    # Barcha manbalar uchun bo'sh fayllar
    for path in [HH_CSV, LINKEDIN_CSV, OLX_CSV, ISHUZ_CSV]:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["job_id", "name", "company", "location", "skills", "description_html", "link"])
