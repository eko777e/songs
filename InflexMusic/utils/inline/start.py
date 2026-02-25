from pyrogram.types import InlineKeyboardButton

import config
from InflexMusic import app

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="💻 Coded By", url=f"https://t.me/Uzeyirrrrrrrrrr"
            ),
        ],
    ]
    return buttons



def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Qrupa Əlavə Et",
                url=f"https://t.me/{app.username}?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users",
            ),
            InlineKeyboardButton(text="💻 Coded by", url=f"https://t.me/Uzeyirrrrrrrrrr"),
            InlineKeyboardButton(text="🎧 Playlist", url=f"https://t.me/Uzeyirplaylist")
        ],
        [
            InlineKeyboardButton(text="💡 Komandalar", callback_data="settings_back_helper"),
        ],
        
    ]
    return buttons
