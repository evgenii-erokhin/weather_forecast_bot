import logging
import os
from typing import List

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

GISMETIO_TOKEN = os.getenv('API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

FORCAST_ENDPOINT = 'https://api.gismeteo.net/v2/weather/forecast/?'
CURRENT_ENDPOINT = 'https://api.gismeteo.net/v2/weather/current/?'
TOMOROW = 'aggregate/?'
HEADERS = {'X-Gismeteo-Token': GISMETIO_TOKEN}
ONE_DAY = 1
TWO_DAYS = 2

OFFSET = 8
OFFSET_TIME = 11
OFFSET_DATE = 10

ELEMENT = 0

DATE = 0
DESCRIPTION = 1
HUMIDITY = 2
PRESSURE = 3
TEMPERATURE = 4
WIND_SPEED = 5
WIND_ORIENTATION = 6

GEO_MAGNIT_DESCRIBE = {
    1: 'Нет заметных геомагнитных возмущений',
    2: 'Небольшие геомагниные возмущения',
    3: 'Слабая геомагнитная буря',
    4: 'Малая геомагнитная буря',
    5: 'Умеренная геомагнитная буря',
    6: 'Сильная геомагнитная буря',
    7: 'Жесткий геомагнитный шторм',
    8: 'Экстремальный шторм',
}

WIND_DIRECTION = {
    0: 'Штиль',
    1: 'Северный',
    2: 'Северо-восточный',
    3: 'Восточный',
    4: 'Юго-восточный',
    5: 'Южный',
    6: 'Юго-западный',
    7: 'Западный',
    8: 'Северо-западный',
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция, которая приветсвует пользователя при старте бота.
    '''
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=('Добро пожаловать! Я бот прогноза погоды. Выбери в Меню'
              ' интересующий тип прогноза и я пришлю его тебе')
    )


def get_api_answer(url: str, days: int = None) -> List[dict]:
    '''
    Функция отправляет GET запрос на эндпоинт сервиса Gismeteo
    и получив данные прогноза, возвращает ответ в вызванную функцию.
    '''
    payload = {
        'latitude': 57.7,
        'longitude': 40.94
    }
    if days:
        payload['days'] = days

    request = requests.get(url, headers=HEADERS, params=payload)
    response = request.json()['response']
    return response


def parse_weather_data(response: List[dict] or dict,
                       offset: bool) -> List[tuple]:
    '''
    Функция получает ответ сервера в виде словаря или списока словарей.
    Обрабатывает ответ сервера агрегируя данные за определённый
    промежуток времени, возвращая список с сгруппированными данными.

    Если запрашивается прогноз на завтра, применяется смещение
    из-за особености API, которое передает данные вместе с текущем днём.
    '''
    data = {
        'time': [],
        'description': [],
        'humidity': [],
        'pressure': [],
        'temperature': [],
        'wind': [],
        'wind_direction': [],
        'gm': [],
    }

    if isinstance(response, dict):
        for key in response:
            if key == 'date':
                data['time'].append(response[key]['local'])
            if key == 'description':
                data['description'].append(response[key]['full'])
            if key == 'humidity':
                data['humidity'].append(response[key]['percent'])
            if key == 'pressure':
                data['pressure'].append(response[key]['mm_hg_atm'])
            if key == 'temperature':
                data['temperature'].append(response[key]['air']['C'])
            if key == 'wind':
                data['wind'].append(response[key]['speed']['m_s'])
                data['wind_direction'].append(response[key]
                                              ['direction']['scale_8'])
            if key == 'gm':
                data['gm'].append(response[key])

    else:
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
                    data['wind_direction'].append(response[gap][key]
                                                  ['direction']['scale_8'])
                if key == 'gm':
                    data['gm'].append(response[gap][key])

    forecast_data = list(zip(
        data['time'],
        data['description'],
        data['humidity'],
        data['pressure'],
        data['temperature'],
        data['wind'],
        data['wind_direction'],
    ))
    return forecast_data


def prepare_message(data: List[tuple]) -> str:
    '''
    Функция, котороя получив агрегированые данные,
    возвращает сформированное сообщение прогноза погоды.
    '''
    forecast = f'Погода на {data[ELEMENT][DATE][:OFFSET_DATE]}:\n'

    for row in data:
        forecast += (
            f'{row[DATE][OFFSET_TIME:]}: '
            f'Температура воздуха составит: {row[TEMPERATURE]}° С. '
            f'Влажность воздуха: {row[HUMIDITY]}%. '
            f'Давление: {row[PRESSURE]} мм. рт. ст. '
            f'Ветер: {WIND_DIRECTION[row[WIND_ORIENTATION]]}, '
            f'{row[WIND_SPEED]} м/с, '
            f'{row[DESCRIPTION]}.\n\n'
            )
    return forecast


async def get_current_weather(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция для агрегирующая данные погоды на текущей момент.
    '''
    response = get_api_answer(CURRENT_ENDPOINT)
    data = parse_weather_data(response, False)
    message = prepare_message(data)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


async def get_weather_forecast_today(update: Update,
                                     context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция передающая прогноз погоды на весь сегодняшний день.
    '''
    response = get_api_answer(FORCAST_ENDPOINT, ONE_DAY)
    data = parse_weather_data(response, False)
    message = prepare_message(data)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


async def get_forecast_tomorow(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция передающая прогноз погоды на завтра.
    '''
    response = get_api_answer(FORCAST_ENDPOINT + TOMOROW, TWO_DAYS)
    data = parse_weather_data(response, True)
    message = prepare_message(data)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


def get_my_coordinates():
    '''
    Функция для получения координат.
    Для последующего вычесления погоды по определенной локации.
    (В планах реализации)
    '''
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

    forecast_weather_today = CommandHandler('weather_today',
                                            get_weather_forecast_today)

    forecast_weather_tomorow = CommandHandler('weather_tomorow',
                                              get_forecast_tomorow)
    application.add_handler(starting)
    application.add_handler(current_weather)
    application.add_handler(forecast_weather_today)
    application.add_handler(forecast_weather_tomorow)

    application.run_polling()


if __name__ == '__main__':
    main()
