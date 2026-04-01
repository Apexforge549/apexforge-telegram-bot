print("NEW DEPLOYMENT:5 WORKING")

import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler

#importing start logic from start.py
from handlers.start import start, set_username, USERNAME

#importing profile logic from profile.py
from handlers.profile import profile

#importing balance logic from balance.py
from handlers.balance import balance

#importing check in logic from check.py
from handlers.check import checkin

#importing deposit logic from deposit.py
from handlers.deposit import deposit

BOT_TOKEN = os.getenv("BOT_TOKEN")

#Bot connection
def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_username)]
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)

    #handler for profile button
    app.add_handler(MessageHandler(filters.Regex("^👤 Profile$"), profile))

    #handler for balance button
    app.add_handler(MessageHandler(filters.Regex("^📊 Balance$"), balance))

    #handler for check in button
    app.add_handler(MessageHandler(filters.Regex("^✅ Check-in$"), checkin))

    #handler for deposit button
    app.add_handler(MessageHandler(filters.Regex("^💳 Deposit$"), deposit))

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

