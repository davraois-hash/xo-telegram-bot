import os
import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")  # махфӣ, аз Render Env Variable
CHANNEL_USERNAME = "@learn_coding_new"  # username-и канали ту (Public!)

GAME_LINK = "https://play.google.com/store/apps/details?id=com.barnoma.xoapp1"

STATS = {
    "installs": 12500,
    "reviews": 320,
    "rating": 4.7
}

# ================= ОБУНА ПРОВЕРКА =================
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await check_subscription(user.id, context):
        keyboard = [
            [InlineKeyboardButton("📢 Обуна шудан", url="https://t.me/learn_coding_new")],
            [InlineKeyboardButton("✅ Ман обуна шудам", callback_data="check_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❗ Барои истифодаи бот аввал ба канал обуна шавед:",
            reply_markup=reply_markup
        )
        return
    await show_main_menu(update)

# ================= MAIN MENU =================
async def show_main_menu(update):
    keyboard = [
        [InlineKeyboardButton("🎮 Мини Game бо Шаҳбозҷон", callback_data="game")],
        [InlineKeyboardButton("💬 ChatBot", callback_data="chatbot")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("🔗 Линк Бозӣ", callback_data="link")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(
            "🤖 ХО БОЗИ BOT\n\nИнтихоб кунед:",
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.message.edit_text(
            "🤖 ХО БОЗИ BOT\n\nИнтихоб кунед:",
            reply_markup=reply_markup
        )

# ================= CALLBACK HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_sub":
        if await check_subscription(query.from_user.id, context):
            await show_main_menu(update)
        else:
            await query.message.reply_text("❌ Шумо ҳоло обуна нашудаед!")

    elif query.data == "stats":
        await query.message.edit_text(
            f"""📊 Статистика:

⬇️ Насбҳо: {STATS['installs']}
⭐ Отзывҳо: {STATS['reviews']}
🌟 Рейтинг: {STATS['rating']}
"""
        )

    elif query.data == "link":
        await query.message.edit_text(f"🔗 Линк бозӣ:\n{GAME_LINK}")

    elif query.data == "game":
        await start_game(query, context)

    elif query.data == "chatbot":
        await query.message.edit_text("💬 Ба ман паём фиристед, ман ҷавоб медиҳам!")

# ================= MINI GAME =================
async def start_game(query, context):
    number = random.randint(1, 5)
    context.bot_data["number"] = number
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="guess_1"),
            InlineKeyboardButton("2", callback_data="guess_2"),
            InlineKeyboardButton("3", callback_data="guess_3")
        ],
        [
            InlineKeyboardButton("4", callback_data="guess_4"),
            InlineKeyboardButton("5", callback_data="guess_5")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
        "🎮 Шаҳбозҷон рақам интихоб кард (1-5)\n\nТу фикр кун кадом рақам?",
        reply_markup=reply_markup
    )

async def guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chosen = int(query.data.split("_")[1])
    correct = context.bot_data.get("number")
    if chosen == correct:
        text = "🔥 Ту бурдӣ! Шаҳбозҷон шикаст хӯрд 😎"
    else:
        text = f"😅 Не! Рақами дуруст {correct} буд."
    await query.message.edit_text(text)

# ================= CHATBOT =================
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    reply = "😶 Манифест ҷавоб нест"
    if "салом" in text:
        reply = "Салом! 😊 Шумо чӣ хелед?"
    elif "чи хел" in text:
        reply = "Хубам, ташаккур! 😎"
    elif "xo" in text or "бозӣ" in text:
        reply = "🎮 XO Бозӣ барои шумо омода аст! /start пахш кунед"
    await update.message.reply_text(reply)

# ================= AUTO POST =================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%d.%m.%Y")
    text = f"""
📢 ХО БОЗИ UPDATE ({now})

⬇️ Насбҳо: {STATS['installs']}
⭐ Рейтинг: {STATS['rating']}
🔗 {GAME_LINK}
"""
    await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=text)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(check_sub|stats|link|game|chatbot)$"))
    app.add_handler(CallbackQueryHandler(guess_handler, pattern="^guess_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    app.job_queue.run_repeating(auto_post, interval=3600, first=10)

    print("🤖 XO PROFESSIONAL BOT started...")
    app.run_polling()

if __name__ == "__main__":
    main()
