from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters
)
from database import db
from utils.admin_check import is_admin

tournaments_collection = db["tournaments"]

# 🔹 STATES
ROOM_CODE, ROOM_PASS = range(2)


# ---------------- VIEW TOURNAMENTS ----------------
async def view_tournaments(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    tournaments = list(
        tournaments_collection.find(
            {"status": {"$in": ["open", "closed", "full", "ongoing"]}}
        )
    )

    if not tournaments:
        await update.message.reply_text("❌ No tournaments found.")
        return

    for t in tournaments:

        tid = t.get("tournament_id")

        message = (
            f"🆔 ID: {tid}\n"
            f"🎮 Game: {t.get('game')}\n"
            f"💰 Entry: ₹{t.get('entry_fee')}\n"
            f"🏆 Prize: ₹{t.get('prize_pool')}\n"
            f"👥 Slots: {len(t.get('joined_users', []))}/{t.get('slots')}\n"
            f"📊 Status: {t.get('status')}\n"
            f"⏰ Time: {t.get('match_time')}\n"
            f"🔑 Room Code: {t.get('room_code')}\n"
            f"🔒 Password: {t.get('room_password')}"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔑 Room Code", callback_data=f"roomcode_{tid}"),
                InlineKeyboardButton("🔒 Password", callback_data=f"roompass_{tid}")
            ],
            [
                InlineKeyboardButton("👥 Players", callback_data=f"players_{tid}"),
                InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_{tid}")
            ]
        ])

        await update.message.reply_text(message, reply_markup=keyboard)


# ---------------- ROOM CODE ----------------
async def set_room_code_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    tid = query.data.split("_")[1]
    context.user_data["tid"] = tid

    await query.message.reply_text("🔑 Enter Room Code:")

    return ROOM_CODE


async def save_room_code(update: Update, context: ContextTypes.DEFAULT_TYPE):

    code = update.message.text.strip()
    tid = context.user_data.get("tid")

    tournaments_collection.update_one(
        {"tournament_id": tid},
        {"$set": {"room_code": code}}
    )

    await update.message.reply_text("✅ Room code updated.")

    return ConversationHandler.END


# ---------------- ROOM PASSWORD ----------------
async def set_room_pass_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    tid = query.data.split("_")[1]
    context.user_data["tid"] = tid

    await query.message.reply_text("🔒 Enter Room Password:")

    return ROOM_PASS


async def save_room_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):

    password = update.message.text.strip()
    tid = context.user_data.get("tid")

    tournaments_collection.update_one(
        {"tournament_id": tid},
        {"$set": {"room_password": password}}
    )

    await update.message.reply_text("✅ Room password updated.")

    return ConversationHandler.END


# ---------------- PLAYERS ----------------
async def show_players(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    tid = query.data.split("_")[1]

    t = tournaments_collection.find_one({"tournament_id": tid})

    players = t.get("joined_users", [])

    if not players:
        msg = "No players joined."
    else:
        msg = ", ".join(players)

    await query.message.reply_text(f"👥 Players for {tid}:\n{msg}")


# ---------------- REFRESH ----------------
async def refresh_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    tid = query.data.split("_")[1]

    t = tournaments_collection.find_one({"tournament_id": tid})

    message = (
        f"🔄 *Updated Details*\n\n"
        f"🆔 ID: {tid}\n"
        f"💰 Entry: ₹{t.get('entry_fee')}\n"
        f"👥 Slots: {len(t.get('joined_users', []))}/{t.get('slots')}\n"
        f"📊 Status: {t.get('status')}\n"
        f"🔑 Room Code: {t.get('room_code')}\n"
        f"🔒 Password: {t.get('room_password')}"
    )

    await query.message.reply_text(message, parse_mode="Markdown")
