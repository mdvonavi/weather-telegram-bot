import telebot
import pyowm

bot = telebot.TeleBot('#') #bot API key
owm=pyowm.OWM('#', language = 'ru') #OWM AIP key

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Введите команду в формате "/погода город", где "город" - название Вашего города')

@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Введите команду в формате "/погода город", где "город" - название Вашего города')

@bot.message_handler(commands=['погода'])
def start_message(message):
    if len(message.text.split(' ')) > 1:
        city = message.text.split(' ')[1]
        print(city)
        try:
            observation = owm.weather_at_place(city)
            w = observation.get_weather()
            temp=w.get_temperature('celsius')['temp']

            answer = f"В городе {city} сейчас {w.get_detailed_status()} \n"
            answer += f"Температура в районе {round(temp)} градусов\n\n"

            bot.send_message(message.chat.id, answer)
            print(city)
        except:
            bot.send_message(message.chat.id, 'Произошла ошибка или город не найден. Попробуйте позднее. Для справки наберите /help.')
    else:
        bot.send_message(message.chat.id, 'Введите команду в формате "/погода город", где "город" - название Вашего города')

bot.polling(none_stop = True)