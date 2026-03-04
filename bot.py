import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Get bot token from Railway environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Wow! The bot is connected 🚀")

# Create bot application
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Add /start command handler
app.add_handler(CommandHandler("start", start))

# Run the bot
app.run_polling()
