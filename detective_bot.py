# -*- coding: utf-8 -*-
"""
DETEKTIV BOT - Ball, Virtual Pul va Horror Ishlar Tizimi bilan
"""

import logging
import sqlite3
import os
import http.server
import socketserver
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from detective_cases import CASES

# Telegram Bot Tokeni
BOT_TOKEN = "8545471952:AAH1tCgLuffjh-ltmdPsmu8mqX7r-kXMAno"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ RENDER PORT UCHUN WEBSERVER ============
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        logger.info(f"Port {port} da soxta veb-server ishga tushdi...")
        httpd.serve_forever()

# ============ BAZA SOZLAMALARI (SQLite) ============
def init_db():
    conn = sqlite3.connect("detective_game.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            score INTEGER DEFAULT 0,
            money INTEGER DEFAULT 0,
            unlocked_cases TEXT DEFAULT '1,2,3,4,5,6,7,8,9,10,11,12,13,14'
        )
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("detective_game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT score, money, unlocked_cases FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id, score, money) VALUES (?, 0, 0)", (user_id,))
        conn.commit()
        return 0, 0, '1,2,3,4,5,6,7,8,9,10,11,12,13,14'
    conn.close()
    return row[0], row[1], row[2]

def update_user_stats(user_id, add_score, add_money):
    score, money, unlocked = get_user(user_id)
    new_score = score + add_score
    new_money = money + add_money
    conn = sqlite3.connect("detective_game.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET score = ?, money = ? WHERE user_id = ?", (new_score, new_money, user_id))
    conn.commit()
    conn.close()

def unlock_case_for_user(user_id, case_id, price):
    score, money, unlocked = get_user(user_id)
    if money < price:
        return False
    
    unlocked_list = unlocked.split(',')
    if str(case_id) not in unlocked_list:
        unlocked_list.append(str(case_id))
    
    new_unlocked = ','.join(unlocked_list)
    new_money = money - price
    
    conn = sqlite3.connect("detective_game.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET money = ?, unlocked_cases = ? WHERE user_id = ?", (new_money, new_unlocked, user_id))
    conn.commit()
    conn.close()
    return True

# ============ BOT HANDLERLARI ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    score, money, _ = get_user(user_id)
    
    text = (
        "🕵️‍♂️ *DETEKTIV O'YINIGA XUSH KELIBSIZ!*\n\n"
        "O'zingizni haqiqiy detektiv sifatida sinab ko'ring. "
        "Jinoyatlarni fosh qiling, ballar va virtual pul ishlang!\n\n"
        f"📊 *Sizning balingiz:* {score} ball\n"
        f"💰 *Virtual hisobingiz:* {money} $\n\n"
        "Buyruqlar:\n"
        "/profil - Statistikangizni ko'rish\n"
        "/royxat - Barcha ishlar va Horror bosqichlar\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def profil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    score, money, _ = get_user(user_id)
    await update.message.reply_text(
        f"👤 *SHAXSIY PROFIL*\n\n⭐ Ball: {score}\n💰 Virtual Pul: {money}$",
        parse_mode="Markdown"
    )

async def royxat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    _, money, unlocked = get_user(user_id)
    unlocked_list = unlocked.split(',')
    
    keyboard = []
    for c in CASES:
        is_open = str(c['id']) in unlocked_list
        status = "✅ Ochiq" if is_open else f"🔒 {c['price']}$"
        btn_text = f"#{c['id']} {c['title']} ({c['level']}) - {status}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"open_{c['id']}")])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📋 *Barcha jinoyat ishlari va Horror bosqichlar:*", reply_markup=reply_markup, parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if data.startswith("open_"):
        case_id = int(data.split("_")[1])
        case = next((c for c in CASES if c['id'] == case_id), None)
        _, money, unlocked = get_user(user_id)
        
        if str(case_id) not in unlocked.split(','):
            success = unlock_case_for_user(user_id, case_id, case['price'])
            if not success:
                await query.message.reply_text(f"❌ Bu ishni ochish uchun {case['price']}$ kerak! Sizda: {money}$ bor.")
                return
            await query.message.reply_text(f"🎉 Ish #{case_id} muvaffaqiyatli ochildi!")
            
        context.user_data['current_case'] = case
        
        text = f"🔎 *ISH #{case['id']}: {case['title']}* [{case['level']}]\n\n"
        text += f"📍 Joy: {case['location']}\n🕐 Vaqt: {case['time']}\n\n{case['description']}\n\n"
        text += "🧩 *Dalillar:*\n"
        for i, ev in enumerate(case["evidence"], 1):
            text += f"{i}. {ev}\n"
        text += "\n👇 *Aybdorni tanlang:*"
        
        buttons = []
        for suspect in case['suspects'].keys():
            buttons.append([InlineKeyboardButton(suspect, callback_data=f"guess_{suspect}")])
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        
    elif data.startswith("guess_"):
        selected = data.split("_")[1]
        case = context.user_data.get('current_case')
        if not case:
            await query.message.reply_text("Iltimos, avval /royxat orqali ish tanlang.")
            return
            
        if selected == case['guilty']:
            update_user_stats(user_id, 10, 50)
            text = (
                f"🎉 *TO'G'RI TOPDINGIZ!* Aybdor: *{case['guilty']}*\n\n"
                f" Mukofot: **+10 Ball** va **+50$** virtual pul!\n\n"
                f"📝 *Yechim:* {case['solution']}"
            )
        else:
            update_user_stats(user_id, 0, 0)
            text = f"❌ *XATO!* Siz {selected}ni tanladingiz. Lekin u aybdor emas edi.\n\n+0 ball."
            
        await query.message.reply_text(text, parse_mode="Markdown")

def main():
    init_db()
    
    # Render port xatosini aylanib o'tish uchun veb-serverni alohida oqimda yurgizamiz
    threading.Thread(target=run_dummy_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profil", profil))
    app.add_handler(CommandHandler("royxat", royxat))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()