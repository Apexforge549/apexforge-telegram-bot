from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import db, users_collection
from keyboards import cancel_join_keyboard, tournament_keyboard
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import uuid

tournaments_collection = db["tournaments"]
transactions_collection = db["transactions"]
IST = ZoneInfo("Asia/Kolkata")

# STATE
JOIN_STATE = 0


# ---------------- SHOW TOURNAMENTS ----------------
async def join_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    user = users_collection.find_one({"uid": user_id})

    if not user.get("game_username"):
        await update.message.reply_text(
            "❌ First complete your game profile to join tournaments.",
            reply_markup=tournament_keyboard
        )
        return ConversationHandler.END

    tournaments = list(
        tournaments_collection.find({
            "status": {"$in": ["open", "full", "closed"]}
        })
    )

    if not tournaments:
        await update.message.reply_text(
            "❌ No tournaments available right now.",
            reply_markup=tournament_keyboard
        )
        return ConversationHandler.END

    for t in tournaments:

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Join", callback_data=f"join_{t['tournament_id']}")]
        ])

        await update.message.reply_text(
            f"🎮 {t['game']} {t['mode']}\n"
            f"ℹ️ Tournament Id: {t['tournament_id']}\n"
            f"💰 Entry: ₹{t['entry_fee']}\n"
            f"💸 Prize Pool: ₹{t['prize_pool']}\n"
            f"✅ Status: {t['status']}\n"
            f"👥 Slots: {len(t['joined_users'])}/{t['slots']}\n"
            f"🏆 1st Prize: ✅{t['first']}\n"
            f"🏆 Finalist Prize: ✅{t['finalist']}\n"
            f"⏱︎ Match Time: {t['match_time']}\n",
            reply_markup=keyboard
        )

    await update.message.reply_text(
        "👇 Use ❌ Cancel Joining to exit.",
        reply_markup=cancel_join_keyboard
    )

    return JOIN_STATE


# ---------------- JOIN CALLBACK ----------------
async def join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = users_collection.find_one({"uid": user_id})

    tournament_id = query.data.split("_")[1]
    tournament = tournaments_collection.find_one({"tournament_id": tournament_id})

    match_time_str = tournament["match_time"]
    today = datetime.now(IST).date()
    current_time = datetime.now(IST)
    match_time_naive = datetime.strptime(match_time_str, "%I:%M %p")
    match_time = datetime.combine(today, match_time_naive.time()).replace(tzinfo=IST)
    closing_time = match_time - timedelta(minutes=5)

    if current_time >= match_time:
        await query.message.reply_text("⏳ Tournament is already ongoing.")
        return JOIN_STATE

    if current_time >= closing_time:
        await query.message.reply_text("❌ Registration closed.")
        return JOIN_STATE

    if len(tournament["joined_users"]) >= tournament["slots"]:
        await query.message.reply_text("❌ Slots full.")
        return JOIN_STATE

    if user["game_username"] in tournament["joined_users"]:
        await query.message.reply_text("⚠️ Already joined.")
        return JOIN_STATE

    entry_fee = tournament["entry_fee"]

    deposit = user.get("deposit_balance", 0)
    winning = user.get("winning_balance", 0)
    total = deposit + winning

    if total < entry_fee:
        await query.message.reply_text("❌ Insufficient balance.")
        return JOIN_STATE

    if deposit >= entry_fee:
        deposit_deduct = entry_fee
        winning_deduct = 0
    else:
        deposit_deduct = deposit
        winning_deduct = entry_fee - deposit

    users_collection.update_one(
        {"uid": user_id},
        {
            "$inc": {
                "deposit_balance": -deposit_deduct,
                "winning_balance": -winning_deduct,
                "balance": -entry_fee
            }
        }
    )

    tournaments_collection.update_one(
        {"tournament_id": tournament_id},
        {"$addToSet": {"joined_users": user["game_username"]}}
    )

    txn_id = str(uuid.uuid4())[:8]

    transactions_collection.insert_one({
        "txn_id": txn_id,
        "uid": user_id,
        "game_username": user.get("game_username", "N/A"),
        "type": "tournament_join",
        "amount": entry_fee,
        "tournament_id": tournament_id,
        "deposit_used": deposit_deduct,
        "winning_used": winning_deduct,
        "status": "success",
        "created_at": datetime.now(IST),
        "result": "pending",
        "earning": 0
    })

    await query.message.reply_text(
        "✅ Joined successfully!",
        reply_markup=tournament_keyboard
    )

    return ConversationHandler.END


# ---------------- CANCEL ----------------
async def cancel_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Joining cancelled.\n\nReturning to Tournament Menu.",
        reply_markup=tournament_keyboard
    )

    return ConversationHandler.END
