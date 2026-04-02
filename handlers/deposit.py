from telegram import Update
from telegram.ext import ContextTypes
from keyboards import deposit_keyboard
import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from database import users_collection, db


async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💳 Deposit Menu\n\nSelect an option below:",
        reply_markup=deposit_keyboard
    )

# Main deposit logic
transactions_collection = db["transactions"]

IST = ZoneInfo("Asia/Kolkata")

# States
AMOUNT, WAIT_DONE, UPI_NAME, UPI_ID = range(4)

QR_FILE_ID = "AgACAgUAAxkBAAPoac00dDegXy5ZQbMHPn-nJ78_-SQAAnYPaxtFXmlWRuPI0cZyV2IBAAMCAAN4AAM6BA"


# ---------------- ENTRY ----------------
async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 *Deposit*\n\n💰 Please type the amount you want to deposit:",
        parse_mode="Markdown"
    )
    return AMOUNT


# ---------------- AMOUNT ----------------
async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text(
            "❌ Write the amount in numbers only."
        )
        return AMOUNT

    amount = int(text)

    if amount <= 0:
        await update.message.reply_text("❌ Enter a valid amount.")
        return AMOUNT

    context.user_data["amount"] = amount

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Done", callback_data="deposit_done")]
    ])

    await update.message.reply_photo(
        photo=QR_FILE_ID,
        caption=(
            "📌 *Complete Your Payment*\n\n"
            "1️⃣ Scan the QR in any UPI app\n"
            "2️⃣ Send *exact amount*\n"
            "3️⃣ Click *Done* after payment\n\n"
            "⚠️ Do not send wrong amount."
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    return WAIT_DONE


# ---------------- DONE BUTTON ----------------
async def done_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📝 Enter your *UPI Name* (Account Holder Name):",
        parse_mode="Markdown"
    )

    return UPI_NAME


# ---------------- UPI NAME ----------------
async def handle_upi_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["upi_name"] = update.message.text.strip()

    await update.message.reply_text(
        "🏦 Now enter your *UPI ID*\n\nExample: name@upi",
        parse_mode="Markdown"
    )

    return UPI_ID


# ---------------- UPI ID + SAVE ----------------
async def handle_upi_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    upi_id = update.message.text.strip()

    context.user_data["upi_id"] = upi_id

    user_id = update.effective_user.id
    user = users_collection.find_one({"uid": user_id})

    txn_id = str(uuid.uuid4())[:8]

    now_ist = datetime.now(IST)

    # SAVE TO DB
    transactions_collection.insert_one({
        "txn_id": txn_id,
        "uid": user_id,
        "username": user["username"],
        "type": "deposit",
        "amount": context.user_data["amount"],
        "upi_name": context.user_data["upi_name"],
        "upi_id": context.user_data["upi_id"],
        "status": "pending",
        "created_at": now_ist
    })

    # CLEAR SESSION DATA
    context.user_data.clear()

    await update.message.reply_text(
        "✅ *Deposit Request Submitted*\n\n"
        "⏳ Kindly wait patiently.\n"
        "Your request will be verified within *1 hours*.\n\n"
        "🙏 Thank you for your patience!",
        parse_mode="Markdown"
    )

    return ConversationHandler.END


#Logic for deposit history button
transactions_collection = db["transactions"]
IST = ZoneInfo("Asia/Kolkata")


async def deposit_history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    # Fetch only this user's deposit transactions
    deposits = list(
        transactions_collection.find(
            {
                "uid": user_id,
                "type": "deposit"
            }
        ).sort("created_at", -1).limit(5)
    )

    if not deposits:
        await update.message.reply_text(
            "📭 *No deposit history found.*",
            parse_mode="Markdown"
        )
        return

    message = "📜 *Your Recent Deposit History*\n\n"

    for txn in deposits:

        txn_id = txn.get("txn_id", "N/A")
        amount = txn.get("amount", 0)
        status = txn.get("status", "pending").capitalize()

        created_at = txn.get("created_at")

        # Convert time to IST (if stored in UTC)
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
