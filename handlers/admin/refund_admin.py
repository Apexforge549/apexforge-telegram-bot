from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database import db
from utils.admin_check import is_admin

tournaments_collection = db["tournaments"]
transactions_collection = db["transactions"]
users_collection = db["users"]

# 🔹 STATE
GET_TOURNAMENT_ID = 0


# ---------------- ENTRY ----------------
async def refund_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized.")
        return ConversationHandler.END

    await update.message.reply_text("💰 Enter Tournament ID to process refund:")

    return GET_TOURNAMENT_ID


# ---------------- HANDLE TOURNAMENT ID ----------------
async def process_refund(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tournament_id = update.message.text.strip()

    # 🔍 Fetch tournament
    tournament = tournaments_collection.find_one({"tournament_id": tournament_id})

    if not tournament:
        await update.message.reply_text("❌ Tournament not found.")
        return ConversationHandler.END

    # ❌ Block if already refunded
    if tournament.get("refunded"):
        await update.message.reply_text("⚠️ This tournament is already refunded.")
        return ConversationHandler.END

    # ❌ Block if result already processed
    if tournament.get("result_processed"):
        await update.message.reply_text(
            "❌ Cannot refund. Result already processed."
        )
        return ConversationHandler.END

    # 🔍 Fetch all participants
    txns = list(
        transactions_collection.find({
            "type": "tournament_join",
            "tournament_id": tournament_id
        })
    )

    if not txns:
        await update.message.reply_text("❌ No participants found.")
        return ConversationHandler.END

    # 🔁 PROCESS EACH USER
    for txn in txns:

        uid = txn.get("uid")
        deposit_used = txn.get("deposit_used", 0)
        winning_used = txn.get("winning_used", 0)

        total_refund = deposit_used + winning_used

        # 🔄 Update user balance
        users_collection.update_one(
            {"uid": uid},
            {
                "$inc": {
                    "deposit_balance": deposit_used,
                    "winning_balance": winning_used,
                    "balance": total_refund
                }
            }
        )

        # 🔄 Update transaction
        transactions_collection.update_one(
            {"txn_id": txn["txn_id"]},
            {
                "$set": {
                    "status": "refunded",
                    "result": "refunded",
                    "earning": total_refund
                }
            }
        )

        # 📩 Notify user
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=(
                    f"💰 *Refund Processed*\n\n"
                    f"Your entry fee ₹{total_refund} for Tournament ID: {tournament_id} has been refunded."
                ),
                parse_mode="Markdown"
            )
        except:
            pass  # user may block bot

    # 🔥 AFTER LOOP → mark tournament refunded
    tournaments_collection.update_one(
        {"tournament_id": tournament_id},
        {
            "$set": {
                "status": "cancelled",
                "refunded": True
            }
        }
    )

    await update.message.reply_text(
        "✅ Refund processed successfully for all users."
    )

    return ConversationHandler.END
