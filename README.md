# Weather Forecast Bot

### Описание:
[Телеграм бот](https://t.me/forecasts_bot) для получения уведомлений об изменениях в погоде через API Gismeteo.
Прогноз погоды можно получить используя команды:
* `/current_weather` - погода на текущий момент
* `/weather_today` - погода на сегодня
* `/weather_tomorrow` - погода на завтра
 
### Технологии:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
<img src="https://img.shields.io/badge/Python_Telegram_Bot-blue?style=for-the-badge&logo=python telegram bot&logoColor=green"/>


### Подготовка к использованию:
1. Используя `BotFather` создать телеграм бот.
2. Через интерфейс `BotFather` добавить следующие команды боту.
    ```
    /current_weather - погода на текущий момент
    /weather_today - погода на сегодня
    /weather_tomorrow - погода на завтра
    ```
3. В корне проекта создать файл .env и заполните его по шаблону:
    ```
    GISMETEO_TOKEN=<Ваш токен полученый у Gismeteo> 
    TELEGRAM_TOKEN=<Token Вашего Телеграм бота> 
    ```
### Как запустить используя Docker:
1. Находясь в директории с файлом `docker-compose.yml` введите в терминале команду:
    ```commandline
    docker compose up -d
    ```
### Как запустить локально:
1. В корне проекта создать виртуальное окружение.
- Win:
    ```
    python -m venv venv
    ```
    - Linux/MacOs:
    ```
    python3 -m venv venv
    ```
2. Активируйте виртуальное окружение.
- Win:
  ```
  source venv/Scripts/activate
  ```
- Linux/MacOs:
  ```
  source venv/bib/activate
  ```
3. Установить зависимости.
    ```
    pip install -r requirements.txt
    ```
4. Запустите исполняемый файл.
    ```
    python main.py
    ```
### Работа с ботом
1. Чтобы получить прогноз, откройте ТГ бот, через вложение отправьте текущие координаты используя встроенную функцию в Телеграмм.
2. Выберите одну из команд для получения прогноза.
    ## Пример:
   **команда**: `/current_weather`
   <br> 
   **ответ**:
    ```
    Погода на 2023-10-11:
    11:00:00: Температура воздуха составит: 8.3° С.
    Влажность воздуха: 69%. Давление: 752 мм. рт. ст. 
    Ветер: Юго-западный, 3 м/с, Облачно.
    ```
### Контакты:
**Евгений Ерохин**
<br>

<a href="https://t.me/juandart" target="_blank">
<img src=https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white />
</a>
<a href="mailto:evgeniierokhin@proton.me?">
<img src=https://img.shields.io/badge/ProtonMail-8B89CC?style=for-the-badge&logo=protonmail&logoColor=white />
</a>
