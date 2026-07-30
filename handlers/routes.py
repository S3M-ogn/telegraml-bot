from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
import aiosqlite

router = Router()


def get_main_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="О боте")],
            [KeyboardButton(text="Расписание"), KeyboardButton(text="Цены"), KeyboardButton(text="Запись")],
            [KeyboardButton(text="Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_main_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подробнее", callback_data="info_more")]
        ]
    )
    return keyboard



@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Здравствуйте!\nВ этом боте вы сможете узанть актуальное расписание для записи\nА также возможность узнать актуальные цены!\nЕсли понадобиться помощь то напишите команду /help",
        reply_markup=get_main_reply_keyboard()
    )


@router.callback_query(lambda c: c.data == "info_more")
async def process_more_info(callback: CallbackQuery):
    await callback.message.answer("Вот более подробная информация о боте:\n Бот помогает быстрее записаться на запись а также узнавать о всех новинках!")
    await callback.answer()

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "📋 Команды:\n"
        "/start - запустить бота\n"
        "/help - список команд\n"
        "/about - про нас",
        reply_markup=get_main_reply_keyboard()
    )

@router.message(Command("about"))
@router.message(F.text.lower() == "о боте")
async def about(message: Message):
    await message.answer(
        f"🤖 Бот создан для удобства и в дальнейшем будет улучшаться!\n"
        f"Твое имя: {message.from_user.full_name}",
        reply_markup=get_main_inline_keyboard()
    )

@router.message(Command("rasp"))
@router.message(F.text.lower() == "расписание")
async def rasp(message: Message):
    await message.answer(
        "🗓️Актуальное расписание:\n\n"
        "Ⓜ️ БЕГОВАЯ:\n"
        "ПН - 10:00 (СВОБОДНО) | 12:00 (ЗАНЯТО)\n"
        "ВТ - 15:00 (СВОБОДНО) | 19:00 (ЗАНЯТО)\n"
        "СР - ВЫХОДНОЙ ДЕНЬ\n"
        "ЧТ - 10:00 (СВОБОДНО) | 14:00 (СВОБОДНО)\n"
        "ПТ - 16:00 (ЗАНЯТО) | 18:00 (СВОБОДНО)",
    )

@router.message(Command("ceny"))
@router.message(F.text.lower() == "цены")
async def send_photo(message: Message):
    try:

        photo = FSInputFile('files/price.jpg')  
        await message.answer_photo(
            photo=photo,
            caption="Актуальные цены на услуги"  
        )
    except Exception as e:
        await message.answer("Изображение с ценами не найдено.")


@router.message(Command("zapis"))
@router.message(F.text.lower() == "запись")
async def zapis(message: Message):
    await message.answer(
        "Для того, чтобы записаться на свободный день и время\nОбратитесь к @LilitHaroyan",
        reply_markup=get_main_reply_keyboard()
    )



@router.message(F.text.lower() == "помощь")
async def help_text(message: Message):
    await help_command(message)

@router.message()
async def mess(message: Message):
    await message.answer(
        "Если нужна помощь в использовании бота, просто напиши команду /help"
    )
