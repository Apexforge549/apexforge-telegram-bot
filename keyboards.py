from telegram import ReplyKeyboardMarkup

# Main keyboard after registration
main_keyboard = ReplyKeyboardMarkup(
    [
        ["🏆 Tournaments"],
        ["✅ Check-in", "👤 Profile"],
        ["📊 Balance", "ℹ️ About"],
        ["📤 Withdraw", "💳 Deposit"]
    ],
    resize_keyboard=True
)
