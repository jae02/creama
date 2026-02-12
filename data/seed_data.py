# -*- coding: utf-8 -*-
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from models import Base, Cafe, SensoryData

# Database connection - try different passwords
passwords = ['skymp159', 'root', '', '1234', 'mysql']
engine = None

print("Trying to connect to MySQL...")
for password in passwords:
    try:
        DATABASE_URL = f"mysql+pymysql://root:{password}@localhost:3306/"
        test_engine = create_engine(DATABASE_URL, echo=False)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"Connected with password: '{password}'")
        
        # Create database if not exists
        with test_engine.connect() as conn:
            conn.execute(text("CREATE DATABASE IF NOT EXISTS creama_db"))
            conn.commit()
        
        # Now connect to creama_db
        DATABASE_URL = f"mysql+pymysql://root:{password}@localhost:3306/creama_db"
        engine = create_engine(DATABASE_URL, echo=True)
        break
    except Exception as e:
        print(f"Failed with password '{password}': {str(e)[:50]}")
        continue

if not engine:
    print("Could not connect to MySQL. Please check your MySQL credentials.")
    exit(1)

# Create tables
Base.metadata.create_all(engine)


def seed_cafes():
    """Insert 3 distinct cafes with different sensory profiles"""
    
    with Session(engine) as session:
        # Clear existing data
        session.query(SensoryData).delete()
        session.query(Cafe).delete()
        session.commit()

        # Cafe A: Creama Signature (Specialty Cafe - High Acidity, Fruity, Bright)
        cafe_a = Cafe(
            name="Creama Signature Roastery",
            address="Seoul, Gangnam-gu, Apgujeong-ro 123",
            latitude=37.5276,
            longitude=127.0382,
            main_image_url="https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800"
        )
        session.add(cafe_a)
        session.flush()  # Get the ID

        sensory_a = SensoryData(
            cafe_id=cafe_a.id,
            # Taste: High acidity, medium body (light specialty style)
            acidity=4.5,
            body=3.0,
            sweetness=3.5,
            bitterness=2.0,
            aroma=4.8,
            # Vibe: Bright workspace, moderate noise
            noise_level=40,
            lighting=85,
            comfort=60,
            keywords=json.dumps(["Specialty", "Single Origin", "Bright", "Fruity", "Roastery"])
        )
        session.add(sensory_a)

        # Cafe B: Date Spot (Dark Chocolate, Cozy, Low Light)
        cafe_b = Cafe(
            name="Velvet Lounge Cafe",
            address="Seoul, Mapo-gu, Hongdae-ro 456",
            latitude=37.5563,
            longitude=126.9245,
            main_image_url="https://images.unsplash.com/photo-1511920170033-f8396924c348?w=800"
        )
        session.add(cafe_b)
        session.flush()

        sensory_b = SensoryData(
            cafe_id=cafe_b.id,
            # Taste: High body, rich chocolate notes
            acidity=2.0,
            body=4.8,
            sweetness=2.5,
            bitterness=4.2,
            aroma=4.0,
            # Vibe: Dark mood lighting, quiet, very comfortable
            noise_level=20,
            lighting=25,
            comfort=95,
            keywords=json.dumps(["Date Spot", "Cozy", "Dark Chocolate", "Jazz", "Sofa"])
        )
        session.add(sensory_b)

        # Cafe C: Workspace (Balanced, Quiet, Standard Tables)
        cafe_c = Cafe(
            name="Focus Study Cafe",
            address="Seoul, Seocho-gu, Gangnam-daero 789",
            latitude=37.4959,
            longitude=127.0277,
            main_image_url="https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800"
        )
        session.add(cafe_c)
        session.flush()

        sensory_c = SensoryData(
            cafe_id=cafe_c.id,
            # Taste: Balanced profile for productivity
            acidity=3.0,
            body=3.5,
            sweetness=3.0,
            bitterness=3.2,
            aroma=3.5,
            # Vibe: Very quiet, bright lighting, standard comfort
            noise_level=10,
            lighting=90,
            comfort=50,
            keywords=json.dumps(["Study", "Workspace", "Quiet", "Fast WiFi", "Power Outlets"])
        )
        session.add(sensory_c)

        # Commit all changes
        session.commit()
        print("Successfully seeded 3 cafes with distinct profiles!")


if __name__ == "__main__":
    print("Starting seed process...")
    seed_cafes()
    print("Seed complete!")
