from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import db
from utils.admin_check import is_admin
from datetime import datetime
from zoneinfo import ZoneInfo

transactions_collection = db["transactions"]
users_collection = db["users"]

IST = ZoneInfo("Asia/Kolkata")


# ---------------- SHOW PENDING DEPOSITS ----------------
async def show_deposits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Show deposits called")

    if not is_admin(update.effective_user.id):
        return

    # 🔥 Fetch oldest → newest (IMPORTANT)
    deposits = list(
        transactions_collection.find(
            {"type": "deposit", "status": "pending"}
        )
        .sort("created_at", 1)
        .limit(5)
    )

    if not deposits:
        await update.message.reply_text("📭 No pending deposits.")
        return

    for txn in deposits:

        txn_id = txn.get("txn_id")
        uid = txn.get("uid")
        amount = txn.get("amount")
        status = txn.get("status")
        upi_name = txn.get("upi_name", "N/A")
        upi_id = txn.get("upi_id", "N/A")

        created_at = txn.get("created_at")
        if created_at:
            created_at = created_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(IST)
            date_str = created_at.strftime("%d %b %Y, %I:%M %p")
        else:
            date_str = "N/A"

        # 🔥 INLINE BUTTONS
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Success", callback_data=f"dep_success_{txn_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"dep_reject_{txn_id}")
            ],
            [
                InlineKeyboardButton("🔁 Reverse", callback_data=f"dep_reverse_{txn_id}")
            ]
        ])

        message = (
            f"🆔 Txn ID: `{txn_id}`\n"
            f"👤 UID: `{uid}`\n"
            f"📌 Type: deposit\n"
            f"📊 Status: {status}\n"
            f"💰 Amount: ₹{amount}\n"
            f"📝 UPI Name: {upi_name}\n"
            f"🏦 UPI ID: {upi_id}\n"
            f"📅 Date: {date_str}"
        )

        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )


# ---------------- HANDLE CALLBACK ----------------
async def handle_deposit_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        return

    data = query.data.split("_")
    action = data[1]
    txn_id = data[2]

    txn = transactions_collection.find_one({"txn_id": txn_id})

    if not txn:
        await query.message.reply_text("❌ Transaction not found.")
        return

    uid = txn["uid"]
    amount = txn["amount"]
    status = txn["status"]

    user = users_collection.find_one({"uid": uid})

    # ---------------- SUCCESS ----------------
    if action == "success":

        if status != "pending":
            await query.message.reply_text(
                f"⚠️ Already {status} for txn_id={txn_id}"
            )
            return

        # Update txn
        transactions_collection.update_one(
            {"txn_id": txn_id},
            {"$set": {"status": "success"}}
        )

        # Add balance
        users_collection.update_one(
            {"uid": uid},
            {
                "$inc": {
                    "balance": amount,
                    "deposit_balance": amount
                }
            }
        )

        await query.message.reply_text("✅ Deposit marked SUCCESS and balance updated.")


    # ---------------- REJECT ----------------
    elif action == "reject":

        if status != "pending":
            await query.message.reply_text(
                f"⚠️ Already {status} for txn_id={txn_id}"
            )
            return

        transactions_collection.update_one(
            {"txn_id": txn_id},
            {"$set": {"status": "rejected"}}
        )

        await query.message.reply_text("❌ Deposit REJECTED.")


    # ---------------- REVERSE ----------------
    elif action == "reverse":

        # CASE 1 → FROM SUCCESS
        if status == "success":

            # 🔥 Safety check
            if user["balance"] < amount or user["deposit_balance"] < amount:
                await query.message.reply_text(
                    "❌ Cannot reverse. User has insufficient balance."
                )
                return

            # Deduct balance
            users_collection.update_one(
                {"uid": uid},
                {
                    "$inc": {
                        "balance": -amount,
                        "deposit_balance": -amount
                    }
                }
            )

            transactions_collection.update_one(
                {"txn_id": txn_id},
                {"$set": {"status": "pending"}}
            )

            await query.message.reply_text("🔁 Reversed SUCCESS → back to PENDING.")


        # CASE 2 → FROM REJECT
        elif status == "rejected":

            transactions_collection.update_one(
                {"txn_id": txn_id},
                {"$set": {"status": "pending"}}
            )

            await query.message.reply_text("🔁 Reversed REJECT → back to PENDING.")


        else:
            await query.message.reply_text("⚠️ Cannot reverse this state.")
