# -*- coding: utf-8 -*-
"""
Creama - DB 초기화 (가짜 데이터 삭제)

사용법:
  python reset_db.py          # 확인 프롬프트 표시
  python reset_db.py --force  # 확인 없이 삭제
"""

import argparse
from models import Base, Cafe, SensoryData, get_engine, get_session
from sqlalchemy import text


def reset_database(force=False):
    engine = get_engine()
    session = get_session(engine)

    # 현재 데이터 수 확인
    cafe_count = session.query(Cafe).count()
    sd_count = session.query(SensoryData).count()

    print("=" * 50)
    print("[DB 초기화] 현재 데이터:")
    print(f"  cafes:        {cafe_count}건")
    print(f"  sensory_data: {sd_count}건")
    print("=" * 50)

    if cafe_count == 0 and sd_count == 0:
        print("\n이미 비어 있습니다. 작업 불필요.")
        session.close()
        return

    if not force:
        answer = input("\n정말 모든 데이터를 삭제하시겠습니까? (yes/no): ").strip().lower()
        if answer != "yes":
            print("취소되었습니다.")
            session.close()
            return

    print("\n[1/3] sensory_data 삭제...")
    session.execute(text("DELETE FROM sensory_data"))

    print("[2/3] reviews 삭제...")
    try:
        session.execute(text("DELETE FROM reviews"))
    except Exception:
        pass  # reviews 테이블이 없을 수 있음

    print("[3/3] cafes 삭제...")
    session.execute(text("DELETE FROM cafes"))

    # AUTO_INCREMENT 초기화
    try:
        session.execute(text("ALTER TABLE cafes AUTO_INCREMENT = 1"))
        session.execute(text("ALTER TABLE sensory_data AUTO_INCREMENT = 1"))
    except Exception:
        pass

    session.commit()
    session.close()

    print("\n[완료] 모든 데이터가 삭제되었습니다.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creama DB 초기화")
    parser.add_argument("--force", action="store_true", help="확인 없이 삭제")
    args = parser.parse_args()
    reset_database(force=args.force)
