# For single admin
ADMIN_ID = 123456789  # 🔁 replace with your Telegram ID

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# For multiple admins
ADMIN_IDS = [123456789, 987654321]  # 🔁 add multiple IDs

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Usage 
#from utils.admin_check import is_admin

#if not is_admin(update.effective_user.id):
    #return
