print("NEW DEPLOYMENT:5 WORKING")

import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import CallbackQueryHandler

#importing start logic from start.py
from handlers.start import start, set_username, USERNAME

#importing profile logic from profile.py and update upi id logic [delete update upi id when withdraw.py activates]
from handlers.profile import (
    profile,    # Only keep this after withdraw is activated
    update_upi_start,
    handle_upi_input,
    UPI_INPUT
)

#importing balance logic from balance.py
from handlers.balance import balance

#importing check in logic from check.py
from handlers.check import checkin

#importing back logic from back.py
from handlers.back import go_back

#importing deposit menu from deposit.py
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
    cancel_deposit,
    AMOUNT, WAIT_DONE, UPI_NAME, UPI_ID
)

# Importing the withdraw menu from withdraw.py
from handlers.withdraw import withdraw

# Importing the withdraw history
from handlers.withdraw import withdraw_history

# Importing the withdraw logic
from handlers.withdraw import (
    withdraw,
    withdraw_enter_amount,
    handle_withdraw_amount,
    handle_w_upi_name,
    handle_w_upi_id,
    cancel_withdraw,
    W_AMOUNT, W_UPI_NAME, W_UPI_ID
)

# Importing the tournaments menu from tournaments.py
from handlers.tournaments import tournaments

# Importing the game profile logic from game_profile.py
from handlers.game_profile import (
    game_profile,
    change_profile_start,
    handle_game_uid,
    handle_game_username,
    cancel_game_profile,
    G_UID, G_USERNAME
)

# Importing join tournament logic from join_tournament.py
from handlers.join_tournament import join_tournament, join_callback, cancel_join

# Importing about logic from about.py
from handlers.about import about

# Importing tournament history from tournament_history.py
from handlers.tournament_history import tournament_history

#---------------ADMIN PANEL----------------

# Importing admin panel from admin_panel.py
from handlers.admin.admin_panel import admin_panel

# Importing result.py from handlers/admin/result.py
from handlers.admin.result_admin import (
    result_start,
    get_tournament_id,
    get_winners,
    GET_TOURNAMENT_ID,
    GET_WINNERS,
    cancel_result
)

# Importing deposit_admin.py 
from handlers.admin.deposit_admin import show_deposits, handle_deposit_actions

# Importing refund_admin.py
from handlers.admin.refund_admin import (
    refund_start,
    handle_refund,
    cancel_refund,
    GET_TOURNAMENT_ID
)

#---------------ADMIN PANEL----------------

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
    

    # Conversation handler for Enter amount button in deposit button
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

    # Conversation Handler for withdraw amount button in withdraw button
    withdraw_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^💸 Withdraw Amount$"), withdraw_enter_amount)
    ],
    states={
        W_AMOUNT: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_withdraw),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_withdraw_amount)
        ],
        W_UPI_NAME: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_withdraw),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_w_upi_name)
        ],
        W_UPI_ID: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_withdraw),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_w_upi_id)
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^❌ Cancel$"), cancel_withdraw)
    ]
    )

    app.add_handler(withdraw_conv)

    # Conversation handler for game profile button
    game_profile_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^📊 Game Profile$"), game_profile),
        CallbackQueryHandler(change_profile_start, pattern="^change_profile$")
    ],
    states={
        G_UID: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_game_profile),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_game_uid)
        ],
        G_USERNAME: [
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_game_profile),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_game_username)
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^❌ Cancel$"), cancel_game_profile)
    ]
    )
    app.add_handler(game_profile_conv)

    # Conversation handler for update upi id in profile.py
    # Delete this later when withdraw.py activates
    upi_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(update_upi_start, pattern="^update_upi$")
        ],
        states={
            UPI_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_upi_input)
            ]
        },
        fallbacks=[]
    )
    app.add_handler(upi_conv)
    
    
    #---------------ADMIN PANEL----------------

    # conversation handler for results button
    result_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🏆 Results$"), result_start)
        ],
        states={
            GET_TOURNAMENT_ID: [
                MessageHandler(filters.Regex("^❌ Cancel$"), cancel_result),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_tournament_id)
            ],
            GET_WINNERS: [
                MessageHandler(filters.Regex("^❌ Cancel$"), cancel_result),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_winners)
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_result)
        ]
    )
    app.add_handler(result_conv)

    # conversation handler for refunds button
    refund_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💰 Refunds$"), refund_start)
        ],
        states={
            GET_TOURNAMENT_ID: [
                MessageHandler(filters.Regex("^❌ Cancel$"), cancel_refund),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_refund)
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_refund)
        ]
    )
    app.add_handler(refund_conv)

    #---------------ADMIN PANEL----------------

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

    # Handler for withdraw history
    app.add_handler(MessageHandler(filters.Regex("^📜 Withdraw History$"), withdraw_history))

    # Handler for tournaments menu
    app.add_handler(MessageHandler(filters.Regex("^🏆 Tournaments$"), tournaments))

    # Handler for game profile
    #app.add_handler(MessageHandler(filters.Regex("^📊 Game Profile$"), game_profile))

    # Handler for join tournament button
    app.add_handler(MessageHandler(filters.Regex("^🎮 Join Tournament$"), join_tournament))
    # Inline join button
    app.add_handler(CallbackQueryHandler(join_callback, pattern="^join_")) 
    # Cancel button
    app.add_handler(MessageHandler(filters.Regex("^❌ Cancel$"), cancel_join))

    # Handler for about button
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ About$"), about))

    # Handler for tournament history button
    app.add_handler(MessageHandler(filters.Regex("^📜 Tournament History$"), tournament_history))

    #---------------ADMIN PANEL----------------

    # Handler for admin panel
    app.add_handler(CommandHandler("admin", admin_panel))

    # Handler for deposit_admin.py
    # Button click → show deposits
    app.add_handler(MessageHandler(filters.Regex("^💳 Deposits$"), show_deposits))
    # Inline button handler
    app.add_handler(CallbackQueryHandler(handle_deposit_actions, pattern="^dep_"))
    
    #---------------ADMIN PANEL----------------

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

