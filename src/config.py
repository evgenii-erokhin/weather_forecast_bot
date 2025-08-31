import os

from dotenv import load_dotenv

load_dotenv()

GISMETEO_TOKEN = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

FORCAST_ENDPOINT = "https://api.gismeteo.net/v2/weather/forecast/?"
CURRENT_ENDPOINT = "https://api.gismeteo.net/v2/weather/current/?"
TOMORROW = "aggregate/?"
HEADERS = {"X-Gismeteo-Token": GISMETEO_TOKEN}
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
    0: "Штиль",
    1: "Северный",
    2: "Северо-восточный",
    3: "Восточный",
    4: "Юго-восточный",
    5: "Южный",
    6: "Юго-западный",
    7: "Западный",
    8: "Северо-западный",
}
