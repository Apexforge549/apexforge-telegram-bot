from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from database import users_collection


async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if users_collection is None:
        await update.message.reply_text("Database connection error.")
        return

    user_id = update.effective_user.id

    user = users_collection.find_one({"uid": user_id})

    if not user:
        await update.message.reply_text("User not registered. Use /start first.")
        return

    now = datetime.utcnow()

    last_checkin = user.get("last_checkin")

    # Check if already checked in today
    if last_checkin:
        if last_checkin.date() == now.date():
            await update.message.reply_text(
                "You have checked in today. Come tomorrow. Have a nice day 😊"
            )
            return

    # Give reward ₹1
    users_collection.update_one(
        {"uid": user_id},
        {
            "$inc": {
                "deposit_balance": 1,
                "balance": 1
            },
            "$set": {
                "last_checkin": now
            }
        }
    )

    await update.message.reply_text(
        "✅ Check-in successful!\n\n💰 ₹1 has been added to your wallet."
  )
