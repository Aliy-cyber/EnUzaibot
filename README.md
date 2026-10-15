# 📚 English-Uzbek Oxford Academic Dictionary Bot

Gemini AI va Python (aiogram 3.x) asosida yaratilgan zamonaviy, akademik Inglizcha-O'zbekcha va O'zbekcha-Inglizcha lug'at Telegram boti.

## ✨ Imkoniyatlari
- **EN ➔ UZ**: Transkripsiya, ma'nolar, 5-10 ta Oksford qolipidagi namunalar, sinonimlar, grammatika va idiomalar
- **UZ ➔ EN**: Inglizcha muqobillar, nozik farqlari va batafsil kartochka
- **🔊 Audio talaffuz**: Inglizcha so'z uchun — o'sha so'zning audiosi. O'zbekcha so'z uchun — inglizcha tarjimaning audiosi
- **⚡ SQLite Kesh**: Avval qidirilgan so'zlar darhol keshdan olinadi
- **📝 Chiroyli formatlash**: Xabarlar o'qilishi oson

---

## 🖥️ Mahalliy ishga tushirish (bitta tugma)

### Windows:
`start_bot.bat` faylini ikki marta bosing — bot darhol ishga tushadi.

### Terminal orqali:
```bash
pip install -r requirements.txt
python bot.py
```

---

## ☁️ Render.com da doimiy ishga tushirish (bepul, 24/7)

### 1-qadam: GitHubga joylash
```bash
cd eng_uzb_dictionary_bot
git init
git add .
git commit -m "Initial commit: ENG-UZB Dictionary Bot"
git branch -M main
git remote add origin https://github.com/SIZNING_GITHUB/eng-uzb-dictionary-bot.git
git push -u origin main
```

### 2-qadam: Render.com da deploy qilish
1. https://render.com saytiga kiring va GitHub akkauntingiz bilan tizimga kiring
2. Dashboard → **New +** → **Background Worker** bosing
3. GitHub repongizni tanlang (eng-uzb-dictionary-bot)
4. Sozlamalar:
   - **Name**: eng-uzb-dictionary-bot
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
5. **Environment** bo'limida ikkita o'zgaruvchi qo'shing:
   - `BOT_TOKEN` = sizning bot tokeningiz
   - `GEMINI_API_KEY` = sizning Gemini API kalitingiz
6. **Create Background Worker** tugmasini bosing

Bot 2-3 daqiqa ichida avtomatik deploy bo'ladi va 24/7 ishlaydi!

---

## 📂 Loyiha tuzilishi
```
eng_uzb_dictionary_bot/
├── .env                # Tokenlar (GitHubga yuklanMAYDI)
├── .gitignore          # Git uchun e'tiborsiz fayllar
├── requirements.txt    # Kutubxonalar
├── runtime.txt         # Python versiyasi (Render uchun)
├── render.yaml         # Render.com konfiguratsiyasi
├── start_bot.bat       # Windows uchun bir tugmali ishga tushirish
├── database.py         # SQLite kesh tizimi
├── gemini_service.py   # Gemini AI xizmati
├── bot.py              # Asosiy Telegram bot
└── README.md           # Ushbu hujjat
```
# EnUzaibot
