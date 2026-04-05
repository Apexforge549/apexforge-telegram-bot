from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database import db
from utils.admin_check import is_admin
from handlers.result_calc import process_tournament_result
from keyboards import cancel_keyboard, admin_keyboard

tournaments_collection = db["tournaments"]

# 🔹 STATES
GET_TOURNAMENT_ID, GET_WINNERS = range(2)


# ---------------- ENTRY POINT ----------------
async def result_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 🔐 ADMIN CHECK
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized.")
        return ConversationHandler.END

    await update.message.reply_text(
        "🏆 Enter Tournament ID to process result:",
        reply_markup=cancel_keyboard
    )

    return GET_TOURNAMENT_ID


# ---------------- GET TOURNAMENT ID ----------------
async def get_tournament_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tournament_id = update.message.text.strip()

    tournament = tournaments_collection.find_one({"tournament_id": tournament_id})

    # ❗ Tournament not found
    if not tournament:
        await update.message.reply_text("❌ Tournament not found. Try again.")
        return GET_TOURNAMENT_ID

    # ❗ Prevent double processing
    if tournament.get("result_processed"):
        await update.message.reply_text(
            "⚠️ Result already processed for this tournament.",
            reply_markup=admin_keyboard
        )
        return ConversationHandler.END

    # Save tournament_id in session
    context.user_data["tournament_id"] = tournament_id

    await update.message.reply_text(
        "👑 Enter winners (comma separated):\n\nExample:\nplayer1,player2,player3",
        reply_markup=cancel_keyboard
    )

    return GET_WINNERS


# ---------------- GET WINNERS ----------------
async def get_winners(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()
    tournament_id = context.user_data.get("tournament_id")

    tournament = tournaments_collection.find_one({"tournament_id": tournament_id})

    # 🔥 Parse winners
    winners = [w.strip() for w in text.split(",") if w.strip()]

    # ❗ Empty input check
    if not winners:
        await update.message.reply_text("❌ Invalid input. Enter at least one winner.")
        return GET_WINNERS

    # 🔥 Remove duplicates
    winners = list(set(winners))

    # ❗ Validate winners actually joined tournament
    joined_users = tournament.get("joined_users", [])

    invalid_users = [w for w in winners if w not in joined_users]

    if invalid_users:
        await update.message.reply_text(
            f"❌ These users did not join the tournament:\n{', '.join(invalid_users)}"
        )
        return GET_WINNERS

    # 🔥 SAVE WINNERS + COMPLETE
    tournaments_collection.update_one(
        {"tournament_id": tournament_id},
        {
            "$set": {
                "winners": winners,
                "status": "completed"
            }
        }
    )

    # 🔥 CALL RESULT ENGINE
    await process_tournament_result(tournament_id)

    # Clear session
    context.user_data.clear()

    await update.message.reply_text(
        "✅ Result processed successfully!\n\n💰 Rewards distributed.",
        reply_markup=admin_keyboard
    )

    return ConversationHandler.END


# ---------------- CANCEL ----------------
async def cancel_result(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Process cancelled.\n\nReturning to Admin Panel.",
        reply_markup=admin_keyboard
    )

    return ConversationHandler.END
