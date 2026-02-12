import os
from pyrogram import enums, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
import os
from pyrogram import enums, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from config import (BANNED_USERS, SONG_DOWNLOAD_DURATION,
                    SONG_DOWNLOAD_DURATION_LIMIT)
from InflexMusic import YouTube, app
from InflexMusic.utils.decorators.language import language, languageCB
from InflexMusic.utils.formatters import convert_bytes
from InflexMusic.utils.inline.song import song_markup


@app.on_message(
    filters.command(["song"]) & filters.private & ~BANNED_USERS
)
@language
async def song_search_results(client, message: Message, _):
    if len(message.command) < 2:
        return await message.reply_text(_["song_2"])

    query = message.text.split(None, 1)[1]
    mystic = await message.reply_text(_["mahni_1"])

    try:
        title, duration_min, duration_sec, thumbnail, vidid = await YouTube.details(query)
    except:
        return await mystic.edit_text(_["mahni_3"])

    if str(duration_min) == "None":
        return await mystic.edit_text(_["song_3"])

    if int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
        return await mystic.edit_text(
            _["play_6"].format(SONG_DOWNLOAD_DURATION, duration_min)
        )

    buttons = [
        [
            InlineKeyboardButton(
                text="🎵 Audio",
                callback_data=f"song_download audio|{vidid}",
            ),
        ]
    ]

    await mystic.delete()
    return await message.reply_photo(
        thumbnail,
        caption=_["song_4"].format(title),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@app.on_callback_query(filters.regex(pattern=r"song_download") & ~BANNED_USERS)
@languageCB
async def song_download_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer("Yüklənir..")
    except:
        pass

    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    stype, vidid = callback_request.split("|")

    mystic = await CallbackQuery.edit_message_text(_["song_8"])
    yturl = f"https://www.youtube.com/watch?v={vidid}"

    try:
        file_path, status = await YouTube.download(
            yturl,
            mystic,
            songaudio=True,
            songvideo=None,
            title=None,
        )
    except Exception as e:
        return await mystic.edit_text(_["song_9"].format(e))

    if not status or not file_path:
        return await mystic.edit_text(_["song_10"])

    title, duration_min, duration_sec, thumbnail, vidid = await YouTube.details(yturl)
    thumb_image_path = await client.download_media(thumbnail)

    await mystic.edit_text(_["song_11"])
    await app.send_chat_action(
        chat_id=CallbackQuery.message.chat.id,
        action=enums.ChatAction.UPLOAD_AUDIO,
    )

    try:
        await app.send_audio(
            chat_id=CallbackQuery.message.chat.id,
            audio=file_path,
            caption=f"🎵 Başlıq: {title}\n\n🤖 Bot: @{BOT_USERNAME}",
            thumb=thumb_image_path,
            title=title,
            performer=f"@{BOT_USERNAME}",
        )
        await mystic.delete()
    except Exception as e:
        return await mystic.edit_text(_["song_10"] + f"\n\nError: {e}")

    os.remove(file_path)
