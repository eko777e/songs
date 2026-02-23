import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from InflexMusic import app


@app.on_message(filters.command("search"))
async def search_music(client: Client, message: Message):

    # Boş yazılarsa
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
            "extract_flat": True,
            "nocheckcertificate": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)

        if not info or "entries" not in info or not info["entries"]:
            return await searching.edit_text("❌ <b>Musiqi tapılmadı.</b>")

        video = info["entries"][0]

        title = video.get("title", "Tapılmadı")
        uploader = video.get("uploader", "Naməlum")
        views = video.get("view_count") or 0
        upload_date = video.get("upload_date", "Naməlum")
        url = video.get("url")

        # Link düzəltmə
        if url and not url.startswith("http"):
            url = f"https://www.youtube.com/watch?v={url}"

        # Baxış sayı formatlama
        views = f"{int(views):,}" if isinstance(views, int) else views

        # Tarix formatlama
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
        await searching.edit_text("❌ <b>Musiqi tapılmadı və ya YouTube blokladı.</b>")
