from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from .models import Base
import redis
load_dotenv()


DSN = os.getenv("DSN")
if not DSN:
    raise RuntimeError("DSN environment variable is not set")

engine = create_engine(DSN, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_redis_client():
    r = redis.Redis(host = os.getenv("REDIS_HOST"), port = os.getenv("REDIS_PORT"), decode_responses=True)
    return r

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Call this once at startup (NOT on import)
    Base.metadata.create_all(bind=engine)
