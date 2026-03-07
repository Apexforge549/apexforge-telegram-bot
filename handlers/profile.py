from telegram import Update
from telegram.ext import ContextTypes
from database import users_collection


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

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

    message = (
        "👤 Your Profile 📌\n\n"
        f"👤 Username: {username}\n"
        f"🆔 UID: {uid}\n"
        f"📅 Joined On: {joined_on}"
    )

    await update.message.reply_text(message)
