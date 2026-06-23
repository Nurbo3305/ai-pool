from flask import Flask
from threading import Thread
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai
from google.genai import types as ai_types
from dotenv import load_dotenv

app = Flask('')

@app.route('/')
def home():
    return "Бот запущен и работает!"

def run():
    # Render сам выдает порт, на котором должен работать "сайт"
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()


load_dotenv()  # Эта строка находит файл .env и загружает ключи
# Инициализируем бота и диспетчер

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Инициализируем клиента Gemini
ai_client = genai.Client(api_key=GEMINI_API_KEY)

async def main():
    keep_alive() # <--- Добавь эту строчку сюда!
    print("ИИ-Бот запущен через VS Code...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    # 1. Запускаем веб-сервер в фоновом потоке
    keep_alive()
    print("Веб-сервер запущен, включаю бота...")
    
    # 2. Запускаем самого бота (замени на свою команду, если она отличается)
    bot.infinity_polling(none_stop=True)


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




app = Flask('')

@app.route('/')
def home():
    return "Бот запущен!"

def run():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Главная функция запуска aiogram
async def main():
    keep_alive() # Включаем веб-сервер для Render
    print("Сервер запущен, включаю aiogram бота...")
    
    # Твой объект dispatcher (dp) должен быть создан выше в коде
    await dp.start_polling(bot) 

if __name__ == "__main__":
    asyncio.run(main())