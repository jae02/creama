from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()


class Cafe(Base):
    __tablename__ = 'cafes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    latitude = Column(Float(precision=10))
    longitude = Column(Float(precision=10))
    main_image_url = Column(String(1000))

    # Relationship
    sensory_data_list = relationship("SensoryData", back_populates="cafe", cascade="all, delete-orphan")


class SensoryData(Base):
    __tablename__ = 'sensory_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cafe_id = Column(Integer, ForeignKey('cafes.id'), nullable=False)

    # Taste Metrics (0.0 - 5.0)
    acidity = Column(Float, nullable=False)
    body = Column(Float, nullable=False)
    sweetness = Column(Float, nullable=False)
    bitterness = Column(Float, nullable=False)
    aroma = Column(Float, nullable=False)

    # Vibe Metrics (0 - 100)
    noise_level = Column(Integer, nullable=False)
    lighting = Column(Integer, nullable=False)
    comfort = Column(Integer, nullable=False)

    # Tags (JSON stored as text)
    keywords = Column(Text)

    # Relationship
    cafe = relationship("Cafe", back_populates="sensory_data_list")
