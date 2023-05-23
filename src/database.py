from sqlmodel import SQLModel, create_engine

from decouple import config

engine = create_engine(config('DB_URL')) 

def create_database():
    SQLModel.metadata.create_all(engine, checkfirst=True) 
