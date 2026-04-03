from telegram import Update
from telegram.ext import ContextTypes
from keyboards import tournament_keyboard

# Opening the Tournaments keyboard
async def tournaments(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🏆 *Tournaments Menu*\n\nSelect an option:",
        parse_mode="Markdown",
        reply_markup=tournament_keyboard
    )
