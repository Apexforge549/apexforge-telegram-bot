from telegram import Update
from telegram.ext import ContextTypes
from database import users_collection


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if users_collection is None:
        await update.message.reply_text("Database connection error.")
        return

    user_id = update.effective_user.id

    user = users_collection.find_one({"uid": user_id})

    if not user:
        await update.message.reply_text("User not registered. Please use /start first.")
        return

    # Safely get fields (default = 0 if not present)
    total_balance = user.get("balance", 0)
    deposit_balance = user.get("deposit_balance", 0)
    winning_balance = user.get("winning_balance", 0)

    message = (
        "💰 Your Wallet 💳\n\n"
        f"🤑 Total Balance: ₹{total_balance}\n"
        f"📥 Deposit Balance: ₹{deposit_balance}\n"
        f"💸 Withdraw Balance: ₹{winning_balance}"
    )

    await update.message.reply_text(message)
