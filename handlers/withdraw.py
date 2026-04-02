from telegram import Update
from telegram.ext import ContextTypes
from keyboards import withdraw_keyboard

# Shows the Withdraw menu
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📤 *Withdraw Menu*\n\nSelect an option below:",
        parse_mode="Markdown",
        reply_markup=withdraw_keyboard
    )
