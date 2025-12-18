import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID

# -------------------- Логирование --------------------
logging.basicConfig(level=logging.INFO)

# -------------------- Инициализация бота --------------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# -------------------- Остатки товара --------------------
stock = {
    "Мужская S": 1,
    "Мужская M": 2,
    "Женская XS": 2,
    "Женская S": 2,
    "Женская M": 2,
    "Женская L": 2,
}

registrations = {}

# -------------------- Кнопки --------------------
buy_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👕 Приобрести футболку spivak run", callback_data="buy")]
    ]
)

def size_keyboard():
    buttons = []
    for size, count in stock.items():
        if count > 0:
            buttons.append([
                InlineKeyboardButton(
                    text=f"{size} ({count} шт.)",
                    callback_data=f"size_{size}"
                )
            ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def cancel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить регистрацию", callback_data="cancel")]
        ]
    )

# -------------------- /start --------------------
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! 👋\n"
        "Здесь можно приобрести мерч spivak run.\n\n"
        "Нажми кнопку ниже 👇",
        reply_markup=buy_button
    )

# -------------------- Кнопка купить --------------------
@dp.callback_query(F.data == "buy")
async def choose_size(callback: CallbackQuery):
    await callback.message.answer(
        "Выбери размер футболки:",
        reply_markup=size_keyboard()
    )
    await callback.answer()

# -------------------- Выбор размера --------------------
@dp.callback_query(F.data.startswith("size_"))
async def process_size(callback: CallbackQuery):
    size = callback.data.replace("size_", "")
    user = callback.from_user

    logging.info(f"SIZE select {size} by {user.id}")

    if stock.get(size, 0) <= 0:
        await callback.answer("Размер закончился", show_alert=True)
        return

    if user.id in registrations:
        await callback.answer("Ты уже зарегистрирован", show_alert=True)
        return

    stock[size] -= 1
    registrations[user.id] = size

    try:
        await bot.send_message(
            ADMIN_ID,
            f"РЕГИСТРАЦИЯ SPIVAK RUN\n\n"
            f"ID: {user.id}\n"
            f"Имя: {user.full_name}\n"
            f"Username: @{user.username if user.username else 'нет'}\n"
            f"Размер: {size}"
        )
    except Exception as e:
        logging.error(f"ADMIN MESSAGE ERROR: {e}")

    await callback.message.answer(
        f"Ты зарегистрирован!\n📏 Размер: {size}",
        reply_markup=cancel_keyboard()
    )

    await callback.answer()

# -------------------- Отмена регистрации --------------------
@dp.callback_query(F.data == "cancel")
async def cancel_registration(callback: CallbackQuery):
    user = callback.from_user

    if user.id not in registrations:
        await callback.answer("У тебя нет активной регистрации", show_alert=True)
        return

    size = registrations.pop(user.id)
    stock[size] += 1

    logging.info(f"CANCEL registration {user.id} size {size}")

    try:
        await bot.send_message(
            ADMIN_ID,
            f"ОТМЕНА РЕГИСТРАЦИИ SPIVAK RUN\n\n"
            f"ID: {user.id}\n"
            f"Имя: {user.full_name}\n"
            f"Размер: {size}"
        )
    except Exception as e:
        logging.error(f"ADMIN MESSAGE ERROR: {e}")

    await callback.message.answer(
        "Регистрация отменена.\n"
        "Если хочешь — можешь выбрать размер снова 👕"
    )

    await callback.answer()

# -------------------- Публикация поста в канале --------------------
@dp.message(F.text == "/post")
async def post_to_channel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    with open("tshirt.jpg", "rb") as photo:  # локальный файл с фото
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo,
            caption=(
                "👕 МЕРЧ SPIVAK RUN\n\n"
                "Официальная футболка spivak run\n"
                "Ограниченный тираж\n\n"
                "Нажми кнопку ниже, чтобы зарегистрироваться 👇"
            ),
            reply_markup=buy_button
        )

    await message.answer("✅ Пост с фото и кнопкой опубликован в канале")


# -------------------- Запуск бота --------------------
async def main():
    logging.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
