import os
from pyrogram import enums, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaVideo,
    Message,
)
from config import BANNED_USERS, SONG_DOWNLOAD_DURATION, SONG_DOWNLOAD_DURATION_LIMIT
from InflexMusic import YouTube, app
from InflexMusic.utils.decorators.language import language, languageCB

# 🔎 YouTube search funksiyası (yt-dlp ilə)
import yt_dlp

async def search_youtube(query: str, limit: int = 10):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        results = []
        for entry in info.get("entries", []):
            results.append({
                "title": entry.get("title"),
                "id": entry.get("id"),
                "duration": entry.get("duration"),
                "thumbnail": entry.get("thumbnail"),
            })
        return results


@app.on_message(
    filters.command(["song"]) & filters.group & ~BANNED_USERS
)
@language
async def song_commad_group(client, message: Message, _):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="📚 Kömək",
                    url=f"https://t.me/UzeyirMusic_Bot?start=song",
                ),
            ]
        ]
    )
    await message.reply_text(_["song_1"], reply_markup=upl)


@app.on_message(
    filters.command(["musiqi"]) & filters.private & ~BANNED_USERS
)
@language
async def song_commad_private(client, message: Message, _):
    await message.delete()
    url = await YouTube.url(message)
    if url:
        if not await YouTube.exists(url):
            return await message.reply_text(_["song_5"])
        mystic = await message.reply_text(_["mahni_1"])
        (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        ) = await YouTube.details(url)
        if str(duration_min) == "None":
            return await mystic.edit_text(_["song_3"])
        if int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
            return await mystic.edit_text(
                _["mahni_4"].format(SONG_DOWNLOAD_DURATION, duration_min)
            )
        buttons = [
            [
                InlineKeyboardButton(
                    text="🎵 Audio",
                    callback_data=f"song_download audio|{vidid}",
                ),
                InlineKeyboardButton(
                    text="🔏 Bağla",
                    callback_data="song_close",
                ),
            ]
        ]
        await mystic.delete()
        return await message.reply_photo(
            thumbnail,
            caption=_["song_4"].format(title),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["song_2"])
    mystic = await message.reply_text(_["mahni_1"])
    query = message.text.split(None, 1)[1]
    try:
        (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        ) = await YouTube.details(query)
    except:
        return await mystic.edit_text(_["mahni_3"])
    if str(duration_min) == "None":
        return await mystic.edit_text(_["song_3"])
    if int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
        return await mystic.edit_text(
            _["mahni_6"].format(SONG_DOWNLOAD_DURATION, duration_min)
        )
    buttons = [
        [
            InlineKeyboardButton(
                text="🎵 Audio",
                callback_data=f"song_download audio|{vidid}",
            ),
            InlineKeyboardButton(
                text="🔏 Bağla",
                callback_data="song_close",
            ),
        ]
    ]
    await mystic.delete()
    return await message.reply_photo(
        thumbnail,
        caption=_["song_4"].format(title),
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    
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
        results = await search_youtube(query, limit=10)
    except Exception as e:
        return await mystic.edit_text(_["mahni_3"] + f"\n\nError: {e}")
    
    if not results:
        return await mystic.edit_text(_["song_5"])
    
    # Mətn hissəsi: 1. Musiqi adı, 2. Musiqi adı...
    text_lines = []
    buttons = []
    row = []
    for idx, result in enumerate(results, start=1):
        text_lines.append(f"{idx}. {result['title']}")
        row.append(
            InlineKeyboardButton(
                text=str(idx),
                callback_data=f"song_choose {result['id']}"
            )
        )
        # hər 5 düymədən sonra yeni sətir
        if len(row) == 5:
            buttons.append(row)
            row = []
    # qalıq düymələr varsa əlavə et
    if row:
        buttons.append(row)
    
    await mystic.delete()
    return await message.reply_text(
        "\n".join(text_lines),
        reply_markup=InlineKeyboardMarkup(buttons),
    )

@app.on_callback_query(filters.regex(pattern=r"song_choose") & ~BANNED_USERS)
@languageCB
async def song_choose_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer("✅ Seçildi...")
    except:
        pass
    
    vidid = CallbackQuery.data.split(None, 1)[1]
    yturl = f"https://www.youtube.com/watch?v={vidid}"
    
    mystic = await CallbackQuery.edit_message_text(_["mahni_12"])
    try:
        title, duration_min, duration_sec, thumbnail, vidid = await YouTube.details(yturl)
    except:
        return await mystic.edit_text(_["mahni_3"])
    
    if int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
        return await mystic.edit_text(
            _["mahni_6"].format(SONG_DOWNLOAD_DURATION, duration_min)
        )
    
    buttons = [
        [
            InlineKeyboardButton(
                text="🎵 Audio",
                callback_data=f"song_download audio|{vidid}",
            ),
            InlineKeyboardButton(
                text="🔏 Bağla",
                callback_data="song_close",
            ),
        ]
    ]
    await mystic.delete()
    return await CallbackQuery.message.reply_photo(
        thumbnail,
        caption=_["song_4"].format(title),
        reply_markup=InlineKeyboardMarkup(buttons),
    )

@app.on_callback_query(filters.regex(pattern=r"song_download") & ~BANNED_USERS)
@languageCB
async def song_download_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer("🎵 Yüklənir..")
    except:
        pass

    callback_data = CallbackQuery.data.strip()
    # "song_download audio|vidid" formatında gəlir
    callback_request = callback_data.split(None, 1)[1]
    stype, vidid = callback_request.split("|")

    # Şəkilli mesajı silirik və yerinə yalnız yazı olan mesaj göndəririk
    await CallbackQuery.message.delete()
    mystic = await client.send_message(
        chat_id=CallbackQuery.message.chat.id, 
        text=_["song_8"]  # "Yüklənir..." yazısı
    )

    yturl = f"https://www.youtube.com/watch?v={vidid}"

    try:
        file_path, status = await YouTube.download(
            yturl,
            mystic,
            songaudio=True if stype == "audio" else None,
            songvideo=True if stype == "video" else None,
            title=None,
        )
    except Exception as e:
        return await mystic.edit_text(_["song_9"].format(e))

    if not status or not file_path:
        return await mystic.edit_text(_["song_10"])

    # Metadan başlıq və müddəti alırıq
    title, duration_min, duration_sec, thumbnail, vidid = await YouTube.details(yturl)

    # Playlist kanalı
    PLAYLIST_USERNAME = "@UzeyirPlaylist"
    playlist_button = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="🎧 Playlist", url="https://t.me/UzeyirPlaylist")]]
    )
    playlist1_button = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="✚ Məni Qrupa Əlavə Et ✚", url="https://t.me/UzeyirMusic_Bot?startgroup=true")]]
        )

    if stype == "video":
        await mystic.edit_text(_["song_11"])  # "Göndərilir..." yazısı
        await app.send_chat_action(
            chat_id=CallbackQuery.message.chat.id,
            action=enums.ChatAction.UPLOAD_VIDEO,
        )
        try:
            await client.send_video(
                chat_id=CallbackQuery.message.chat.id,
                video=file_path,
                duration=int(duration_sec),
                caption=f"🎥 <b>Başlıq:</b> {title}\n\n📢: @ByTaGiMusicBot",
                reply_markup=playlist_button
            )
            await mystic.delete()
        except Exception:
            return await mystic.edit_text(_["song_10"])
        if os.path.exists(file_path):
            os.remove(file_path)

    elif stype == "audio":
        await mystic.edit_text(_["song_11"])  # "Göndərilir..." yazısı
        await app.send_chat_action(
            chat_id=CallbackQuery.message.chat.id,
            action=enums.ChatAction.UPLOAD_AUDIO,
        )
        try:
            # İstifadəçiyə göndəririk
            await client.send_audio(
                chat_id=CallbackQuery.message.chat.id,
                audio=file_path,
                caption=f"🎵 <b>Adı:</b> {title}\n\n🤖 <b>Yüklədi:</b> @UzeyirMusic_Bot",
                title=title,
                performer="UzeyirMusic🇦🇿",
                duration=int(duration_sec),
                reply_markup=playlist_button
            )

            # Playlist kanalına göndəririk (düymə əlavə olunmayacaq)
            await client.send_audio(
                chat_id=PLAYLIST_USERNAME,
                audio=file_path,
                caption=f"🎵 <b>Adı:</b> {title}\n"
                        f"👤 <b>İstəyən:</b> {CallbackQuery.from_user.mention}\n\n"
                        f"🤖 <b>Yüklədi:</b> @UzeyirMusic_Bot",
                title=title,
                performer="UzeyirMusic🇦🇿",
                duration=int(duration_sec),
                reply_markup=playlist1_button
            )

            await mystic.delete()
        except Exception:
            return await mystic.edit_text(_["song_10"])
        if os.path.exists(file_path):
            os.remove(file_path)

# 🔏 Bağla düyməsi callback
@app.on_callback_query(filters.regex(pattern=r"song_close") & ~BANNED_USERS)
async def song_close_cb(client, CallbackQuery):
    try:
        await CallbackQuery.answer("🔏 Bağlandı")
    except:
        pass

    try:
        await CallbackQuery.message.delete()
    except:
        pass
