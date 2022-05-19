import time
from multiprocessing.context import Process # модуль следующей строки
import schedule
import telebot
from bs4 import BeautifulSoup # к ней еще надо pip install lxml(хрен знает зачем, какой-то гребаный формат, и фиг с ним)
import requests
import sqlite3


token = '5329498864:AAGLf3LCXwJ-0I6lzEDyax6z_jYnZ8qyeVw' # токен бота
bot = telebot.TeleBot(token)


db = sqlite3.connect('valuti.sqlite', check_same_thread=False) # подключение к бд
cur = db.cursor()



def send_message1(): # функция отложенной отправки
    text = cur.execute('SELECT id, valuta FROM users') # извлечение подписанных юзеров из бд
    for el in text:
        message = get_stocks(str(el[1])) # получение курса с помощью ф-и парсера
        bot.send_message(int(el[0]), 'Ежедневный курс валют:\nRUB/'+str(el[1])+': '+message) # отправка сообщения


schedule.every().day.at("03:11").do(send_message1) # время отправки

class ScheduleMessage():  # класс отправки шедл, нихрееееенаааааа не понимаю что за дичь, но оно надо......
    def try_send_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)
    def start_process():
        p1 = Process(target=ScheduleMessage.try_send_schedule, args=())
        p1.start()






def get_stocks(valuta): # парсер курса валют
    url = 'https://форум-трейдеров.рф/chart-online.php?' # подключение к юрл
    page = requests.get(url) #  получение кода страницы
    soup = BeautifulSoup(page.text, 'lxml') # расшифровка кода страницы

    usd = str(soup.select('span')[9]).split('>')[1].split('<')[0] # получение непосредственно курса валюты
    eur = str(soup.select('span')[14]).split('>')[1].split('<')[0]
    if valuta == 'eur': return eur
    else: return usd  # возвращение зн-я курса



@bot.message_handler(commands=['start']) # ф-я запуска бота
def start_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Смотреть курсы валют', 'Получать курсы валют') # создание клаввиатуры
    bot.send_message(message.chat.id, 'Привет!\nЯ бот котрый может тебе показать курс валют в настоящее время! \nА так же я могу отправлять курсы каких то валют в определённое время!', reply_markup = keyboard)


@bot.message_handler(content_types=['text']) # обработка начальной клавиатуры
def send_text(message):
    if message.text == 'Смотреть курсы валют':
        kb1 = telebot.types.InlineKeyboardMarkup() # создание инлайн клаввиатуры
        kb1.add(telebot.types.InlineKeyboardButton(text='USD', callback_data='usd'), telebot.types.InlineKeyboardButton(text='EUR', callback_data='eur'))
        bot.send_message(message.chat.id, 'Выберете валюту:', reply_markup=kb1)

    if message.text == 'Получать курсы валют':
        kb2 = telebot.types.InlineKeyboardMarkup()
        kb2.add(telebot.types.InlineKeyboardButton(text='USD', callback_data='usd_get'), telebot.types.InlineKeyboardButton(text='EUR', callback_data='eur_get'))
        bot.send_message(message.chat.id, 'Выберете валюту для ежедневного получения:', reply_markup=kb2)

@bot.callback_query_handler(func=lambda call: True) # обработка инлайн команд
def query_handler(call):
    if call.data == 'usd':
        usd = get_stocks('usd')
        bot.send_message(call.message.chat.id, 'RUB/USD: '+usd) # отправка курса валют

    if call.data == 'eur':
        eur = get_stocks('eur')
        bot.send_message(call.message.chat.id, 'RUB/EUR: '+eur)

    if call.data == 'eur_get':
        cur.execute('INSERT INTO Users (id, valuta) VALUES (?, ?)', (call.message.chat.id, 'eur', ))
        db.commit()
        bot.send_message(call.message.chat.id, 'Теперь вы будете ежедневно получать курс этой валюты!')

    if call.data == 'usd_get':
        cur.execute('INSERT INTO Users (id, valuta) VALUES (?, ?)', (call.message.chat.id, 'usd', ))
        db.commit()
        bot.send_message(call.message.chat.id, 'Теперь вы будете ежедневно получать курс этой валюты!')


if __name__ == '__main__': # просто дичь
    ScheduleMessage.start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass
