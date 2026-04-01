from telegram import Update
from telegram.ext import ContextTypes
from keyboards import deposit_keyboard


async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💳 Deposit Menu\n\nSelect an option below:",
        reply_markup=deposit_keyboard
    )
