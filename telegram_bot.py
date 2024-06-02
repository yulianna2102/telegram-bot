import logging
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import hashlib
from googletrans import Translator

token = '6413099986:AAFmtKBffyfR6Qe3Kye-bk0b4YdU8NBzjs4'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

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
            is_registered INTEGER DEFAULT 0
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


def cancel_booking(booking_id):
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()


    cursor.execute('SELECT room_id FROM bookings WHERE id=?', (booking_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise ValueError(f"Booking ID {booking_id} does not exist.")

    room_id = result[0]


    cursor.execute('DELETE FROM bookings WHERE id=?', (booking_id,))
    cursor.execute('UPDATE rooms SET is_available=1 WHERE id=?', (room_id,))
    conn.commit()
    conn.close()

    return f"Booking ID {booking_id} for room ID {room_id} has been successfully canceled."



class BookingForm(StatesGroup):
    room_id = State()
    start_date = State()
    end_date = State()


class CancelForm(StatesGroup):
    booking_id = State()


@dp.message_handler(Command('start'))
async def send_welcome(message: types.Message):
    await message.reply("Hey! I'm your hotel booking bot. You can use the following commands:\n"
                        "/register - Register your account\n"
                        "/availability - Check available rooms\n"
                        "/book - Book a room\n"
                        "/cancel - Cancel a booking")

@dp.message_handler(Command('register'))
async def register_user_command(message: types.Message):
    await message.reply("Please enter your name:")
    await RegistrationForm.name.set()

class RegistrationForm(StatesGroup):
    name = State()
    surname = State()
    password = State()

@dp.message_handler(state=RegistrationForm.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await RegistrationForm.next()
    await message.reply("Please enter your surname:")


@dp.message_handler(state=RegistrationForm.surname)
async def process_surname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['surname'] = message.text
    await RegistrationForm.next()
    await message.reply("Please enter your password:")


@dp.message_handler(state=RegistrationForm.password)
async def process_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

    user_id = message.from_user.id
    username = message.from_user.username
    name = data['name']
    surname = data['surname']
    password = data['password']

    register_user(user_id, username, name, surname, password)
    await message.reply("You have been successfully registered!")
    await state.finish()


@dp.message_handler(Command('availability'))
async def send_availability(message: types.Message):
    if not is_user_registered(message.from_user.id):
        await message.reply("Please register using /register command first.")
        return
    else:
        rooms = get_available_rooms()
        if not rooms:
            await message.reply("No available rooms.")
        else:
            available_rooms = '\n'.join([f'{room[1]}' for room in rooms])
            await message.reply(f'Available rooms:\n{available_rooms}')


@dp.message_handler(Command('book'))
async def book_start(message: types.Message):
    if not is_user_registered(message.from_user.id):
        await message.reply("Please register using /register command first.")
        return
    await BookingForm.room_id.set()
    await message.reply("Please enter the room ID you want to book:")


@dp.message_handler(state=BookingForm.room_id)
async def book_room(message: types.Message, state: FSMContext):
    room_id = int(message.text)
    conn = sqlite3.connect('hotel_booking.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_available FROM rooms WHERE id = ?", (room_id,))
    room = cursor.fetchone()
    conn.close()
    if room is None or not room[0]:
        await message.reply("Apologies, this room has already been booked. Choose another one:")
        await BookingForm.room_id.set()
    else:
        await state.update_data(room_id=room_id)
        await message.reply("Please enter the start date of your booking (format: yyyy-mm-dd):")
        await BookingForm.next()


@dp.message_handler(state=BookingForm.room_id)
async def process_room_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['room_id'] = message.text
    await BookingForm.next()
    await message.reply("Please enter the start date (YYYY-MM-DD):")


@dp.message_handler(state=BookingForm.start_date)
async def process_start_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['start_date'] = message.text
    await BookingForm.next()
    await message.reply("Please enter the end date (YYYY-MM-DD):")


@dp.message_handler(state=BookingForm.end_date)
async def process_end_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['end_date'] = message.text
        room_id = int(data['room_id'])
        start_date = data['start_date']
        end_date = data['end_date']
        user_id = message.from_user.id

        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            booking_id = book_a_room(room_id, user_id, start_date, end_date)
            await message.reply(
                f'Room {room_id} booked from {start_date} to {end_date}.\nYour booking ID is: {booking_id}.'
                f'\nWhen you come to our hotel, tell the manager your full name, booking id, and your password.'
                f'\nHave a great time!')

        except ValueError:
            await message.reply("Invalid date format. Please use YYYY-MM-DD.")
        except Exception as e:
            await message.reply(f"An error occurred: {e}")

    await state.finish()


@dp.message_handler(Command('cancel'))
async def cancel_start(message: types.Message):
    if not is_user_registered(message.from_user.id):
        await message.reply("Please register using /register command first.")
        return
    await CancelForm.booking_id.set()
    await message.reply("Please enter the booking ID you want to cancel:")


@dp.message_handler(state=CancelForm.booking_id)
async def process_cancel_id(message: types.Message, state: FSMContext):
    booking_id = message.text
    if not booking_id.isdigit():
        await message.reply("Booking ID must be a number. Please try again.")
        return

    booking_id = int(booking_id)
    try:
        result = cancel_booking(booking_id)
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


if __name__ == '__main__':
    initialize_database()
    executor.start_polling(dp, skip_updates=True)




