import telebot
import config
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
items = []
it3 = types.KeyboardButton('Да')
it4 = types.KeyboardButton('Нет')

items.append(it3.text)
items.append(it4.text)
yn_markup = markup.add(it3, it4)


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    it1 = types.KeyboardButton('Добавляем')
    it2 = types.KeyboardButton('Я просто посмотреть')
    items.append(it1.text)
    items.append(it2.text)

    start_markup = markup.add(it1, it2)
    bot.send_message(message.chat.id, 'Привет, я - Бот-отзовик. Ты можешь добавить свой отзыв на какой-либо товар или'
                                      ' почитать отзывы других людей. Что делаем?', reply_markup=start_markup)


@bot.message_handler(content_types=['text'])
def add_items(message):
    if message.chat.type == 'private':
        if message.text == 'Добавляем':
            msg = bot.send_message(message.chat.id, 'Отлично, начнем с картинки, прикрепи ее:',
                                   reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, photo)


def add_cattegory(message):
    handle_text(message.text, 'cattegory')
    msg = bot.send_message(message.chat.id, 'Напиши название товара', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, add_name)


def add_name(message):
    handle_text(message.text, 'name')
    msg = bot.send_message(message.chat.id, 'Напиши отзыв о товаре', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, add_desc)


def add_desc(message):
    handle_text(message.text, 'description')
    msg = bot.send_message(message.chat.id, 'Отлично. Напиши "Чек", чтобы увидеть отзыв')
    bot.register_next_step_handler(msg, send_review)


def send_review(message):
    msg_ok = bot.send_message(message.chat.id, 'Проверь, все ли правильно', reply_markup=types.ReplyKeyboardRemove())
    catt_f = open('cattegory.txt', 'r')
    catt = catt_f.read()
    name_f = open('name.txt', 'r')
    name = name_f.read()
    desc_f = open('description.txt', 'r')
    desc = desc_f.read()
    rev = bot.send_photo(message.chat.id, open('./image.jpg', 'rb'),
                         caption=f'Название: {name}\nКатегория: {catt}\nОтзыв покупателя: {desc}')


def checking_itmes(message):
    pass


def handle_text(message, name):
    txt = message
    file = open(f'{name}.txt', 'w')
    for line in txt:
        file.write(line)
    file.close()


@bot.message_handler(content_types=['photo'])
def photo(message):
    print('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    file_info = bot.get_file(fileID)
    print('file.file_path =', file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_photo(message.chat.id, open('./image.jpg', 'rb'))
    msg = bot.send_message(message.chat.id, 'Балдеж', reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, 'Напиши категорию товара', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, add_cattegory)


bot.polling(none_stop=True)
