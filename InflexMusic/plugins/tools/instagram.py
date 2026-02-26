import os
import re
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from InflexMusic import app

# ================= SETTINGS =================
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

INSTAGRAM_REGEX = r"(https?://(?:www\.)?instagram\.com/[^\s]+)"

# ================= PROGRESS BAR =================
def progress_bar(percent: float, total: int = 10):
    filled = int(percent / 100 * total)
    empty = total - filled
    return "█" * filled + "░" * empty

# ================= HANDLER =================
@app.on_message(
    filters.regex(INSTAGRAM_REGEX)
    & (filters.private | filters.group)
)
async def instagram_handler(client, message: Message):
    link = message.text.strip()

    status_msg = await message.reply_text(
        "🙋🏻‍♀️ <b>Zəhmət olmasa gözləyin</b>\n"
        "💁🏻‍♀️ <b>Yüklənmə növü:</b> Instagram\n\n"
        "📥 <b>Yüklənir:</b> <code>0%</code>\n"
        "<code>░░░░░░░░░░</code>"
    )

    file_path = os.path.join(DOWNLOAD_DIR, f"{message.id}.mp4")

    cmd = [
        "yt-dlp",
        "-f", "best",
        "--newline",
        "-o", file_path,
        link
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        last_percent = -1

        while True:
            line = await process.stdout.readline()
            if not line:
                break

            line = line.decode("utf-8", errors="ignore")

            if "[download]" in line and "%" in line:
                match = re.search(r"(\d+(?:\.\d+)?)%", line)
                if match:
                    percent = float(match.group(1))
                    rounded = int(percent)

                    if rounded != last_percent:
                        last_percent = rounded
                        bar = progress_bar(percent)

                        await status_msg.edit(
                            "🙋🏻‍♀️ <b>Zəhmət olmasa gözləyin</b>\n"
                            "💁🏻‍♀️ <b>Yüklənmə növü:</b> Instagram\n\n"
                            f"📥 <b>Yüklənir:</b> <code>{percent:.1f}%</code>\n"
                            f"<code>{bar}</code>"
                        )

        await process.wait()

        if not os.path.exists(file_path):
            await status_msg.edit("❌ <b>Video yüklənə bilmədi</b>")
            return

        await client.send_video(
            chat_id=message.chat.id,
            video=file_path,
            caption=(
                "🙋🏻‍♀️ <b>Video hazırdır</b>\n"
                "💁🏻‍♀️ <b>Platforma növ:</b> <code>Instagram</code>"
            )
        )

        await status_msg.delete()
        os.remove(file_path)

    except Exception as e:
        await status_msg.edit(f"❌ Xəta baş verdi:\n<code>{e}</code>")
