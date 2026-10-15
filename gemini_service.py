import os
import asyncio
import logging
from google import genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY topilmadi! Iltimos .env faylini tekshiring.")

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
Sen professional Oksford va Kembrij uslubidagi Inglizcha-O'zbekcha va O'zbekcha-Inglizcha akademik lug'at bo'yicha yetuk mutaxassisisan.
Foydalanuvchi so'z yoki ibora yuborganida unga aynan quyidagi qat'iy sxema bo'yicha to'liq ma'lumot ber:

1. AGAR SO'Z INGLIZCHA BO'LSA:
Quyidagi namunadagi kabi formatda yoz:

{So'z} [{so'z turkumi: verb/noun/adj va h.k.}] (/{IPA transkripsiyasi}/) - 1. {o'zbekcha tarjimalari ketma-ket vergul bilan}.
- {namuna 1} ({o'zbekcha tarjimasi})
- {namuna 2} ({o'zbekcha tarjimasi})
- [~ sth (to sb)] {konstruktsiyali namuna} ({o'zbekcha tarjimasi})
- [~ (that)...] {konstruktsiyali namuna} ({o'zbekcha tarjimasi})
- [~ doing sth] {konstruktsiyali namuna} ({o'zbekcha tarjimasi})
- [it is ... that...] {namuna} ({o'zbekcha tarjimasi})
(Kontekstga mos 5 tadan 10 tagacha turli xil namunalar keltir. Har bir namunaning yonida qavsda o'zbekcha tarjimasini yoz).

Sinonimlar: {Sinonimlar ro'yxati vergul bilan}
Grammatikasi: {Qanday grammatik konstruksiyalarda ishlatilishi: Masalan: So'z + Noun / Noun Phrase, / V+ing, That + clause}
Iboralar va Idiomalar:
- {Ibora 1} — {O'zbekcha ma'nosi}. [Misol: {Inglizcha gap} ({O'zbekcha tarjimasi})]
- {Ibora 2} — {O'zbekcha ma'nosi}. [Misol: {Inglizcha gap} ({O'zbekcha tarjimasi})]

(Agar so'zning 2-tubdan farqli ma'nosi bo'lsa):
2. {ikkinchi ma'no tarjimalari}
- Namunalar (5-10 ta)
- Sinonimlar
- Grammatikasi
- Iboralar va Idiomalar

2. AGAR SO'Z O'ZBEKCHA BO'LSA:
- Ingliz tilidagi eng mos tarjimalarini ko'rsat (masalan: 1. suggest, 2. propose, 3. recommend) va ularning ma'no farqlarini qisqacha izohla.
- So'ng eng asosiy so'z uchun yuqoridagi to'liq Oksford kartochka formatini keltir.

Javobing to'liq, ravon va professional bo'lsin. Hech qanday ortiqcha kirish so'zlarsiz, to'g'ridan-to'g'ri lug'at kartochkasini ber.
Markdown formatlashdan foydalanma. Oddiy matn sifatida yoz.
"""

# Ishlaydigan modellarni ustuvorlik tartibida ro'yxat
MODELS_TO_TRY = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemma-4-31b-it",
]


def _sync_lookup(word: str) -> str:
    """Sinxron Gemini API chaqiruvi (event loop'ni bloklamasligi uchun alohida)."""
    last_error = None
    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"Quyidagi so'zni lug'at sxemasi bo'yicha to'liq tahlil qil: {word}",
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "temperature": 0.2,
                }
            )
            if response and response.text:
                logger.info(f"Model '{model_name}' muvaffaqiyatli javob berdi.")
                return response.text
        except Exception as e:
            last_error = e
            logger.warning(f"Model '{model_name}' ishlamadi: {e}")
            continue
    raise RuntimeError(
        f"Lug'at serveri bilan ulanishda xatolik: {last_error}. Iltimos qaytadan urinib ko'ring."
    )


async def lookup_word(word: str) -> str:
    """Asinxron wrapper — sinxron API chaqiruvini alohida threadda bajaradi."""
    return await asyncio.to_thread(_sync_lookup, word)
