from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ..core import setting

engine = create_engine(setting.DATABASE_URL)

Base = declarative_base()

SessionLocal = sessionmaker(autoflush=False, autocommit= False, bind=engine)

def connect_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def create_all():
    Base.metadata.create_all(bind=engine)
    
DataBase = Annotated[Session, Depends(connect_db)]