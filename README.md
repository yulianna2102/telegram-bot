`````python`````
import logging
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import hashlib


token = '6413099986:AAFmtKBffyfR6Qe3Kye-bk0b4YdU8NBzjs4'


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


translations = {
    'en': {
        'welcome': "Hey!👋🏻 I'm your room booking bot. You can use the following commands:\n"
                   "/register - Register your account\n"
                   "/availability - Check available rooms\n"
                   "/book - Book a room\n"
                   "/cancel - Cancel a booking\n"
                   "/view_profile - View your profile\n"
                   "/set_language - Set your preferred language\n"
                   "/delete_account - delete your account\n"
                   "If you're having any problems, contact +380983404568",
        'register_prompt': "Please enter your name:",
        'surname_prompt': "Please enter your surname:",
        'password_prompt': "Please enter your password:",
        'registration_success': "You have been successfully registered!✨",
        'registration_already': "You are already registered",
        'please_register': "Please register first.",
        'availability_prompt': "You can view more details following this link: {link}\n(Make sure to open on a desktop device)\nIf you are having issues with opening the website, send 'Send' and I'll write down all the information.",
        'no_rooms': "No available rooms.",
        'available_rooms': "Here are the available rooms: \n\n\n{rooms}",
        'book_room_id': "Please enter the room ID you want to book:",
        'room_unavailable': "Apologies, this room has already been booked. Choose another one:",
        'start_date_prompt': "Please enter the start date of your booking (format: yyyy-mm-dd):",
        'end_date_prompt': "Please enter the end date (YYYY-MM-DD):",
        'invalid_date': "Invalid date format. Please use YYYY-MM-DD.",
        'booking_success': "Room {room_id} booked from {start_date} to {end_date}.\nYour booking ID is: {booking_id}.\nWhen you come to our hotel, tell the manager your full name, booking id, and your password.\nHave a great time!",
        'cancel_prompt': "Please enter the booking ID you want to cancel:",
        'cancel_success': "Booking ID {booking_id} for room ID {room_id} has been successfully canceled.",
        'booking_id_error': "Booking ID must be a number. Please try again.",
        'booking_not_exists': "The booking ID {booking_id} does not exist. Please check and try again.",
        'view_profile': "Here's the link to view your profile: {link}\nMake sure to open it on your desktop!",
        'choose_language': "Please choose your language / Будь ласка, виберіть свою мову / يرجى اختيار لغتك",
        'delete_success': "Your account has been successfully deleted.",
        'no_account_to_delete': "You do not have an account to delete.",
        'language_success': "Language has been set successfully🇺🇸",
        'user_id': 'User ID',
        'bookings': 'Bookings',
        'booking_id': 'Booking ID',
        'room_id': 'Room ID',
        'start_date': 'Start Date',
        'end_date': 'End Date',
        'no_bookings': 'No bookings found.',
        'user_not_found': 'User not found.'
    },
    'uk': {
        'welcome': "Привіт!👋🏻 Я ваш бот для бронювання номерів. Ви можете використовувати наступні команди:\n"
                   "/register - Зареєструвати свій обліковий запис\n"
                   "/availability - Перевірити доступні номери\n"
                   "/book - Забронювати номер\n"
                   "/cancel - Скасувати бронювання\n"
                   "/view_profile - Переглянути свій профіль\n"
                   "/set_language - Встановити бажану мову\n"
                   "/delete_account - Видалити обліковий запис\n"
                   "Якщо у вас виникли проблеми, зв'яжіться з +380983404568",
        'register_prompt': "Будь ласка, введіть своє ім'я:",
        'surname_prompt': "Будь ласка, введіть своє прізвище:",
        'password_prompt': "Будь ласка, введіть свій пароль:",
        'registration_success': "Ви успішно зареєстровані!✨",
        'registration_already': "Ви вже зареєстровані.",
        'please_register': "Будь-ласка, зареєструйтесь спочатку.",
        'availability_prompt': "Ви можете переглянути більше деталей за цим посиланням: {link}\n(Переконайтеся, що відкрили на настільному пристрої)\nЯкщо у вас виникли проблеми з відкриттям веб-сайту, надішліть 'Send' і я запишу всю інформацію.",
        'no_rooms': "Немає доступних номерів.",
        'available_rooms': "Ось доступні номери: \n\n\n{rooms}",
        'book_room_id': "Будь ласка, введіть ID номера, який хочете забронювати:",
        'room_unavailable': "Вибачте, цей номер вже заброньовано. Виберіть інший:",
        'start_date_prompt': "Будь ласка, введіть дату початку бронювання (формат: yyyy-mm-dd):",
        'end_date_prompt': "Будь ласка, введіть дату закінчення (YYYY-MM-DD):",
        'invalid_date': "Неправильний формат дати. Будь ласка, використовуйте YYYY-MM-DD.",
        'booking_success': "Номер {room_id} заброньовано з {start_date} по {end_date}.\nВаш ID бронювання: {booking_id}.\nКоли ви прийдете до нашого готелю, скажіть менеджеру своє повне ім'я, ID бронювання та пароль.\nГарного вам часу!",
        'cancel_prompt': "Будь ласка, введіть ID бронювання, який хочете скасувати:",
        'cancel_success': "Бронювання з ID {booking_id} для номера {room_id} було успішно скасовано.",
        'booking_id_error': "ID бронювання має бути числом. Будь ласка, спробуйте ще раз.",
        'booking_not_exists': "Бронювання з ID {booking_id} не існує. Будь ласка, перевірте та спробуйте ще раз.",
        'view_profile': "Ось посилання для перегляду вашого профілю: {link}\nПереконайтеся, що відкрили на настільному пристрої!",
        'choose_language': "Будь ласка, виберіть свою мову / Please choose your language / يرجى اختيار لغتك",
        'delete_success': "Ваш обліковий запис успішно видалено.",
        'no_account_to_delete': "У вас немає облікового запису для видалення.",
        'language_success': "Мову успішно встановлено🇺🇦",
        'user_id': 'ID користувача',
        'bookings': 'Бронювання',
        'booking_id': 'ID бронювання',
        'room_id': 'Номер кімнати',
        'start_date': 'Дата початку',
        'end_date': 'Дата завершення',
        'no_bookings': 'Бронювань не знайдено.',
        'user_not_found': 'Користувача не знайдено.'
    },
    'ar': {
        'welcome': "مرحبًا!👋🏻 أنا بوت حجز الغرف الخاص بك. يمكنك استخدام الأوامر التالية:\n"
                   "/register - تسجيل حسابك\n"
                   "/availability - التحقق من الغرف المتاحة\n"
                   "/book - حجز غرفة\n"
                   "/cancel - إلغاء الحجز\n"
                   "/view_profile - عرض ملفك الشخصي\n"
                   "/set_language - تعيين لغتك المفضلة\n"
                   "/delete_account - حذف حسابك\n"
                   "إذا كنت تواجه أي مشاكل، اتصل بالرقم +380983404568",
        'register_prompt': "يرجى إدخال اسمك:",
        'surname_prompt': "يرجى إدخال اسم عائلتك:",
        'password_prompt': "يرجى إدخال كلمة المرور الخاصة بك:",
        'registration_success': "لقد تم تسجيلك بنجاح!✨",
        'registration_already': "أنت مسجل بالفعل.",
        'please_register': "الرجاء التسجيل أولاً",
        'availability_prompt': "يمكنك الاطلاع على المزيد من التفاصيل عبر هذا الرابط: {link}\n(تأكد من فتحه على جهاز سطح المكتب)\nإذا كنت تواجه مشكلات في فتح الموقع، أرسل 'Send' وسأكتب لك جميع المعلومات.",
        'no_rooms': "لا توجد غرف متاحة.",
        'available_rooms': "إليك الغرف المتاحة: \n\n\n{rooms}",
        'book_room_id': "يرجى إدخال معرف الغرفة التي تريد حجزها:",
        'room_unavailable': "عذرًا، هذه الغرفة محجوزة بالفعل. اختر غرفة أخرى:",
        'start_date_prompt': "يرجى إدخال تاريخ بدء الحجز (التنسيق: yyyy-mm-dd):",
        'end_date_prompt': "يرجى إدخال تاريخ انتهاء الحجز (YYYY-MM-DD):",
        'invalid_date': "تنسيق التاريخ غير صالح. يرجى استخدام YYYY-MM-DD.",
        'booking_success': "تم حجز الغرفة {room_id} من {start_date} إلى {end_date}.\nمعرف الحجز الخاص بك هو: {booking_id}.\nعند وصولك إلى فندقنا، أخبر المدير باسمك الكامل ومعرف الحجز وكلمة المرور.\nأتمنى لك وقتًا رائعًا!",
        'cancel_prompt': "يرجى إدخال معرف الحجز الذي تريد إلغاءه:",
        'cancel_success': "تم إلغاء الحجز بالمعرف {booking_id} للغرفة {room_id} بنجاح.",
        'booking_id_error': "يجب أن يكون معرف الحجز رقمًا. يرجى المحاولة مرة أخرى.",
        'booking_not_exists': "معرف الحجز {booking_id} غير موجود. يرجى التحقق والمحاولة مرة أخرى.",
        'view_profile': "إليك الرابط لعرض ملفك الشخصي: {link}\nتأكد من فتحه على جهاز سطح المكتب!",
        'choose_language': "يرجى اختيار لغتك / Будь ласка, виберіть свою мову / Please choose your language",
        'delete_success': "تم حذف حسابك بنجاح.",
        'no_account_to_delete': "ليس لديك حساب لحذفه.",
        'language_success': "تم تعيين اللغة بنجاح🇦🇪",
        'user_id': 'معرف المستخدم',
        'bookings': 'الحجوزات',
        'booking_id': 'معرف الحجز',
        'room_id': 'معرف الغرفة',
        'start_date': 'تاريخ البدء',
        'end_date': 'تاريخ الانتهاء',
        'no_bookings': 'لا يوجد حجوزات.',
        'user_not_found': 'المستخدم غير موجود.'
    }
}

def initialize_database():
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            surname TEXT,
            password_hash TEXT,
            is_registered INTEGER DEFAULT 0,
            language TEXT DEFAULT 'en'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_languages (
            user_id INTEGER PRIMARY KEY,
            language TEXT
        )
    ''')

    conn.commit()
    conn.close()


def register_user(user_id, username, name, surname, password):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('INSERT INTO users (user_id, username, name, surname, password_hash, is_registered) VALUES (?, ?, ?, ?, ?, 1)',
                   (user_id, username, name, surname, password_hash))
    conn.commit()
    conn.close()

def is_user_registered(user_id):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('SELECT is_registered FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1


def delete_user_account(user_id):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    if user:
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        result = True
    else:
        result = False

    conn.close()
    return result


@dp.message_handler(commands=['delete_account'])
async def delete_account_command(message: types.Message):
    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'
    if delete_user_account(user_id):
        await message.reply(translations[language_code]['delete_success'])
    else:
        await message.reply(translations[language_code]['no_account_to_delete'])


def get_available_rooms():
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, room_number FROM rooms WHERE is_available=1')
    rooms = cursor.fetchall()
    conn.close()
    return rooms


def book_a_room(room_id, user_id, start_date, end_date):
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bookings (room_id, user_id, start_date, end_date)
    VALUES (?, ?, ?, ?)
    ''', (room_id, user_id, start_date, end_date))


    booking_id = cursor.lastrowid

    cursor.execute('UPDATE rooms SET is_available=0 WHERE id=?', (room_id,))
    conn.commit()
    conn.close()

    return booking_id


def cancel_booking(booking_id, language_code):
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT room_id FROM bookings WHERE id=?', (booking_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise ValueError(translations[language_code]['booking_not_exist'].format(booking_id=booking_id))

    room_id = result[0]

    cursor.execute('DELETE FROM bookings WHERE id=?', (booking_id,))
    cursor.execute('UPDATE rooms SET is_available=1 WHERE id=?', (room_id,))
    conn.commit()
    conn.close()

    return translations[language_code]['cancel_success'].format(booking_id=booking_id, room_id=room_id)

def get_room_cost(room_id):
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT cost FROM rooms WHERE id = ?', (room_id,))
    cost = cursor.fetchone()[0]
    conn.close()
    return cost

def get_room_balcony(room_id):
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balcony FROM rooms WHERE id = ?', (room_id,))
    balcony = cursor.fetchone()[0]
    conn.close()
    return balcony

def get_room_bed_type(room_id):
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT bed_type FROM rooms WHERE id = ?', (room_id,))
    bed_type = cursor.fetchone()[0]
    conn.close()
    return bed_type


class BookingForm(StatesGroup):
    room_id = State()
    start_date = State()
    end_date = State()


class CancelForm(StatesGroup):
    booking_id = State()


class LanguageForm(StatesGroup):
    language = State()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton('/register'), KeyboardButton('/set_language'))
    await message.reply('use the /set_language command first\n Спочатку використайте команду /set_language\nاستخدم الأمر "/set_language" في البدايةً ', reply_markup=keyboard)

@dp.message_handler(Command('register'))
async def register_user_command(message: types.Message):
    user_language = get_the_user_language(message.from_user.id)
    await message.reply(translations[user_language]['register_prompt'])
    await RegistrationForm.name.set()



class RegistrationForm(StatesGroup):
    name = State()
    surname = State()
    password = State()


@dp.message_handler(state=RegistrationForm.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'

    await RegistrationForm.next()
    await message.reply(translations[language_code]['surname_prompt'])


@dp.message_handler(state=RegistrationForm.surname)
async def process_surname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['surname'] = message.text
    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'
    await RegistrationForm.next()
    await message.reply(translations[language_code]['password_prompt'])


@dp.message_handler(state=RegistrationForm.password)
async def process_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

    user_id = message.from_user.id
    username = message.from_user.username
    name = data['name']
    surname = data['surname']
    password = data['password']

    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'

    try:
        register_user(user_id, username, name, surname, password)
        await message.reply(translations[language_code]['registration_success'])
    except sqlite3.IntegrityError:
        await message.reply(translations[language_code]['registration_already'])
    await state.finish()

def get_user_language(user_id):
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute("SELECT language FROM user_languages WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


@dp.message_handler(Command('availability'))
async def send_availability(message: types.Message):
    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'

    if not is_user_registered(user_id):
        await message.reply(translations[language_code]['please_register'])
        return

    web_app_link = "http://127.0.0.1:1234"
    await message.reply(translations[language_code]['availability_prompt'].format(link=web_app_link))


@dp.message_handler(lambda message: message.text == 'Send')
async def send_room_info(message: types.Message):
    translations['en']['room_number'] = "Room number"
    translations['en']['cost'] = "Cost"
    translations['en']['balcony'] = "Balcony"
    translations['en']['bed_type'] = "Bed type"
    translations['en']['yes'] = "Yes"
    translations['en']['no'] = "No"
    translations['uk']['room_number'] = "Номер кімнати"
    translations['uk']['cost'] = "Вартість"
    translations['uk']['balcony'] = "Балкон"
    translations['uk']['bed_type'] = "Тип ліжка"
    translations['uk']['yes'] = "Так"
    translations['uk']['no'] = "Ні"
    translations['ar']['room_number'] = "رقم الغرفة"
    translations['ar']['cost'] = "التكلفة"
    translations['ar']['balcony'] = "شرفة"
    translations['ar']['bed_type'] = "نوع السرير"
    translations['ar']['yes'] = "نعم"
    translations['ar']['no'] = "لا"
    translations['en']['single_bed'] = "Single"
    translations['en']['double_bed'] = "Double"
    translations['en']['queen_bed'] = "Queen"
    translations['en']['king_bed'] = "King"
    translations['uk']['single_bed'] = "Односпальне"
    translations['uk']['double_bed'] = "Двоспальне"
    translations['uk']['queen_bed'] = "Квін-сайз"
    translations['uk']['king_bed'] = "Кінг-сайз"
    translations['ar']['single_bed'] = "سرير مفرد"
    translations['ar']['double_bed'] = "سرير مزدوج"
    translations['ar']['queen_bed'] = "سرير كوين"
    translations['ar']['king_bed'] = "سرير كينج"

    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'

    if not is_user_registered(user_id):
        await message.reply(translations[language_code]['please_register'])
        return

    rooms = get_available_rooms()
    if not rooms:
        await message.reply(translations[language_code]['no_rooms'])
    else:
        available_rooms = ''
        for room in rooms:
            room_id = room[0]
            room_number = room[1]
            cost = get_room_cost(room_id)
            balcony = get_room_balcony(room_id)
            bed_type = get_room_bed_type(room_id)
            if bed_type == "Single":
                bed_type_translated = translations[language_code]['single_bed']
            elif bed_type == "Double":
                bed_type_translated = translations[language_code]['double_bed']
            elif bed_type == "Queen":
                bed_type_translated = translations[language_code]['queen_bed']
            elif bed_type == "King":
                bed_type_translated = translations[language_code]['king_bed']
            else:
                bed_type_translated = bed_type

            room_info = (f"{translations[language_code]['room_number']}: {room_number}\n"
                         f"{translations[language_code]['cost']}: {cost}$\n"
                         f"{translations[language_code]['balcony']}: {translations[language_code]['yes'] if balcony else translations[language_code]['no']}\n"
                         f"{translations[language_code]['bed_type']}: {bed_type_translated}\n\n")
            available_rooms += room_info
        await message.reply(translations[language_code]['available_rooms'].format(rooms=available_rooms))


@dp.message_handler(Command('book'))
async def book_start(message: types.Message):
    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'

    if not is_user_registered(user_id):
        await message.reply(translations[language_code]['please_register'])
        return
    await BookingForm.room_id.set()
    await message.reply(translations[language_code]['book_room_id'])


@dp.message_handler(state=BookingForm.room_id)
async def book_room(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'

    room_id = int(message.text)
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_available FROM rooms WHERE id = ?", (room_id,))
    room = cursor.fetchone()
    conn.close()
    if room is None or not room[0]:
        await message.reply(translations[language_code]['room_unavailable'])
        await BookingForm.room_id.set()
    else:
        await state.update_data(room_id=room_id)
        await message.reply(translations[language_code]['start_date_prompt'])
        await BookingForm.next()


@dp.message_handler(state=BookingForm.start_date)
async def process_start_date(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'
    start_date = message.text
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        async with state.proxy() as data:
            data['start_date'] = start_date
        await BookingForm.next()
        await message.reply(translations[language_code]['end_date_prompt'])
    except ValueError:
        await message.reply(translations[language_code]['invalid_date'])


@dp.message_handler(state=BookingForm.end_date)
async def process_end_date(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'

    end_date = message.text
    try:
        datetime.strptime(end_date, '%Y-%m-%d')
        async with state.proxy() as data:
            data['end_date'] = end_date
            room_id = int(data['room_id'])
            start_date = data['start_date']
            user_id = message.from_user.id

            booking_id = book_a_room(room_id, user_id, start_date, end_date)
            await message.reply(
                translations[language_code]['booking_success'].format(room_id=room_id, start_date=start_date, end_date=end_date, booking_id=booking_id))
        await state.finish()
    except ValueError:
        await message.reply(translations[language_code]['invalid_date'])
    except Exception as e:
        await message.reply(f"An error occurred: {e}")

    await state.finish()


@dp.message_handler(Command('cancel'))
async def cancel_start(message: types.Message):
    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'

    if not is_user_registered(user_id):
        await message.reply(translations[language_code]['please_register'])
        return
    await CancelForm.booking_id.set()
    await message.reply(translations[language_code]['cancel_prompt'])



@dp.message_handler(commands=['view_profile'])
async def view_profile(message: types.Message):
    user_id = message.from_user.id
    language_code = get_the_user_language(user_id)
    if not language_code:
        language_code = 'en'

    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, surname, username FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()

    if user_info:
        name, surname, username = user_info
        conn = sqlite3.connect('hotel_booking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, room_id, start_date, end_date FROM bookings WHERE user_id = ?", (user_id,))
        bookings = cursor.fetchall()

        profile_info = f"👤 {name} {surname} (@{username})\n\n"
        profile_info += f"🎭 {translations[language_code].get('user_id', 'User ID')}: {user_id}\n\n"

        if bookings:
            profile_info += f"📅 {translations[language_code].get('bookings', 'Bookings')}:\n"
            for booking in bookings:
                booking_id, room_id, start_date, end_date = booking
                profile_info += f"  {translations[language_code].get('booking_id', 'Booking ID')}: {booking_id}\n"
                profile_info += f"  {translations[language_code].get('room_id', 'Room ID')}: {room_id}\n"
                profile_info += f"  {translations[language_code].get('start_date', 'Start Date')}: {start_date}\n"
                profile_info += f"  {translations[language_code].get('end_date', 'End Date')}: {end_date}\n\n"
        else:
            profile_info += f"{translations[language_code].get('no_bookings', 'No bookings found.')}\n"

        await message.reply(profile_info)
    else:
        await message.reply(translations[language_code].get('user_not_found', 'User not found.'))

    conn.close()

@dp.message_handler(state=CancelForm.booking_id)
async def process_cancel_id(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language_code = get_user_language(user_id)
    if not language_code:
        language_code = 'en'

    booking_id = message.text
    if not booking_id.isdigit():
        await message.reply(translations[language_code]['booking_id_error'])
        return

    booking_id = int(booking_id)
    try:
        result = cancel_booking(booking_id, language_code)
        await message.reply(result)
        logger.info(f"Cancel Booking Result: {result}")
    except ValueError as ve:
        await message.reply(str(ve))
        logger.error(f"Error: {ve}")
    except Exception as e:
        await message.reply(f"An error occurred while canceling the booking: {e}")
        logger.error(f"Error: {e}")
    finally:
        await state.finish()




@dp.message_handler(Command('set_language'))
async def set_language(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("English 🇺🇸", callback_data="set_language_en"),
        InlineKeyboardButton("Українська 🇺🇦", callback_data="set_language_uk"),
        InlineKeyboardButton("العربية 🇸🇦", callback_data="set_language_ar")
    )
    await message.answer("Please choose your language / Будь ласка, виберіть свою мову / يرجى اختيار لغتك", reply_markup=keyboard)


@dp.message_handler(Command('change_language'))
async def change_language(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("English 🇺🇸", callback_data="change_language_en"),
        InlineKeyboardButton("Українська 🇺🇦", callback_data="change_language_uk"),
        InlineKeyboardButton("العربية 🇸🇦", callback_data="change_language_ar")
    )
    await message.answer("Please choose your language / Будь ласка, виберіть свою мову / يرجى اختيار لغتك",
                         reply_markup=keyboard)






def get_the_user_language(user_id):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM user_languages WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

async def set_user_language(user_id, language_code):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_languages (user_id, language) VALUES (?,?)", (user_id, language_code))
    conn.commit()
    conn.close()

async def get_user_language(user_id):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM user_languages WHERE user_id =?", (user_id,))
    language_code = cursor.fetchone()[0]
    conn.close()
    return language_code

@dp.message_handler(Command('change_language'))
async def change_language(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("English 🇺🇸", callback_data="set_language_en"),
        InlineKeyboardButton("Українська 🇺🇦", callback_data="set_language_uk"),
        InlineKeyboardButton("العربية 🇸🇦", callback_data="set_language_ar")
    )
    await message.answer("Please choose your language / Будь ласка, виберіть свою мову / يرجى اختيار لغتك", reply_markup=keyboard)

@dp.callback_query_handler()
async def language_callback(query: types.CallbackQuery, state: FSMContext):
    language_code = query.data.split('_')[-1]
    user_id = query.from_user.id
    await set_user_language(user_id, language_code)
    language_code = await get_user_language(user_id)
    await query.message.answer(translations[language_code]['language_success'])
    await query.message.answer(translations[language_code]['welcome'])
    await state.reset_state()

@dp.message_handler()
async def handle_message(message: types.Message, state: FSMContext):
    language_code = await get_user_language(message.from_user.id)
    await message.answer(translations[language_code]['welcome'])


@dp.callback_query_handler(state=LanguageForm.language)
async def process_language(callback_query: types.CallbackQuery, state: FSMContext):
    language = callback_query.data
    await state.update_data(language=language)
    await callback_query.message.reply(translations[language]['language_set'])
    await state.reset_state()


if __name__ == '__main__':
    initialize_database()
    executor.start_polling(dp, skip_updates=True)






````````






