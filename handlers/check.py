from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from zoneinfo import ZoneInfo
from database import users_collection

# Indian timezone
IST = ZoneInfo("Asia/Kolkata")


async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if users_collection is None:
        await update.message.reply_text("Database connection error.")
        return

    user_id = update.effective_user.id
    user = users_collection.find_one({"uid": user_id})

    if not user:
        await update.message.reply_text("User not registered. Use /start first.")
        return

    now = datetime.now(IST)
    today = now.date()

    last_checkin = user.get("last_checkin")

    # Check if already checked in today (IST)
    if last_checkin:
        last_checkin_ist = last_checkin.replace(tzinfo=ZoneInfo("UTC")).astimezone(IST)

        if last_checkin_ist.date() == today:
            await update.message.reply_text(
                "✅ You have already checked in today. Come back tomorrow!☺️"
            )
            return

    # Update DB (₹1 reward)
    users_collection.update_one(
        {"uid": user_id},
        {
            "$inc": {
                "deposit_balance": 1,
                "balance": 1
            },
            "$set": {
                "last_checkin": datetime.utcnow()
            }
        }
    )

    # Fetch updated balance
    updated_user = users_collection.find_one({"uid": user_id})
    updated_balance = updated_user.get("balance", 0)

    # ✅ First message
    await update.message.reply_text(
        "✅ You have successfully checked in! 🎉\n\n"
        "💰 Your balance has been increased by +₹1. 📈\n\n"
        "🔄 Come back tomorrow to check-in again! ⏳😊"
    )

    # ✅ Second message
    await update.message.reply_text(
        f"💵 Your updated balance is now: ₹{updated_balance} 🎊🚀\n\n"
        "🔹 Keep checking in daily to earn more rewards! 🎁"
    )
