import os
import re
import asyncio
from pyrogram import filters
from pyrogram.types import Message
import yt_dlp
from InflexMusic import app

def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


async def download_song(query):
    loop = asyncio.get_event_loop()

    search_opts = {
        "quiet": True,
        "skip_download": True,
        "default_search": "ytsearch1",
        "cookiefile": "cookies/cookies.txt",  # 🔥 ƏLAVƏ OLUNDU
    }

    download_opts = {
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "geo_bypass_country": "US",
        "cookiefile": "cookies/cookies.txt",  # 🔥 ƏLAVƏ OLUNDU
        "http_headers": {
            "User-Agent": "Mozilla/5.0",
        },
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    def run():
        # 1️⃣ Axtarış
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            video = info["entries"][0]
            url = video["webpage_url"]
            title = safe_filename(video["title"])

        # 2️⃣ Download
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([url])

        return f"{title}.mp3", title

    return await loop.run_in_executor(None, run)


@app.on_message(filters.command("song") & filters.private)
async def song_handler(client, message: Message):

    if len(message.command) < 2:
        return await message.reply("❗ İstifadə:\n/song <mahnı adı>")

    query = " ".join(message.command[1:])
    msg = await message.reply("🎧 <b>Musiqi yüklənilir...</b>")

    try:
        file_name, title = await download_song(query)

        await app.send_audio(
            chat_id=message.chat.id,
            audio=file_name,
            caption=f"🎵 **Başlıq:** {title}\n\n📢 @BotAzNews"
        )

        await msg.delete()

        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as e:
        await msg.edit(f"❌ Xəta baş verdi:\n{str(e)}")
