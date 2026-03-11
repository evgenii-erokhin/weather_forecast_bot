import asyncio
import json
import logging
import os

from redis import RedisError
from redis.asyncio import Redis

from config import REDIS_TTL


redis_host = os.getenv('REDIS_HOST', 'localhost')
port = int(os.getenv('REDIS_PORT', 6379))
ttl = REDIS_TTL
password = os.getenv('REDIS_PASSWORD', None)

redis_client = Redis(host=redis_host, port=port, db=0, password=password)


async def set_cached_forecast(kind: str, latitude: float, longitude: float, api_response: dict) -> None:
    """
    Устанаввливает ключ для доступа к прогнозу по типу прогноза и координатам.
    :param kind: Тип прогноза: now, today, tomorrow
    :param latitude: широта полученная от пользователя
    :param longitude: долгота полученная от пользователя
    :param api_response: ответ от сервиса прогноза погоды
    :return: None
    """
    key = f'{kind}:{latitude}:{longitude}'
    data = json.dumps(api_response)
    await  redis_client.setex(key, ttl, data)

async def get_cached_forecast(kind: str, latitude: float, longitude:float) -> dict:
    """
    Ответ пользователю из кэша Redis прогноз погоды по полученым координатам.
    :param kind: Тип прогноза: now, today, tomorrow
    :param latitude: широта полученная от пользователя
    :param longitude: долгота полученная от пользователя
    :return: Dict
    """
    key = f'{kind}:{latitude}:{longitude}'
    try:
        data = await redis_client.get(key)
        if data is None:
            return None
        return json.loads(data)
    except RedisError as e:
        logging.error(f"Error getting cached forecast: {e}")
        raise e



if __name__ == "__main__":
    async def main():
        api_response = {
            "date": {"local": "2026-03-09T12:34:56+03:00"},
            "description": {"full": "Пасмурно, небольшой снег"},
            "humidity": {"percent": 86},
            "pressure": {"mm_hg_atm": 742},
            "temperature": {"air": {"C": 3.2}},
            "wind": {"speed": {"m_s": 4.5}, "direction": {"scale_8": 3}},
        }
        await set_cached_forecast("current", 59.75, 27.61, api_response)
        data = await get_cached_forecast("current", 59.75, 27.61)
        print(data)
    asyncio.run(main())