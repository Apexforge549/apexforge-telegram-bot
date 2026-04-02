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

#importing deposit history logic from deposit.py
from handlers.deposit import deposit_history

#importing the main deposit logic from deposit.py
from handlers.deposit import (
    deposit_enter_amount,
    handle_deposit_amount,
    done_callback,
    handle_upi_name,
    handle_upi_id,
    AMOUNT, WAIT_DONE, UPI_NAME, UPI_ID
)

# Importing the withdraw menu from withdraw.py
from handlers.withdraw import withdraw

# Importing the withdraw logic
from handlers.withdraw import (
    withdraw,
    withdraw_enter_amount,
    handle_withdraw_amount,
    handle_upi_name,
    handle_upi_id,
    cancel_withdraw,
    AMOUNT, UPI_NAME, UPI_ID
)

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
    

    #handler for Enter amount button in deposit button
    deposit_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^💰 Deposit Amount$"), deposit_enter_amount)
    ],
    states={
        AMOUNT: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_deposit),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deposit_amount)
        ],
        WAIT_DONE: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_deposit),
            CallbackQueryHandler(done_callback, pattern="^deposit_done$")
        ],
        UPI_NAME: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_deposit),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_upi_name)
        ],
        UPI_ID: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_deposit),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_upi_id)
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^❌ Cancel$"), cancel_deposit),
    ]
    )

    app.add_handler(deposit_conv)

    # Handler for withdraw amount buttion in withdraw button
    withdraw_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^💸 Withdraw Amount$"), withdraw_enter_amount)
    ],
    states={
        AMOUNT: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_withdraw),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_withdraw_amount)
        ],
        UPI_NAME: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_withdraw),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_upi_name)
        ],
        UPI_ID: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_withdraw),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_upi_id)
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^❌ Cancel$"), cancel_withdraw)
    ]
    )

    app.add_handler(withdraw_conv)


    
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

    #handler for deposit history 
    app.add_handler(MessageHandler(filters.Regex("^📜 Deposit History$"), deposit_history))

    # Handler for withdraw menu
    app.add_handler(MessageHandler(filters.Regex("^📤 Withdraw$"), withdraw))

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

