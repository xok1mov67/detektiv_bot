# -*- coding: utf-8 -*-
"""
DETEKTIV BOT - finder_topBot
35 ta jinoyat ishi, ball tizimi (+10/+0) va hazil "to'lov darvozasi" bilan.

O'rnatish: pip install -r requirements.txt
.env fayl yarating: BOT_TOKEN=sizning_tokeningiz
Ishga tushirish: python detective_bot.py
"""

import asyncio
import json
import logging
import os
import random
import re
from pathlib import Path

from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from detective_cases import CASES

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi! .env faylga BOT_TOKEN=... qo'shing yoki "
        "serverda muhit o'zgaruvchisi sifatida o'rnating."
    )

PAYWALL_EVERY = 15
DATA_FILE = Path(__file__).parent / "user_data.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

CASES_BY_ID = {c["id"]: c for c in CASES}
user_current_case = {}


def _load_data() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            logger.warning("user_data.json o'qib bo'lmadi, bo'sh holatdan boshlanadi.")
    return {}


def _save_data(data: dict) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error("user_data.json saqlashda xatolik: %s", e)


USER_DATA = _load_data()


def get_user_record(user_id: int) -> dict:
    key = str(user_id)
    if key not in USER_DATA:
        USER_DATA[key] = {
            "score": 0, "solved_correct": 0, "solved_wrong": 0,
            "solved_case_ids": [], "gate_ack": 0,
        }
    return USER_DATA[key]


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text)


def names_match(guess: str, guilty: str) -> bool:
    g, a = normalize(guess), normalize(guilty)
    return bool(g) and (g == a or g in a or a in g)


WELCOME_TEXT = (
    "🕵️‍♂️ *DETEKTIV BOTGA XUSH KELIBSIZ!*\n\n"
    f"Bu yerda sizni {len(CASES)} ta murakkab jinoyat ishi kutmoqda.\n\n"
    "Buyruqlar:\n"
    "/ish - tasodifiy yangi ish olish\n"
    "/royxat - barcha ishlar ro'yxati\n"
    "/tanla <raqam> - ma'lum ishni tanlash\n"
    "/dalil - joriy ish dalillarini qayta ko'rish\n"
    "/javob <ism> - aybdorni taxmin qilish (to'g'ri bo'lsa +10 ball)\n"
    "/yechim - javobni ko'rish (ball berilmaydi!)\n"
    "/ball - ballaringizni ko'rish\n"
)


def format_case(case: dict) -> str:
    text = f"🔎 *ISH #{case['id']}: {case['title']}*\n\n"
    text += f"📍 Joy: {case['location']}\n🕐 Vaqt: {case['time']}\n\n"
    text += f"{case['description']}\n\n🧩 *Dalillar:*\n"
    for i, ev in enumerate(case["evidence"], 1):
        text += f"{i}. {ev}\n"
    text += "\n👤 *Gumon qilinuvchilar:*\n"
    for name, testimony in case["suspects"].items():
        text += f"\n*{name}*: {testimony}\n"
    text += f"\n❓ *Savol:* {case['question']}\n"
    text += "\nTaxminingiz tayyor bo'lsa: /javob <ism>\nJavobni ko'rish uchun: /yechim"
    return text


def format_solution(case: dict) -> str:
    return (
        f"✅ *ISH #{case['id']} YECHIMI*\n\nAybdor: *{case['guilty']}*\n\n"
        f"Mantiqiy izoh:\n{case['solution']}\n\nYangi ish uchun /ish yozing."
    )


def format_paywall(count: int) -> str:
    return (
        "🎉 *TABRIKLAYMIZ!*\n\n"
        f"Siz allaqachon *{count}* ta ishni to'g'ri yechdingiz!\n\n"
        "😄 Bu shunchaki o'yin bo'lgani uchun, keyingi ishlarni ochish "
        "uchun \"ramziy to'lov\" talab qilinadi — *haqiqiy pul emas*, "
        "shunchaki o'yin hazili!\n\nDavom etish uchun: /tolov"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown")


async def yordam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown")


def _paywall_blocking(user_id: int) -> bool:
    rec = get_user_record(user_id)
    stage = rec["solved_correct"] // PAYWALL_EVERY
    return stage > 0 and rec["gate_ack"] < stage


async def ish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if _paywall_blocking(user_id):
        rec = get_user_record(user_id)
        await update.message.reply_text(format_paywall(rec["solved_correct"]), parse_mode="Markdown")
        return
    case = random.choice(CASES)
    user_current_case[user_id] = case
    await update.message.reply_text(format_case(case), parse_mode="Markdown")


async def royxat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 *Barcha ishlar ro'yxati:*\n\n"
    for c in CASES:
        text += f"{c['id']}. {c['title']}\n"
    text += "\nTanlash uchun: /tanla <raqam>"
    await update.message.reply_text(text, parse_mode="Markdown")


async def tanla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if _paywall_blocking(user_id):
        rec = get_user_record(user_id)
        await update.message.reply_text(format_paywall(rec["solved_correct"]), parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("Ish raqamini kiriting. Misol: /tanla 5")
        return
    try:
        case_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Iltimos, raqam kiriting. Misol: /tanla 5")
        return
    if case_id not in CASES_BY_ID:
        await update.message.reply_text(f"1 dan {len(CASES)} gacha raqam kiriting. /royxat orqali ko'ring.")
        return
    case = CASES_BY_ID[case_id]
    user_current_case[user_id] = case
    await update.message.reply_text(format_case(case), parse_mode="Markdown")


async def dalil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    case = user_current_case.get(update.effective_user.id)
    if not case:
        await update.message.reply_text("Avval /ish yoki /tanla orqali ish tanlang.")
        return
    await update.message.reply_text(format_case(case), parse_mode="Markdown")


async def javob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    case = user_current_case.get(user_id)
    if not case:
        await update.message.reply_text("Avval /ish yoki /tanla orqali ish tanlang.")
        return
    if not context.args:
        await update.message.reply_text("Aybdorning ismini kiriting. Misol: /javob Nodira")
        return

    guess = " ".join(context.args)
    rec = get_user_record(user_id)
    already_scored = case["id"] in rec["solved_case_ids"]

    if names_match(guess, case["guilty"]):
        if not already_scored:
            rec["score"] += 10
            rec["solved_correct"] += 1
            rec["solved_case_ids"].append(case["id"])
            _save_data(USER_DATA)
            await update.message.reply_text(
                f"✅ *TO'G'RI!* Aybdor — {case['guilty']}.\n+10 ball! Jami: {rec['score']}\n\n"
                f"{case['solution']}\n\nYangi ish uchun /ish yozing.",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text(
                f"✅ To'g'ri (bu ish uchun ball avval berilgan). /ish yozing.",
                parse_mode="Markdown",
            )
    else:
        if not already_scored:
            rec["solved_wrong"] += 1
            _save_data(USER_DATA)
        await update.message.reply_text(
            "❌ Noto'g'ri. +0 ball.\n/dalil - dalillarni qayta ko'rish\n/yechim - javobni ko'rish"
        )


async def yechim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    case = user_current_case.get(update.effective_user.id)
    if not case:
        await update.message.reply_text("Avval /ish yoki /tanla orqali ish tanlang.")
        return
    await update.message.reply_text(format_solution(case), parse_mode="Markdown")


async def ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rec = get_user_record(update.effective_user.id)
    total = rec["solved_correct"] + rec["solved_wrong"]
    text = (
        f"🏆 *Statistikangiz*\n\nJami ball: *{rec['score']}*\n"
        f"To'g'ri: {rec['solved_correct']}\nNoto'g'ri: {rec['solved_wrong']}\n"
        f"Jami urinish: {total}\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def tolov(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    rec = get_user_record(user_id)
    stage = rec["solved_correct"] // PAYWALL_EVERY
    if stage == 0:
        await update.message.reply_text(
            f"Hozircha to'lov kerak emas — har {PAYWALL_EVERY} ta to'g'ri javobdan keyin hazil uchun chiqadi 😄"
        )
        return
    if rec["gate_ack"] >= stage:
        await update.message.reply_text("Siz allaqachon davom etishingiz mumkin! /ish yozing.")
        return
    rec["gate_ack"] = stage
    _save_data(USER_DATA)
    await update.message.reply_text(
        "💳 \"To'lov\" qabul qilindi! (haqiqiy pul emas, shunchaki hazil 😄)\n\nEndi /ish yozing!"
    )


async def health(request):
    """UptimeRobot shu manzilga ping yuborib turadi, bot 'uxlab qolmasligi' uchun."""
    return web.Response(text="Bot ishlayapti!")


async def handle_webhook(request):
    application = request.app["bot_app"]
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response(text="OK")


async def run():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("yordam", yordam))
    application.add_handler(CommandHandler("ish", ish))
    application.add_handler(CommandHandler("royxat", royxat))
    application.add_handler(CommandHandler("tanla", tanla))
    application.add_handler(CommandHandler("dalil", dalil))
    application.add_handler(CommandHandler("javob", javob))
    application.add_handler(CommandHandler("yechim", yechim))
    application.add_handler(CommandHandler("ball", ball))
    application.add_handler(CommandHandler("tolov", tolov))

    # Render "Web Service" avtomatik beradigan manzil va port.
    external_url = os.environ.get("RENDER_EXTERNAL_URL")
    port = int(os.environ.get("PORT", "10000"))

    await application.initialize()

    if external_url:
        # Serverda (Render) — webhook rejimi: bot doim yonib turadi,
        # UptimeRobot esa "/" manzilini ping qilib uni uxlashdan saqlaydi.
        webhook_url = f"{external_url}/webhook"
        await application.bot.set_webhook(url=webhook_url)
        await application.start()

        app = web.Application()
        app["bot_app"] = application
        app.router.add_post("/webhook", handle_webhook)
        app.router.add_get("/", health)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()

        print(f"Bot webhook rejimida ishga tushdi: {webhook_url}")
        while True:
            await asyncio.sleep(3600)
    else:
        # Lokal kompyuterda sinash uchun — oddiy polling rejimi.
        print("Bot lokal (polling) rejimida ishga tushdi... (@finder_topBot)")
        await application.updater.start_polling()
        await application.start()
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(run())
