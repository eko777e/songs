import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from InflexMusic import app

@app.on_message(filters.command("search"))
async def search_music(client: Client, message: Message):

    # Əgər mahnı adı yazılmayıbsa
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>Axtarış etmək üçün musiqi adı yazmalısınız</b>\n"
            "✅ <b>Format:</b> /search Üzeyir Mehdizadə - Qara Gözlər",
            disable_web_page_preview=True
        )

    query = " ".join(message.command[1:])

    searching = await message.reply_text("🔍 <b>Musiqi axtarış edilir..</b>")

    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "format": "bestaudio",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]

        title = info.get("title", "Tapılmadı")
        uploader = info.get("uploader", "Naməlum")
        views = info.get("view_count", 0)
        upload_date = info.get("upload_date", "Naməlum")
        url = info.get("webpage_url", "Tapılmadı")

        # Tarixi formatlama (YYYYMMDD → YYYY-MM-DD)
        if upload_date != "Naməlum" and len(upload_date) == 8:
            upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"

        text = (
            "🎧 <b>Musiqi məlumatları tapıldı</b>\n"
            f"🎵 Adı: {title}\n"
            f"📢 Kanal: {uploader}\n"
            f"👁️ Baxış: {views}\n"
            f"📆 Tarix: {upload_date}\n"
            f"🔗 Link: {url}\n\n"
            "💻 Coded by: @Uzeyirrrrrrrrrr"
        )

        await searching.edit_text(text, disable_web_page_preview=True)

    except Exception as e:
        await searching.edit_text("❌ <b>Musiqi tapılmadı və ya xəta baş verdi.</b>")
