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

# 💳 Deposit keyboard
deposit_keyboard = ReplyKeyboardMarkup(
    [
        ["💰 Deposit Amount"],
        ["📜 Deposit History"],
        ["🔙 Back"]
    ],
    resize_keyboard=True
)


# 📤 Withdrawal keyboad
withdraw_keyboard = ReplyKeyboardMarkup(
    [
        ["💸 Withdraw Amount"],
        ["📜 Withdraw History"],
        ["🔙 Back"]
    ],
    resize_keyboard=True
)

# ❌ Cancel keyboard
cancel_keyboard = ReplyKeyboardMarkup(
    [["❌ Cancel"]],
    resize_keyboard=True
)

# 🏆 Tournaments keyboard
tournament_keyboard = ReplyKeyboardMarkup(
    [
        ["🎮 Join Tournament"],
        ["📊 Game Profile", "📜 Tournament History"],
        ["🔙 Back"]
    ],
    resize_keyboard=True
)

# Admin keyboard
admin_keyboard = ReplyKeyboardMarkup(
    [
        ["📌 Create Tournament", "📋 Manage Tournaments"],
        ["💳 Deposits", "💸 Withdrawals"],
        ["🏆 Results", "💰 Refunds"],
        ["🔙 Back"]
    ],
    resize_keyboard=True
)

# Manage tournaments keyboard
manage_tournaments_keyboard = ReplyKeyboardMarkup(
    [
        ["📄 View Tournaments"],
        ["✏️ Edit Tournament"],
        ["❌ Delete Tournament"],
        ["🔙 Back"]
    ],
    resize_keyboard=True
)
