# backend/app/core/database.py
import databases
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Database connection
database = databases.Database(settings.DATABASE_URL)
engine = sqlalchemy.create_engine(settings.DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Base class for models
Base = declarative_base(metadata=metadata)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_database():
    """Dependency to get database connection"""
    return database

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()