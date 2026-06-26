from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Salut {hbold(message.from_user.full_name)}! 🇫🇷\n\n"
        "Bienvenue sur SalutBot — votre tuteur de français personnel.\n\n"
        "Écrivez-moi un message en français chaque jour pour recevoir des corrections "
        "grammaticales, des explications et des suggestions pour enrichir votre vocabulaire.\n\n"
        "Commandes :\n"
        "/help — Afficher l'aide"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 **Comment utiliser SalutBot**\n\n"
        "1. Écrivez un message en français (texte uniquement).\n"
        "2. Le bot vérifie le nombre de mots et analyse votre texte.\n"
        "3. Vous recevez une correction avec explications et suggestions.\n\n"
        "Essayez d'écrire au moins le nombre minimum de mots requis chaque jour !"
    )
