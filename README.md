# Weather Forecast Bot

### Описание:
Телеграм бот для получения данных прогноза погоды через <a href='https://www.gismeteo.ru/api/'>API Gismeteo </a>.
<br>
Прогноз погоды можно получить используя команды из меню бота:
* `/current_weather` - погода на текущий момент
* `/weather_today` - погода на сегодня
* `/weather_tomorow` - погода на завтра

### Планы по реализации:
- добавить базу данных для хранения координат пользователей
   
### Технологии:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
<img src="https://img.shields.io/badge/Python_Telegram_Bot-blue?style=for-the-badge&logo=python telegram bot&logoColor=green"/>
![PythonAnywhere](https://img.shields.io/badge/pythonanywhere-%232F9FD7.svg?style=for-the-badge&logo=pythonanywhere&logoColor=151515)
### Как запустить:
1. Используя BotFather создать телеграм бот.
2. Через интерфейс BotFather добавить следующие команды боту.
   ```
    /current_weather - погода на текущий момент
    /weather_today - погода на сегодня
    /weather_tomorow - погода на завтра
   ```
3. В корне проекта создать файл .env  и заполните его по шаблону:
```
GISMETIO_TOKEN=<Ваш токен полученый у Gismeteo> 
TELEGRAM_TOKEN=<Token Вашего Телеграм бота> 
```
4. В корне проекта создать виртуальное окружение.
- Win:
  ```
  python -m venv venv
  ```
- Linux/MacOs:
  ```
  python3 -m venv venv
  ```
5. Активируйте виртуальное окружение.
- Win:
  ```
  source venv/Scripts/activate
  ```
- Linux/MacOs:
  ```
  source venv/bib/activate
  ```
6. Установить зависимости.
```
pip install -r requirements.txt
```
7. Запустите исполняемый файл.
```
python main.py
```
8. Чтобы получить прогноз, откройте ТГ бот, через вложение отправьте текущие координаты используя встроенную функцию в Телеграмм.
9. Выберите одну из  команд для получения прогноза.
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
<a href="mailto:evgeniy_erokhin@outlook.com?">
<img src=https://img.shields.io/badge/Microsoft_Outlook-0078D4?style=for-the-badge&logo=microsoft-outlook&logoColor=white/>
</a>
