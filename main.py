import logging
import os
from pprint import pprint

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

load_dotenv()

GISMETIO_TOKEN = os.getenv('API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

FORCAST_ENDPOINT = 'https://api.gismeteo.net/v2/weather/forecast/?'
FORCAST_TOMOROW = 'https://api.gismeteo.net/v2/weather/forecast/?aggregate/?'
CURRENT_ENDPOINT = 'https://api.gismeteo.net/v2/weather/current/?'
HEADERS = {'X-Gismeteo-Token': GISMETIO_TOKEN}
OFFSET = 8


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=('Добро пожаловать! Я бот прогноза погоды. Выбери в Меню'
              ' интересующий тип прогноза и я пришлю его тебе')
    )


def get_api_answer(url: dict, days=None) -> list:
    payload = {
        'latitude': 57.7,
        'longitude': 40.94
    }
    if days:
        payload['days'] = days

    request = requests.get(url, headers=HEADERS, params=payload)
    response = request.json()['response']
    return response


def parse_weather_data(response: list, offset: bool) -> list:
    data = {
        'time': [],
        'description': [],
        'humidity': [],
        'pressure': [],
        'temperature': [],
        'wind': []
    }

    if offset:
        response = response[OFFSET:]

    for gap in range(len(response)):
        for key in response[gap]:
            if key == 'date':
                data['time'].append(response[gap][key]['local'])
            if key == 'description':
                data['description'].append(response[gap][key]['full'])
            if key == 'humidity':
                data['humidity'].append(response[gap][key]['percent'])
            if key == 'pressure':
                data['pressure'].append(response[gap][key]['mm_hg_atm'])
            if key == 'temperature':
                data['temperature'].append(response[gap][key]['air']['C'])
            if key == 'wind':
                data['wind'].append(response[gap][key]['speed']['m_s'])

    forecast_data = list(zip(
        data['time'],
        data['description'],
        data['humidity'],
        data['pressure'],
        data['temperature'],
        data['wind']
    ))
    return forecast_data


def prepare_message(data: list) -> str:
    forecast = f'Погода на {data[0][0][:10]}:\n'
    pprint(data)

    for item in data:
        forecast += f' {item[0][11:16]} температура воздуха составит {item[4]} градусов Цельсия. {item[2]}\n\n'
    return forecast


async def get_current_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция для агрегирующая данные погоды на текущей момент.
    '''
    response = get_api_answer(CURRENT_ENDPOINT)

    data = parse_weather_data(response)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='OK'
    )


async def get_weather_forecast_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция передающая прогноз погоды на весь сегодняшний день.
    '''
    response = get_api_answer(FORCAST_ENDPOINT, 1)
    data = parse_weather_data(response, False)
    message = prepare_message(data)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


async def get_forecast_tomorow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция передающая прогноз погоды на завтра.
    '''
    response = get_api_answer(FORCAST_TOMOROW, 2)
    data = parse_weather_data(response, True)
    message = prepare_message(data)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )
# async def get_current_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     payload = {
#         'latitude': 57.7,
#         'longitude': 40.94,
#     }
#     r = requests.get(CURRENT_ENDPOINT, headers=HEADERS, params=payload)
#     pressure = r.json().get('response').get('pressure').get('mm_hg_atm')
#     temperature = r.json().get('response').get('temperature').get('air').get('C')
#     discribe = r.json().get('response').get('description').get('full')

#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=f'Погода сейчас: давление - {pressure} мм. рт. ст.'
#         f' Температура воздуха {temperature} градусов C.'
#         f' {discribe}'
#         )


# async def get_weather_forecast_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     payload = {
#         'latitude': 57.7,
#         'longitude': 40.94,
#         'days': 1
#     }
#     r = requests.get(FORCAST_ENDPOINT, headers=HEADERS, params=payload)
#     data = r.json()['response']
#     lst_temperature = []
#     lst_time = []
#     lst_description = []

#     for gap in range(len(data)):
#         for temp in data[gap]:
#             if temp == 'temperature':
#                 lst_temperature.append(data[gap]['temperature']['comfort']['C'])

#     for gap in range(len(data)):
#         for timestamp in data[gap]:
#             if timestamp == 'date':
#                 lst_time.append(data[gap]['date']['local'])

#     for gap in range(len(data)):
#         for description in data[gap]:
#             if description == 'description':
#                 lst_description.append(data[gap]['description']['full'])

#     lst = list(zip(lst_time, lst_temperature, lst_description))

#     forecast_str = f'Погода на {lst[0][0][:10]}:\n'
#     for item in lst:
#         forecast_str += f' {item[0][11:16]} температура воздуха составит {item[1]} градусов Цельсия. {item[2]}\n\n'

#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=forecast_str
#         )


# async def get_forecast_tomorow(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     payload = {
#         'latitude': 57.7,
#         'longitude': 40.94,
#         'days': 2
#     }
#     request = requests.get(FORCAST_TOMOROW, headers=HEADERS, params=payload)

#     data = request.json()['response'][8:]
#     lst_temperature = []
#     lst_time = []
#     lst_description = []

#     for gap in range(len(data)):
#         for temp in data[gap]:
#             if temp == 'temperature':
#                 lst_temperature.append(data[gap]['temperature']['comfort']['C'])

#     for gap in range(len(data)):
#         for timestamp in data[gap]:
#             if timestamp == 'date':
#                 lst_time.append(data[gap]['date']['local'])

#     for gap in range(len(data)):
#         for description in data[gap]:
#             if description == 'description':
#                 lst_description.append(data[gap]['description']['full'])

#     lst = list(zip(lst_time, lst_temperature, lst_description))

#     forecast_str = 'Погода на завтра:\n'
#     for item in lst:
#         forecast_str += f' {item[0]} температура воздуха составит {item[1]} градусов Цельсия. {item[2]}\n\n'

#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=forecast_str
#         )


def get_my_coordinates(update, context):
    pass


def send_message():
    pass


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        filename='main.log',
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
    )
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    starting = CommandHandler('start', start)
    current_weather = CommandHandler('current_weather', get_current_weather)
    forecast_weather_today = CommandHandler('weather_today', get_weather_forecast_today)
    forecast_weather_tomorow = CommandHandler('weather_tomorow', get_forecast_tomorow)
    application.add_handler(starting)
    application.add_handler(current_weather)
    application.add_handler(forecast_weather_today)
    application.add_handler(forecast_weather_tomorow)

    application.run_polling()


if __name__ == '__main__':
    main()
