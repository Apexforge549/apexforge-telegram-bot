import re
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from zoneinfo import ZoneInfo
from datetime import datetime
from database import users_collection
from keyboards import main_keyboard

# Conversation state
USERNAME = 1


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if users_collection is None:
        await update.message.reply_text("Database connection error.")
        return ConversationHandler.END

    user_id = update.effective_user.id

    existing_user = users_collection.find_one({"uid": user_id})

    if existing_user:
        await update.message.reply_text(
            f"Welcome back {existing_user['username']}!",
            reply_markup=main_keyboard
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Welcome to ApexForge eSports!\n\nPlease create a username (max 10 letters or numbers)."
    )

    return USERNAME


# Username handler for registration
async def set_username(update: Update, context: ContextTypes.DEFAULT_TYPE):

    username = update.message.text.strip()
    user_id = update.effective_user.id

    if len(username) > 10:
        await update.message.reply_text("Username must be maximum 10 characters.")
        return USERNAME

    if not re.match("^[A-Za-z0-9]+$", username):
        await update.message.reply_text("Username can only contain letters and numbers.")
        return USERNAME

    existing = users_collection.find_one({
        "username": {"$regex": f"^{username}$", "$options": "i"}
    })

    if existing:
        await update.message.reply_text("This username is already taken. Try another.")
        return USERNAME

    users_collection.insert_one({
        "uid": user_id,
        "username": username,
        "joined_on": datetime.utcnow(),
        "last_checkin": None,
        "balance": 20,                      # Registration bonus
        "deposit_balance": 20,              # Registration bonus
        "winning_balance": 0,
        "withdraw_limit": 0,
        "last_withdraw_date": datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
    })

    await update.message.reply_text(
        f"Registration successful! Welcome {username} 🚀\n\n🎁 You received ₹20 bonus!",
        reply_markup=main_keyboard
    )

    return ConversationHandler.END
