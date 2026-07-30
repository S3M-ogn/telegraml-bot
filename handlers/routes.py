from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
import aiosqlite

router = Router()
ADMIN_ID = 6646323664  


class BookingStates(StatesGroup):
    waiting_name = State()
    waiting_phone = State()


SCHEDULE = {
    "Пт 31.07": {
        "10:30": "свободно",
        "11:00": "свободно",
        "11:30": "свободно",
        "12:00": "свободно",
        "12:30": "свободно",
        "13:00": "свободно",
        "13:30": "свободно",
        "14:00": "свободно",
        "14:30": "свободно",
        "15:00": "свободно",
        "15:30": "свободно",
        "16:00": "занято"
    },
    "Сб 01.08": {
        "10:30": "занято",
        "13:00": "свободно",
        "13:30": "свободно",
        "14:00": "свободно",
        "14:30": "свободно",
        "15:00": "свободно",
        "15:30": "свободно",
        "16:00": "свободно",
        "16:30": "свободно",
        "17:00": "свободно",
        "17:30": "свободно",
        "18:00": "свободно"
    },
    "Вс 02.08": {
        "10:30": "свободно",
        "11:00": "свободно",
        "11:30": "свободно",
        "12:00": "свободно",
        "12:30": "свободно",
        "13:00": "свободно",
        "13:30": "свободно",
        "14:00": "свободно",
        "14:30": "свободно",
        "15:00": "свободно",
        "15:30": "свободно",
        "16:00": "свободно",
        "16:30": "свободно",
        "17:00": "свободно",
        "17:30": "свободно",
        "18:00": "свободно"
    },
    "Пн 03.08": {
        "10:30": "свободно",
        "11:00": "свободно",
        "11:30": "свободно",
        "12:00": "свободно",
        "12:30": "свободно",
        "13:00": "свободно",
        "13:30": "свободно",
        "14:00": "свободно",
        "14:30": "свободно",
        "15:00": "свободно",
        "15:30": "свободно",
        "16:00": "свободно",
        "16:30": "свободно",
        "17:00": "свободно",
        "17:30": "свободно",
        "18:00": "свободно"
    }
}


async def init_db():
    async with aiosqlite.connect("Lilith.sql") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_name TEXT,
                user_phone TEXT,
                day TEXT,
                time TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        await db.commit()

async def save_booking(user_id, user_name, user_phone, day, time):
    async with aiosqlite.connect("Lilith.sql") as db:
        await db.execute(
            "INSERT INTO bookings (user_id, user_name, user_phone, day, time) VALUES (?, ?, ?, ?, ?)",
            (user_id, user_name, user_phone, day, time)
        )
        await db.commit()

async def get_bookings_for_admin():
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT id, user_name, user_phone, day, time FROM bookings WHERE status = 'pending'"
        )
        return await cursor.fetchall()

async def get_user_bookings(user_id):
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT day, time, status FROM bookings WHERE user_id = ?",
            (user_id,)
        )
        return await cursor.fetchall()

# ============ КЛАВИАТУРЫ ============
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

def get_schedule_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пт 31.07", callback_data="day_Пт 31.07")],
            [InlineKeyboardButton(text="Сб 01.08", callback_data="day_Сб 01.08")],
            [InlineKeyboardButton(text="Вс 02.08", callback_data="day_Вс 02.08")],
            [InlineKeyboardButton(text="Пн 03.08", callback_data="day_Пн 03.08")]
        ]
    )
    return keyboard

def get_time_keyboard(day):
    times = SCHEDULE.get(day, {})
    keyboard = InlineKeyboardMarkup()
    
    for time, status in times.items():
        if status == "свободно":
            keyboard.add(InlineKeyboardButton(
                text=time,
                callback_data=f"time_{day}_{time.replace(':', '')}"
            ))
    
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back_schedule"))
    return keyboard

def get_booking_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Мои записи", callback_data="my_bookings")],
            [InlineKeyboardButton(text="Назад", callback_data="back_main")]
        ]
    )
    return keyboard

# ============ ХЕНДЛЕРЫ ============

@router.message(Command("start"))
async def start(message: Message):
    await init_db()
    await message.answer(
        "Здравствуйте!\nВ этом боте вы сможете узнать актуальное расписание для записи\nА также возможность узнать актуальные цены!\nЕсли понадобится помощь, напишите команду /help",
        reply_markup=get_main_reply_keyboard()
    )

@router.callback_query(lambda c: c.data == "info_more")
async def process_more_info(callback: CallbackQuery):
    await callback.message.answer("Вот более подробная информация о боте:\nБот помогает быстрее записаться на запись, а также узнавать о всех новинках!")
    await callback.answer()

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Команды:\n"
        "/start - запустить бота\n"
        "/help - список команд\n"
        "/about - про нас\n"
        "/schedule - посмотреть расписание\n"
        "/book - записаться\n"
        "/my - мои записи",
        reply_markup=get_main_reply_keyboard()
    )

@router.message(Command("about"))
@router.message(F.text.lower() == "о боте")
async def about(message: Message):
    await message.answer(
        f"Бот создан для удобства и в дальнейшем будет улучшаться!\n"
        f"Твое имя: {message.from_user.full_name}",
        reply_markup=get_main_inline_keyboard()
    )

@router.message(Command("rasp"))
@router.message(F.text.lower() == "расписание")
async def rasp(message: Message):
    text = "Актуальное расписание:\n\n"
    
    for day, times in SCHEDULE.items():
        text += f"{day}:\n"
        for time, status in times.items():
            text += f"  {time} - {status}\n"
        text += "\n"
    
    text += "Выберите день для записи:"
    
    await message.answer(text, reply_markup=get_schedule_keyboard())

@router.callback_query(lambda c: c.data.startswith("day_"))
async def select_day(callback: CallbackQuery):
    day = callback.data.replace("day_", "")
    
    text = f"{day}\n\nСвободное время:\n"
    times = SCHEDULE.get(day, {})
    
    free_times = [t for t, s in times.items() if s == "свободно"]
    
    if not free_times:
        text = f"{day}\n\nНет свободного времени. Выберите другой день."
        await callback.message.edit_text(text, reply_markup=get_schedule_keyboard())
        await callback.answer()
        return
    
    for time in free_times:
        text += f"{time}\n"
    
    text += "\nВыберите время:"
    
    await callback.message.edit_text(text, reply_markup=get_time_keyboard(day))
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("time_"))
async def select_time(callback: CallbackQuery, state: FSMContext):
    data = callback.data.replace("time_", "")
    parts = data.split("_")
    day = parts[0]
    time = f"{parts[1][:2]}:{parts[1][2:]}"
    
    await state.update_data(day=day, time=time)
    
    await callback.message.edit_text(
        f"Вы выбрали: {day} в {time}\n\nВведите ваше имя:"
    )
    await state.set_state(BookingStates.waiting_name)
    await callback.answer()

@router.message(BookingStates.waiting_name)
async def get_name(message: Message, state: FSMContext):
    if len(message.text) < 2:
        await message.answer("Пожалуйста, введите полное имя (минимум 2 символа)")
        return
    
    await state.update_data(user_name=message.text)
    await message.answer("Введите ваш номер телефона:")
    await state.set_state(BookingStates.waiting_phone)

@router.message(BookingStates.waiting_phone)
async def get_phone(message: Message, state: FSMContext, bot):
    if len(message.text) < 5:
        await message.answer("Пожалуйста, введите корректный номер телефона")
        return
    
    data = await state.get_data()
    
    await save_booking(
        user_id=message.from_user.id,
        user_name=data.get("user_name"),
        user_phone=message.text,
        day=data.get("day"),
        time=data.get("time")
    )
    
    await message.answer(
        f"Вы записаны на {data.get('day')} в {data.get('time')}\n\n"
        f"Ожидайте подтверждения от администратора.",
        reply_markup=get_main_reply_keyboard()
    )
    
    admin_text = f"Новая запись:\nИмя: {data.get('user_name')}\nТелефон: {message.text}\nДень: {data.get('day')}\nВремя: {data.get('time')}"
    
    await bot.send_message(ADMIN_ID, admin_text)
    
    await state.clear()

@router.message(Command("book"))
@router.message(F.text.lower() == "запись")
async def book(message: Message):
    await message.answer(
        "Выберите день для записи:",
        reply_markup=get_schedule_keyboard()
    )

@router.message(Command("my"))
async def my_bookings(message: Message):
    bookings = await get_user_bookings(message.from_user.id)
    
    if not bookings:
        await message.answer(
            "У вас нет записей.\n\nХотите записаться? Напишите /book",
            reply_markup=get_main_reply_keyboard()
        )
        return
    
    text = "Ваши записи:\n\n"
    for day, time, status in bookings:
        status_text = "ожидает подтверждения" if status == "pending" else "подтверждена"
        text += f"{day} в {time} - {status_text}\n"
    
    await message.answer(text, reply_markup=get_main_reply_keyboard())

@router.callback_query(lambda c: c.data == "my_bookings")
async def my_bookings_callback(callback: CallbackQuery):
    bookings = await get_user_bookings(callback.from_user.id)
    
    if not bookings:
        await callback.message.edit_text(
            "У вас нет записей.\n\nХотите записаться? Напишите /book",
            reply_markup=get_main_reply_keyboard()
        )
        await callback.answer()
        return
    
    text = "Ваши записи:\n\n"
    for day, time, status in bookings:
        status_text = "ожидает подтверждения" if status == "pending" else "подтверждена"
        text += f"{day} в {time} - {status_text}\n"
    
    await callback.message.edit_text(text, reply_markup=get_main_reply_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_schedule")
async def back_to_schedule(callback: CallbackQuery):
    text = "Актуальное расписание:\n\n"
    
    for day, times in SCHEDULE.items():
        text += f"{day}:\n"
        for time, status in times.items():
            text += f"  {time} - {status}\n"
        text += "\n"
    
    text += "Выберите день для записи:"
    
    await callback.message.edit_text(text, reply_markup=get_schedule_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "Здравствуйте!\nВ этом боте вы сможете узнать актуальное расписание для записи\nА также возможность узнать актуальные цены!\nЕсли понадобится помощь, напишите команду /help",
        reply_markup=get_main_reply_keyboard()
    )
    await callback.answer()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа")
        return
    
    bookings = await get_bookings_for_admin()
    
    if not bookings:
        await message.answer("Нет новых записей")
        return
    
    text = "Новые записи:\n\n"
    for id, name, phone, day, time in bookings:
        text += f"#{id} {name} {phone} {day} {time}\n"
    
    await message.answer(text)

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

@router.message(F.text.lower() == "помощь")
async def help_text(message: Message):
    await help_command(message)

@router.message()
async def mess(message: Message):
    await message.answer(
        "Если нужна помощь в использовании бота, просто напиши команду /help"
    )
