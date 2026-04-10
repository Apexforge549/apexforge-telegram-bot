from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import cancel_deposit_keyboard, deposit_keyboard
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from database import users_collection, db

transactions_collection = db["transactions"]
IST = ZoneInfo("Asia/Kolkata")

# States
AMOUNT, WAIT_DONE, UPI_NAME, UPI_ID = range(4)

QR_FILE_ID = "AgACAgUAAxkBAAPoac00dDegXy5ZQbMHPn-nJ78_-SQAAnYPaxtFXmlWRuPI0cZyV2IBAAMCAAN4AAM6BA"


# ---------------- MENU ----------------
async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 Deposit Menu\n\nSelect an option below:",
        reply_markup=deposit_keyboard
    )


# ---------------- ENTRY ----------------
async def deposit_enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 *Deposit*\n\n💰 Please type the amount you want to deposit:",
        parse_mode="Markdown",
        reply_markup=cancel_deposit_keyboard
    )
    return AMOUNT


# ---------------- AMOUNT ----------------
async def handle_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("❌ Write the amount in numbers only.")
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


# ---------------- DONE ----------------
async def done_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📝 Enter your *UPI Name* (Account Holder Name):"
    )

    return UPI_NAME


# ---------------- UPI NAME ----------------
async def handle_upi_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    name = update.message.text.strip()

    if len(name) < 3:
        await update.message.reply_text("❌ Enter a valid name.")
        return UPI_NAME

    context.user_data["upi_name"] = name

    await update.message.reply_text(
        "🏦 Now enter your *UPI ID*\n\nExample: name@upi",
        reply_markup=cancel_deposit_keyboard
    )

    return UPI_ID


# ---------------- UPI ID ----------------
async def handle_upi_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    upi_id = update.message.text.strip()

    if "@" not in upi_id:
        await update.message.reply_text("❌ Enter a valid UPI ID.")
        return UPI_ID

    context.user_data["upi_id"] = upi_id

    user_id = update.effective_user.id
    user = users_collection.find_one({"uid": user_id})

    username = user.get("username", "Unknown") if user else "Unknown"

    txn_id = str(uuid.uuid4())[:8]
    now_ist = datetime.now(IST)

    transactions_collection.insert_one({
        "txn_id": txn_id,
        "uid": user_id,
        "username": username,
        "type": "deposit",
        "amount": context.user_data["amount"],
        "upi_name": context.user_data["upi_name"],
        "upi_id": context.user_data["upi_id"],
        "status": "pending",
        "created_at": now_ist
    })

    context.user_data.clear()

    await update.message.reply_text(
        "✅ *Deposit Request Submitted*\n\n"
        "⏳ Kindly wait patiently.\n"
        "Your request will be verified within 1 hour.\n\n"
        "🙏 Thank you for your patience!",
        reply_markup=deposit_keyboard
    )

    return ConversationHandler.END


# ---------------- CANCEL ----------------
async def cancel_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()
    if update.message:
        await update.message.reply_text(
            "❌ Deposit cancelled.",
            reply_markup=deposit_keyboard
        )

    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "❌ Deposit cancelled.",
        )

    await query.message.reply_text(
        "❌ Deposit cancelled.\n\nReturning to Deposit Menu.",
        reply_markup=deposit_keyboard
    )

    return ConversationHandler.END


# ---------------- HISTORY ----------------
async def deposit_history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    deposits = list(
        transactions_collection.find(
            {"uid": user_id, "type": "deposit"}
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
