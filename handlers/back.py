from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_keyboard


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🔙 Back to main menu",
        reply_markup=main_keyboard
    )
