from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from src.app.config import settings
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:vSaVzzRqQn@34.45.129.153:5432/segwise-webhook-db"

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables!")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_size=20, max_overflow=30
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()