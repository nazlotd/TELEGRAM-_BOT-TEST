import random
import json
import os
import time
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = "8445260599:AAHmIkXc3VFMCPHyzp9QW2pK2NNe0KDKoKE"
DATA_FILE = "users.json"


# ---------------- DATABASE ----------------
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_user(user_id):
    data = load_users()
    if str(user_id) not in data:
        data[str(user_id)] = {
            "coin": 100,
            "last_daily": 0
        }
        save_users(data)
    return data[str(user_id)]


def update_user(user_id, user_data):
    data = load_users()
    data[str(user_id)] = user_data
    save_users(data)


# ---------------- COMMANDS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user(user.id)
    await update.message.reply_text(
        f"Hai {user.first_name}\n"
        "Aku utility bot.\n\n"
        "/daily - claim duit\n"
        "/coin - check balance\n"
        "/dice - gamble\n"
        "/fact - random fact\n"
        "/quote - random quote\n"
        "/ping - server status"
    )


async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 Coin: {user['coin']}")


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    now = time.time()
    if now - user["last_daily"] < 86400:
        remaining = int(86400 - (now - user["last_daily"]))
        await update.message.reply_text(f"Tunggu {remaining//3600} jam lagi.")
        return

    reward = random.randint(50, 150)
    user["coin"] += reward
    user["last_daily"] = now
    update_user(user_id, user)

    await update.message.reply_text(f"🎁 Daily reward: +{reward} coin")


async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if user["coin"] < 10:
        await update.message.reply_text("Coin tak cukup (min 10)")
        return

    user_roll = random.randint(1, 6)
    bot_roll = random.randint(1, 6)

    result = f"Kau: {user_roll}\nBot: {bot_roll}\n"

    if user_roll > bot_roll:
        win = 20
        user["coin"] += win
        result += f"Menang +{win}"
    elif user_roll < bot_roll:
        lose = 15
        user["coin"] -= lose
        result += f"Kalah -{lose}"
    else:
        result += "Draw"

    update_user(user_id, user)
    await update.message.reply_text(result)


FACTS = [
    "Octopus ada 3 jantung",
    "Saturn boleh terapung atas air",
    "Tulang manusia lebih kuat dari besi (per berat)",
    "Shark lebih tua dari pokok"
]

async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(FACTS))


QUOTES = [
    "Discipline beats motivation",
    "Slow progress still progress",
    "Skill > Luck",
    "Consistency builds power"
]

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(QUOTES))


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%H:%M:%S")
    await update.message.reply_text(f"🟢 Alive | {now}")


# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("coin", coin))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("fact", fact))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("ping", ping))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
