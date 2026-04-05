from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import(
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)
from database import users_collection 

# State
UPI_INPUT = 0

# ---------------- PROFILE ----------------
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Profile is triggered")

    user_id = update.effective_user.id

    if users_collection is None:
        await update.message.reply_text("Database connection error.")
        return

    user = users_collection.find_one({"uid": user_id})

    if not user:
        await update.message.reply_text("User not registered. Please use /start first.")
        return

    username = user["username"]
    uid = user["uid"]
    joined_on = user["joined_on"].strftime("%d %b %Y")

    if joined_on:
        joined_on = joined_on.strftime("%d %b %Y")
    else:
        joined_on = "N/A"

    upi_id = user.get("upi_id", "Not set")

    # 🔥 INLINE BUTTON
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Update UPI ID", callback_data="update_upi")]
    ])

    message = (
        "👤 Your Profile 📌\n\n"
        f"👤 Username: {username}\n"
        f"🆔 UID: {uid}\n"
        f"📅 Joined On: {joined_on}"
    )

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# ---------------- BUTTON CLICK ----------------
async def update_upi_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🏦 *Enter your UPI ID*\n\nExample: name@upi",
        parse_mode="Markdown"
    )

    return UPI_INPUT

# ---------------- HANDLE INPUT ----------------
async def handle_upi_input(update: Update, context: ContextTypes.DEFAULT_TYPE):

    upi_id = update.message.text.strip()
    user_id = update.effective_user.id

    users_collection.update_one(
        {"uid": user_id},
        {
            "$set": {
                "upi_id": upi_id
            }
        }
    )

    await update.message.reply_text(
        "✅ *UPI ID updated successfully!*",
        parse_mode="Markdown"
    )

    return ConversationHandler.END
