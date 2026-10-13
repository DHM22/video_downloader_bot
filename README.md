# بوت تحميل فيديوهات تيك توك وتويتر 🎬

ترسل للبوت رابط فيديو، ويرجع لك الفيديو نفسه كملف.

## المتطلبات (كلها مجانية)
| الشي | الفائدة |
|---|---|
| حساب تليجرام + [@BotFather](https://t.me/BotFather) | تسوي البوت وتاخذ التوكن |
| Python 3.10+ | لغة البوت |
| `python-telegram-bot` | التعامل مع تليجرام |
| `yt-dlp` | يسحب الفيديو من تيك توك وتويتر ومواقع كثيرة غيرها |
| `ffmpeg` | يدمج الصوت مع الصورة لو كانوا منفصلين |
| سيرفر | يشغّل البوت 24 ساعة (تحت خيارات مجانية) |

## التشغيل على جهازك
```bash
cd video_downloader_bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # وحط التوكن حقك داخله
python bot.py
```
ولازم يكون `ffmpeg` مثبت (`sudo apt install ffmpeg` أو `brew install ffmpeg`).

## الاستضافة المجانية
- **Oracle Cloud Free Tier**: سيرفر مجاني دائم، وهو أفضل خيار.
- **Google Cloud e2-micro**: سيرفر صغير مجاني دائم.
- **جهازك أو Raspberry Pi**: يشتغل البوت طول ما الجهاز شغّال.

فيه `Dockerfile` جاهز: `docker build -t video-bot . && docker run -d --env-file .env video-bot`

## ملاحظات مهمة
- **حد 50 ميجا**: تليجرام ما يسمح للبوتات ترفع أكثر من 50MB. فيديوهات تيك توك وتويتر غالباً أصغر من كذا.
- **حدّث yt-dlp دايماً**: المواقع تغيّر أنظمتها كثير، فلو التحميل وقف شغّل `pip install -U "yt-dlp[default,curl-cffi]"`.
- **الحسابات الخاصة** والفيديوهات المحذوفة ما تتحمّل.
- استخدمه لمحتوى مسموح لك تحمّله، واحترم حقوق أصحاب الفيديوهات.
