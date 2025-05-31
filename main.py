import http
import logging
import os
import sys
from typing import List

import exceptions
from json.decoder import JSONDecodeError
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters)

from coordinates_db import create_database, write_data_to_database, return_coordinates_from_database


load_dotenv()

GISMETEO_TOKEN = os.getenv('API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

FORCAST_ENDPOINT = 'https://api.gismeteo.net/v2/weather/forecast/?'
CURRENT_ENDPOINT = 'https://api.gismeteo.net/v2/weather/current/?'
TOMORROW = 'aggregate/?'
HEADERS = {'X-Gismeteo-Token': GISMETEO_TOKEN}
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


async def special_cases(update: Update, context:
                        ContextTypes.DEFAULT_TYPE):
    '''
    Функция, которая обрабатывает непредусмотренные команды от пользователя.
    '''
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text='Извините, я Вас не понял. Попробуйте выбрать команду из "Menu"'
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция, которая приветсвует пользователя при старте бота.
    '''
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
             'Добро пожаловать! Я бот прогноза погоды. \n\n'
             'Чтобы узнать прогноз, отправьте мне свою геопозицию. '
             'Далее выберите в Меню интересующий тип прогноза '
             'и я пришлю его Вам'
        )
    )


async def get_coordinate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция получает координаты пользователя через отправку вложения
    и записывает их в базу данных. Отправляет пользователю сообщение
    об успешности полученных координат.
    '''

    latitude = update.effective_message.location.latitude
    longitude = update.effective_message.location.longitude
    chat_id = update.effective_chat.id

    write_data_to_database(chat_id, latitude, longitude)

    await context.bot.send_message(
         chat_id=chat_id,
         text='Спасибо, Ваши координаты получены!'
     )


def get_api_answer(chat_id: int, url: str, days: int = None) -> List[dict]:
    '''
    Функция отправляет GET запрос на эндпоинт сервиса Gismeteo
    и получив данные прогноза, возвращает ответ в вызванную функцию.
    '''
    latitude, longitude = return_coordinates_from_database(chat_id)
    payload = {
        'latitude': latitude,
        'longitude': longitude,
    }
    if days:
        payload['days'] = days

    try:
        response = requests.get(url, headers=HEADERS, params=payload)
        if response.status_code != http.HTTPStatus.OK:
            raise exceptions.IncorrectStatusCode(
                f'Не корректный статус код {response.status_code}'
            )
    except requests.exceptions.ConnectionError as error:
        raise exceptions.ConnectionFailed(f'Ошибка соединения - {error}')

    try:
        response = response.json()['response']
    except JSONDecodeError as error:
        raise exceptions.CannotDecodJson(
            f'json не был декодирован в типы python {error}'
        )

    return response


def parse_weather_data(response: List[dict] or dict,
                       offset: bool) -> List[tuple]:
    '''
    Функция получает ответ сервера в виде словаря или списка словарей.
    Обрабатывает ответ сервера агрегируя данные за определённый
    промежуток времени, возвращая список со сгруппированными данными.

    Если запрашивается прогноз на завтра, применяется смещение
    из-за особенности API, которое передает данные вместе с текущем днём.
    '''
    data = {
        'time': [],
        'description': [],
        'humidity': [],
        'pressure': [],
        'temperature': [],
        'wind': [],
        'wind_direction': [],
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
    Функция, которая получив агрегированные данные,
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
    chat_id = update.effective_chat.id
    response = get_api_answer(chat_id, CURRENT_ENDPOINT)
    data = parse_weather_data(response, False)
    message = prepare_message(data)
    await context.bot.send_message(
        chat_id=chat_id,
        text=message
    )


async def get_weather_forecast_today(update: Update,
                                     context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция передающая прогноз погоды на весь сегодняшний день.
    '''
    chat_id = update.effective_chat.id
    response = get_api_answer(chat_id, FORCAST_ENDPOINT, ONE_DAY)
    data = parse_weather_data(response, False)
    message = prepare_message(data)
    await context.bot.send_message(
        chat_id=chat_id,
        text=message
    )


async def get_forecast_tomorrow(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
    '''
    Функция передающая прогноз погоды на завтра.
    '''
    chat_id = update.effective_chat.id
    response = get_api_answer(chat_id, FORCAST_ENDPOINT + TOMORROW, TWO_DAYS)
    data = parse_weather_data(response, True)
    message = prepare_message(data)
    await context.bot.send_message(
        chat_id=chat_id,
        text=message
    )


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        stream=sys.stdout,
        format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
    )

    create_database()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    starting = CommandHandler('start', start)
    current_weather = CommandHandler('current_weather', get_current_weather)

    forecast_weather_today = CommandHandler('weather_today',
                                            get_weather_forecast_today)

    forecast_weather_tomorrow = CommandHandler('weather_tomorrow',
                                               get_forecast_tomorrow)
    special_thing = MessageHandler(filters.TEXT, special_cases)
    coordinate = MessageHandler(filters.LOCATION, get_coordinate)

    application.add_handler(starting)
    application.add_handler(current_weather)
    application.add_handler(forecast_weather_today)
    application.add_handler(forecast_weather_tomorrow)
    application.add_handler(coordinate)
    application.add_handler(special_thing)

    application.run_polling()


if __name__ == '__main__':
    main()
