from telegram import Update
from telegram.ext import ContextTypes


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🎮 *Welcome to ApexForge Esports* 🚀\n\n"
        "ApexForge is your ultimate platform to compete, win, and earn real rewards through skill-based tournaments.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🏆 *What You Can Do:*\n"
        "• Join exciting tournaments\n"
        "• Compete with real players\n"
        "• Win cash rewards 💰\n"
        "• Track your stats & balance\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💳 *Payments & Wallet:*\n"
        "• Secure deposit system\n"
        "• Fast withdrawal processing\n"
        "• Transparent transaction history\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ *Important Guidelines:*\n"
        "• Only valid payments will be accepted.\n"
        "• Do not share fake payment proofs.\n"
        "• Withdrawals are processed within 1 hour after the tournament ends.\n"
        "• Follow fair play rules.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔒 *Safe & Trusted Platform*\n"
        "Your data and transactions are securely managed.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📞 *Support:*\n"
        "For any issues or queries, contact admin support @Jtshm in telegram\n\n"
        "🔥 Play Smart. Win Big. Earn More.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 **Join Our Official Telegram Channel!** 🎮\n"
        "Stay updated with **real-time tournament updates**, announcements, and important info 📢⚡\n"
        "Telegram channel: https://t.me/apexforgeesportsofficial",
        parse_mode="Markdown"
    )
