import asyncio
import os
import random

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

import database


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()


database.init_db()


# -------------------------
# Вспомогательная функция
# -------------------------

async def notify_all(text):
    for user_id in database.users():
        try:
            await bot.send_message(
                user_id,
                text
            )
        except:
            pass


# -------------------------
# Старт
# -------------------------

@dp.message(Command("start"))
async def start(message: Message):

    database.add_user(
        message.from_user.id,
        message.from_user.first_name
    )

    await message.answer(
        "📚 Добро пожаловать в книжный клуб!\n\n"
        "Команды:\n\n"
        "➕ /addbook — предложить книгу\n"
        "📋 /list — посмотреть варианты\n"
        "🎲 /pick — выбрать книгу\n"
        "📖 /progress 30 — обновить прогресс\n"
        "👥 /club — общий прогресс\n"
        "🎉 /finish — закончить книгу\n"
        "📚 /history — история"
    )


# -------------------------
# Добавление книги
# -------------------------

@dp.message(Command("addbook"))
async def addbook(message: Message):

    title = message.text.replace(
        "/addbook",
        ""
    ).strip()


    if not title:

        await message.answer(
            "📚 Напиши так:\n\n"
            "/addbook название книги"
        )

        return


    database.add_book(
        title,
        message.from_user.id
    )


    await message.answer(
        f"✅ Добавлено:\n\n"
        f"📖 {title}"
    )



# -------------------------
# Список вариантов
# -------------------------

@dp.message(Command("list"))
async def book_list(message: Message):

    books = database.candidates()


    if not books:

        await message.answer(
            "📭 Пока нет предложенных книг"
        )

        return


    text = "🎲 Кандидаты:\n\n"

    for i, book in enumerate(books,1):
        text += f"{i}. {book}\n"


    await message.answer(text)



# -------------------------
# Выбор книги
# -------------------------

@dp.message(Command("pick"))
async def pick(message: Message):

    books = database.candidates()


    if not books:

        await message.answer(
            "📭 Сначала добавьте варианты"
        )

        return


    book=random.choice(books)


    database.set_current(book)


    await notify_all(
        "🥁🥁🥁\n\n"
        "🎲 Судьба клуба решила!\n\n"
        f"📖 Читаем:\n"
        f"{book}\n\n"
        "Начинаем чтение 📚"
    )



# -------------------------
# Прогресс
# -------------------------

@dp.message(Command("progress"))
async def progress(message: Message):

    try:

        percent=int(
            message.text.split()[1]
        )

    except:

        await message.answer(
            "Используй:\n\n"
            "/progress 50"
        )

        return


    database.add_progress(
        message.from_user.id,
        percent
    )


    await message.answer(
        f"✏️ Прогресс обновлён:\n"
        f"{percent}%"
    )

# -------------------------
# Общий прогресс
# -------------------------

@dp.message(Command("club"))
async def club(message: Message):

    book=database.get_current()


    if not book:

        await message.answer(
            "📭 Сейчас нет активной книги"
        )

        return


    text=f"📖 {book}\n\n"


    progress=database.get_progress()


    if not progress:

        text+="Пока никто не добавил прогресс"

    else:

        for name,percent in progress:
            text+=f"{name} — {percent}%\n"


    await message.answer(text)

# -------------------------
# Завершение книги
# -------------------------

@dp.message(Command("finish"))
async def finish(message: Message):

    book=database.finish_book()


    if not book:

        await message.answer(
            "📭 Нет активной книги"
        )

        return


    await notify_all(
        "🎉 Книга завершена!\n\n"
        f"📖 {book}\n\n"
        "Можно выбирать следующую 📚"
    )

# -------------------------
# История
# -------------------------

@dp.message(Command("history"))
async def history(message: Message):

    books=database.history()


    if not books:

        await message.answer(
            "📭 История пока пустая"
        )

        return


    text="📚 Последние книги:\n\n"


    for i,book in enumerate(books,1):

        text+=f"{i}. {book} ✅\n"


    await message.answer(text)

# -------------------------
# Запуск
# -------------------------

async def main():

    await dp.start_polling(bot)

if __name__=="__main__":

    asyncio.run(main())
