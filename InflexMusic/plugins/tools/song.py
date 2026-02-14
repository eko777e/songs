import os
import re
import yt_dlp

from pyrogram import enums, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaVideo,
    Message,
    CallbackQuery
)

from config import (
    BANNED_USERS,
    SONG_DOWNLOAD_DURATION,
    SONG_DOWNLOAD_DURATION_LIMIT
)

from SakkuMusic import YouTube, app
from SakkuMusic.utils.decorators.language import language, languageCB
from SakkuMusic.utils.formatters import convert_bytes
from SakkuMusic.utils.inline.song import song_markup


# ===============================
# SEARCH CACHE
# ===============================

search_cache = {}

def format_duration(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"


# ===============================
# GROUP COMMAND (UNCHANGED)
# ===============================

@app.on_message(
    filters.command(["song", "video"])
    & filters.group
    & ~BANNED_USERS
)
@language
async def song_commad_group(client, message: Message, _):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["SG_B_1"],
                    url=f"https://t.me/{app.username}?start=song",
                ),
            ]
        ]
    )
    await message.reply_text(_["song_1"], reply_markup=upl)


# ===============================
# PRIVATE SEARCH SYSTEM (NEW UI)
# ===============================

@app.on_message(
    filters.command(["song"])
    & filters.private
    & ~BANNED_USERS
)
async def song_search(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "🎵 Zəhmət olmasa mahnı adı yazın.\n\nMisal:\n/song Tural Sedali"
        )

    query = message.text.split(None, 1)[1]
    msg = await message.reply_text("🔍 **Axtarış edilir...**")

    with yt_dlp.YoutubeDL({"quiet": True}) as ytdl:
        results = ytdl.extract_info(
            f"ytsearch10:{query}",
            download=False
        )["entries"]

    if not results:
        return await msg.edit_text("❌ Heç nə tapılmadı.")

    search_cache[message.from_user.id] = {
        "results": results,
        "index": 0,
        "reporting": False
    }

    await send_result(msg, message.from_user.id)


# ===============================
# RESULT DISPLAY
# ===============================

async def send_result(msg, user_id):

    data = search_cache[user_id]
    result = data["results"][data["index"]]

    title = result["title"]
    views = result.get("view_count", 0)
    channel = result.get("uploader", "Unknown")
    thumb = result["thumbnail"]

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️ Geri", callback_data="prev"),
            InlineKeyboardButton("✅ Yüklə", callback_data="download"),
            InlineKeyboardButton("➡️ İrəli", callback_data="next"),
        ],
        [
            InlineKeyboardButton("🔍 Məlumat", callback_data="info"),
            InlineKeyboardButton("⚠️ Report", callback_data="report"),
        ],
        [
            InlineKeyboardButton("❌ Bağla", callback_data="close")
        ]
    ])

    caption = f"""
**Axtarış nəticələri:**

🎵 Adı: {title}
👁️ Baxış: {views}
📢 Yayım: {channel}
"""

    await msg.delete()
    await msg.reply_photo(
        thumb,
        caption=caption,
        reply_markup=buttons
    )


# ===============================
# CALLBACK SYSTEM
# ===============================

@app.on_callback_query(~BANNED_USERS)
async def song_ui_callbacks(client, query: CallbackQuery):

    user_id = query.from_user.id

    if user_id not in search_cache:
        return await query.answer("Sessiya bitib.", show_alert=True)

    data = search_cache[user_id]
    results = data["results"]

    # NEXT
    if query.data == "next":
        if data["index"] < len(results) - 1:
            data["index"] += 1
        await query.message.delete()
        await send_result(query.message, user_id)

    # PREV
    elif query.data == "prev":
        if data["index"] > 0:
            data["index"] -= 1
        await query.message.delete()
        await send_result(query.message, user_id)

    # CLOSE
    elif query.data == "close":
        await query.message.delete()

    # DOWNLOAD
    elif query.data == "download":

        result = results[data["index"]]
        yturl = result["webpage_url"]

        await query.message.edit_caption("⬇️ **Yüklənir...**")

        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "%(title)s.%(ext)s",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ytdl:
            info = ytdl.extract_info(yturl, download=True)
            filename = ytdl.prepare_filename(info)

        caption = f"""
🎵 **Başlıq:** {info['title']}
⏰ **Müddət:** {format_duration(info['duration'])}

📢: @ByTaGiMusicBot
"""

        await client.send_audio(
            chat_id=query.message.chat.id,
            audio=filename,
            caption=caption,
            performer="ByTaGiMusic 🇦🇿",
            title=info['title']
        )

        os.remove(filename)

    # INFO PAGE
    elif query.data == "info":

        result = results[data["index"]]

        caption = f"""
🎵 **Başlıq:** {result['title']}
⏰ **Müddət:** {format_duration(result['duration'])}
👁️ **Baxış sayı:** {result.get('view_count',0)}
📤 **Kanal:** {result.get('uploader','Unknown')}
🗓️ **Tarix:** {result.get('upload_date','Unknown')}

📢: @ByTaGiMusicBot
"""

        back = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Geri", callback_data="back_main")]
        ])

        await query.message.edit_caption(
            caption,
            reply_markup=back
        )

    # BACK
    elif query.data == "back_main":
        await query.message.delete()
        await send_result(query.message, user_id)

    # REPORT
    elif query.data == "report":

        back = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Geri", callback_data="back_main")]
        ])

        await query.message.edit_caption(
            "⚠️ **Musiqinin nə kimi xətası var?**",
            reply_markup=back
        )

        search_cache[user_id]["reporting"] = True

    await query.answer()


# ===============================
# REPORT RECEIVE
# ===============================

@app.on_message(filters.private & ~filters.command(["song"]))
async def report_receiver(client, message: Message):

    user_id = message.from_user.id

    if user_id in search_cache and search_cache[user_id].get("reporting"):

        await message.reply_text(
            "**Mesajınız təsdiq edildi** ✅\n"
            "**Admin tərəfindən xətaya baxılacaq**"
        )

        search_cache[user_id]["reporting"] = False
