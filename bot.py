import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

stock = {
    "Мужская S": 2,
    "Мужская M": 2,
    "Женская XS": 2,
    "Женская S": 2,
    "Женская M": 2,
    "Женская L": 2,
}

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

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Регистрация на покупку футболки spivak run 👕",
        reply_markup=buy_button
    )

@dp.callback_query(F.data == "buy")
async def choose_size(callback: CallbackQuery):
    await callback.message.answer(
        "Выбери размер:",
        reply_markup=size_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("size_"))
async def process_size(callback: CallbackQuery):
    size = callback.data.replace("size_", "")

    if stock.get(size, 0) <= 0:
        await callback.answer("Размер закончился", show_alert=True)
        return

    stock[size] -= 1
    user = callback.from_user

    await bot.send_message(
        ADMIN_ID,
        f"👕 Регистрация на футболку spivak run\n\n"
        f"Участник: {user.full_name}\n"
        f"Username: @{user.username if user.username else 'нет'}\n"
        f"Размер: {size}"
    )

    await callback.message.answer(
        f"✅ Ты зарегистрирован на покупку футболки!\nРазмер: {size}"
    )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())