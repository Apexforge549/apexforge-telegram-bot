from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db, users_collection
from keyboards import cancel_keyboard, tournament_keyboard
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

tournaments_collection = db["tournaments"]
transactions_collection = db["transactions"]
IST = ZoneInfo("Asia/Kolkata")


# ---------------- SHOW TOURNAMENTS ----------------
async def join_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    user = users_collection.find_one({"uid": user_id})

    # 🔥 CHECK GAME PROFILE
    if not user.get("game_username"):
        await update.message.reply_text(
            "❌ First complete your game profile to join tournaments.",
            reply_markup=tournament_keyboard
        )
        return

    #tournaments = list(tournaments_collection.find({"status": "open"}))
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
        return

    # Send each tournament
    for t in tournaments:

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Join", callback_data=f"join_{t['tournament_id']}")]
        ])

        await update.message.reply_text(
            f"🎮 {t['game']} {t['mode']}\n"
            f"ℹ️ Tournament Id: {t['tournament_id']}\n"
            f"💰 Entry: ₹{t['entry_fee']}\n"
            #f"💸 Prize Pool: ₹{t['prize_pool']}\n"
            f"✅ Status: {t['status']}\n"
            f"👥 Slots: {len(t['joined_users'])}/{t['slots']}\n"
            f"🏆 1st Prize: {t['first']}\n"
            f"🏆 Finalist Prize: ✅{t['finalist']}\n"
            f"⏱︎ Match Time: {t['match_time']}\n",
            reply_markup=keyboard
        )

    # Show cancel button
    await update.message.reply_text(
    "🎯 *TOURNAMENT KEY POINTS* 🎯\n\n"

    "🔥 *1. Minimum Players Required*\n"
    "At least *10 players* must join the tournament.\n"
    "If not, don’t worry — *your entry fee will be fully refunded 💸*\n\n"

    "💰 *2. Prize Pool System*\n"
    "The prize pool will be *80% of the total entry fees collected* 🏆\n\n"

    "📢 *3. Transparency Guaranteed*\n"
    "After the match ends, the *total entry fees collected* will be shared in the Telegram channel 📊\n\n"

    "🥈 *4. Who Are Finalists?*\n"
    "All players who reach the *last round (except the winner)* are considered *Finalists* 👑",

    parse_mode="Markdown",
    reply_markup=cancel_keyboard
    )


# ---------------- JOIN CALLBACK ----------------
async def join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = users_collection.find_one({"uid": user_id})

    tournament_id = query.data.split("_")[1]
    tournament = tournaments_collection.find_one({"tournament_id": tournament_id})

    # 🔥 SLOT CHECK
    if len(tournament["joined_users"]) >= tournament["slots"]:
        await query.message.reply_text(
            "❌ Sorry the slots are full for this tournament. Kindly join another."
        )
        return

    # 🔥 DUPLICATE CHECK (by username)
    if user["game_username"] in tournament["joined_users"]:
        await query.message.reply_text("⚠️ You already joined this tournament.")
        return

    entry_fee = tournament["entry_fee"]

    deposit = user.get("deposit_balance", 0)
    winning = user.get("winning_balance", 0)
    total = deposit + winning

    # 🔥 BALANCE CHECK
    if total < entry_fee:
        await query.message.reply_text("❌ Insufficient balance.")
        return

    # 🔥 DEDUCTION LOGIC
    if deposit >= entry_fee:
        deposit_deduct = entry_fee
        winning_deduct = 0
    else:
        deposit_deduct = deposit
        winning_deduct = entry_fee - deposit

    # 🔥 UPDATE USER BALANCE
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

    # 🔥 ADD USER (game_username ONLY as you requested)
    tournaments_collection.update_one(
        {"tournament_id": tournament_id},
        {
            "$addToSet": {"joined_users": user["game_username"]}
        }
    )

    # 🔥 CHECK AND UPDATE STATUS TO FULL
    updated_tournament = tournaments_collection.find_one({"tournament_id": tournament_id})

    if len(updated_tournament["joined_users"]) >= updated_tournament["slots"]:
        tournaments_collection.update_one(
            {"tournament_id": tournament_id},
            {"$set": {"status": "full"}}
        )

    # 🔥 SAVE TRANSACTION
    txn_id = str(uuid.uuid4())[:8]

    transactions_collection.insert_one({
        "txn_id": txn_id,
        "uid": user_id,
        "type": "tournament_join",
        "amount": entry_fee,
        "tournament_id": tournament_id,
        "deposit_used": deposit_deduct,
        "winning_used": winning_deduct,
        "status": "success",
        "created_at": datetime.now(IST)
    })

    await query.message.reply_text(
        "✅ Successfully joined tournament!\n\n"
        "📢 Room details will be sent before match.",
        reply_markup=tournament_keyboard
    )


# ---------------- CANCEL ----------------
async def cancel_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Cancelled.\n\nReturning to Tournament Menu.",
        reply_markup=tournament_keyboard
    )
