import telebot
import pyowm
import apiai
import json
import requests

bot = telebot.TeleBot('#') #bot API key
owm = pyowm.OWM('#', language = 'ru') #OWM AIP key
help_string = 'Привет! Введите команду в формате "/погода город", где "город" - название Вашего города'
error_string = 'Произошла ошибка или город не найден. Попробуйте позднее. Для справки наберите /help.'

def city_correct(city):
    """correct city name and get type of city and region"""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Token #', #dadata API key
    }
    data = str('{ "query": "' + city + '", "locations": [{"country": "*"}], "count": 1}')

    data = data.encode("utf-8")
    response = requests.post('https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address', headers=headers, data=data)

    try: #if ruquest is correct
        city_name = response.json()['suggestions'][0]['data']['city']
        city_type = response.json()['suggestions'][0]['data']['city_type_full']
        settlement_name = response.json()['suggestions'][0]['data']['settlement']
        settlement_type = response.json()['suggestions'][0]['data']['settlement_type_full']
        region = response.json()['suggestions'][0]['data']['region']

        print(city_name, city_type, settlement_name, settlement_type)
        if (city_name == None) and (settlement_name == None): #if city name and settlement name is None
            return 'unknown'
        elif settlement_name == None:
            return (city_type, city_name, region)
        else:
            return (settlement_type, settlement_name, region)
    except:
        return ('unknown', 'unknown')

def send_message(message, chatID):
    """sending message to user by chatID"""

    #print(message.from_user.username)
    #if message.text[0] == '/': #if we got some '/' command
        #print(message.text[0])
        #start_message(message)
    #else:

    request = apiai.ApiAI('f3ffb090b48142c38a7dc4b84c26354b').text_request() #dialogfow API key
    request.lang = 'ru'
    request.session_id = str(chatID) #TODO it's work?
    request.query = message.text
    response = json.loads(request.getresponse().read())
    print(response['result'])
    #print(response['result']['metadata']['intentName'])
    if response['result']['metadata']['intentName'] == 'smalltalk.dialog.weather' and response['result']['actionIncomplete'] == False: #if we got weather request and DF correct recognize query
        city = city_correct(response['result']['fulfillment']['speech']) #correct city name
        if city[1] == 'unknown':
            bot.send_message(chatID, 'Мне город неизвестен этот, попробуй использовать именительный падеж в названии города.')
        else:
            region = city[2] #get region from response
            start_message('/погода {}'.format(city[1]), chatID, city[0], region)

    elif response['result']['action'] == 'smalltalk.greetings.hello': #if user say hello or something
        bot.send_message(chatID, response['result']['fulfillment']['speech'].format(message.from_user.username))
    else:
        bot.send_message(chatID, response['result']['fulfillment']['speech'])
    #print(response['result']['action'])
    return 1

@bot.message_handler(content_types=['text']) #if user send text bot will talk
def get_text_messages(message):
    print(message.text)
    send_message(message, message.chat.id)

"""@bot.message_handler(commands=['start']) #if user send /start bot send back help
def start_message(message):
    bot.send_message(message.chat.id, help_string)"""

@bot.message_handler(commands=['help']) #if user send /help bot send back help
def start_message(message):
    bot.send_message(message.chat.id, help_string)

@bot.message_handler(commands=['погода']) #if user send /погода bot send back weather info
def start_message(message, chatID, city_type, region):
    if len(message.split(' ')) > 1:
        if city_type == 'город': #correct settlement type name
            city_type = 'городе'
        elif city_type == 'село':
            city_type = 'селе'
        elif city_type == 'поселок':
            city_type = 'поселке'
        elif city_type == 'деревня':
            city_type = 'деревне'
        elif city_type == 'рабочий поселок':
            city_type = 'рабочем поселке'
        city = message.split(' ')[1]
        print(city)
        try: #if user send right city name
            observation = owm.weather_at_place(city)
            w = observation.get_weather()
            temp=w.get_temperature('celsius')['temp']

            answer = f"В {city_type} {city} ({region}) сейчас {w.get_detailed_status()} \n"
            answer += f"Температура в районе {round(temp)} градусов\n\n"

            bot.send_message(chatID, answer)
            #print(city)
        except:
            bot.send_message(chatID, error_string)
    else:
        bot.send_message(chatID, help_string)

bot.polling(none_stop = True)

