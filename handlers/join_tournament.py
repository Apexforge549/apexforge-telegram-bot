from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db, users_collection
from keyboards import cancel_keyboard, tournament_keyboard
from datetime import datetime, timedelta
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
            f"💸 Prize Pool: ₹{t['prize_pool']}\n"
            f"✅ Status: {t['status']}\n"
            f"👥 Slots: {len(t['joined_users'])}/{t['slots']}\n"
            f"🏆 1st Prize: ✅{t['first']}\n"
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

    "💰 **3. Dynamic Prize Pool Alert!**\n"
    "Once a tournament crosses **10 players**, the **prize pool keeps increasing with every new join** 📈🔥\n\n"

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

    # ✅ Time parsing
    match_time_str = tournament["match_time"]  # e.g. "10:00 AM"
    today = datetime.now(IST).date()
    current_time = datetime.now(IST)
    match_time_naive = datetime.strptime(match_time_str, "%I:%M %p")
    match_time = datetime.combine(today, match_time_naive.time()).replace(tzinfo=IST)
    closing_time = match_time - timedelta(minutes=5)

    # 🔥 ONGOING CHECK
    if current_time >= match_time:
        tournaments_collection.update_one(
            {"tournament_id": tournament_id},
            {"$set": {"status": "ongoing"}}
        )

        await query.message.reply_text(
            "⏳ Tournament is already ongoing.\n\nKindly join another tournament."
        )

        return

    
    # 🔥 TIME CHECK LOGIC
    if current_time >= closing_time:
        tournaments_collection.update_one(
            {"tournament_id": tournament_id},
            {"$set": {"status": "closed"}}
        )

        await query.message.reply_text(
            "❌ Registration closed. Match starting in less than 5 minutes."
        )

        return

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


    # 🔥 CALCULATE TOTAL ENTRY & PRIZE POOL

    updated_tournament = tournaments_collection.find_one({"tournament_id": tournament_id})
    entry_fee = updated_tournament.get("entry_fee", 0)
    joined_count = len(updated_tournament.get("joined_users", []))

    # Calculate total entry
    total_entry = entry_fee * joined_count

    # Calculate prize pool (80%)
    calculated_prize_pool = int(total_entry * 0.8)

    # 🔥 ALWAYS update total_entry
    update_data = {
        "total_entry": total_entry
    }

    # 🔥 ONLY update prize_pool if > 40
    if calculated_prize_pool > 50:
        update_data["prize_pool"] = calculated_prize_pool

    # 🔥 UPDATE DB
    tournaments_collection.update_one(
        {"tournament_id": tournament_id},
        {"$set": update_data}
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
    game_username = user.get("game_username", "N/A")
    upi_id = user.get("upi_id", "Not set")             # remove when withdraw will be activated

    transactions_collection.insert_one({
        "txn_id": txn_id,
        "uid": user_id,
        "game_username": game_username,
        "upi_id": upi_id,                             # remove when withdraw will be activated
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
        "✅ Successfully joined tournament!\n\n"
        "📢 Room details will be sent before match.\n"
        "📢 Check 📜 Tournament History for room details.",
        reply_markup=tournament_keyboard
    )


# ---------------- CANCEL ----------------
async def cancel_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Cancelled.\n\nReturning to Tournament Menu.",
        reply_markup=tournament_keyboard
    )
