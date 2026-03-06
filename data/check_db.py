# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, text

DOCKER_DB = "mysql+pymysql://root:skymp159@localhost:3307/creama_db"
e = create_engine(DOCKER_DB)

with e.connect() as conn:
    total = conn.execute(text("SELECT COUNT(*) FROM cafes")).fetchone()[0]
    with_kakao = conn.execute(text("SELECT COUNT(*) FROM cafes WHERE kakao_id IS NOT NULL")).fetchone()[0]
    with_vibe = conn.execute(text("SELECT COUNT(*) FROM sensory_data WHERE vibe_keywords IS NOT NULL AND vibe_keywords != ''")).fetchone()[0]
    no_vibe = conn.execute(text("SELECT COUNT(*) FROM sensory_data WHERE vibe_keywords IS NULL OR vibe_keywords = ''")).fetchone()[0]

    print(f"총 카페: {total}")
    print(f"  실제 분석 데이터(kakao_id 있음): {with_kakao}")
    print(f"  더미 데이터(kakao_id 없음): {total - with_kakao}")
    print(f"  vibe_keywords 있음: {with_vibe}")
    print(f"  vibe_keywords 없음/빈값: {no_vibe}")

    # 샘플 확인
    rows = conn.execute(text("""
        SELECT c.id, c.name, s.vibe_keywords, s.recommended_for 
        FROM cafes c JOIN sensory_data s ON c.id = s.cafe_id 
        WHERE c.kakao_id IS NOT NULL 
        LIMIT 5
    """)).fetchall()
    print("\n분석 데이터 샘플:")
    for r in rows:
        print(f"  [{r[0]}] {r[1]}: vibe='{r[2]}', rec='{r[3]}'")
