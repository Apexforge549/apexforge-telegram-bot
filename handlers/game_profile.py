from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import users_collection
from keyboards import cancel_keyboard

# States
G_UID, G_USERNAME = range(2)


# ---------------- MAIN BUTTON ----------------
async def game_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    user = users_collection.find_one({"uid": user_id})

    # Check if profile exists
    if "game_uid" in user and "game_username" in user and "wins" in user:

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ Change Game Profile", callback_data="change_profile")]
        ])

        await update.message.reply_text(
            f"🎮 *Your Game Profile*\n\n"
            f"👤 Username: {user['game_username']}\n"
            f"🆔 Game UID: {user['game_uid']}\n"
            f"🏆 Wins: {user.get('wins', 0)}",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

        return ConversationHandler.END

    # First-time setup
    await update.message.reply_text(
        "🆔 Enter your Game UID (numbers only):",
        reply_markup=cancel_keyboard
    )

    return G_UID


# ---------------- CHANGE BUTTON ----------------
async def change_profile_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🆔 Enter your new Game UID (numbers only):",
        reply_markup=cancel_keyboard
    )

    return G_UID


# ---------------- HANDLE UID ----------------
async def handle_game_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid_text = update.message.text.strip()

    # Only numbers check
    if not uid_text.isdigit():
        await update.message.reply_text("❌ Game UID must contain numbers only.")
        return G_UID

    context.user_data["game_uid"] = uid_text

    await update.message.reply_text(
        "👤 Enter your Game Username:",
        reply_markup=cancel_keyboard
    )

    return G_USERNAME


# ---------------- HANDLE USERNAME ----------------
async def handle_game_username(update: Update, context: ContextTypes.DEFAULT_TYPE):

    username = update.message.text.strip()
    user_id = update.effective_user.id

    users_collection.update_one(
        {"uid": user_id},
        {
            "$set": {
                "game_uid": context.user_data["game_uid"],
                "game_username": username,
                "wins": 0  # initialize if not present
            }
        }
    )

    context.user_data.clear()

    await update.message.reply_text(
        "✅ Game profile saved successfully!"
    )

    return ConversationHandler.END


# ---------------- CANCEL ----------------
async def cancel_game_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
      "❌ Process cancelled.",
      reply_markup=tournament_keyboard
    )

    return ConversationHandler.END
