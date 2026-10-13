"""بوت تليجرام لتحميل الفيديوهات من تيك توك وتويتر/X (وأي موقع يدعمه yt-dlp)."""

import asyncio
import logging
import os
import re
import tempfile
from pathlib import Path

import yt_dlp
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("video-bot")

# حد رفع الملفات للبوتات عبر Bot API الرسمي هو 50 ميجا
MAX_UPLOAD_BYTES = 50 * 1024 * 1024

URL_RE = re.compile(r"https?://\S+")
SUPPORTED_HOSTS = ("tiktok.com", "twitter.com", "x.com", "instagram.com", "youtube.com", "youtu.be")

# نحد عدد التحميلات المتزامنة عشان ما نضغط السيرفر المجاني
DOWNLOAD_SLOTS = asyncio.Semaphore(int(os.getenv("MAX_PARALLEL_DOWNLOADS", "3")))


def download_video(url: str, out_dir: str) -> Path:
    """يحمّل الفيديو ويرجع مسار الملف. يشتغل بشكل متزامن، فلازم يُستدعى داخل thread."""
    opts = {
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        # نفضّل mp4 جاهز (صوت + صورة) وحجمه أقل من حد تليجرام
        "format": "b[ext=mp4][filesize<50M]/b[filesize<50M]/bv*[filesize<45M]+ba/b",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info))
    if not path.exists():
        # بعد الدمج ممكن يتغير الامتداد
        candidates = list(Path(out_dir).glob(f"{info['id']}.*"))
        if not candidates:
            raise FileNotFoundError("ما لقيت الملف بعد التحميل")
        path = candidates[0]
    return path


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "هلا! 👋\n"
        "أرسل لي رابط فيديو من تيك توك أو تويتر (X) وأرجع لك الفيديو بدون علامة مائية قدر الإمكان."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    match = URL_RE.search(update.message.text or "")
    if not match:
        await update.message.reply_text("أرسل رابط فيديو صحيح 🙏")
        return

    url = match.group(0)
    if not any(host in url for host in SUPPORTED_HOSTS):
        await update.message.reply_text("الرابط هذا غير مدعوم حالياً. جرّب تيك توك أو تويتر.")
        return

    status = await update.message.reply_text("⏳ جاري التحميل...")
    async with DOWNLOAD_SLOTS:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                await context.bot.send_chat_action(update.effective_chat.id, ChatAction.UPLOAD_VIDEO)
                path = await asyncio.to_thread(download_video, url, tmp)
            except Exception:
                log.exception("download failed for %s", url)
                await status.edit_text("❌ ما قدرت أحمّل الفيديو. تأكد إن الرابط عام (مو خاص) وجرّب مرة ثانية.")
                return

            if path.stat().st_size > MAX_UPLOAD_BYTES:
                await status.edit_text("❌ الفيديو أكبر من 50 ميجا، وهذا حد تليجرام للبوتات.")
                return

            with path.open("rb") as f:
                await update.message.reply_video(f, supports_streaming=True, read_timeout=120, write_timeout=120)
    await status.delete()


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("حط BOT_TOKEN في ملف .env (انسخ .env.example)")

    app = Application.builder().token(token).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    log.info("البوت شغّال...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
