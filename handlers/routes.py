from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
import aiosqlite
import re
from datetime import datetime, timedelta

router = Router()
ADMIN_ID = 5931039603

# ============ СОСТОЯНИЯ ДЛЯ ЗАПИСИ ============
class BookingStates(StatesGroup):
    choosing_category = State()
    choosing_service = State()
    waiting_name = State()
    waiting_phone = State()

# ============ УСЛУГИ ============
SERVICES = {
    "Женские": {
        "Стрижки короткие": {"price": 1300, "duration": 30},
        "Стрижки средние": {"price": 1800, "duration": 45},
        "Стрижки длинные": {"price": 2000, "duration": 60},
        "Укладка волос": {"price": 2000, "duration": 60},
        "Окрашивание короткое": {"price": 1500, "duration": 120},
        "Окрашивание среднее": {"price": 2000, "duration": 120},
        "Окрашивание длинное": {"price": 2500, "duration": 150},
        "Окрашивание сложное": {"price": 5000, "duration": 240},
        "Уход за волосами": {"price": 1500, "duration": 60}
    },
    "Мужские": {
        "Одна насадка": {"price": 500, "duration": 20},
        "Две насадки": {"price": 600, "duration": 20},
        "Модельная стрижка": {"price": 1000, "duration": 30}
    }
}

# ============ РАСПИСАНИЕ ============
SCHEDULE = {
    "Чт 10.08": {
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
        "17:00": "свободно",
        "18:00": "свободно"
    },
    "Пт 11.08": {
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
    "Сб 12.08": {
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
    "Вс 13.08": {
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
    "Пн 14.08": {
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
    "Вт 15.08": {
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
    "Ср 16.08": "ВЫХОДНОЙ ДЕНЬ",
    "Чт 17.08": {
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
                service TEXT,
                duration INTEGER,
                status TEXT DEFAULT 'pending'
            )
        """)
        await db.commit()

async def save_booking(user_id, user_name, user_phone, day, time, service, duration):
    async with aiosqlite.connect("Lilith.sql") as db:
        await db.execute(
            "INSERT INTO bookings (user_id, user_name, user_phone, day, time, service, duration) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, user_name, user_phone, day, time, service, duration)
        )
        await db.commit()

async def check_time_available(day, time, duration):
    if day not in SCHEDULE:
        return False
    
    if SCHEDULE[day] == "ВЫХОДНОЙ ДЕНЬ":
        return False
    
    if time not in SCHEDULE[day]:
        return False
    
    if SCHEDULE[day][time] == "занято":
        return False
    
    time_obj = datetime.strptime(time, "%H:%M")
    end_time = time_obj + timedelta(minutes=duration)
    
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT time, duration FROM bookings WHERE day = ? AND status != 'rejected'",
            (day,)
        )
        bookings = await cursor.fetchall()
        
        for booked_time, booked_duration in bookings:
            booked_start = datetime.strptime(booked_time, "%H:%M")
            booked_end = booked_start + timedelta(minutes=booked_duration)
            
            if (time_obj < booked_end and end_time > booked_start):
                return False
    
    return True

async def get_pending_bookings():
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT id, user_name, user_phone, day, time, service FROM bookings WHERE status = 'pending'"
        )
        return await cursor.fetchall()

async def get_user_bookings(user_id):
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT day, time, service, status FROM bookings WHERE user_id = ? ORDER BY id DESC",
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
            "SELECT id, user_id, user_name, user_phone, day, time, service, status FROM bookings WHERE id = ?",
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
    days = [day for day in SCHEDULE.keys() if SCHEDULE[day] != "ВЫХОДНОЙ ДЕНЬ"]
    buttons = []
    
    for day in days:
        buttons.append([InlineKeyboardButton(text=day, callback_data=f"day_{day}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def get_time_keyboard(day):
    if day not in SCHEDULE or SCHEDULE[day] == "ВЫХОДНОЙ ДЕНЬ":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="back_schedule")]
            ]
        )
        return keyboard
    
    times = SCHEDULE.get(day, {})
    buttons = []
    
    for time, status in times.items():
        if status == "свободно":
            is_available = await check_time_available(day, time, 20)
            if is_available:
                buttons.append([InlineKeyboardButton(
                    text=time,
                    callback_data=f"time_{day}_{time.replace(':', '')}"
                )])
    
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_schedule")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_category_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Женские виды", callback_data="category_Женские")],
            [InlineKeyboardButton(text="Мужские виды", callback_data="category_Мужские")],
            [InlineKeyboardButton(text="Назад", callback_data="back_schedule")]
        ]
    )
    return keyboard

def get_services_keyboard(category):
    services = SERVICES.get(category, {})
    buttons = []
    
    for service, info in services.items():
        duration_hours = info['duration'] // 60
        duration_minutes = info['duration'] % 60
        duration_text = f"{duration_hours}ч {duration_minutes}мин" if duration_hours > 0 else f"{duration_minutes}мин"
        buttons.append([InlineKeyboardButton(
            text=f"{service} - {info['price']}₽ ({duration_text})",
            callback_data=f"service_{category}_{service}"
        )])
    
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_category")])
    
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
    
    for day, value in SCHEDULE.items():
        if value == "ВЫХОДНОЙ ДЕНЬ":
            text += f"{day}: ВЫХОДНОЙ\n\n"
            continue
        
        text += f"{day}:\n"
        for time, status in value.items():
            if status == "занято":
                text += f"  {time} - занято\n"
            else:
                is_available = await check_time_available(day, time, 20)
                if is_available:
                    text += f"  {time} - свободно\n"
                else:
                    text += f"  {time} - занято\n"
        text += "\n"
    
    text += "Выберите день для записи:"
    
    await message.answer(text, reply_markup=get_schedule_keyboard())

@router.callback_query(lambda c: c.data.startswith("day_"))
async def select_day(callback: CallbackQuery):
    day = callback.data.replace("day_", "")
    
    if day not in SCHEDULE or SCHEDULE[day] == "ВЫХОДНОЙ ДЕНЬ":
        await callback.message.edit_text(
            f"{day}\n\nВыходной день. Выберите другой день.",
            reply_markup=get_schedule_keyboard()
        )
        await callback.answer()
        return
    
    text = f"{day}\n\nСвободное время:\n"
    times = SCHEDULE.get(day, {})
    
    free_times = []
    for time, status in times.items():
        if status == "свободно":
            is_available = await check_time_available(day, time, 20)
            if is_available:
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
    
    is_available = await check_time_available(day, time, 20)
    if not is_available:
        await callback.answer("Это время уже занято!", show_alert=True)
        await callback.message.edit_text(
            "Это время уже занято. Выберите другое время.",
            reply_markup=await get_time_keyboard(day)
        )
        return
    
    await state.update_data(day=day, time=time)
    
    await callback.message.edit_text(
        f"Вы выбрали: {day} в {time}\n\n"
        "Выберите категорию услуги:",
        reply_markup=get_category_keyboard()
    )
    await state.set_state(BookingStates.choosing_category)
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_category")
async def back_to_category(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    day = data.get("day")
    time = data.get("time")
    
    await callback.message.edit_text(
        f"Вы выбрали: {day} в {time}\n\n"
        "Выберите категорию услуги:",
        reply_markup=get_category_keyboard()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("category_"))
async def select_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace("category_", "")
    await state.update_data(category=category)
    
    data = await state.get_data()
    day = data.get("day")
    time = data.get("time")
    
    await callback.message.edit_text(
        f"Вы выбрали: {day} в {time}\n"
        f"Категория: {category}\n\n"
        "Выберите услугу:",
        reply_markup=get_services_keyboard(category)
    )
    await state.set_state(BookingStates.choosing_service)
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("service_"))
async def select_service(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.replace("service_", "").split("_")
    category = data_parts[0]
    service_name = "_".join(data_parts[1:])
    
    service_info = SERVICES.get(category, {}).get(service_name)
    if not service_info:
        await callback.answer("Услуга не найдена", show_alert=True)
        return
    
    duration = service_info['duration']
    price = service_info['price']
    
    data = await state.get_data()
    day = data.get("day")
    time = data.get("time")
    
    is_available = await check_time_available(day, time, duration)
    if not is_available:
        duration_hours = duration // 60
        duration_minutes = duration % 60
        duration_text = f"{duration_hours}ч {duration_minutes}мин" if duration_hours > 0 else f"{duration_minutes}мин"
        
        await callback.message.edit_text(
            f"Извините, для услуги '{service_name}' требуется {duration_text}.\n"
            f"Это время уже занято. Пожалуйста, выберите другое время.",
            reply_markup=await get_time_keyboard(day)
        )
        await callback.answer()
        return
    
    await state.update_data(service=service_name, duration=duration, price=price)
    
    duration_hours = duration // 60
    duration_minutes = duration % 60
    duration_text = f"{duration_hours}ч {duration_minutes}мин" if duration_hours > 0 else f"{duration_minutes}мин"
    
    await callback.message.edit_text(
        f"Вы выбрали:\n"
        f"День: {day}\n"
        f"Время: {time}\n"
        f"Услуга: {service_name}\n"
        f"Длительность: {duration_text}\n"
        f"Цена: {price}₽\n\n"
        "Введите ваше имя:",
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
    service = data.get("service")
    duration = data.get("duration")
    
    is_available = await check_time_available(day, time, duration)
    if not is_available:
        await message.answer(
            "Извините, это время уже занято с учетом длительности услуги.\n\n"
            "Пожалуйста, выберите другое время через /book"
        )
        await state.clear()
        return
    
    await save_booking(
        user_id=message.from_user.id,
        user_name=data.get("user_name"),
        user_phone=phone,
        day=day,
        time=time,
        service=service,
        duration=duration
    )
    
    async with aiosqlite.connect("Lilith.sql") as db:
        cursor = await db.execute(
            "SELECT id FROM bookings WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (message.from_user.id,)
        )
        booking = await cursor.fetchone()
        booking_id = booking[0] if booking else None
    
    duration_hours = duration // 60
    duration_minutes = duration % 60
    duration_text = f"{duration_hours}ч {duration_minutes}мин" if duration_hours > 0 else f"{duration_minutes}мин"
    
    await message.answer(
        f"Вы записаны!\n\n"
        f"День: {day}\n"
        f"Время: {time}\n"
        f"Услуга: {service}\n"
        f"Длительность: {duration_text}\n"
        f"Цена: {data.get('price')}₽\n\n"
        f"Ожидайте подтверждения от администратора.",
        reply_markup=get_main_reply_keyboard()
    )
    
    admin_text = (
        f"Новая запись:\n\n"
        f"Имя: {data.get('user_name')}\n"
        f"Телефон: {phone}\n"
        f"День: {day}\n"
        f"Время: {time}\n"
        f"Услуга: {service}\n"
        f"Длительность: {duration_text}\n"
        f"Цена: {data.get('price')}₽"
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
    for day, time, service, status in bookings:
        status_text = {
            'pending': 'ожидает подтверждения',
            'confirmed': 'подтверждена',
            'rejected': 'отклонена'
        }.get(status, status)
        text += f"{day} в {time} - {service} - {status_text}\n"
    
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
        f"{booking[4]} в {booking[5]}\n"
        f"Услуга: {booking[6]}"
    )
    
    try:
        await bot.send_message(
            booking[1],
            f"Ваша запись на {booking[4]} в {booking[5]} ПОДТВЕРЖДЕНА!\n"
            f"Услуга: {booking[6]}\n\nЖдем вас!"
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
        f"{booking[4]} в {booking[5]}\n"
        f"Услуга: {booking[6]}"
    )
    
    try:
        await bot.send_message(
            booking[1],
            f"Ваша запись на {booking[4]} в {booking[5]} ОТКЛОНЕНА.\n"
            f"Услуга: {booking[6]}\n\nПопробуйте выбрать другое время."
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
    for id, name, phone, day, time, service in bookings:
        text += f"#{id} {name} {phone} {day} {time} {service}\n"
    
    await message.answer(text)

@router.callback_query(lambda c: c.data == "back_schedule")
async def back_to_schedule(callback: CallbackQuery):
    text = "Актуальное расписание:\n\n"
    
    for day, value in SCHEDULE.items():
        if value == "ВЫХОДНОЙ ДЕНЬ":
            text += f"{day}: ВЫХОДНОЙ\n\n"
            continue
        
        text += f"{day}:\n"
        for time, status in value.items():
            if status == "занято":
                text += f"  {time} - занято\n"
            else:
                is_available = await check_time_available(day, time, 20)
                if is_available:
                    text += f"  {time} - свободно\n"
                else:
                    text += f"  {time} - занято\n"
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
