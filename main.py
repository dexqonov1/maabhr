# main.py
import asyncio
import csv
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# ------------------ Load env ------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "").strip() or None
CHANNEL_ID_ENV = os.getenv("CHANNEL_ID", "").strip()
CHANNEL_ID = int(CHANNEL_ID_ENV) if CHANNEL_ID_ENV else None

# ------------------ Paths ------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_JSON = os.path.join(DATA_DIR, "users.json")
# Asosiy jobs.csv
JOBS_CSV = os.path.join(DATA_DIR, "jobs.csv")
# Yangi manbalar uchun fayllar
HH_CSV = os.path.join(DATA_DIR, "hh.csv")
LINKEDIN_CSV = os.path.join(DATA_DIR, "linkedin.csv")
OLX_CSV = os.path.join(DATA_DIR, "olx.csv")
ISHUZ_CSV = os.path.join(DATA_DIR, "ishuz.csv")

PASSWORDS_CSV = os.path.join(DATA_DIR, "passwords.csv")

# Cart limit
CART_LIMIT = 2000

# ------------------ Bot init (aiogram 3.7+) ------------------
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


# ------------------ Languages ------------------
# Lug'at: til -> kalit -> matn (format() yoki f-string uchun {placeholders})
LANG_TEXTS: Dict[str, Dict[str, str]] = {
    "uz": {
        "choose_language_title": "Tilni tanlang — Choose a language — Выберите язык",
        "btn_lang_uz": "🇺🇿 Oʻzbek",
        "btn_lang_en": "🇬🇧 English",
        "btn_lang_ru": "🇷🇺 Русский",

        "hello_registered": "Salom <b>{full_name}</b>!\nSiz allaqachon roʻyxatdan oʻtgansiz ✅",
        "ask_join": "Assalomu alaykum!\n\nBotdan toʻliq foydalanish uchun iltimos, avval @maabuz kanaliga aʼzo boʻling.",
        "btn_goto_channel": "🔗 @maabuz kanaliga o‘tish",
        "btn_joined": "✅ Aʼzo bo‘ldim",
        "not_joined": "Siz hali aʼzo boʻlmadingiz. Iltimos avval kanalga aʼzo boʻling, keyin \"Aʼzo bo‘ldim\"ni bosing.",

        "ask_password": "A’zo ekanligingiz tasdiqlandi ✅\n\nEndi botdan toʻliq foydalanish uchun <b>MAAB INNOVATION</b> tomonidan berilgan maxsus parolni kiriting.",
        "wrong_password": "❌ Parol notoʻgʻri. Qaytadan urinib koʻring.",
        "ask_first_name": "✅ Tasdiqlandi! Endi ismingizni kiriting (masalan: <b>Jasur</b>).",
        "ask_last_name": "Familiyangizni kiriting (masalan: <b>Rahimov</b>).",
        "ask_phone": "Telefon raqamingizni yuboring (masalan: <code>+998 90 123 45 67</code>) yoki pastdagi tugma orqali ulashing.",
        "btn_share_phone": "📞 Raqamni ulashish",
        "btn_manual_phone": "📱 Qo‘lda kiritaman",
        "phone_bad_format": "❌ Noto‘g‘ri format.\nIltimos, raqamni quyidagi formatda kiriting:\n<code>+998 90 123 45 67</code>",
        "reg_success": "✅ Siz muvaffaqiyatli roʻyxatdan oʻtdingiz!",

        "menu_view_jobs": "🧾 Ishlarni ko‘rish",
        "menu_my_cart": "🛒 Mening savatim",
        "menu_change_lang": "🌐 Tilni o‘zgartirish",

        "cart_empty": "🛒 Sizning savatingiz hozircha bo‘sh.",
        "cart_item_line": "<b>{name}</b>\n🏢 {company}\n📍 {location}\n🔗 <a href=\"{link}\">Topshirish (Link)</a>",
        "btn_remove_from_cart": "❌ Savatdan olib tashlash",
        "btn_back_menu": "↩️ Menyuga qaytish",

        "jobs_none": "Hozircha ishlar mavjud emas.",
        "jobs_header": "Quyidagi ish ro‘yxatidan tanlang:\n<i>Topildi: {total} ta | Sahifa: {page}/{pages} | Ko‘rsatilmoqda: {start}–{end}</i>",
        "jobs_list_footer": "<i>Pastdan raqamni bosing ⬇️</i>",
        "btn_prev": "⬅️ Orqaga",
        "btn_next": "➡️ Oldinga",
        "btn_menu": "🏠 Menyuga qaytish",

        "btn_add_cart": "🛒 Savatga qo‘shish",
        "btn_dislike": "❌ Yo‘qmadi",
        "btn_back_list": "⬅️ Ro‘yxatga qaytish",
        "added_ok": "Ish savatga qo‘shildi.",
        "added_dup": "Bu ish allaqachon savatda.",
        "added_limit": "Savat limiti {limit} ta.",
        "removed_ok": "✅ Ish savatdan olib tashlandi. ↩️ Menyuga qaytish uchun /start.",

        "disliked_ok": "Ushbu ish sizga yoqmagan deb belgilandi.",
        "disliked_dup": "Bu ish allaqachon sizga yoqmagan deb belgilangan.",
        "no_visible_jobs": "👏 Siz barcha mavjud ishlarni koʻrib chiqqansiz yoki rad etgansiz.",

        "not_registered": "Avval ro‘yxatdan o‘ting: /start"
    },
    "en": {
        "choose_language_title": "Choose a language — Tilni tanlang — Выберите язык",
        "btn_lang_uz": "🇺🇿 Oʻzbek",
        "btn_lang_en": "🇬🇧 English",
        "btn_lang_ru": "🇷🇺 Русский",

        "hello_registered": "Hi <b>{full_name}</b>!\nYou are already registered ✅",
        "ask_join": "Welcome!\n\nTo use the bot fully, please join the @maabuz channel first.",
        "btn_goto_channel": "🔗 Go to @maabuz channel",
        "btn_joined": "✅ I joined",
        "not_joined": "You haven’t joined yet. Please join the channel first, then press \"I joined\".",

        "ask_password": "Membership confirmed ✅\n\nNow enter the special access password provided by <b>MAAB INNOVATION</b>.",
        "wrong_password": "❌ Wrong password. Please try again.",
        "ask_first_name": "✅ Approved! Now enter your first name (e.g., <b>John</b>).",
        "ask_last_name": "Enter your last name (e.g., <b>Smith</b>).",
        "ask_phone": "Send your phone number (e.g., <code>+998 90 123 45 67</code>) or share via the button below.",
        "btn_share_phone": "📞 Share phone",
        "btn_manual_phone": "📱 Enter manually",
        "phone_bad_format": "❌ Invalid format.\nPlease use:\n<code>+998 90 123 45 67</code>",
        "reg_success": "✅ You have successfully registered!",

        "menu_view_jobs": "🧾 View Jobs",
        "menu_my_cart": "🛒 My Cart",
        "menu_change_lang": "🌐 Change language",

        "cart_empty": "🛒 Your cart is empty.",
        "cart_item_line": "<b>{name}</b>\n🏢 {company}\n📍 {location}\n🔗 <a href=\"{link}\">Apply (Link)</a>",
        "btn_remove_from_cart": "❌ Remove from cart",
        "btn_back_menu": "↩️ Back to menu",

        "jobs_none": "No jobs available yet.",
        "jobs_header": "Choose from the list below:\n<i>Found: {total} | Page: {page}/{pages} | Showing: {start}–{end}</i>",
        "jobs_list_footer": "<i>Tap a number below ⬇️</i>",
        "btn_prev": "⬅️ Previous",
        "btn_next": "➡️ Next",
        "btn_menu": "🏠 Back to menu",

        "btn_add_cart": "🛒 Add to cart",
        "btn_dislike": "❌ Not interested",
        "btn_back_list": "⬅️ Back to list",
        "added_ok": "Job added to cart.",
        "added_dup": "This job is already in the cart.",
        "added_limit": "Cart limit is {limit}.",
        "removed_ok": "✅ Job removed from cart. ↩️ Use /start to return to menu.",

        "disliked_ok": "This job is marked as not interested.",
        "disliked_dup": "This job is already marked as not interested.",
        "no_visible_jobs": "👏 You have viewed or dismissed all available jobs.",

        "not_registered": "Please register first: /start"
    },
    "ru": {
        "choose_language_title": "Выберите язык — Choose a language — Tilni tanlang",
        "btn_lang_uz": "🇺🇿 Oʻzbek",
        "btn_lang_en": "🇬🇧 English",
        "btn_lang_ru": "🇷🇺 Русский",

        "hello_registered": "Здравствуйте, <b>{full_name}</b>!\nВы уже зарегистрированы ✅",
        "ask_join": "Добро пожаловать!\n\nДля полного доступа к боту сначала вступите в канал @maabuz.",
        "btn_goto_channel": "🔗 Перейти в канал @maabuz",
        "btn_joined": "✅ Я вступил(а)",
        "not_joined": "Вы ещё не вступили. Пожалуйста, сначала вступите в канал и нажмите «Я вступил(а)».",

        "ask_password": "Подтверждено ✅\n\nТеперь введите специальный пароль доступа, выданный <b>MAAB INNOVATION</b>.",
        "wrong_password": "❌ Неверный пароль. Попробуйте ещё раз.",
        "ask_first_name": "✅ Отлично! Введите имя (например, <b>Иван</b>).",
        "ask_last_name": "Введите фамилию (например, <b>Иванов</b>).",
        "ask_phone": "Отправьте номер телефона (например, <code>+998 90 123 45 67</code>) или поделитесь через кнопку ниже.",
        "btn_share_phone": "📞 Поделиться номером",
        "btn_manual_phone": "📱 Ввести вручную",
        "phone_bad_format": "❌ Неверный формат.\nИспользуйте:\n<code>+998 90 123 45 67</code>",
        "reg_success": "✅ Вы успешно зарегистрированы!",

        "menu_view_jobs": "🧾 Вакансии",
        "menu_my_cart": "🛒 Моя корзина",
        "menu_change_lang": "🌐 Сменить язык",

        "cart_empty": "🛒 Ваша корзина пуста.",
        "cart_item_line": "<b>{name}</b>\n🏢 {company}\n📍 {location}\n🔗 <a href=\"{link}\">Откликнуться (ссылка)</a>",
        "btn_remove_from_cart": "❌ Удалить из корзины",
        "btn_back_menu": "↩️ В меню",

        "jobs_none": "Пока нет доступных вакансий.",
        "jobs_header": "Выберите из списка ниже:\n<i>Найдено: {total} | Стр.: {page}/{pages} | Показано: {start}–{end}</i>",
        "jobs_list_footer": "<i>Нажмите цифру ниже ⬇️</i>",
        "btn_prev": "⬅️ Назад",
        "btn_next": "➡️ Вперёд",
        "btn_menu": "🏠 В меню",

        "btn_add_cart": "🛒 В корзину",
        "btn_dislike": "❌ Неинтересно",
        "btn_back_list": "⬅️ Назад к списку",
        "added_ok": "Вакансия добавлена в корзину.",
        "added_dup": "Эта вакансия уже в корзине.",
        "added_limit": "Лимит корзины {limit}.",
        "removed_ok": "✅ Вакансия удалена из корзины. ↩️ Для возврата используйте /start.",

        "disliked_ok": "Вакансия отмечена как неинтересная.",
        "disliked_dup": "Эта вакансия уже отмечена как неинтересная.",
        "no_visible_jobs": "👏 Вы просмотрели или отклонили все доступные вакансии.",

        "not_registered": "Сначала пройдите регистрацию: /start"
    }
}


# ------------------ Helpers: i18n ------------------
def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in LANG_TEXTS else "uz"
    text = LANG_TEXTS[lang].get(key, LANG_TEXTS["uz"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


# ------------------ Ensure files ------------------
def _ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_JSON):
        with open(USERS_JSON, "w", encoding="utf-8") as f:
            f.write("{}")
    if not os.path.exists(PASSWORDS_CSV):
        with open(PASSWORDS_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["password"])
            writer.writerow(["MAAB-2025"])
    if not os.path.exists(JOBS_CSV):
        with open(JOBS_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["job_id","name","company","location","skills","description_html","link"])
            writer.writerow([1,"Data Scientist","BI-Group","Uzbekistan, Tashkent","Python;SQL;Power BI;Excel","<p><strong>Looking to take your first serious step?</strong></p>","https://uz.linkedin.com/jobs/view/123"])
    # Yangi manba fayllarni ham avtomatik yaratamiz
    for p in [HH_CSV, LINKEDIN_CSV, OLX_CSV, ISHUZ_CSV]:
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["job_id", "name", "company", "location", "skills", "description_html", "link"])


# ------------------ Storage helpers ------------------
def load_users() -> Dict[str, Any]:
    with open(USERS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data: Dict[str, Any]) -> None:
    tmp = USERS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USERS_JSON)



def get_or_create_profile(tg_id: int) -> Dict[str, Any]:
    users = load_users()
    key = str(tg_id)
    if key not in users:
        users[key] = {
            "id": len(users) + 1,
            "tg_id": tg_id,
            "first_name": None,
            "last_name": None,
            "phone": None,
            "registered": False,
            "created_at": datetime.utcnow().isoformat(timespec="seconds"),
            "cart": [],
            "disliked": [],
            "lang": None  # "uz" | "en" | "ru"
        }
        save_users(users)
    return users[key]

from datetime import datetime, timedelta
def update_profile(tg_id: int, **fields):
    users = load_users()
    key = str(tg_id)
    if key not in users:
        users[key] = {
            "id": len(users) + 1,
            "tg_id": tg_id,
            "first_name": None,
            "last_name": None,
            "phone": None,
            "registered": False,
            "created_at": datetime.utcnow().isoformat(timespec="seconds"),
            "cart": [],
            "disliked": [],
            "lang": None
        }
    users[key].update(fields)
    save_users(users)


def load_passwords() -> set:
    passwords = set()
    if os.path.exists(PASSWORDS_CSV):
        with open(PASSWORDS_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pwd = (row.get("password") or "").strip()
                if pwd:
                    passwords.add(pwd)
    return passwords


# def load_jobs() -> List[Dict[str, Any]]:
#     jobs = []
#     if os.path.exists(JOBS_CSV):
#         with open(JOBS_CSV, "r", encoding="utf-8") as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 try:
#                     row["job_id"] = int(row.get("job_id", "").strip())
#                 except Exception:
#                     continue
#                 jobs.append({
#                     "job_id": row["job_id"],
#                     "name": row.get("name", ""),
#                     "company": row.get("company", ""),
#                     "location": row.get("location", ""),
#                     "skills": row.get("skills", ""),
#                     "description_html": row.get("description_html", ""),
#                     "link": row.get("link", "")
#                 })
#     jobs.sort(key=lambda x: x["job_id"])
#     return jobs
def load_jobs(source: Optional[str] = None) -> List[Dict[str, Any]]:
    files = {
        "hh": HH_CSV,
        "linkedin": LINKEDIN_CSV,
        "olx": OLX_CSV,
        "ishuz": ISHUZ_CSV,
    }

    def read_csv(path):
        jobs = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        row["job_id"] = int(row.get("job_id", "").strip())
                    except:
                        continue
                    jobs.append({
                        "job_id": row["job_id"],
                        "name": row.get("name", ""),
                        "company": row.get("company", ""),
                        "location": row.get("location", ""),
                        "skills": row.get("skills", ""),
                        "description_html": row.get("description_html", ""),
                        "link": row.get("link", "")
                    })
        return jobs

    if source and source in files:
        # faqat tanlangan manbadan o‘qiydi
        return read_csv(files[source])
    elif source == "all":
        # barcha manbalarni birlashtiradi
        all_jobs = []
        for fpath in files.values():
            all_jobs.extend(read_csv(fpath))
        return all_jobs
    else:
        # eski jobs.csv dan o‘qiydi
        return read_csv(JOBS_CSV)


# ------------------ UI builders (i18n) ------------------
def language_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=LANG_TEXTS["uz"]["btn_lang_uz"], callback_data="setlang:uz")
    builder.button(text=LANG_TEXTS["en"]["btn_lang_en"], callback_data="setlang:en")
    builder.button(text=LANG_TEXTS["ru"]["btn_lang_ru"], callback_data="setlang:ru")
    builder.adjust(3)
    return builder.as_markup()


def join_channel_kb(lang: str) -> InlineKeyboardMarkup:
    if CHANNEL_USERNAME:
        chan_link = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
    else:
        chan_link = "https://t.me/"
    buttons = [
        [InlineKeyboardButton(text=t(lang, "btn_goto_channel"), url=chan_link)],
        [InlineKeyboardButton(text=t(lang, "btn_joined"), callback_data="check_join")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=t(lang, "menu_view_jobs"))
    kb.button(text=t(lang, "menu_my_cart"))
    kb.button(text=t(lang, "menu_change_lang"))
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)


def contact_request_kb(lang: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=t(lang, "btn_share_phone"), request_contact=True)
    kb.button(text=t(lang, "btn_manual_phone"))
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def pagination_kb(total_jobs: int, page: int, per_page: int = 10,
                  jobs_list: Optional[List[Dict[str, Any]]] = None, lang: str = "uz") -> InlineKeyboardMarkup:
    """
    Pastda faqat raqamli tugmalar (1..count) bo'ladi.
    Har bir raqam callbackida shu sahifadagi mos job_id yuboriladi: pickid:{job_id}:{page}
    """
    jobs = jobs_list or load_jobs()
    builder = InlineKeyboardBuilder()

    start = page * per_page
    end = min(start + per_page, len(jobs))
    count = end - start

    # 1..count raqamli tugmalar, lekin callback – job_id bilan
    row: List[InlineKeyboardButton] = []
    for i in range(count):
        job = jobs[start + i]
        number_label = str(i + 1)  # ko'rinishi 1..count
        row.append(InlineKeyboardButton(text=number_label, callback_data=f"pickid:{job['job_id']}:{page}"))
        if (i + 1) % 5 == 0:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)

    # Navigatsiya
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text=t(lang, "btn_prev"), callback_data=f"page:{page-1}"))
    if end < len(jobs):
        nav_row.append(InlineKeyboardButton(text=t(lang, "btn_next"), callback_data=f"page:{page+1}"))
    if nav_row:
        builder.row(*nav_row)

    # Menyu
    builder.row(InlineKeyboardButton(text=t(lang, "btn_menu"), callback_data="back_menu"))
    return builder.as_markup()


def job_detail_kb(job_id: int, page: int, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_add_cart"), callback_data=f"add:{job_id}:{page}")
    builder.button(text=t(lang, "btn_dislike"), callback_data=f"dislike:{job_id}:{page}")
    builder.button(text=t(lang, "btn_back_list"), callback_data=f"page:{page}")
    builder.adjust(1)
    return builder.as_markup()


def cart_item_remove_kb(job_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_remove_from_cart"), callback_data=f"rm:{job_id}")],
        [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="back_menu")]
    ])


# ------------------ FSM states ------------------
class Reg(StatesGroup):
    waiting_password = State()
    waiting_first_name = State()
    waiting_last_name = State()
    waiting_phone = State()


# ------------------ Membership check ------------------
async def is_member(user_id: int) -> bool:
    try:
        chat = CHANNEL_ID if CHANNEL_ID is not None else (CHANNEL_USERNAME or None)
        if not chat:
            return True
        member = await bot.get_chat_member(chat_id=chat, user_id=user_id)
        status = member.status
        return status in ("member", "administrator", "creator")
    except Exception:
        return False


# ------------------ Domain helpers ------------------
def add_to_cart(tg_id: int, job_id: int) -> Tuple[bool, str]:
    users = load_users()
    key = str(tg_id)
    prof = users.get(key)
    if not prof:
        return False, "Profile not found."
    cart: List[int] = prof.get("cart", [])
    if job_id in cart:
        return False, "dup"
    if len(cart) >= CART_LIMIT:
        return False, "limit"
    cart.append(job_id)
    prof["cart"] = cart
    users[key] = prof
    save_users(users)
    return True, "ok"


def remove_from_cart(tg_id: int, job_id: int) -> Tuple[bool, str]:
    users = load_users()
    key = str(tg_id)
    prof = users.get(key)
    if not prof:
        return False, "Profile not found."
    cart: List[int] = prof.get("cart", [])
    if job_id not in cart:
        return False, "not_in"
    cart.remove(job_id)
    prof["cart"] = cart
    users[key] = prof
    save_users(users)
    return True, "ok"


def dislike_job(tg_id: int, job_id: int) -> Tuple[bool, str]:
    users = load_users()
    key = str(tg_id)
    prof = users.get(key)
    if not prof:
        return False, "Profile not found."
    disliked: List[int] = prof.get("disliked", [])
    if job_id in disliked:
        return False, "dup"
    disliked.append(job_id)
    prof["disliked"] = disliked
    users[key] = prof
    save_users(users)
    return True, "ok"


def find_job_by_id(job_id: int) -> Optional[Dict[str, Any]]:
    for j in load_jobs():
        if j["job_id"] == job_id:
            return j
    return None


def jobs_header_text(lang: str, total: int, page: int, per_page: int = 10) -> str:
    pages = max(1, (total + per_page - 1) // per_page)
    start = page * per_page + 1 if total else 0
    end = min((page + 1) * per_page, total)
    return t(lang, "jobs_header", total=total, page=page + 1, pages=pages, start=start, end=end)


def jobs_page_text(jobs_list: List[Dict[str, Any]], page: int, per_page: int = 10) -> str:
    start = page * per_page
    end = min(start + per_page, len(jobs_list))
    lines = []
    for i, job in enumerate(jobs_list[start:end], start=1):
        lines.append(f"{i}. {job.get('name', '')}")
    return "\n".join(lines)



# ------------------ Handlers ------------------
@dp.message(CommandStart())
async def start_cmd(msg: Message, state: FSMContext):
    _ensure_files()
    user = get_or_create_profile(msg.from_user.id)

    # 1) Agar til tanlanmagan bo'lsa — til tanlash
    if not user.get("lang"):
        await msg.answer(t("uz", "choose_language_title"), reply_markup=language_kb())
        return

    lang = user["lang"]

    # 2) Agar ro'yxatdan o'tgan bo'lsa — menyuga
    if user.get("registered"):
        full_name = (user.get("first_name") or "") + " " + (user.get("last_name") or "")
        await msg.answer(t(lang, "hello_registered", full_name=full_name.strip()), reply_markup=main_menu_kb(lang))
        return

    # 3) Aks holda — kanalga a'zo bo'lish bosqichi
    await msg.answer(t(lang, "ask_join"), reply_markup=join_channel_kb(lang))


@dp.callback_query(F.data.startswith("setlang:"))
async def set_language(clb: CallbackQuery):
    _, lang_code = clb.data.split(":")
    if lang_code not in ("uz", "en", "ru"):
        lang_code = "uz"
    update_profile(clb.from_user.id, lang=lang_code)

    user = get_or_create_profile(clb.from_user.id)
    if user.get("registered"):
        full_name = (user.get("first_name") or "") + " " + (user.get("last_name") or "")
        await clb.message.edit_text(t(lang_code, "hello_registered", full_name=full_name.strip()))
        await clb.message.answer(t(lang_code, "menu_view_jobs"), reply_markup=main_menu_kb(lang_code))
        await clb.answer()
        return

    await clb.message.edit_text(t(lang_code, "ask_join"), reply_markup=join_channel_kb(lang_code))
    await clb.answer()


@dp.callback_query(F.data == "check_join")
async def on_check_join(clb: CallbackQuery, state: FSMContext):
    lang = get_or_create_profile(clb.from_user.id).get("lang") or "uz"
    ok = await is_member(clb.from_user.id)
    if not ok:
        await clb.message.edit_text(t(lang, "not_joined"), reply_markup=join_channel_kb(lang))
        await clb.answer()
        return

    await state.set_state(Reg.waiting_password)
    await clb.message.edit_text(t(lang, "ask_password"))
    await clb.answer()


@dp.message(Reg.waiting_password)
async def on_password(msg: Message, state: FSMContext):
    lang = get_or_create_profile(msg.from_user.id).get("lang") or "uz"
    pwd = (msg.text or "").strip()
    if not pwd:
        await msg.answer(t(lang, "ask_password"))
        return
    passwords = load_passwords()
    if pwd not in passwords:
        await msg.answer(t(lang, "wrong_password"))
        return

    await state.set_state(Reg.waiting_first_name)
    await msg.answer(t(lang, "ask_first_name"), reply_markup=ReplyKeyboardRemove())


@dp.message(Reg.waiting_first_name)
async def on_first_name(msg: Message, state: FSMContext):
    lang = get_or_create_profile(msg.from_user.id).get("lang") or "uz"
    first_name = (msg.text or "").strip()
    if not first_name:
        await msg.answer(t(lang, "ask_first_name"))
        return
    await state.update_data(first_name=first_name)
    await state.set_state(Reg.waiting_last_name)
    await msg.answer(t(lang, "ask_last_name"))


@dp.message(Reg.waiting_last_name)
async def on_last_name(msg: Message, state: FSMContext):
    lang = get_or_create_profile(msg.from_user.id).get("lang") or "uz"
    last_name = (msg.text or "").strip()
    if not last_name:
        await msg.answer(t(lang, "ask_last_name"))
        return
    await state.update_data(last_name=last_name)
    await state.set_state(Reg.waiting_phone)
    await msg.answer(t(lang, "ask_phone"), reply_markup=contact_request_kb(lang))


@dp.message(Reg.waiting_phone, F.contact)
async def on_phone_contact(msg: Message, state: FSMContext):
    lang = get_or_create_profile(msg.from_user.id).get("lang") or "uz"
    phone = (msg.contact.phone_number or "").strip()
    data = await state.get_data()
    update_profile(
        msg.from_user.id,
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        phone=phone,
        registered=True
    )
    await state.clear()
    await msg.answer(t(lang, "reg_success"), reply_markup=main_menu_kb(lang))


@dp.message(Reg.waiting_phone)
async def on_phone_text(msg: Message, state: FSMContext):
    lang = get_or_create_profile(msg.from_user.id).get("lang") or "uz"
    text_in = (msg.text or "").strip()

    # "Qo'lda kiritaman" tugmasi bosilganda faqat format ko'rsatamiz
    if text_in == t(lang, "btn_manual_phone"):
        await msg.answer(t(lang, "ask_phone"))
        return

    # Telefon raqami formati (faqat +998 ga mos)
    pattern = r"^\+998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$"
    if not re.match(pattern, text_in):
        await msg.answer(t(lang, "phone_bad_format"))
        return

    data = await state.get_data()
    update_profile(
        msg.from_user.id,
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        phone=text_in,
        registered=True
    )
    await state.clear()
    await msg.answer(t(lang, "reg_success"), reply_markup=main_menu_kb(lang))

def job_source_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔸 Hh.uz", callback_data="src:hh")],
        [InlineKeyboardButton(text="🔸 LinkedIn", callback_data="src:linkedin")],
        [InlineKeyboardButton(text="🔸 Olx.uz", callback_data="src:olx")],
        [InlineKeyboardButton(text="🔸 Ish.UZ", callback_data="src:ishuz")],
        [InlineKeyboardButton(text="🌐 Hammasi", callback_data="src:all")],
    ])

# -------- Main menu actions --------
# def job_source_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔸 Hh.uz", callback_data="src:hh")],
        [InlineKeyboardButton(text="🔸 LinkedIn", callback_data="src:linkedin")],
        [InlineKeyboardButton(text="🔸 Olx.uz", callback_data="src:olx")],
        [InlineKeyboardButton(text="🔸 Ish.UZ", callback_data="src:ishuz")],
        [InlineKeyboardButton(text="🌐 Hammasi", callback_data="src:all")],
    ])


@dp.message(F.text.in_({
    LANG_TEXTS["uz"]["menu_view_jobs"],
    LANG_TEXTS["en"]["menu_view_jobs"],
    LANG_TEXTS["ru"]["menu_view_jobs"]
}))
async def on_view_jobs(msg: Message):
    prof = get_or_create_profile(msg.from_user.id)
    lang = prof.get("lang") or "uz"

    if not prof.get("registered"):
        await msg.answer(t(lang, "not_registered"))
        return

    await msg.answer(
        "Qaysi manbadan ish ko‘rmoqchisiz?",
        reply_markup=job_source_kb(lang)
    )


@dp.message(F.text.in_({LANG_TEXTS["uz"]["menu_my_cart"], LANG_TEXTS["en"]["menu_my_cart"], LANG_TEXTS["ru"]["menu_my_cart"]}))
async def on_my_cart(msg: Message):
    prof = get_or_create_profile(msg.from_user.id)
    lang = prof.get("lang") or "uz"
    cart = prof.get("cart", [])
    if not cart:
        await msg.answer(t(lang, "cart_empty"))
        return

    for jid in list(cart):
        job = find_job_by_id(jid)
        if not job:
            continue
        txt = t(lang, "cart_item_line", name=job["name"], company=job["company"], location=job["location"], link=job["link"])
        await msg.answer(txt, reply_markup=cart_item_remove_kb(job_id=jid, lang=lang))
    await msg.answer(t(lang, "btn_back_menu"), reply_markup=main_menu_kb(lang))


@dp.message(F.text.in_({LANG_TEXTS["uz"]["menu_change_lang"], LANG_TEXTS["en"]["menu_change_lang"], LANG_TEXTS["ru"]["menu_change_lang"]}))
async def on_change_lang(msg: Message):
    # Foydalanuvchiga til tanlashni qayta ko'rsatamiz
    await msg.answer(t("uz", "choose_language_title"), reply_markup=language_kb())

@dp.callback_query(F.data.startswith("src:"))
async def on_source_select(clb: CallbackQuery):
    prof = get_or_create_profile(clb.from_user.id)
    lang = prof.get("lang") or "uz"
    source = clb.data.split(":")[1]

    jobs = load_jobs(source if source != "all" else "all")
    disliked = prof.get("disliked", [])
    visible_jobs = [j for j in jobs if j["job_id"] not in disliked]

    if not visible_jobs:
        await clb.message.edit_text(t(lang, "no_visible_jobs"))
        await clb.answer()
        return

    page = 0
    header = jobs_header_text(lang=lang, total=len(visible_jobs), page=page, per_page=10)
    listing = jobs_page_text(visible_jobs, page, per_page=10)
    text = f"{header}\n\n{listing}\n\n{t(lang, 'jobs_list_footer')}"

    await clb.message.edit_text(
        text,
        reply_markup=pagination_kb(len(visible_jobs), page, jobs_list=visible_jobs, lang=lang)
    )
    await clb.answer()

# -------- Pagination & details callbacks --------
@dp.callback_query(F.data.startswith("page:"))
async def on_page_nav(clb: CallbackQuery):
    prof = get_or_create_profile(clb.from_user.id)
    lang = prof.get("lang") or "uz"
    page = int(clb.data.split(":")[1])
    all_jobs = load_jobs()
    disliked = prof.get("disliked", [])
    visible_jobs = [j for j in all_jobs if j["job_id"] not in disliked]

    if not visible_jobs:
        await clb.message.edit_text(t(lang, "no_visible_jobs"))
        await clb.answer()
        return

    header = jobs_header_text(lang=lang, total=len(visible_jobs), page=page, per_page=10)
    listing = jobs_page_text(visible_jobs, page, per_page=10)
    text = f"{header}\n\n{listing}\n\n{t(lang, 'jobs_list_footer')}"

    await clb.message.edit_text(
        text,
        reply_markup=pagination_kb(len(visible_jobs), page, jobs_list=visible_jobs, lang=lang)
    )
    await clb.answer()


@dp.callback_query(F.data.startswith("pickid:"))
async def on_pick_item(clb: CallbackQuery):
    prof = get_or_create_profile(clb.from_user.id)
    lang = prof.get("lang") or "uz"

    _, job_id_str, page_str = clb.data.split(":")
    job_id = int(job_id_str)
    page = int(page_str)

    job = find_job_by_id(job_id)
    if not job:
        await clb.answer("Topilmadi.", show_alert=True)
        return

    # HTML tozalash (Telegramga mos)
    desc = job.get('description_html', '')
    desc = desc.replace('<p>', '\n').replace('</p>', '\n')
    desc = desc.replace('<strong>', '<b>').replace('</strong>', '</b>')
    desc = desc.replace('<em>', '<i>').replace('</em>', '</i>')

    txt = (
        f"<b>{job['name']}</b>\n"
        f"🏢 {job['company']}\n"
        f"📍 {job['location']}\n"
        f"🛠️ {job['skills']}\n\n"
        f"{desc.strip()}\n\n"
        f"🔗 <a href=\"{job['link']}\">Topshirish (Link)</a>"
    )
    await clb.message.edit_text(
        txt,
        reply_markup=job_detail_kb(job_id=job_id, page=page, lang=lang),
        disable_web_page_preview=False
    )
    await clb.answer()


@dp.callback_query(F.data.startswith("add:"))
async def on_add_to_cart(clb: CallbackQuery):
    prof = get_or_create_profile(clb.from_user.id)
    lang = prof.get("lang") or "uz"

    _, job_id_str, page_str = clb.data.split(":")
    job_id = int(job_id_str)
    ok, status = add_to_cart(clb.from_user.id, job_id)
    if not ok:
        if status == "dup":
            await clb.answer(t(lang, "added_dup"), show_alert=True)
        elif status == "limit":
            await clb.answer(t(lang, "added_limit", limit=CART_LIMIT), show_alert=True)
        else:
            await clb.answer("Error", show_alert=True)
    else:
        await clb.answer(t(lang, "added_ok"), show_alert=False)

    # qayta tafsilot qoldiramiz (o'zgarmaydi)
    job = find_job_by_id(job_id)
    if job:
        desc = job.get('description_html', '')
        desc = desc.replace('<p>', '\n').replace('</p>', '\n')
        desc = desc.replace('<strong>', '<b>').replace('</strong>', '</b>')
        desc = desc.replace('<em>', '<i>').replace('</em>', '</i>')
        txt = (
            f"<b>{job['name']}</b>\n"
            f"🏢 {job['company']}\n"
            f"📍 {job['location']}\n"
            f"🛠️ {job['skills']}\n\n"
            f"{desc.strip()}\n\n"
            f"🔗 <a href=\"{job['link']}\">Topshirish (Link)</a>"
        )
        page = int(page_str)
        await clb.message.edit_text(
            txt,
            reply_markup=job_detail_kb(job_id=job_id, page=page, lang=lang),
            disable_web_page_preview=False
        )


@dp.callback_query(F.data.startswith("dislike:"))
async def on_dislike_job(clb: CallbackQuery):
    prof = get_or_create_profile(clb.from_user.id)
    lang = prof.get("lang") or "uz"

    _, job_id_str, page_str = clb.data.split(":")
    job_id = int(job_id_str)
    page = int(page_str)

    ok, status = dislike_job(clb.from_user.id, job_id)
    if not ok and status == "dup":
        await clb.answer(t(lang, "disliked_dup"), show_alert=False)
    else:
        await clb.answer(t(lang, "disliked_ok"), show_alert=False)

    # Ro'yxatni yangilab chizamiz
    all_jobs = load_jobs()
    disliked = get_or_create_profile(clb.from_user.id).get("disliked", [])
    visible_jobs = [j for j in all_jobs if j["job_id"] not in disliked]

    if not visible_jobs:
        await clb.message.edit_text(t(lang, "no_visible_jobs"))
        return

    if page * 10 >= len(visible_jobs):
        page = max(0, page - 1)

    header = jobs_header_text(lang=lang, total=len(visible_jobs), page=page, per_page=10)
    listing = jobs_page_text(visible_jobs, page, per_page=10)
    text = f"{header}\n\n{listing}\n\n{t(lang, 'jobs_list_footer')}"

    await clb.message.edit_text(
        text,
        reply_markup=pagination_kb(len(visible_jobs), page, jobs_list=visible_jobs, lang=lang)
    )


@dp.callback_query(F.data.startswith("rm:"))
async def on_remove_item(clb: CallbackQuery):
    prof = get_or_create_profile(clb.from_user.id)
    lang = prof.get("lang") or "uz"

    _, job_id_str = clb.data.split(":")
    job_id = int(job_id_str)
    ok, _ = remove_from_cart(clb.from_user.id, job_id)
    if ok:
        await clb.answer(t(lang, "removed_ok"), show_alert=False)
        await clb.message.edit_text(t(lang, "removed_ok"))
        await clb.message.answer(t(lang, "btn_back_menu"), reply_markup=main_menu_kb(lang))
    else:
        await clb.answer("Error", show_alert=True)


@dp.callback_query(F.data == "back_menu")
async def on_back_menu(clb: CallbackQuery):
    lang = get_or_create_profile(clb.from_user.id).get("lang") or "uz"
    await clb.message.edit_text(t(lang, "btn_back_menu"))
    await clb.message.answer(t(lang, "btn_back_menu"), reply_markup=main_menu_kb(lang))
    await clb.answer()


# ------------------ Entry point ------------------
async def main():
    _ensure_files()
    print("Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
