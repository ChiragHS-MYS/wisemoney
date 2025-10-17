from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wisemoney.db")  # fallback to SQLite

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create a session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for models
Base = declarative_base()

# Initialize DB (creates tables)
def init_db():
    Base.metadata.create_all(bind=engine)
