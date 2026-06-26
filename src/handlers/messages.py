from aiogram import Router, F
from aiogram.types import Message

from src.database.connection import DatabaseManager
from src.database.crud import save_progress
from src.services.openrouter import analyze_french

router = Router()


@router.message(F.text)
async def handle_french_message(message: Message, user: dict, db_manager: DatabaseManager):
    text = message.text.strip()
    word_count = len(text.split())
    min_words = user["min_words"]

    if word_count < min_words:
        await message.reply(
            f"Ton message ne contient que {word_count} mot(s). "
            f"Tu dois écrire au moins {min_words} mots. Essaye encore !"
        )
        return

    await message.reply("🔍 Analyse en cours...")

    try:
        result = await analyze_french(text)
        if "error" in result:
            await message.reply(f"❌ Erreur lors de l'analyse : {result['error']}")
            return

        analysis = result["analysis"]
        await message.reply(analysis)

        await save_progress(
            db_manager.conn,
            user["telegram_id"],
            text,
            word_count,
            analysis,
        )
    except Exception as e:
        await message.reply(f"❌ Une erreur est survenue : {e}")
