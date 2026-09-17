import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_URL=os.getenv("TRAFFICPULSE_DB_URL","sqlite:///./trafficpulse.db")
connect_args={"check_same_thread":False} if DB_URL.startswith("sqlite") else {}
engine=create_engine(DB_URL,connect_args=connect_args)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)

class Base(DeclarativeBase): pass

def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
