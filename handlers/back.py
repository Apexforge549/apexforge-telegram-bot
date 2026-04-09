from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_keyboard, admin_keyboard
from utils.admin_check import is_admin


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🔙 Back to main menu",
        reply_markup=main_keyboard
    )

async def admin_go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    await update.message.reply_text(
        "🔙 Back to main menu",
        reply_markup=admin_keyboard
    )
