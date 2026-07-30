from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
import aiosqlite
import re

router = Router()
ADMIN_ID = 5931039603  
# ============ СОСТОЯНИЯ ДЛЯ ЗАПИСИ ============
class BookingStates(StatesGroup):
    waiting_name = State()
    waiting_phone = State()

# ============ РАСПИСАНИЕ ============
SCHEDULE = {
    "АДРЕС САЛОНА : Савушкина 124 корпус 1\n"
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

# ============ БАЗА ДАННЫХ ============
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

async def check_booking_exists(day, time):
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT id FROM bookings WHERE day = ? AND time = ? AND status != 'rejected'",
            (day, time)
        )
        result = await cursor.fetchone()
        return result is not None

async def get_pending_bookings():
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT id, user_name, user_phone, day, time FROM bookings WHERE status = 'pending'"
        )
        return await cursor.fetchall()

async def get_user_bookings(user_id):
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT day, time, status FROM bookings WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )
        return await cursor.fetchall()

async def update_booking_status(booking_id, status):
    async with aiosqlite.connect("Lilith.sql") as db:
        await db.execute(
            "UPDATE bookings SET status = ? WHERE id = ?",
            (status, booking_id)
        )
        await db.commit()

async def get_booking_by_id(booking_id):
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT id, user_id, user_name, user_phone, day, time, status FROM bookings WHERE id = ?",
            (booking_id,)
        )
        return await cursor.fetchone()

# ============ КЛАВИАТУРЫ ============
def get_main_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="О боте")],
            [KeyboardButton(text="Расписание"), KeyboardButton(text="Цены"), KeyboardButton(text="Запись")],
            [KeyboardButton(text="Мои записи"), KeyboardButton(text="Помощь")]
        ],
        resize_keyboard=True
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

async def get_time_keyboard(day):
    times = SCHEDULE.get(day, {})
    buttons = []
    
    for time, status in times.items():
        if status == "свободно":
            is_booked = await check_booking_exists(day, time)
            if not is_booked:
                buttons.append([InlineKeyboardButton(
                    text=time,
                    callback_data=f"time_{day}_{time.replace(':', '')}"
                )])
    
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_schedule")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_cancel_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить запись", callback_data="cancel_booking")]
        ]
    )
    return keyboard

def get_admin_booking_keyboard(booking_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подтвердить", callback_data=f"admin_confirm_{booking_id}"),
                InlineKeyboardButton(text="Отклонить", callback_data=f"admin_reject_{booking_id}")
            ]
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
        reply_markup=get_main_reply_keyboard()
    )

@router.message(Command("rasp"))
@router.message(F.text.lower() == "расписание")
async def rasp(message: Message):
    text = "Актуальное расписание:\n\n"
    
    for day, times in SCHEDULE.items():
        text += f"{day}:\n"
        for time, status in times.items():
            is_booked = await check_booking_exists(day, time)
            if is_booked and status == "свободно":
                text += f"  {time} - занято\n"
            else:
                text += f"  {time} - {status}\n"
        text += "\n"
    
    text += "Выберите день для записи:"
    
    await message.answer(text, reply_markup=get_schedule_keyboard())

@router.callback_query(lambda c: c.data.startswith("day_"))
async def select_day(callback: CallbackQuery):
    day = callback.data.replace("day_", "")
    
    text = f"{day}\n\nСвободное время:\n"
    times = SCHEDULE.get(day, {})
    
    free_times = []
    for time, status in times.items():
        if status == "свободно":
            is_booked = await check_booking_exists(day, time)
            if not is_booked:
                free_times.append(time)
    
    if not free_times:
        text = f"{day}\n\nНет свободного времени. Выберите другой день."
        await callback.message.edit_text(text, reply_markup=get_schedule_keyboard())
        await callback.answer()
        return
    
    for time in free_times:
        text += f"{time}\n"
    
    text += "\nВыберите время:"
    
    await callback.message.edit_text(text, reply_markup=await get_time_keyboard(day))
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("time_"))
async def select_time(callback: CallbackQuery, state: FSMContext):
    data = callback.data.replace("time_", "")
    parts = data.split("_")
    day = parts[0]
    time = f"{parts[1][:2]}:{parts[1][2:]}"
    
    is_booked = await check_booking_exists(day, time)
    if is_booked:
        await callback.answer("Это время уже занято!", show_alert=True)
        await callback.message.edit_text(
            "Это время уже занято. Выберите другое время.",
            reply_markup=await get_time_keyboard(day)
        )
        return
    
    await state.update_data(day=day, time=time)
    
    await callback.message.edit_text(
        f"Вы выбрали: {day} в {time}\n\nВведите ваше имя:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(BookingStates.waiting_name)
    await callback.answer()

@router.callback_query(lambda c: c.data == "cancel_booking")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Запись отменена.\n\nВы можете начать заново через /book",
        reply_markup=get_main_reply_keyboard()
    )
    await callback.answer()

@router.message(BookingStates.waiting_name)
async def get_name(message: Message, state: FSMContext):
    if not re.match(r'^[а-яА-Яa-zA-Z\s\-]{2,50}$', message.text):
        await message.answer(
            "Пожалуйста, введите корректное имя (только буквы).\n\n"
            "Пример: Анна Иванова",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.update_data(user_name=message.text)
    await message.answer(
        "Введите ваш номер телефона:\n\nФормат: +7 999 123-45-67",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(BookingStates.waiting_phone)

@router.message(BookingStates.waiting_phone)
async def get_phone(message: Message, state: FSMContext, bot):
    phone = message.text.strip()
    
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    
    if not re.match(r'^\+?\d{10,15}$', phone_clean):
        await message.answer(
            "Неверный формат номера телефона!\n\n"
            "Примеры правильного формата:\n"
            "+7 999 123-45-67\n"
            "89991234567\n\n"
            "Пожалуйста, введите номер еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    data = await state.get_data()
    day = data.get("day")
    time = data.get("time")
    
    is_booked = await check_booking_exists(day, time)
    if is_booked:
        await message.answer(
            "Извините, это время уже занято другим пользователем.\n\n"
            "Пожалуйста, выберите другое время через /book"
        )
        await state.clear()
        return
    
    await save_booking(
        user_id=message.from_user.id,
        user_name=data.get("user_name"),
        user_phone=phone,
        day=day,
        time=time
    )
    
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT id FROM bookings WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (message.from_user.id,)
        )
        booking = await cursor.fetchone()
        booking_id = booking[0] if booking else None
    
    await message.answer(
        f"Вы записаны на {day} в {time}\n\n"
        f"Ожидайте подтверждения от администратора.",
        reply_markup=get_main_reply_keyboard()
    )
    
    admin_text = (
        f"Новая запись:\n\n"
        f"Имя: {data.get('user_name')}\n"
        f"Телефон: {phone}\n"
        f"День: {day}\n"
        f"Время: {time}"
    )
    
    admin_keyboard = get_admin_booking_keyboard(booking_id) if booking_id else None
    
    await bot.send_message(
        ADMIN_ID,
        admin_text,
        reply_markup=admin_keyboard
    )
    
    await state.clear()

@router.message(Command("book"))
@router.message(F.text.lower() == "запись")
async def book(message: Message):
    await message.answer(
        "Выберите день для записи:",
        reply_markup=get_schedule_keyboard()
    )

@router.message(Command("my"))
@router.message(F.text.lower() == "мои записи")
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
        status_text = {
            'pending': 'ожидает подтверждения',
            'confirmed': 'подтверждена',
            'rejected': 'отклонена'
        }.get(status, status)
        text += f"{day} в {time} - {status_text}\n"
    
    await message.answer(text, reply_markup=get_main_reply_keyboard())

@router.callback_query(lambda c: c.data.startswith("admin_confirm_"))
async def admin_confirm(callback: CallbackQuery, bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    booking_id = int(callback.data.replace("admin_confirm_", ""))
    
    booking = await get_booking_by_id(booking_id)
    
    if not booking:
        await callback.answer("Запись не найдена", show_alert=True)
        return
    
    await update_booking_status(booking_id, "confirmed")
    
    await callback.message.edit_text(
        f"Запись подтверждена!\n\n"
        f"{booking[2]}\n"
        f"{booking[3]}\n"
        f"{booking[4]} в {booking[5]}"
    )
    
    try:
        await bot.send_message(
            booking[1],
            f"Ваша запись на {booking[4]} в {booking[5]} ПОДТВЕРЖДЕНА!\n\nЖдем вас!"
        )
    except Exception as e:
        print(f"Не удалось уведомить пользователя: {e}")
    
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("admin_reject_"))
async def admin_reject(callback: CallbackQuery, bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    booking_id = int(callback.data.replace("admin_reject_", ""))
    
    booking = await get_booking_by_id(booking_id)
    
    if not booking:
        await callback.answer("Запись не найдена", show_alert=True)
        return
    
    await update_booking_status(booking_id, "rejected")
    
    await callback.message.edit_text(
        f"Запись отклонена!\n\n"
        f"{booking[2]}\n"
        f"{booking[3]}\n"
        f"{booking[4]} в {booking[5]}"
    )
    
    try:
        await bot.send_message(
            booking[1],
            f"Ваша запись на {booking[4]} в {booking[5]} ОТКЛОНЕНА.\n\nПопробуйте выбрать другое время."
        )
    except Exception as e:
        print(f"Не удалось уведомить пользователя: {e}")
    
    await callback.answer()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа")
        return
    
    bookings = await get_pending_bookings()
    
    if not bookings:
        await message.answer("Нет новых записей")
        return
    
    text = "Новые записи:\n\n"
    for id, name, phone, day, time in bookings:
        text += f"#{id} {name} {phone} {day} {time}\n"
    
    await message.answer(text)

@router.callback_query(lambda c: c.data == "back_schedule")
async def back_to_schedule(callback: CallbackQuery):
    text = "Актуальное расписание:\n\n"
    
    for day, times in SCHEDULE.items():
        text += f"{day}:\n"
        for time, status in times.items():
            is_booked = await check_booking_exists(day, time)
            if is_booked and status == "свободно":
                text += f"  {time} - занято\n"
            else:
                text += f"  {time} - {status}\n"
        text += "\n"
    
    text += "Выберите день для записи:"
    
    await callback.message.edit_text(text, reply_markup=get_schedule_keyboard())
    await callback.answer()

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
