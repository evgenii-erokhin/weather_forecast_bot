import http
import logging
import sys
from json.decoder import JSONDecodeError
from typing import List

import aiohttp
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters)

import exceptions
from config import (CURRENT_ENDPOINT, DATE, DESCRIPTION, ELEMENT,
                    FORCAST_ENDPOINT, HEADERS, HUMIDITY, OFFSET, OFFSET_DATE,
                    OFFSET_TIME, ONE_DAY, PRESSURE, TELEGRAM_TOKEN,
                    TEMPERATURE, TOMORROW, TWO_DAYS, WIND_DIRECTION,
                    WIND_ORIENTATION, WIND_SPEED)
from db.query.orm import (create_data_base_and_tables, get_coordinates,
                          update_coordinates)


async def special_cases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает непредусмотренные команды от пользователя.

    :param update: Объект Update, содержащий информацию о событии Telegram
    :param context: Контекст выполнения, предоставляет доступ к bot и другим полезным свойствам
    :return: None
    """
    chat_id = update.effective_chat.id
    logging.info(
        f"User with username: {update.effective_user.username} "
        f"and chat_id: {chat_id} "
        f"sends unknown command: {update.effective_message.text}"
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text='Извините, я Вас не понял. Попробуйте выбрать команду из "Menu"',
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start, отправляющий приветственное сообщение пользователю.

    :param update: Объект Update, содержащий информацию о событии Telegram
    :param context: Контекст выполнения, предоставляет доступ к bot и другим полезным свойствам
    :return: None
    """
    chat_id = update.effective_chat.id
    logging.info(
        f"User with username: {update.effective_user.username}"
        f"and chat_id: {chat_id}: "
        f"starts the bot"
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "Добро пожаловать! Я бот прогноза погоды. \n\n"
            "Чтобы узнать прогноз погоды: "
            "1. Отправьте мне свою геопозицию через вложение. "
            "2. Выберите в Меню интересующий тип прогноза погоды. \n\n"
            "Доступные команды: \n"
            "`/current_weatrher` - прогноз погоды на текущее время \n"
            "`/forecast_today` - прогноз погоды на сегодня \n"
            "`/forecast_tomorrow` - прогноз погоды на завтра"
        ),
    )


async def get_coordinate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает отправку геопозиции пользователем и сохраняет координаты в базу данных.

    :param update: Объект Update, содержащий информацию о событии Telegram
    :param context: Контекст выполнения, предоставляет доступ к bot и другим полезным свойствам
    :return: None
    """
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    latitude = update.effective_message.location.latitude
    longitude = update.effective_message.location.longitude

    update_coordinates(username, first_name, chat_id, latitude, longitude)
    logging.info(
        f"User with username: {username}"
        f"and chat_id: {chat_id} "
        f"sends coordinates."
    )
    await context.bot.send_message(
        chat_id=chat_id, text="Спасибо, Ваши координаты получены!"
    )


async def get_api_answer(chat_id: int, url: str, days: int = None) -> List[dict]:
    """
    Отправляет GET-запрос к API Gismeteo и возвращает данные прогноза погоды.

    :param chat_id: ID чата Telegram, откуда извлекаются координаты
    :param url: URL-эндпоинт запроса
    :param days: Количество дней прогноза (опционально)
    :return: Список словарей с погодными данными
    :raise exceptions.IncorrectStatusCode: Если статус ответа не 200 OK
    :raise exceptions.ConnectionFailed: Если не удалось установить соединение
    :raise exceptions.CannotDecodJson: Если не удалось декодировать JSON-ответ
    """
    latitude, longitude = get_coordinates(chat_id)
    payload = {
        "latitude": latitude,
        "longitude": longitude,
    }
    if days:
        payload["days"] = days

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, params=payload) as response:
                if response.status != http.HTTPStatus.OK:
                    logging.error(
                        f"API Gismeteo returned incorrect status code. Status code - {response.status} for user_id - {chat_id}"
                    )
                    raise exceptions.IncorrectStatusCode(
                        f"Status code was not 200: {response.status}"
                    )
                try:
                    json_response = await response.json()
                    logging.info("JSON successfully decoded to types python")
                except (aiohttp.ContentTypeError, JSONDecodeError) as error:
                    logging.error(
                        f"JSON was not decoded to types python: {error} for user_id - {chat_id}"
                    )
                    raise exceptions.CannotDecodJson(
                        f"json was not decoded to types python: {error}"
                    )
            logging.info(
                f"Request to API Gismeteo was successful for user_id - {chat_id}"
            )
            return json_response.get("response")
    except aiohttp.ClientError as error:
        logging.error("Cannot connect to API Gismeteo. User_id - {chat_id}")
        raise exceptions.ConnectionFailed(f"Connection failed - {error}")


def parse_weather_data(response: List[dict] or dict, offset: bool) -> List[tuple]:
    """
    Парсит погодные данные из ответа API.

    :param response: Ответ API Gismeteo
    :param offset: Применять ли смещение для прогноза на завтра
    :return: Список кортежей с погодными данными
    """
    data = {
        "time": [],
        "description": [],
        "humidity": [],
        "pressure": [],
        "temperature": [],
        "wind": [],
        "wind_direction": [],
    }

    if isinstance(response, dict):
        for key in response:
            if key == "date":
                data["time"].append(response[key]["local"])
            if key == "description":
                data["description"].append(response[key]["full"])
            if key == "humidity":
                data["humidity"].append(response[key]["percent"])
            if key == "pressure":
                data["pressure"].append(response[key]["mm_hg_atm"])
            if key == "temperature":
                data["temperature"].append(response[key]["air"]["C"])
            if key == "wind":
                data["wind"].append(response[key]["speed"]["m_s"])
                data["wind_direction"].append(response[key]["direction"]["scale_8"])

    else:
        if offset:
            response = response[OFFSET:]

        for gap in range(len(response)):
            for key in response[gap]:
                if key == "date":
                    data["time"].append(response[gap][key]["local"])
                if key == "description":
                    data["description"].append(response[gap][key]["full"])
                if key == "humidity":
                    data["humidity"].append(response[gap][key]["percent"])
                if key == "pressure":
                    data["pressure"].append(response[gap][key]["mm_hg_atm"])
                if key == "temperature":
                    data["temperature"].append(response[gap][key]["air"]["C"])
                if key == "wind":
                    data["wind"].append(response[gap][key]["speed"]["m_s"])
                    data["wind_direction"].append(
                        response[gap][key]["direction"]["scale_8"]
                    )

    forecast_data = list(
        zip(
            data["time"],
            data["description"],
            data["humidity"],
            data["pressure"],
            data["temperature"],
            data["wind"],
            data["wind_direction"],
        )
    )
    logging.info("Weather data was parsed successfully")
    return forecast_data


def prepare_message(data: List[tuple]) -> str:
    """
    Формирует текстовое сообщение с прогнозом погоды.

    :param data: Список кортежей с погодными данными
    :return: Форматированное сообщение для отправки пользователю
    """
    forecast = f"Погода на {data[ELEMENT][DATE][:OFFSET_DATE]}:\n"

    for row in data:
        forecast += (
            f"{row[DATE][OFFSET_TIME:]}: "
            f"Температура воздуха составит: {row[TEMPERATURE]}° С. "
            f"Влажность воздуха: {row[HUMIDITY]}%. "
            f"Давление: {row[PRESSURE]} мм. рт. ст. "
            f"Ветер: {WIND_DIRECTION[row[WIND_ORIENTATION]]}, "
            f"{row[WIND_SPEED]} м/с, "
            f"{row[DESCRIPTION]}.\n\n"
        )
    logging.info("Message was prepared successfully")
    return forecast


async def get_current_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получает и отправляет текущую погоду.

    :param update: Объект Update, содержащий информацию о событии Telegram
    :param context: Контекст выполнения, предоставляет доступ к bot и другим полезным свойствам
    :return: None
    """
    chat_id = update.effective_chat.id
    response = await get_api_answer(chat_id, CURRENT_ENDPOINT)
    data = parse_weather_data(response, False)
    message = prepare_message(data)
    logging.info(
        f"To user: {update.effective_user.username} "
        f"sent current weather forecast. "
        f"user_id: {chat_id}"
    )
    await context.bot.send_message(chat_id=chat_id, text=message)


async def get_weather_forecast_today(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Получает и отправляет прогноз погоды на сегодня.

    :param update: Объект Update, содержащий информацию о событии Telegram
    :param context: Контекст выполнения, предоставляет доступ к bot и другим полезным свойствам
    :return: None
    """
    chat_id = update.effective_chat.id
    response = await get_api_answer(chat_id, FORCAST_ENDPOINT, ONE_DAY)
    data = parse_weather_data(response, False)
    message = prepare_message(data)
    logging.info(
        f"To user: {update.effective_user.username} "
        f"sent weather forecast for today. "
        f"user_id: {chat_id}"
    )
    await context.bot.send_message(chat_id=chat_id, text=message)


async def get_forecast_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получает и отправляет прогноз погоды на завтра.

    :param update: Объект Update, содержащий информацию о событии Telegram
    :param context: Контекст выполнения, предоставляет доступ к bot и другим полезным свойствам
    :return: None
    """
    chat_id = update.effective_chat.id
    response = await get_api_answer(chat_id, FORCAST_ENDPOINT + TOMORROW, TWO_DAYS)
    data = parse_weather_data(response, True)
    message = prepare_message(data)
    logging.info(
        f"To user: {update.effective_user.username} "
        f"sent weather forecast for tomorrow. "
        f"user_id: {chat_id}"
    )
    await context.bot.send_message(chat_id=chat_id, text=message)


def main():
    """
    Основная функция запуска бота.

    :return: None
    """
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s - %(levelname)s - %(message)s - %(name)s",
    )

    try:
        create_data_base_and_tables()
        logging.info("Database was created successfully")
    except Exception as e:
        logging.error(f"Database was not created. We got an error: {e}")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    starting = CommandHandler("start", start)
    current_weather = CommandHandler("current_weather", get_current_weather)

    forecast_weather_today = CommandHandler("weather_today", get_weather_forecast_today)

    forecast_weather_tomorrow = CommandHandler(
        "weather_tomorrow", get_forecast_tomorrow
    )
    special_thing = MessageHandler(filters.TEXT, special_cases)
    coordinate = MessageHandler(filters.LOCATION, get_coordinate)

    application.add_handler(starting)
    application.add_handler(current_weather)
    application.add_handler(forecast_weather_today)
    application.add_handler(forecast_weather_tomorrow)
    application.add_handler(coordinate)
    application.add_handler(special_thing)

    application.run_polling()


if __name__ == "__main__":
    main()
