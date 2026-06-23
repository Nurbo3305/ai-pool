### Шаг 2. Обновлённый код с памятью (для bot.py)


import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai
from google.genai import types as ai_types

# -- НАСТРОЙКИ --
import os
from dotenv import load_dotenv

load_dotenv()  # Эта строка находит файл .env и загружает ключи
# Инициализируем бота и диспетчер

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Инициализируем клиента Gemini
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Словарь для хранения истории чата для каждого пользователя
# Ключ — id пользователя в Телеграм, значение — объект чата Gemini
user_chats = {}

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    
    # При старте создаем чистый диалог с системной инструкцией (характером бота)
    user_chats[user_id] = ai_client.chats.create(
        model="gemini-2.5-flash",
        config=ai_types.GenerateContentConfig(
            system_instruction="Ты — крутой, сообразительный и дружелюбный ИИ-ассистент в Telegram. Отвечай кратко, ёмко и по делу."
        )
    )
    
    await message.reply(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я твой личный ИИ-бот с памятью. Я запоминаю наш диалог, так что можешь общаться со мной как с реальным собеседником!"
    )

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    
    # Если пользователь не нажал /start, но сразу пишет, создаем ему сессию чата
    if user_id not in user_chats:
        user_chats[user_id] = ai_client.chats.create(model="gemini-2.5-flash")
        
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Берем чат конкретного пользователя и отправляем туда сообщение
        # Метод send_message автоматически сохраняет историю внутри этой сессии!
        chat = user_chats[user_id]
        response = chat.send_message(message.text)
        
        await message.reply(response.text)
        
    except Exception as e:
        await message.reply(f"Ошибка при генерации ответа: {e}")

async def main():
    print("ИИ-Бот запущен через VS Code...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())