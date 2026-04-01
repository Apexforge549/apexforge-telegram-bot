print("NEW DEPLOYMENT:5 WORKING")

import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import CallbackQueryHandler

#importing start logic from start.py
from handlers.start import start, set_username, USERNAME

#importing profile logic from profile.py
from handlers.profile import profile

#importing balance logic from balance.py
from handlers.balance import balance

#importing check in logic from check.py
from handlers.check import checkin

#importing back logic from back.py
from handlers.back import go_back

#importing deposit logic from deposit.py
from handlers.deposit import deposit

#importing the main deposit logic from deposit.py
from handlers.deposit import (
    enter_amount,
    handle_amount,
    done_callback,
    handle_upi_name,
    handle_upi_id,
    AMOUNT, WAIT_DONE, UPI_NAME, UPI_ID
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------------- TEMPORARY CODE (DELETE LATER) ----------------
# This is used to get file_id of QR image
async def get_file_id(update, context):
    photo = update.message.photo[-1]
    print("FILE_ID:", photo.file_id)
# ---------------- END TEMPORARY CODE ----------------


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
    

    #handler for Enter amount button in deposit button
    deposit_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^💰 Enter Amount$"), enter_amount)
    ],
    states={
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount)],
        WAIT_DONE: [CallbackQueryHandler(done_callback, pattern="^deposit_done$")],
        UPI_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_upi_name)],
        UPI_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_upi_id)],
    },
    fallbacks=[]
    )

    app.add_handler(deposit_conv)

    
    #handler for profile button
    app.add_handler(MessageHandler(filters.Regex("^👤 Profile$"), profile))

    #handler for balance button
    app.add_handler(MessageHandler(filters.Regex("^📊 Balance$"), balance))

    #handler for check in button
    app.add_handler(MessageHandler(filters.Regex("^✅ Check-in$"), checkin))

    #handler for back button
    app.add_handler(MessageHandler(filters.Regex("^🔙 Back$"), go_back))

    #handler for deposit button
    app.add_handler(MessageHandler(filters.Regex("^💳 Deposit$"), deposit))

    # ---------------- TEMPORARY HANDLER (DELETE LATER) ----------------
    app.add_handler(MessageHandler(filters.PHOTO, get_file_id))
    # ---------------- END TEMPORARY HANDLER ----------------

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

