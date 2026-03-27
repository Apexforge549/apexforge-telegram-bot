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

    # Convert stored time to IST before comparing
    if last_checkin:
        last_checkin_ist = last_checkin.replace(tzinfo=ZoneInfo("UTC")).astimezone(IST)

        if last_checkin_ist.date() == today:
            await update.message.reply_text(
                "❌ You have checked in today.\nCome tomorrow. Have a nice day 😊"
            )
            return

    # Give ₹1 reward
    users_collection.update_one(
        {"uid": user_id},
        {
            "$inc": {
                "deposit_balance": 1,
                "balance": 1
            },
            "$set": {
                "last_checkin": datetime.utcnow()  # store in UTC (best practice)
            }
        }
    )

    await update.message.reply_text(
        "✅ Check-in successful!\n\n💰 ₹1 has been added to your deposit balance."
    )
