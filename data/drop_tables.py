# -*- coding: utf-8 -*-
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from models import Base, Cafe, SensoryData

# Database password
DATABASE_URL = "mysql+pymysql://root:skymp159@localhost:3306/creama_db"
engine = create_engine(DATABASE_URL, echo=False)

print("Connected to MySQL")

# Drop all tables first
print("Dropping existing tables...")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS sensory_data"))
    conn.execute(text("DROP TABLE IF EXISTS cafes"))
    conn.commit()

print("Tables dropped. Spring Boot will create them with correct schema.")
print("Please start Spring Boot backend first, then run this script again to seed data.")
