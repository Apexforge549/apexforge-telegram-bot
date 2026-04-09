from telegram import Update
from telegram.ext import ContextTypes
from utils.admin_check import is_admin
from keyboards import manage_tournaments_keyboard


async def manage_tournaments(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        return

    await update.message.reply_text(
        "📋 *Manage Tournaments*\n\nSelect an option:",
        parse_mode="Markdown",
        reply_markup=manage_tournaments_keyboard
    )
