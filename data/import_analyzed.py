# -*- coding: utf-8 -*-
"""
Creama - 분석 데이터 DB 임포트 스크립트

사용법:
  python import_analyzed.py                        # 기본: gangnam_analyzed.json
  python import_analyzed.py --file output/군자역_analyzed.json

특징:
  - kakao_id 기준 UPSERT (중복 방지, 업데이트)
  - sensory_data는 카페 기준 삭제 후 재삽입 (fresh)
  - JSON 배열 필드(seat_types, vibe_keywords 등)는 콤마 구분 문자열로 저장
"""

import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# models.py의 DB 연결 및 모델 임포트
from models import Base, Cafe, SensoryData, get_engine, get_session

BASE_DIR = os.path.dirname(__file__)
DEFAULT_INPUT = os.path.join(BASE_DIR, "output", "daily_analyzed.json")


def migrate_schema(engine):
    """
    기존 테이블에 신규 컬럼을 추가.
    이미 있는 컬럼은 무시 (idempotent).
    """
    alter_statements = [
        # cafes 테이블 컬럼
        "ALTER TABLE cafes ADD COLUMN kakao_id VARCHAR(50) NULL",
        "ALTER TABLE cafes ADD COLUMN phone VARCHAR(20) NULL",
        "ALTER TABLE cafes ADD COLUMN operating_hours VARCHAR(200) NULL",
        "ALTER TABLE cafes ADD COLUMN image_urls TEXT NULL",
        # sensory_data 테이블 컬럼
        "ALTER TABLE sensory_data ADD COLUMN music_genre VARCHAR(50) NULL",
        "ALTER TABLE sensory_data ADD COLUMN crowdedness INT NULL",
        "ALTER TABLE sensory_data ADD COLUMN has_concent TINYINT(1) NULL",
        "ALTER TABLE sensory_data ADD COLUMN has_wifi TINYINT(1) NULL",
        "ALTER TABLE sensory_data ADD COLUMN has_parking TINYINT(1) NULL",
        "ALTER TABLE sensory_data ADD COLUMN seat_types TEXT NULL",
        "ALTER TABLE sensory_data ADD COLUMN vibe_keywords TEXT NULL",
        "ALTER TABLE sensory_data ADD COLUMN recommended_for TEXT NULL",
    ]
    with engine.connect() as conn:
        for stmt in alter_statements:
            try:
                conn.execute(text(stmt))
                col = stmt.split("ADD COLUMN")[1].strip().split()[0]
                print(f"  [MIGRATE] 컬럼 추가: {col}")
            except Exception as e:
                # 이미 있는 컬럼(1060 Duplicate column) 무시
                if "1060" in str(e) or "Duplicate column" in str(e):
                    pass
                else:
                    print(f"  [WARN] {e}")
        conn.commit()


def arr_to_str(val):
    """리스트 → 콤마 구분 문자열 변환"""
    if isinstance(val, list):
        return ",".join(str(v) for v in val)
    return val or ""


def import_data(session, cafes_data):
    added = updated = skipped = 0

    for item in cafes_data:
        kakao_id = item.get("kakao_id", "")
        sa = item.get("sensory_analysis", {})

        # kakao_id로 기존 카페 조회
        cafe = session.query(Cafe).filter_by(kakao_id=kakao_id).first() if kakao_id else None

        if cafe is None:
            # 새 카페 추가
            cafe = Cafe(
                name=item.get("name", ""),
                address=item.get("road_address") or item.get("address", ""),
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
                kakao_id=kakao_id,
                phone=item.get("phone", ""),
            )
            session.add(cafe)
            session.flush()
            added += 1
        else:
            # 기존 카페 정보 업데이트
            cafe.name = item.get("name", cafe.name)
            cafe.address = item.get("road_address") or item.get("address", cafe.address)
            cafe.latitude = item.get("latitude", cafe.latitude)
            cafe.longitude = item.get("longitude", cafe.longitude)
            cafe.phone = item.get("phone", cafe.phone)
            updated += 1

        # sensory_data 삭제 후 재삽입
        session.query(SensoryData).filter_by(cafe_id=cafe.id).delete()

        sd = SensoryData(
            cafe_id=cafe.id,
            acidity=sa.get("acidity", 3.0),
            body=sa.get("body", 3.0),
            sweetness=sa.get("sweetness", 3.0),
            bitterness=sa.get("bitterness", 3.0),
            aroma=sa.get("aroma", 3.0),
            noise_level=sa.get("noise_level", 50),
            lighting=sa.get("lighting", 60),
            comfort=sa.get("comfort", 60),
            crowdedness=sa.get("crowdedness", 50),
            music_genre=sa.get("music_genre", ""),
            has_wifi=sa.get("has_wifi", True),
            has_concent=sa.get("has_concent", True),
            has_parking=sa.get("has_parking", False),
            seat_types=arr_to_str(sa.get("seat_types", [])),
            vibe_keywords=arr_to_str(sa.get("vibe_keywords", [])),
            recommended_for=arr_to_str(sa.get("recommended_for", [])),
        )
        session.add(sd)

    session.commit()
    return added, updated, skipped


def main():
    parser = argparse.ArgumentParser(description="Creama 분석 데이터 DB 임포트")
    parser.add_argument("--file", default=DEFAULT_INPUT, help="임포트할 JSON 파일 경로")
    parser.add_argument("--no-migrate", action="store_true", help="스키마 마이그레이션 건너뛰기")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"[ERROR] 파일을 찾을 수 없습니다: {args.file}")
        sys.exit(1)

    print(f"[START] 임포트 파일: {args.file}")
    cafes_data = json.load(open(args.file, "r", encoding="utf-8"))
    print(f"  카페 수: {len(cafes_data)}")

    engine = get_engine()
    session = get_session(engine)

    if not args.no_migrate:
        print("\n[Phase 1] 스키마 마이그레이션...")
        migrate_schema(engine)

    print("\n[Phase 2] 데이터 임포트...")
    added, updated, skipped = import_data(session, cafes_data)

    print(f"\n[완료]")
    print(f"  추가: {added}개")
    print(f"  업데이트: {updated}개")
    print(f"  건너뜀: {skipped}개")
    print(f"  총 처리: {added + updated + skipped}개")

    session.close()


if __name__ == "__main__":
    main()
