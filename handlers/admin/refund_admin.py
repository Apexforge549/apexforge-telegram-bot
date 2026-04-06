from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database import db
from utils.admin_check import is_admin
from keyboards import cancel_keyboard, admin_keyboard

tournaments_collection = db["tournaments"]
transactions_collection = db["transactions"]
users_collection = db["users"]

# 🔹 STATE
GET_TOURNAMENT_ID = 0


# ---------------- ENTRY ----------------
async def refund_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return ConversationHandler.END

    await update.message.reply_text(
        "💰 Enter Tournament ID to process refund:",
        reply_markup=cancel_keyboard
    )

    return GET_TOURNAMENT_ID


# ---------------- HANDLE TOURNAMENT ID ----------------
async def handle_refund(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tournament_id = update.message.text.strip()

    tournament = tournaments_collection.find_one({"tournament_id": tournament_id})

    # ❗ Tournament not found
    if not tournament:
        await update.message.reply_text("❌ Tournament not found. Try again.")
        return GET_TOURNAMENT_ID

    # ❗ Already refunded
    if tournament.get("refunded"):
        await update.message.reply_text(
            "⚠️ Refund already processed for this tournament.",
            reply_markup=admin_keyboard
        )
        return ConversationHandler.END

    # ❗ Block if result already processed
    if tournament.get("result_processed"):
        await update.message.reply_text(
            "❌ Cannot refund. Tournament result already processed.",
            reply_markup=admin_keyboard
        )
        return ConversationHandler.END

    # 🔥 Fetch all participants
    txns = list(
        transactions_collection.find(
            {
                "type": "tournament_join",
                "tournament_id": tournament_id
            }
        )
    )

    # ❗ No participants
    if not txns:
        await update.message.reply_text(
            "❌ No participants found for this tournament.",
            reply_markup=admin_keyboard
        )
        return ConversationHandler.END

    # 🔁 PROCESS ALL USERS FIRST
    for txn in txns:

        uid = txn.get("uid")
        deposit_used = txn.get("deposit_used", 0)
        winning_used = txn.get("winning_used", 0)

        total_refund = deposit_used + winning_used

        # 🔥 Refund balances
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

        # 🔥 Update transaction
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

        # 🔔 Notify user
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=(
                    "💰 *Refund Processed*\n\n"
                    f"Your entry fee ₹{total_refund} for Tournament ID: `{tournament_id}` has been refunded."
                ),
                parse_mode="Markdown"
            )
        except:
            pass  # ignore if user blocked bot

    # 🔥 AFTER LOOP → UPDATE TOURNAMENT
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
        "✅ Refund processed successfully for all users.",
        reply_markup=admin_keyboard
    )

    return ConversationHandler.END


# ---------------- CANCEL ----------------
async def cancel_refund(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Refund cancelled.\n\nReturning to Admin Panel.",
        reply_markup=admin_keyboard
    )

    return ConversationHandler.END
