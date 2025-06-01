from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

#  Database URL pulled from settings module
SQLALCHEMY_DATABASE_URL = settings.database_url

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#  Session factory for DB sessions (used in dependency injection)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models to inherit from
Base = declarative_base()


 