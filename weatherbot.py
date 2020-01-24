import telebot
import pyowm
import apiai
import json

bot = telebot.TeleBot('#') #bot API key
owm = pyowm.OWM('#', language = 'ru') #OWM AIP key
help_string = 'Привет! Введите команду в формате "/погода город", где "город" - название Вашего города'
error_string = 'Произошла ошибка или город не найден. Попробуйте позднее. Для справки наберите /help.'

def send_message(message, chatID):
    print(message.from_user.username)
    if message.text[0] == '/': #if we got some '/' command
        #print(message.text[0])
        start_message(message)
    else:
        request = apiai.ApiAI('#').text_request() #dialogfow API key
        request.lang = 'ru'
        request.session_id = str(chatID) #TODO it's work?
        request.query = message.text
        response = json.loads(request.getresponse().read())
        if response['result']['action'] == 'smalltalk.greetings.hello':
            bot.send_message(chatID, response['result']['fulfillment']['speech'].format(message.from_user.username))
        else:            
            bot.send_message(chatID, response['result']['fulfillment']['speech'])
        #print(response['result']['action']) 
    return 1

@bot.message_handler(content_types=['text']) #if user send text bot will talk
def get_text_messages(message):
    print(message.text)
    send_message(message, message.chat.id)

@bot.message_handler(commands=['start']) #if user send /start bot send back help
def start_message(message):
    bot.send_message(message.chat.id, help_string)

@bot.message_handler(commands=['help']) #if user send /help bot send back help
def start_message(message):
    bot.send_message(message.chat.id, help_string)

@bot.message_handler(commands=['погода']) #if user send /погода bot send back weather info
def start_message(message):
    if len(message.text.split(' ')) > 1:
        city = message.text.split(' ')[1]
        #print(city)
        try: #if user send right city name
            observation = owm.weather_at_place(city)
            w = observation.get_weather()
            temp=w.get_temperature('celsius')['temp']

            answer = f"В городе {city} сейчас {w.get_detailed_status()} \n"
            answer += f"Температура в районе {round(temp)} градусов\n\n"

            bot.send_message(message.chat.id, answer)
            #print(city)
        except:
            bot.send_message(message.chat.id, error_string)
    else:
        bot.send_message(message.chat.id, help_string)

bot.polling(none_stop = True)

