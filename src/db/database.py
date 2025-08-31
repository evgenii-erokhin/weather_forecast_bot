from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(url=SQLALCHEMY_DATABASE_URL)
session_factory = sessionmaker(bind=engine)
