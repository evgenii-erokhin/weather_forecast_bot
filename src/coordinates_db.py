import sqlite3 as sq


def create_database() -> None:
    """
    Инициализирует базу данных.
    """
    with sq.connect('coordinates.db') as con:
        cur = con.cursor()
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS coordinates(
                    chat_id INTEGER,
                    latitude REAL,
                    longitude REAL
                    )
                """)


def write_data_to_database(chat_id: int, latitude: float, longitude: float) -> None:
    """
    Записывает переданные координаты в базу данных.
    """
    with sq.connect('coordinates.db') as con:
        cur = con.cursor()
        cur.execute("""
                    INSERT INTO coordinates(chat_id, latitude, longitude) VALUES(?, ?, ?);""",
                    (chat_id, latitude, longitude))


def return_coordinates_from_database(chat_id) -> list:
    """
    Возвращает последние переданные координаты пользователя.
    """
    con = sq.connect('coordinates.db')
    cur = con.cursor()
    response = cur.execute("""
                SELECT latitude, longitude FROM coordinates WHERE chat_id=?""", (chat_id, )).fetchall()
    return response[-1]
