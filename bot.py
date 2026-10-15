import os
import io
import re
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from gtts import gTTS
from dotenv import load_dotenv

from database import init_db, get_cached_word, save_to_cache
from gemini_service import lookup_word

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! Iltimos .env faylini tekshiring.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def split_message(text: str, max_length: int = 4000) -> list[str]:
    """Telegram xabar cheklovidan (4096 belgi) oshib ketmasligi uchun matnni bo'lib beradi."""
    if len(text) <= max_length:
        return [text]
    parts = []
    while len(text) > max_length:
        split_idx = text.rfind("\n\n", 0, max_length)
        if split_idx == -1:
            split_idx = text.rfind("\n", 0, max_length)
        if split_idx == -1:
            split_idx = max_length
        parts.append(text[:split_idx].strip())
        text = text[split_idx:].strip()
    if text:
        parts.append(text)
    return parts


def extract_english_word(response_text: str) -> str | None:
    """Gemini javobidan birinchi inglizcha so'zni ajratib oladi.

    O'zbekcha so'z qidirilganda Gemini javob boshida odatda:
      1. suggest, 2. propose, 3. recommend
    yoki:
      suggest [verb] (/.../)
    ko'rinishida yozadi. Shu birinchi inglizcha so'zni topamiz.
    """
    # 1-harakat: "word [verb/noun/adj...]" — so'z turkumi qavsda (eng ishonchli)
    match = re.search(r'^([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+\[(verb|noun|adj|adv|pron|prep|conj|det)', response_text, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1).strip().lower()

    # 2-harakat: "word (/IPA/" — IPA transkripsiya qavsda
    match = re.search(r'^([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+\(/', response_text, re.MULTILINE)
    if match:
        return match.group(1).strip().lower()

    # 3-harakat: QATOR BOSHIDA "1. suggest" — anchored to line start
    match = re.search(r'^\s*1\.\s+\*{0,2}([a-zA-Z]+)\*{0,2}', response_text, re.MULTILINE)
    if match:
        return match.group(1).lower()

    # 4-harakat: birinchi qatordan "word [" patternini topish
    first_line = response_text.strip().split('\n')[0]
    match = re.search(r'\b([a-zA-Z]{2,})\s+\[', first_line)
    if match:
        return match.group(1).lower()

    return None


async def send_pronunciation(message: types.Message, word: str):
    """Berilgan inglizcha so'zning audio talaffuzini yuboradi."""
    try:
        tts = gTTS(text=word, lang='en')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_file = types.BufferedInputFile(
            audio_buffer.read(), filename=f"{word}.ogg"
        )
        await message.answer_voice(
            voice=audio_file,
            caption=f"🔊 Talaffuzi: {word}",
        )
    except Exception as e:
        logger.warning(f"Audio yaratishda xato: {e}")


def is_english(text: str) -> bool:
    """Matn inglizcha ekanligini tekshiradi."""
    clean = text.replace("-", "").replace(" ", "")
    return clean.isascii() and clean.isalpha()


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "📚 <b>Inglizcha-O'zbekcha / O'zbekcha-Inglizcha Akademik Lug'at Botiga xush kelibsiz!</b>\n\n"
        "🔹 Istalgan so'z yoki iborani yozing (masalan: <code>suggest</code>, <code>resilient</code> yoki <code>taklif qilmoq</code>).\n\n"
        "🔹 Bot sizga quyidagilarni taqdim etadi:\n"
        "   • To'liq tarjima va transkripsiya\n"
        "   • 5-10 ta turli kontekstdagi namunalar\n"
        "   • Sinonimlar va Grammatik qoliplar\n"
        "   • Iboralar va idiomalar\n"
        "   • 🔊 Audio talaffuz\n\n"
        "📝 /help — Qo'llanma",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "📖 <b>Qo'llanma:</b>\n\n"
        "Shunchaki bitta so'z yozib yuboring.\n"
        "Misol: <code>suggest</code>, <code>tavsiya etmoq</code>, <code>ubiquitous</code>\n\n"
        "Inglizcha yozsangiz — o'zbekcha tarjima, namunalar, grammatika.\n"
        "O'zbekcha yozsangiz — inglizcha muqobillar va to'liq kartochka.",
        parse_mode=ParseMode.HTML
    )


@dp.message(F.text)
async def word_handler(message: types.Message):
    query = message.text.strip()

    if query.startswith("/"):
        return

    if len(query) > 100:
        await message.answer("⚠️ Iltimos, juda uzun matn emas, bitta so'z yoki ibora yozing.")
        return

    wait_msg = await message.answer(
        "🔍 <i>Lug'atdan qidirilmoqda, kuting...</i>",
        parse_mode=ParseMode.HTML
    )
    wait_msg_deleted = False

    try:
        # 1. Keshdan tekshirish
        result = await get_cached_word(query)

        # 2. Agar keshda bo'lmasa, Gemini orqali qidirish
        if not result:
            result = await lookup_word(query)
            await save_to_cache(query, result)

        # Kutish xabarini o'chirish
        try:
            await wait_msg.delete()
            wait_msg_deleted = True
        except Exception:
            wait_msg_deleted = True

        # 3. Natijani yuborish (kerak bo'lsa bo'laklab)
        parts = split_message(result)
        for part in parts:
            await message.answer(part, parse_mode=None)

        # 4. Audio talaffuz yuborish
        if is_english(query):
            # Inglizcha so'z — o'sha so'zning o'zini o'qish
            await send_pronunciation(message, query)
        else:
            # O'zbekcha so'z — javobdan inglizcha tarjimani ajratib, uni o'qish
            eng_word = extract_english_word(result)
            if eng_word:
                await send_pronunciation(message, eng_word)

    except Exception as e:
        logger.error(f"Xatolik: {e}", exc_info=True)
        error_text = f"❌ Xatolik yuz berdi: {str(e)}"
        if not wait_msg_deleted:
            try:
                await wait_msg.edit_text(error_text)
            except Exception:
                await message.answer(error_text)
        else:
            await message.answer(error_text)


async def main():
    await init_db()
    logger.info("Bot bazasi yuklandi va bot ishga tushdi!")
    print(">>> Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda... <<<")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
