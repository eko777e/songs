from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from InflexMusic import app

# ================= HELP PANEL =================
def help_pannel(_, START: Union[bool, int] = None):
    first = [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]
    second = [InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settingsback_helper")]
    
    mark = second if START else first

    return InlineKeyboardMarkup([mark])

# ================= HELP BACK MARKUP =================
def help_back_markup(_):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="settings_back_helper"
                )
            ]
        ]
    )

# ================= PRIVATE HELP PANEL =================
def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
            ),
        ],
    ]
    return InlineKeyboardMarkup(buttons)
