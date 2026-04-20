import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder # Импортируем билдер
from telethon import TelegramClient
from telethon.tl.functions.account import CheckUsernameRequest
import httpx

BOT_TOKEN = "8539154569:AAE8X08Fci6qZeXsYQIrqvJekck7pbO8SDI"
API_ID = 26782706
API_HASH = "5bfeddff8fabab03c05c2f5d87c245a3"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = TelegramClient("session", API_ID, API_HASH)



def get_main_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="❓ Помощь", callback_data="help")
    builder.button(text="🔍 Поиск", callback_data="search_menu")
    builder.adjust(2)
    return builder.as_markup()

def get_search_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 5 букв", callback_data="run_search_5")
    builder.button(text="🔍 6 букв", callback_data="run_search_6")
    builder.button(text="⬅️ Назад", callback_data="main_menu")
    builder.adjust(2, 1) # 2 кнопки в ряд, потом 1 кнопка назад
    return builder.as_markup()



def generate_username(length=5, digits=False):
    vowels = "aeiou"
    consonants = "bcdfghjklmnpqrstvwxyz"
    while True:
        name = ""
        for i in range(length):
            if i % 2 == 0:
                name += random.choice(consonants)
            else:
                name += random.choice(vowels)
        if digits:
            pos = random.randint(0, length - 1)
            name = name[:pos] + str(random.randint(0, 9)) + name[pos+1:]
        return name



async def check_telegram(username: str) -> bool:
    try:
        return await client(CheckUsernameRequest(username))
    except:
        return False

async def check_fragment(username: str) -> bool:
    url = f"https://fragment.com/username/{username}"
    try:
        async with httpx.AsyncClient(timeout=10) as http:
            r = await http.get(url)
        if r.status_code == 200:
            if "Auction" in r.text or "Buy" in r.text or 'Sold' in r.text:
                return False
        return True
    except:
        return True

async def check_username(username: str) -> bool:
    tg = await check_telegram(username)
    if not tg:
        return False
    frag = await check_fragment(username)
    return frag



@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer(
        f"Приветствую, {msg.from_user.first_name}! 👋\n"
        f"Это бот для генерации свободных юзернеймов в Telegram и Fragment.",
        reply_markup=get_main_kb()
    )

@dp.callback_query(F.data == "main_menu")
async def main_menu(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "Главное меню. Выберите действие:",
        reply_markup=get_main_kb()
    )

@dp.callback_query(F.data == "help")
async def help_handler(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "Здесь будет твой рандомный текст помощи. \n\n"
        "Ты можешь изменить его в коде бота.",
        reply_markup=get_main_kb()
    )

@dp.callback_query(F.data == "search_menu")
async def search_menu(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "Выберите длину юзернейма для поиска:",
        reply_markup=get_search_kb()
    )

@dp.callback_query(F.data.startswith("run_search_"))
async def run_search(call: CallbackQuery):
    await call.answer()
    
    length = 5 if "5" in call.data else 6
    await call.message.answer(f"⏳ Начинаю поиск {length}-буквенных ников...")
    
    found = []

    for _ in range(20):
        username = generate_username(length)
        ok = await check_username(username)
        if ok:
            found.append("@" + username)
        await asyncio.sleep(0.4) 

    if found:
        await call.message.answer(
            "✅ Найдено:\n" + "\n".join(found),
            reply_markup=get_main_kb()
        )
    else:
        pass



async def main():
    await client.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
