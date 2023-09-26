# Weather Forecast Bot

### Описание:
Телеграм бот для получения уведомлений об изменениях в погоде через API Gismeteo.
Прогноз погоды можно получить используя команды:
* `/current_weather` - погода на текущий момент
* `/weather_today` - погода на сегодня
* `/weather_tomorow` - погода на завтра
 

P.S. Получеие прогноза погоды пока, реализовано для локации, координаты которой, переданы в переменных окружения.
В следующей версии ожидается добавления функционала получения прогноза по динамически меняющимся координатам пользователя.
### Технологии:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
### Как запустить:
1. В корне проекта создать файл .env  и заполните его по шаблону:
```
GISMETIO_TOKEN=<Ваш токен полученый у Gismeteo> 
TELEGRAM_TOKEN=<Token Вашего Телеграм бота> 
LATITUDE=<Координата широты>
LONGITUDE=<Координата долготы>
```
2. В корне проекта создать виртуальное окружение.
- Win:
  ```
  python -m venv venv
  ```
- Linux/MacOs:
  ```
  python3 -m venv venv
  ```
3. Активируйте виртуальное окружение.
- Win:
  ```
  source venv/Scripts/activate
  ```
- Linux/MacOs:
  ```
  source venv/bib/activate
  ```
4. Установить зависимости.
```
pip install requirements.txt
```
5.Запустите исполняемый файл.
```
python main.py
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
