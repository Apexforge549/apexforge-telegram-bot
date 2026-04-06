from telegram import Update
from telegram.ext import ContextTypes
from database import db

transactions_collection = db["transactions"]
tournaments_collection = db["tournaments"]


async def tournament_history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    # 🔥 Fetch last 5 tournament joins of this user
    txns = list(
        transactions_collection.find(
            {
                "uid": user_id,
                "type": "tournament_join"
            }
        )
        .sort("created_at", -1)
        .limit(5)
    )

    if not txns:
        await update.message.reply_text("📭 No tournament history found.")
        return

    message = "📜 *Your Recent Tournament History*\n\n"

    for txn in txns:

        tournament_id = txn.get("tournament_id", "N/A")
        status = txn.get("status")
        entry_fee = txn.get("amount", 0)
        result = txn.get("result", "pending").capitalize()
        earning = txn.get("earning", 0)

        created_at = txn.get("created_at")
        if created_at:
            date_str = created_at.strftime("%d %b %Y, %I:%M %p")
        else:
            date_str = "N/A"

        # 🔥 Fetch tournament details
        tournament = tournaments_collection.find_one(
            {"tournament_id": tournament_id}
        )

        room_code = tournament.get("room_code", "Not available") if tournament else "N/A"
        room_password = tournament.get("room_password", "Not available") if tournament else "N/A"

        message += (
            f"🎮 *Tournament ID:* `{tournament_id}`\n"
            f"💰 *Entry Fee:* ₹{entry_fee}\n"
            f"🔑 *Room Code:* `{room_code}`\n"
            f"✅ *Status:* `{status}`\n"
            #f"🔒 *Room Password:* `{room_password}`\n"
            f"📅 *Date:* {date_str}\n"
            f"📊 *Result:* {result}\n"
            f"💸 *Earning:* ₹{earning}\n\n"
        )

    await update.message.reply_text(message, parse_mode="Markdown")
