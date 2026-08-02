import asyncio
import json
import os
import random
import threading 

from flask import Flask

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"


# 📦 загрузка данных
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "current_book": None,
            "progress": {},
            "history": [],
            "book_pool": []
        }


# 💾 сохранение
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# 👤 имя пользователя
def get_name(user: types.User):
    return user.first_name or "Без имени"


# 🟢 START
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "📚 Книжный клуб активирован\n\n"
        "Команды:\n"
        "/addbook — предложить книгу\n"
        "/pick — выбрать книгу\n"
        "/club — текущий прогресс\n"
        "/history — что уже прочитано"
    )


# 📚 добавить книгу
@dp.message(Command("addbook"))
async def addbook(message: Message):
    data = load_data()
    text = message.text.replace("/addbook", "").strip()

    if not text:
        await message.answer("Напиши название после команды")
        return

    data["book_pool"].append(text)
    save_data(data)

    await message.answer(
        "📥 Книга добавлена\n\n"
        "Вариант принят. Посмотрим, повезёт ли ей выжить в отборе"
    )


# 🎲 выбрать книгу
@dp.message(Command("pick"))
async def pick(message: Message):
    data = load_data()

    if not data["book_pool"]:
        await message.answer("📭 Нет предложенных книг")
        return

    book = random.choice(data["book_pool"])

    data["current_book"] = book
    data["progress"] = {}
    data["book_pool"] = []

    save_data(data)

    await message.answer(
        f"🎲 Выбор сделан\n\n"
        f"📖 Сейчас читаем: *{book}*\n\n"
        f"Всё. Отмены нет.",
        parse_mode="Markdown"
    )


# 📊 прогресс
@dp.message(Command("progress"))
async def progress(message: Message):
    data = load_data()

    if not data["current_book"]:
        await message.answer("📭 Сейчас нет активной книги")
        return

    try:
        percent = int(message.text.split()[1])
    except:
        await message.answer("Используй: /progress 30")
        return

    user_id = str(message.from_user.id)
    name = get_name(message.from_user)

    data["progress"][user_id] = {
        "name": name,
        "percent": percent
    }

    save_data(data)

    await message.answer(
        f"✏️ Обновлено\n\nТеперь ты на {percent}%"
    )


# 📖 клуб
@dp.message(Command("club"))
async def club(message: Message):
    data = load_data()

    if not data["current_book"]:
        await message.answer("📭 Сейчас нет активной книги")
        return

    text = f"📖 Сейчас читаем: *{data['current_book']}*\n\n👥 Прогресс:\n"

    total = 0
    count = 0

    for user in data["progress"].values():
        text += f"{user['name']} — {user['percent']}%\n"
        total += user["percent"]
        count += 1

    avg = int(total / count) if count else 0

    text += f"\n📊 Средний прогресс: {avg}%\n\n⏳ В процессе"

    await message.answer(text, parse_mode="Markdown")


# 👤 мой статус
@dp.message(Command("me"))
async def me(message: Message):
    data = load_data()

    user_id = str(message.from_user.id)

    if user_id not in data["progress"]:
        await message.answer("🤨 Ты ещё не добавлял прогресс")
        return

    user = data["progress"][user_id]

    await message.answer(
        f"📖 {data['current_book']}\n\n"
        f"Твой прогресс: {user['percent']}%"
    )


# 🎉 завершить книгу
@dp.message(Command("finish"))
async def finish(message: Message):
    data = load_data()

    if not data["current_book"]:
        await message.answer("📭 Нет активной книги")
        return

    data["history"].insert(0, data["current_book"])

    data["current_book"] = None
    data["progress"] = {}

    save_data(data)

    await message.answer("🎉 Книга завершена и отправлена в архив")


# 📚 история (последние 5)
@dp.message(Command("history"))
async def history(message: Message):
    data = load_data()

    if not data["history"]:
        await message.answer("Пока ничего не прочитано")
        return

    text = "📚 Прочитано недавно:\n\n"

    for i, book in enumerate(data["history"][:5], 1):
        text += f"{i}. {book} — ✅\n"

    text += "\n/allhistory — полный список"

    await message.answer(text)


# 📜 вся история
@dp.message(Command("allhistory"))
async def allhistory(message: Message):
    data = load_data()

    if not data["history"]:
        await message.answer("Пока ничего нет")
        return

    text = "📚 Вся история:\n\n"

    for i, book in enumerate(data["history"], 1):
        text += f"{i}. {book} — ✅\n"

    await message.answer(text)



# 🌐 маленький сервер для Render
app = Flask(__name__)


@app.route("/")
def home():
    return "Book club bot is running!"


def run_web():
    app.run(host="0.0.0.0", port=10000)


# 🚀 запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    asyncio.run(main())
