from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

from app.core.config import settings

engine=create_engine(settings.DATABASE_URL,connect_args={"check_same_thread":False})

session=sessionmaker(autocommit=False,autoflush=False,bind=engine)

base=declarative_base()

def get_db():
    db=session()
    try:
        yield db

    finally:
        db.close()    