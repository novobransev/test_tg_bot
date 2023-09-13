import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class TestStates(StatesGroup):
    test = State()


logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчера
API_TOKEN = '6067302316:AAEk9jLtbZPalzgtiQXQGP2Vh0b2nlUyicw'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Подключаемся к базе данных SQLite
conn = sqlite3.connect('messages.db')
cursor = conn.cursor()

# Создаем таблицу для сообщений, если ее нет
cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT)''')
conn.commit()

keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
button1 = types.KeyboardButton('Отправить сообщение')
button2 = types.KeyboardButton('Просмотреть сообщения')
keyboard.add(button1, button2)


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer('Выберите действие:', reply_markup=keyboard)


# Обработчик кнопки "Отправить сообщение"
@dp.message_handler(lambda message: message.text == 'Отправить сообщение')
async def send_message_handler(message: types.Message):
    await message.answer('Введите сообщение:', reply_markup=keyboard)
    await TestStates.test.set()


# Обработчик текстового сообщения после нажатия на кнопку "Отправить сообщение"
@dp.message_handler(state=TestStates.test)
async def save_message_handler(message: types.Message, state: FSMContext):
    # Сохраняем сообщение в базу данных
    text = message.text
    cursor.execute('INSERT INTO messages (text) VALUES (?)', (text,))
    conn.commit()
    await message.answer('Сообщение добавлено', reply_markup=keyboard)
    await state.finish()


# Обработчик кнопки "Просмотреть сообщения"
@dp.message_handler(lambda message: message.text == 'Просмотреть сообщения')
async def show_messages_handler(message: types.Message):
    cursor.execute('SELECT * FROM messages')
    messages = cursor.fetchall()
    if len(messages) > 0:
        for msg in messages:
            await message.answer(msg[1])
            await message.answer('Следующее сообщение', reply_markup=types.ReplyKeyboardRemove())
        await message.answer('Сообщения закончились', reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
