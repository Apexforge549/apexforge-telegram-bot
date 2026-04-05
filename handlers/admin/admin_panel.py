from telegram import Update
from telegram.ext import ContextTypes
from utils.admin_check import is_admin
from keyboards import admin_keyboard


# ---------------- ADMIN PANEL ----------------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    # 🔐 ADMIN CHECK
    if not is_admin(user_id):
        await update.message.reply_text("❌ You are not authorized to access admin panel.")
        return

    # 🛠 ADMIN MENU
    await update.message.reply_text(
        "🛠 *Admin Panel*\n\n"
        "Welcome Admin 👑\n\n"
        "Select an option below:",
        parse_mode="Markdown",
        reply_markup=admin_keyboard
    )
