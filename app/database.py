from sqlmodel import SQLModel, Session, create_engine
from .config import get_settings

DATABASE_URL = f"mysql+pymysql://root:{get_settings().PASSWORD}@localhost:3306/food_delivery_restaurant"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session