# -*- coding: utf-8 -*-
"""
Creama - SQLAlchemy ORM 모델
Java 엔티티(Cafe.java, SensoryData.java)의 미러 버전
"""
import os
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean,
    ForeignKey, create_engine, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, Session
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# DB 접속 URL: .env의 DB_URL 우선, 없으면 기본값
DB_URL = os.getenv(
    "DB_URL",
    "mysql+pymysql://root:skymp159@localhost:3306/creama_db"
)

Base = declarative_base()


def get_engine():
    return create_engine(DB_URL, echo=False)


def get_session(engine=None):
    if engine is None:
        engine = get_engine()
    return Session(engine)


class Cafe(Base):
    __tablename__ = 'cafes'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 카카오 고유 ID (UPSERT용)
    kakao_id = Column(String(50), unique=True, nullable=True)

    name = Column(String(200), nullable=False)
    address = Column(String(500))
    latitude = Column(Float(precision=10))
    longitude = Column(Float(precision=10))
    main_image_url = Column(String(1000))

    # 신규 필드
    phone = Column(String(20))
    operating_hours = Column(String(200))
    image_urls = Column(Text)  # JSON 배열: ["url1","url2","url3"]

    # Relationship
    sensory_data_list = relationship(
        "SensoryData",
        back_populates="cafe",
        cascade="all, delete-orphan"
    )


class SensoryData(Base):
    __tablename__ = 'sensory_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cafe_id = Column(Integer, ForeignKey('cafes.id'), nullable=False)

    # Taste Metrics (0.0 - 5.0)
    acidity = Column(Float, nullable=False, default=3.0)
    body = Column(Float, nullable=False, default=3.0)
    sweetness = Column(Float, nullable=False, default=3.0)
    bitterness = Column(Float, nullable=False, default=3.0)
    aroma = Column(Float, nullable=False, default=3.0)

    # Vibe Metrics (0 - 100)
    noise_level = Column(Integer, nullable=False, default=50)
    lighting = Column(Integer, nullable=False, default=50)
    comfort = Column(Integer, nullable=False, default=50)

    # 신규 Vibe 필드
    music_genre = Column(String(50))        # Jazz, Lo-fi, Acoustic, K-Pop, None 등
    crowdedness = Column(Integer)           # 0: 한산 -> 100: 혼잡
    has_concent = Column(Boolean)           # 콘센트 유무
    has_wifi = Column(Boolean)              # 와이파이 유무
    has_parking = Column(Boolean)           # 주차 가능 여부
    seat_types = Column(Text)              # JSON: ["소파","바","테라스","개인석"]
    vibe_keywords = Column(Text)           # JSON: ["빈티지","모던","아늑한","힙한"]
    recommended_for = Column(Text)         # JSON: ["데이트","작업","모임","혼카페","사진"]

    # Tags (JSON stored as text) - 기존 유지
    keywords = Column(Text)               # JSON array: ["Roastery", "Date", "Jazz"]

    # Relationship
    cafe = relationship("Cafe", back_populates="sensory_data_list")
