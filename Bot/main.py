import asyncio
import random
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from verses import VERSES_BY_TOPIC
from database import init_db, add_user
from actions import ACTIONS
from friend import CHURCH_MEMBERS
from strongholds import STRONGHOLDS
from sermons import SERMONS

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_ЕСЛИ_НЕТ_ПЕРЕМЕННОЙ")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
])

async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Веб-сервер запущен на порту {port}")

@dp.message(Command("start"))
async def start(message: types.Message):
    try:
        await message.delete()
    except:
        pass
        
    add_user(
        chat_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Стих дня", callback_data="verse_today")],
        [InlineKeyboardButton(text="✨ Пророческое действие", callback_data="action_today")],
        [InlineKeyboardButton(text="🤝 Бессмертный друг", callback_data="friend_today")],
        [InlineKeyboardButton(text="💥 Разрушение твердынь", callback_data="strongholds_menu")],
        [InlineKeyboardButton(text="📺 Проповеди", callback_data="sermons_menu")]
    ])
    
    await message.answer(
        "Приветствую тебя, Драгоценное Божье Дитя! ♥️\n\n"
        "Выбери, что ты хочешь сделать сегодня:",
        reply_markup=keyboard
    )

@dp.callback_query()
async def handle_buttons(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass

    if callback.data == "verse_today":
        random_topic = random.choice(list(VERSES_BY_TOPIC.keys()))
        random_verse = random.choice(VERSES_BY_TOPIC[random_topic])
        await callback.message.answer(
            f"📖 *{random_topic}*\n\n_{random_verse}_",
            reply_markup=back_keyboard,
            parse_mode="Markdown"
        )
    
    elif callback.data == "action_today":
        action = random.choice(ACTIONS)
        text = (
            f"✨ *{action['title']}*\n\n"
            f"📖 _{action['verse']}_\n\n"
            f"👉 *Твой шаг на сегодня:*\n{action['step']}"
        )
        await callback.message.answer(text, reply_markup=back_keyboard, parse_mode="Markdown")
    
    elif callback.data == "friend_today":
        chosen_person = random.choice(CHURCH_MEMBERS)
        text = (
            f"🤝 *Игра «Бессмертный друг»*\n\n"
            f"✨ Сегодня твой бессмертный друг — *{chosen_person}*!\n\n"
            f"*Как играть?*\n"
            f"Твоя задача — написать этому человеку и передать ему жизнь и нетление. Вот твои 3 шага:\n\n"
            f"1️⃣ *Отправь ему место Писания* на тему бессмертия и нетления (например, из раздела «Стих дня»).\n\n"
            f"2️⃣ *Попророчествуй ему.* На основе этого стиха скажи слова ободрения, утешения и назидания. Напомни, что в нем живет вечная жизнь Христа.\n\n"
            f"3️⃣ *Задай ему пророческое задание.* Придумай для него конкретный шаг на сегодня, который поможет ему проявить веру и победить уныние.\n\n"
            f"🙏 Не откладывай! Напиши *{chosen_person}* прямо сейчас и стань для него проводником Божьей любви."
        )
        await callback.message.answer(text, reply_markup=back_keyboard, parse_mode="Markdown")

    elif callback.data == "strongholds_menu":
        buttons = []
        for i, key in enumerate(STRONGHOLDS.keys()):
            buttons.append([InlineKeyboardButton(text=key, callback_data=f"sh_{i}")])
        
        buttons.append([InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer(
            "💥 *Разрушение твердынь*\n\n"
            "Выберите ложь, которая вас сейчас атакует:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    elif callback.data.startswith("sh_"):
        index = int(callback.data[3:])
        keys_list = list(STRONGHOLDS.keys())
        stronghold_name = keys_list[index]
        info = STRONGHOLDS[stronghold_name]
        
        text = (
            f"💥 *{stronghold_name}*\n\n"
            f"📖 *Оружие:*\n_{info['verse']}_\n\n"
            f"🔥 *Истина:*\n{info['truth']}\n\n"
            f"🙏 *Молитва:*\n_{info['prayer']}_"
        )
        await callback.message.answer(text, reply_markup=back_keyboard, parse_mode="Markdown")

    elif callback.data == "sermons_menu":
        buttons = []
        for i, sermon in enumerate(SERMONS):
            buttons.append([InlineKeyboardButton(text=sermon['title'], callback_data=f"sermon_{i}")])
        
        buttons.append([InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer(
            "📺 *Проповеди на тему бессмертия и нетления*\n\n"
            "Выберите проповедь, которую хотите послушать:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    elif callback.data.startswith("sermon_"):
        index = int(callback.data[7:])
        sermon = SERMONS[index]
        
        text = (
            f"📺 *{sermon['title']}*\n\n"
            f"{sermon['description']}\n\n"
            f"👉 [Смотреть видео]({sermon['link']})"
        )
        await callback.message.answer(text, reply_markup=back_keyboard, parse_mode="Markdown")

    elif callback.data == "back_to_menu":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 Стих дня", callback_data="verse_today")],
            [InlineKeyboardButton(text="✨ Пророческое действие", callback_data="action_today")],
            [InlineKeyboardButton(text="🤝 Бессмертный друг", callback_data="friend_today")],
            [InlineKeyboardButton(text="💥 Разрушение твердынь", callback_data="strongholds_menu")],
            [InlineKeyboardButton(text="📺 Проповеди", callback_data="sermons_menu")]
        ])
        await callback.message.answer(
            "Приветствую тебя, Драгоценное Божье Дитя! ♥️\n\n"
            "Выбери, что ты хочешь сделать сегодня:",
            reply_markup=keyboard
        )

    await callback.answer()

async def main():
    init_db() 
    await start_web_server()
    print("Бот запущен. Ждем сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
                                                 
