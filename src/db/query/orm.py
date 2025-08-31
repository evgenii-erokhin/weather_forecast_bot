from datetime import datetime

from psycopg import OperationalError
from sqlalchemy.exc import SQLAlchemyError

from db.database import engine, session_factory
from db.models import Base, Coordinates
from exceptions import DatabaseConnectionError, DatabaseError


def create_data_base_and_tables():
    Base.metadata.create_all(engine)


def update_coordinates(
    username: str, first_name: str, chat_id: int, latitude: float, longitude: float
) -> None:

    try:
        with session_factory() as session:
            coordinates = (
                session.query(Coordinates)
                .filter(Coordinates.chat_id == chat_id)
                .first()
            )
            if coordinates:
                coordinates.latitude = latitude
                coordinates.longitude = longitude
                coordinates.updated_at = datetime.now()
            else:
                coordinates = Coordinates(
                    username=username,
                    first_name=first_name,
                    chat_id=chat_id,
                    latitude=latitude,
                    longitude=longitude,
                )
                session.add(coordinates)
            session.commit()

    except OperationalError as e:
        raise DatabaseConnectionError(f"Database connection error: {e}") from e
    except SQLAlchemyError as e:
        raise DatabaseError(f"Database error: {e}") from e
    except Exception as e:
        raise DatabaseError(f"Unexpected error: {e}") from e


def get_coordinates(chat_id: int) -> tuple:
    try:
        with session_factory() as session:
            coordinates = (
                session.query(Coordinates)
                .filter(Coordinates.chat_id == chat_id)
                .first()
            )
            if coordinates:
                return coordinates.latitude, coordinates.longitude
            return None, None
    except OperationalError as e:
        raise DatabaseConnectionError(f"Database connection error: {e}") from e
    except Exception as e:
        raise DatabaseError(f"Unexpected error: {e}") from e
