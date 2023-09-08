import os
import requests
from dotenv import load_dotenv


load_dotenv()

GISMETIO_TOKEN = os.getenv('API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

FORCAST_ENDPOINT = 'https://api.gismeteo.net/v2/weather/forecast/?'
CURRENT_ENDPOINT = 'https://api.gismeteo.net/v2/weather/current/?'
HEADERS = {'X-Gismeteo-Token': GISMETIO_TOKEN}


def get_current_weather(coordinates):
    pass


def get_weather_forecast():
    pass


def get_my_coordinates():
    pass


def send_message():
    pass


def main():
    pass


if __name__ == '__main__':
    main()
