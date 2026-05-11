from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime
import asyncio

# ========================
# BOT TOKEN
# ========================
import os

TOKEN = os.getenv("8681559208:AAEAW25l4RttVlW4EjAxKOs6P7Gbt1P_8WY")

# ========================
# STORAGE
# ========================
active_breaks = {}
smoke_breaks = {}
wc_breaks = {}

# ========================
# HELPERS
# ========================
def now():
    return datetime.now()

def format_time():
    return now().strftime("%d-%m-%Y %I:%M:%S %p")

async def send(update: Update, text: str):
    await update.message.reply_text(text)

# ========================
# CHECK ACTIVE BREAK
# ========================
def is_on_break(user_id):
    return user_id in active_breaks

# ========================
# REMINDER SYSTEM
# ========================
async def break_reminder(context, user_id):
    await asyncio.sleep(60)  # check after 1 minute

    if user_id not in active_breaks:
        return

    data = active_breaks[user_id]

    elapsed = (now() - data["start"]).seconds // 60
    allowed = data["allowed"]

    if elapsed > allowed:
        late = elapsed - allowed

        await context.bot.send_message(
            chat_id=data["chat_id"],
            text=f"""
⚠️ BREAK OVER TIME ALERT

👤 {data['name']}
📌 {data['type']}
⏰ Late By: {late} Minutes

Please use /back immediately!
"""
        )

# ========================
# START WORK
# ========================
async def startwork(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.first_name
    time = format_time()

    await send(update, f"""
✅ WORK STARTED

👤 {user}
🕒 {time}
""")

# ========================
# END WORK
# ========================
async def endwork(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.first_name
    time = format_time()

    await send(update, f"""
🛑 WORK ENDED

👤 {user}
🕒 {time}
""")

# ========================
# UNIVERSAL BREAK FUNCTION
# ========================
def start_break(user_id, user, chat_id, break_type, allowed):
    active_breaks[user_id] = {
        "type": break_type,
        "start": now(),
        "allowed": allowed,
        "chat_id": chat_id,
        "name": user
    }

# ========================
# BREAK COMMANDS
# ========================

async def breakfast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if is_on_break(user_id):
        await send(update, "❌ Already on a break. Use /back first.")
        return

    start_break(user_id, update.effective_user.first_name,
                update.effective_chat.id,
                "Breakfast Break", 45)

    await send(update, f"""
🍳 BREAKFAST STARTED

⏳ 45 Minutes Allowed
🕒 {format_time()}
""")

    asyncio.create_task(break_reminder(context, user_id))


async def lunch(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if is_on_break(user_id):
        await send(update, "❌ Already on a break. Use /back first.")
        return

    start_break(user_id, update.effective_user.first_name,
                update.effective_chat.id,
                "Lunch Break", 45)

    await send(update, f"""
🍔 LUNCH STARTED

⏳ 45 Minutes Allowed
🕒 {format_time()}
""")

    asyncio.create_task(break_reminder(context, user_id))


async def dinner(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if is_on_break(user_id):
        await send(update, "❌ Already on a break. Use /back first.")
        return

    start_break(user_id, update.effective_user.first_name,
                update.effective_chat.id,
                "Dinner Break", 30)

    await send(update, f"""
🍽 DINNER STARTED

⏳ 30 Minutes Allowed
🕒 {format_time()}
""")

    asyncio.create_task(break_reminder(context, user_id))


async def smokebreak(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if is_on_break(user_id):
        await send(update, "❌ Already on a break. Use /back first.")
        return

    smoke_breaks[user_id] = smoke_breaks.get(user_id, 0)

    if smoke_breaks[user_id] >= 5:
        await send(update, "❌ Smoke break limit reached (5/5)")
        return

    smoke_breaks[user_id] += 1

    start_break(user_id, update.effective_user.first_name,
                update.effective_chat.id,
                "Smoke Break", 10)

    await send(update, f"""
🚬 SMOKE BREAK STARTED

⏳ 10 Minutes Allowed
📊 Used: {smoke_breaks[user_id]}/5
🕒 {format_time()}
""")

    asyncio.create_task(break_reminder(context, user_id))


async def wcbreak(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if is_on_break(user_id):
        await send(update, "❌ Already on a break. Use /back first.")
        return

    wc_breaks[user_id] = wc_breaks.get(user_id, 0)

    if wc_breaks[user_id] >= 5:
        await send(update, "❌ WC break limit reached (5/5)")
        return

    wc_breaks[user_id] += 1

    start_break(user_id, update.effective_user.first_name,
                update.effective_chat.id,
                "WC Break", 20)

    await send(update, f"""
🚻 WC BREAK STARTED

⏳ 20 Minutes Allowed
📊 Used: {wc_breaks[user_id]}/5
🕒 {format_time()}
""")

    asyncio.create_task(break_reminder(context, user_id))

# ========================
# UNIVERSAL BACK BUTTON
# ========================
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in active_breaks:
        await send(update, "❌ No active break found")
        return

    data = active_breaks[user_id]

    elapsed = (now() - data["start"]).seconds // 60
    late = max(0, elapsed - data["allowed"])

    await send(update, f"""
✅ BACK TO WORK

👤 {data['name']}
📌 {data['type']}
⏱ Time Used: {elapsed} min
⚠️ Late: {late} min
🕒 {format_time()}
""")

    del active_breaks[user_id]

# ========================
# MAIN APP
# ========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("startwork", startwork))
app.add_handler(CommandHandler("endwork", endwork))
app.add_handler(CommandHandler("breakfast", breakfast))
app.add_handler(CommandHandler("lunch", lunch))
app.add_handler(CommandHandler("dinner", dinner))
app.add_handler(CommandHandler("smokebreak", smokebreak))
app.add_handler(CommandHandler("wcbreak", wcbreak))
app.add_handler(CommandHandler("back", back))

print("Bot is running...")

app.run_polling()