import telebot
from telebot import types
import datetime
import sqlite3
from PIL import Image, ImageFont, ImageDraw
from random import randint


bot = telebot.TeleBot("6108067484:AAEJukj_bvuaZAZIH7ssfknLWuiofZ6R-hI")

@bot.message_handler(commands=['start'])
def start(message):
    connect = sqlite3.connect('datavolteq.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INT,
        user_name TXT,
        name TXT,
        date TXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS volunteers (
            id INT,
            name TXT,
            date TXT,
            rating INT,
            status TXT
        )""")
    connect.commit()

    connect = sqlite3.connect('datavolteq.db')
    cursor = connect.cursor()
    id = message.chat.id
    cursor.execute(f"SELECT id FROM users WHERE id = '{id}'")
    if cursor.fetchone() is None:
        data = [message.chat.id, message.from_user.username, message.chat.first_name, datetime.datetime.now()]
        cursor.execute(f"INSERT INTO users VALUES (?, ?, ?, ?)", (data))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    new_event = types.KeyboardButton("❌Добавить активность❌")
    stat = types.KeyboardButton("✅Посмотреть статистику✅")
    new_volunteers = types.KeyboardButton("✅Добавить нового волонтёра✅")
    doc = types.KeyboardButton("✅Получить документы✅")
    markup.add(new_volunteers, new_event, stat,doc)
    bot.send_message(message.chat.id, "Главное меню", reply_markup=markup)
    connect.commit()

@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == "❌Добавить активность❌":
        # keyboard = types.InlineKeyboardMarkup(row_width=1)
        # cancel_button = types.InlineKeyboardButton(text="Отмена", callback_data="start")
        # switch_button = types.InlineKeyboardButton(text="Добавить новую активность", switch_inline_query_current_chat="")
        # keyboard.add(switch_button, cancel_button)
        # bot.send_message(message.chat.id, "Выберите кнопку", reply_markup=keyboard)
        bot.send_message(message.chat.id, "Раздел находится в разработке")
    if message.text == "✅Посмотреть статистику✅":
        # msg = bot.send_message(message.chat.id,
        #                        "Выберите, что хотите посмотреть")
        #
        # bot.register_next_step_handler(msg, stat)
        stat(message)
        # bot.send_message(message.chat.id, "Раздел находится в разработке")
    if message.text == "✅Добавить нового волонтёра✅":
        msg = bot.send_message(message.chat.id,
                               "Введите имя и фамилию волонтёра через пробел")
        bot.register_next_step_handler(msg, new_volunteer_name)
    if message.text == "✅Получить документы✅":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        certificate = types.KeyboardButton("Создать сертификат за участие в мероприятии")
        book = types.KeyboardButton("Получить книжку волонтёра")
        markup.add(certificate, book)
        msg = bot.send_message(message.chat.id,
                               "Выберите, что хотите получить", reply_markup=markup)
        bot.register_next_step_handler(msg, choose_doc)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "start":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")
    # Если сообщение из инлайн-режима
    elif call.inline_message_id:
        if call.data == "test":
            bot.edit_message_text(inline_message_id=call.inline_message_id, text="Бдыщь")


# Простейший инлайн-хэндлер для ненулевых запросов
@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(query):
    # connect = sqlite3.connect('datavolteq.db')
    # cursor = connect.cursor()
    # cursor.execute(f"SELECT name FROM volunteers WHERE name LIKE '%а%'")
    # data = cursor.fetchall()
    # result = []
    # for item in data:
    #     result.append(str(item[0]))
    # kb = types.InlineKeyboardMarkup()
    # kb.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="test"))
    results = []
    # Обратите внимание: вместо текста - объект input_message_content c текстом!
    first_msg = types.InlineQueryResultArticle(
        id=1, title="Волонтёр 1",
        input_message_content=types.InputTextMessageContent(message_text="Волонтёр 1")
    )
    second_msg = types.InlineQueryResultArticle(
        id=2, title="Волонтёр 2",
        input_message_content=types.InputTextMessageContent(message_text="Волонтёр 2")
    )
    results.append(first_msg)
    results.append(second_msg)
    print(results)
    bot.answer_inline_query(query.id, results)


def new_volunteer_name(message):
    # connect = sqlite3.connect('datavolteq.db')
    # cursor = connect.cursor()
    global name_new
    name_new = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    today_date = types.KeyboardButton("Сегодняшнее число")
    markup.add(today_date)
    msg = bot.send_message(message.chat.id,
                           "Введите дату присоединения волонтёра в VolteQ. В формате дата.месяц.год. Например: 01.01.2024", reply_markup=markup)

    bot.register_next_step_handler(msg, new_volunteer_date)

def new_volunteer_date(message):
    connect = sqlite3.connect('datavolteq.db')
    cursor = connect.cursor()
    text = message.text
    if text == "Сегодняшнее число":
        now = datetime.datetime.now()
        date_new = now.strftime("%d.%m.%Y")
    else:
        date_new = text


    id = message.chat.id
    cursor.execute(f"SELECT MAX(id) FROM volunteers")
    old_id = cursor.fetchone()[0]
    if old_id == None:
        old_id = 0
    new_id = int(old_id) + 1
    data = [new_id, name_new, date_new, 0, "Новичок"]
    cursor.execute(f"INSERT INTO volunteers VALUES (?, ?, ?, ?, ?)", (data))
    bot.send_message(id, "Данные успешно внесены")
    connect.commit()
    start(message)

def event(message):
    event_name = message.text

def stat(message):
    connection = sqlite3.connect('datavolteq.db')
    cursor = connection.cursor()
    # Получение данных из базы данных
    query = "SELECT name FROM volunteers;"
    cursor.execute(query)
    results = cursor.fetchall()
    query = "SELECT COUNT(name) FROM volunteers;"
    cursor.execute(query)
    count = cursor.fetchone()[0]

    data = "Список волонтёров: \n\n"
    for result in results:
        data += f"- {result[0]}\n"
    data += f"\nВсего волонтёров: {count}"
    bot.send_message(message.chat.id, data)


def choose_doc(message):
    text = message.text
    if text == "Получить книжку волонтёра":
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        switch_button = types.InlineKeyboardButton(text="Выбрать волонтёра", switch_inline_query_current_chat="")
        keyboard.add(switch_button)
        bot.send_message(message.chat.id, "Синхронизация с сервером...", reply_markup=types.ReplyKeyboardRemove())
        msg = bot.send_message(message.chat.id,
                               "Нажмите на кнопку ниже", reply_markup=keyboard)
        bot.register_next_step_handler(msg, vol_book)
    elif text == "Создать сертификат за участие в мероприятии":
        msg = bot.send_message(message.chat.id,
                               "Введите Фамилию и имя адресата\n\nИзображение может быть не ровным, так как бот только разрабатывается", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, cert_one)

def vol_book(message):
    text = message.text
    if text == "Волонтёр 1":
        f = open("book1.pdf", "rb")
        bot.send_document(message.chat.id, f)
    elif text == "Волонтёр 2":
        f = open("book2.pdf", "rb")
        bot.send_document(message.chat.id, f)
    start(message)

def cert_one(message):
    global name_name
    name_name = message.text

    msg = bot.send_message(message.chat.id,
                           "Введите Название мероприятия(до 30 символов)\n\nИзображение может быть не ровным, так как бот только разрабатывается",
                           reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, cert_two)


def cert_two(message):
    global event_name
    event_name = message.text
    tink = Image.open('template.png')
    font = ImageFont.truetype('Fonts/Exo-Bold.otf', 67)
    font_id = ImageFont.truetype('Fonts/Exo-Medium.otf', 60)
    d = ImageDraw.Draw(tink)
    d.text((750, 620), name_name, font=font, fill=(0, 0, 0, 255))
    d.text((700, 870), event_name, font=font_id, fill=(0, 0, 0, 255))
    tink.save("file3.png", "PNG")
    img = open('file3.png', 'rb')
    bot.send_message(message.chat.id, "Ваше фото: ")
    bot.send_photo(message.chat.id, img)
    start(message)
bot.polling()