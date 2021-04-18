#!/usr/bin/python

import telebot
import config
from telebot import types
import database
import datetime


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
    bot.send_message(message.chat.id, "start")
    # bot.send_message(message.chat.id, 'Привет, я - Бот-отзовик. Ты можешь добавить свой отзыв на какой-либо товар или'
                                      # ' почитать отзывы других людей. Что делаем?', reply_markup=start_markup)

@bot.message_handler(commands=['help'])
def help(message):
    print('help')
    bot.send_message(message.chat.id, "help help help")

@bot.message_handler(commands=['getitem'])
def get_item_by_id(message):
    itemName = " ".join(extract_arg(message.text))
    send_review(message, itemName)
    # bot.register_next_step_handler(msg, send_review, itemID)

@bot.message_handler(content_types=['text'])
@bot.message_handler(commands=['additem'])
def add_items(message):
    if message.chat.type == 'private':
        # if message.text == 'Добавляем' or :
        msg = bot.send_message(message.chat.id, 'Отлично, начнем с картинки, прикрепи ее:',
                                   reply_markup=types.ReplyKeyboardRemove())
        productData = {
            "name": "",
            "description": "",
            "stars": "",
            "category_id": "",
            "photo": ""
        }
        bot.register_next_step_handler(msg, photo, productData)
            
def extract_arg(arg):
    return arg.split()[1:]

# @bot.message_handler(commands=['yourCommand'])
# def yourCommand(message):
    # status = extract_arg(message.text)

            

def add_cattegory(message, productData):

    handle_text(message.text, 'cattegory')
    productData["category_id"] = message.text
    msg = bot.send_message(message.chat.id, 'Напиши название товара', reply_markup=types.ReplyKeyboardRemove())
    
    bot.register_next_step_handler(msg, add_name, productData)


def add_name(message, productData):
    handle_text(message.text, 'name')
    productData["name"] = message.text
    msg = bot.send_message(message.chat.id, 'Напиши отзыв о товаре', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, add_desc, productData)


def add_desc(message, productData):
    handle_text(message.text, 'description')
    productData["description"] = message.text
    msg = bot.send_message(message.chat.id, 'Отлично. Напиши "Чек", чтобы увидеть отзыв')
    print(productData)
    
    productID = database.add_new_product(productData)
    
    bot.register_next_step_handler(msg, send_review, productID)


def send_review(message, productName):
    # msg_ok = bot.send_message(message.chat.id, 'Проверь, все ли правильно', reply_markup=types.ReplyKeyboardRemove())
    product = database.to_readable(database.search_by_name(productName))
    
    if product:
        # catt = product.category_id
        name = product["name"]
        desc = product["description"]
        rate = product["stars"]
        category = ""
        if "category" in product:
            category = product["category"]
            rev = bot.send_photo(message.chat.id, open(product["photo"], 'rb'),
                                 caption=f'Название: {name}\nКатегория: {category}\nОтзыв покупателя: {desc}\nРейтинг: {rate}')
    else:
        bot.send_message(message.chat.id, "Not found")


def checking_itmes(message):
    pass


def handle_text(message, name):
    txt = message
    file = open(f'{name}.txt', 'w')
    for line in txt:
        file.write(line)
    file.close()


@bot.message_handler(content_types=['photo'])
def photo(message, productData):
    # print('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    # print('fileID =', fileID)
    file_info = bot.get_file(fileID)
    # print('file.file_path =', file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)

    
    
    photoFileName = str(datetime.datetime.now().timestamp())
    
    with open(photoFileName, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_photo(message.chat.id, open(photoFileName, 'rb'))
    
    productData["photo"] = photoFileName
    
    msg = bot.send_message(message.chat.id, 'Балдеж', reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, 'Напиши категорию товара', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, add_cattegory, productData)

    
bot.polling(none_stop=True)
