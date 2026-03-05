print("NEW DEPLOYMENT:3 WORKING")

import os
import re
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from pymongo import MongoClient

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

print("TOKEN:", BOT_TOKEN)

client = None

# MongoDB connection
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("MongoDB connected successfully")
except Exception as e:
    print("MongoDB connection error:", e)

if client:
    db = client["esports_db"]
    users_collection = db["users"]
else:
    users_collection = None

# Conversation state
USERNAME = 1

# Main keyboard after registration
main_keyboard = ReplyKeyboardMarkup(
    [
        ["🎮 Join Tournament"],
        ["💰 Wallet", "👤 Profile"]
    ],
    resize_keyboard=True
)

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


# Username handler
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
        "joined_on": datetime.utcnow()
    })

    await update.message.reply_text(
        f"Registration successful! Welcome {username} 🚀",
        reply_markup=main_keyboard
    )

    return ConversationHandler.END


def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_username)]
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
