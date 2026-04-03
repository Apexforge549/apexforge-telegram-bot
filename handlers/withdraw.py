from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import cancel_keyboard, withdraw_keyboard
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from database import users_collection, db

# Shows the Withdraw menu
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📤 *Withdraw Menu*\n\nSelect an option below:",
        parse_mode="Markdown",
        reply_markup=withdraw_keyboard
    )



# Main withdraw logic

transactions_collection = db["transactions"]
IST = ZoneInfo("Asia/Kolkata")

# States
W_AMOUNT, W_UPI_NAME, W_UPI_ID = range(3)


# ---------------- ENTER AMOUNT ----------------
async def withdraw_enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💸 *Withdraw*\n\n💰 Enter the amount you want to withdraw:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard
    )

    return W_AMOUNT


# ---------------- HANDLE AMOUNT ----------------
async def handle_withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    # Only numbers
    if not text.isdigit():
        await update.message.reply_text("❌ Send the amount in numbers only.")
        return W_AMOUNT

    
    # Withdraw limit check
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
    user_limit = user.get("withdraw_limit", 0)
    last_date = user.get("last_withdraw_date")

    # Reset if new day
    if last_date != today:
        user_limit = 0
        users_collection.update_one(
            {"uid": user_id},
            {
                "$set": {
                    "withdraw_limit": 0,
                    "last_withdraw_date": today
                }
            }
        )

    # Limit check
    if user_limit >= 3:
    await update.message.reply_text(
        "❌ You have reached your daily withdrawal limit (3 times).\n\nTry again tomorrow.",
        reply_markup=withdraw_keyboard
    )
    return ConversationHandler.END
    
    amount = int(text)

    # 🔥 Minimum withdrawal check
    if amount < 10:
        await update.message.reply_text(
            "❌ Minimum withdrawal amount is ₹10.",
            reply_markup=withdraw_keyboard
        )
        return ConversationHandler.END

    user_id = update.effective_user.id
    user = users_collection.find_one({"uid": user_id})

    winning_balance = user.get("winning_balance", 0)

    # Check balance
    if amount > winning_balance:
        await update.message.reply_text(
            "❌ You don't have enough withdraw balance.",
            reply_markup=withdraw_keyboard
        )
        return ConversationHandler.END

    context.user_data["amount"] = amount

    await update.message.reply_text(
        "📝 Enter your UPI Name:",
        reply_markup=cancel_keyboard
    )

    return W_UPI_NAME


# ---------------- HANDLE UPI NAME ----------------
async def handle_w_upi_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["upi_name"] = update.message.text.strip()

    await update.message.reply_text(
        "🏦 Enter your UPI ID (example: name@upi):",
        reply_markup=cancel_keyboard
    )

    return W_UPI_ID


# ---------------- HANDLE UPI ID ----------------
async def handle_w_upi_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    upi_id = update.message.text.strip()

    context.user_data["upi_id"] = upi_id

    user_id = update.effective_user.id
    user = users_collection.find_one({"uid": user_id})

    txn_id = str(uuid.uuid4())[:8]
    now_ist = datetime.now(IST)

    # Updating withdraw limit in the database
    users_collection.update_one(
        {"uid": user_id},
        {"$inc": {"withdraw_limit": 1}}
    )

    # SAVE TO DB
    transactions_collection.insert_one({
        "txn_id": txn_id,
        "uid": user_id,
        "username": user["username"],
        "type": "withdraw",
        "amount": context.user_data["amount"],
        "upi_name": context.user_data["upi_name"],
        "upi_id": context.user_data["upi_id"],
        "status": "pending",
        "created_at": now_ist
    })

    context.user_data.clear()

    await update.message.reply_text(
        "✅ *Withdrawal Request Submitted*\n\n"
        "⏳ It will be processed within *6 hours*.\n"
        "💸 Please wait patiently.",
        parse_mode="Markdown",
        reply_markup=withdraw_keyboard
    )

    return ConversationHandler.END


# ---------------- CANCEL ----------------
async def cancel_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Withdrawal cancelled.\n\nReturning to Withdraw Menu.",
        reply_markup=withdraw_keyboard
    )

    return ConversationHandler.END



# ---------------- Withdraw history ----------------
#transactions_collection = db["transactions"]
#IST = ZoneInfo("Asia/Kolkata")


async def withdraw_history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    # Fetch only THIS user's withdraw transactions
    withdraws = list(
        transactions_collection.find(
            {
                "uid": user_id,
                "type": "withdraw"
            }
        ).sort("created_at", -1).limit(5)
    )

    if not withdraws:
        await update.message.reply_text(
            "📭 *No withdraw history found.*",
            parse_mode="Markdown"
        )
        return

    message = "📜 *Your Recent Withdraw History*\n\n"

    for txn in withdraws:

        txn_id = txn.get("txn_id", "N/A")
        amount = txn.get("amount", 0)
        status = txn.get("status", "pending").capitalize()

        created_at = txn.get("created_at")

        # Convert to IST
        if created_at:
            created_at = created_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(IST)
            date_str = created_at.strftime("%d %b %Y, %I:%M %p")
        else:
            date_str = "N/A"

        message += (
            f"🆔 *Txn ID:* `{txn_id}`\n"
            f"💰 *Amount:* ₹{amount}\n"
            f"📅 *Date:* {date_str}\n"
            f"📊 *Status:* {status}\n\n"
        )

    await update.message.reply_text(message, parse_mode="Markdown")
