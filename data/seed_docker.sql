-- Creama 시드 데이터: 서울 가상 카페 15개
-- 기존 데이터 초기화
DELETE FROM sensory_data;
DELETE FROM cafes;

-- ===== 카페 데이터 =====
INSERT INTO cafes (id, name, address, latitude, longitude, main_image_url, phone, operating_hours, image_urls) VALUES
(1, 'Creama Signature Roastery', '서울 강남구 압구정로 123', 37.5276, 127.0382, 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800', '02-1234-5678', '08:00-22:00', '["https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400","https://images.unsplash.com/photo-1442512595331-e89e73853f31?w=400"]'),
(2, 'Velvet Lounge Cafe', '서울 마포구 홍대입구로 456', 37.5563, 126.9245, 'https://images.unsplash.com/photo-1511920170033-f8396924c348?w=800', '02-2345-6789', '10:00-24:00', '["https://images.unsplash.com/photo-1559305616-3f99cd43e353?w=400","https://images.unsplash.com/photo-1493857671505-72967e2e2760?w=400"]'),
(3, 'Focus Study Cafe', '서울 서초구 강남대로 789', 37.4959, 127.0277, 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800', '02-3456-7890', '07:00-23:00', '["https://images.unsplash.com/photo-1521017432531-fbd92d768814?w=400"]'),
(4, '숲속의 오두막', '서울 성동구 서울숲길 17', 37.5445, 127.0374, 'https://images.unsplash.com/photo-1600093463592-8e36ae95ef56?w=800', '02-4567-8901', '09:00-21:00', '["https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400","https://images.unsplash.com/photo-1453614512568-c4024d13c247?w=400"]'),
(5, '하늘정원 루프탑', '서울 용산구 이태원로 55', 37.5340, 126.9948, 'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=800', '02-5678-9012', '11:00-23:00', '["https://images.unsplash.com/photo-1559925393-8be0ec4767c8?w=400"]'),
(6, '그라운드 북카페', '서울 종로구 북촌로 82', 37.5826, 126.9850, 'https://images.unsplash.com/photo-1524578271613-d550eacf6090?w=800', '02-6789-0123', '10:00-22:00', '["https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400","https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"]'),
(7, '미드나잇 브루', '서울 강남구 논현로 654', 37.5172, 127.0286, 'https://images.unsplash.com/photo-1445116572660-236099ec97a0?w=800', '02-7890-1234', '14:00-02:00', '["https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=400"]'),
(8, '레트로 다방', '서울 중구 을지로 111', 37.5660, 126.9910, 'https://images.unsplash.com/photo-1493606278519-11aa9f86e40a?w=800', '02-8901-2345', '09:00-20:00', '["https://images.unsplash.com/photo-1462539405390-d0bdb635c7d1?w=400","https://images.unsplash.com/photo-1509785307050-d4066910ec1e?w=400"]'),
(9, '모던 그린', '서울 송파구 올림픽로 300', 37.5140, 127.1060, 'https://images.unsplash.com/photo-1559496417-e7f25cb247cd?w=800', '02-9012-3456', '08:00-21:00', '["https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400"]'),
(10, '빈티지 레코드', '서울 마포구 와우산로 94', 37.5506, 126.9250, 'https://images.unsplash.com/photo-1453614512568-c4024d13c247?w=800', '02-0123-4567', '12:00-24:00', '["https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=400","https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=400"]'),
(11, '클라우드 나인', '서울 영등포구 여의대로 108', 37.5256, 126.9260, 'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800', '02-1111-2222', '07:30-19:00', '["https://images.unsplash.com/photo-1497366216548-37526070297c?w=400"]'),
(12, '아틀리에 로스팅', '서울 서대문구 연세로 50', 37.5583, 126.9368, 'https://images.unsplash.com/photo-1442512595331-e89e73853f31?w=800', '02-3333-4444', '08:00-22:00', '["https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400","https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400"]'),
(13, '코지 코너', '서울 광진구 아차산로 200', 37.5385, 127.0823, 'https://images.unsplash.com/photo-1559305616-3f99cd43e353?w=800', '02-5555-6666', '09:00-23:00', '["https://images.unsplash.com/photo-1493857671505-72967e2e2760?w=400"]'),
(14, '선셋 테라스', '서울 강서구 마곡중앙로 161', 37.5598, 126.8373, 'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=800', '02-7777-8888', '10:00-22:00', '["https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400","https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400"]'),
(15, '딥 포레스트', '서울 노원구 동일로 1340', 37.6543, 127.0568, 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800', '02-9999-0000', '08:00-20:00', '["https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400"]');

-- ===== 센서리 데이터 =====
INSERT INTO sensory_data (cafe_id, acidity, body, sweetness, bitterness, aroma, noise_level, lighting, comfort, music_genre, crowdedness, has_concent, has_wifi, has_parking, seat_types, vibe_keywords, recommended_for, keywords) VALUES
-- 1. Creama Signature Roastery (강남 스페셜티)
(1, 4.5, 3.0, 3.5, 2.0, 4.8, 40, 85, 60, 'Lo-fi', 50, true, true, false, '["바","개인석","공유테이블"]', '["모던","세련된","밝은"]', '["작업","미팅","혼카페"]', '["Specialty","Single Origin","Bright","Fruity","Roastery"]'),

-- 2. Velvet Lounge (홍대 데이트)
(2, 2.0, 4.8, 2.5, 4.2, 4.0, 20, 25, 95, 'Jazz', 30, false, true, false, '["소파","2인석","커플석"]', '["아늑한","로맨틱","무드있는","어두운"]', '["데이트","기념일","혼카페"]', '["Date Spot","Cozy","Dark Chocolate","Jazz","Sofa"]'),

-- 3. Focus Study (서초 스터디)
(3, 3.0, 3.5, 3.0, 3.2, 3.5, 10, 90, 50, 'None', 60, true, true, true, '["개인석","칸막이석","공유테이블"]', '["조용한","깨끗한","집중"]', '["작업","공부","시험준비"]', '["Study","Workspace","Quiet","Fast WiFi","Power Outlets"]'),

-- 4. 숲속의 오두막 (성수동 자연)
(4, 3.8, 3.2, 4.0, 2.5, 4.2, 35, 70, 85, 'Acoustic', 40, true, true, false, '["소파","테라스","원목테이블"]', '["자연친화","따뜻한","숲속","힐링"]', '["데이트","힐링","사진","반려동물"]', '["Nature","Forest","Healing","Organic","Pet Friendly"]'),

-- 5. 하늘정원 루프탑 (이태원 뷰)
(5, 3.5, 3.0, 3.8, 2.8, 3.5, 55, 95, 65, 'K-Pop', 70, false, true, false, '["테라스","야외석","바"]', '["탁트인","시원한","도시뷰","루프탑"]', '["데이트","모임","사진","SNS"]', '["Rooftop","City View","Sunset","Instagram","Trendy"]'),

-- 6. 그라운드 북카페 (북촌 책)
(6, 2.5, 4.0, 3.5, 3.8, 3.0, 15, 65, 80, 'Classical', 25, true, true, false, '["1인석","소파","독서석"]', '["빈티지","지적인","고풍스러운","차분한"]', '["독서","혼카페","데이트","사색"]', '["Book Cafe","Vintage","Calm","Reading","Intellectual"]'),

-- 7. 미드나잇 브루 (강남 심야)
(7, 4.0, 4.5, 2.0, 4.8, 4.5, 45, 30, 70, 'Jazz', 55, true, true, false, '["바","카운터석","2인석"]', '["시크한","다크","야경","도시적"]', '["야간작업","데이트","혼술","혼카페"]', '["Late Night","Craft Beer","Espresso","Dark","Urban"]'),

-- 8. 레트로 다방 (을지로 뉴트로)
(8, 2.5, 3.8, 4.5, 3.0, 3.2, 50, 55, 60, 'Oldies', 45, false, true, false, '["의자","테이블","좌식"]', '["레트로","뉴트로","복고","감성적"]', '["사진","데이트","친구","SNS"]', '["Retro","Newtro","Vintage","80s","Film Camera"]'),

-- 9. 모던 그린 (송파 건강)
(9, 3.2, 2.5, 4.2, 1.8, 3.8, 30, 80, 75, 'Lo-fi', 35, true, true, true, '["소파","테라스","공유테이블"]', '["깔끔한","건강한","밝은","식물"]', '["작업","브런치","건강","혼카페"]', '["Organic","Vegan","Healthy","Plant","Matcha"]'),

-- 10. 빈티지 레코드 (홍대 LP)
(10, 3.5, 4.2, 2.8, 3.5, 4.0, 40, 40, 70, 'Vinyl', 50, false, true, false, '["소파","빈백","바"]', '["빈티지","음악","LP","힙한","개성있는"]', '["데이트","친구","음악감상","혼카페"]', '["Vinyl","Record","Music","Hipster","Analog"]'),

-- 11. 클라우드 나인 (여의도 오피스)
(11, 3.0, 3.5, 3.0, 3.0, 3.2, 45, 95, 55, 'None', 75, true, true, true, '["개인석","회의실","공유테이블"]', '["비즈니스","프로페셔널","깔끔한"]', '["미팅","작업","코워킹","업무"]', '["Business","Co-working","Meeting","Professional","Express"]'),

-- 12. 아틀리에 로스팅 (신촌 예술)
(12, 4.2, 3.5, 3.0, 2.5, 4.8, 35, 75, 65, 'Indie', 40, true, true, false, '["공유테이블","바","전시공간"]', '["예술적","창의적","갤러리","인디"]', '["작업","전시관람","혼카페","미팅"]', '["Art","Gallery","Exhibition","Creative","Handdrip"]'),

-- 13. 코지 코너 (건대 아늑)
(13, 2.8, 4.0, 4.0, 3.5, 3.5, 25, 45, 90, 'Acoustic', 35, true, true, false, '["소파","담요석","구석자리"]', '["아늑한","포근한","따뜻한","집같은"]', '["데이트","독서","혼카페","휴식"]', '["Cozy","Warm","Blanket","Homey","Comfort"]'),

-- 14. 선셋 테라스 (마곡 노을)
(14, 3.5, 3.0, 3.8, 2.5, 3.5, 30, 85, 70, 'Bossa Nova', 30, true, true, true, '["테라스","야외석","소파"]', '["여유로운","노을","브런치","탁트인"]', '["데이트","브런치","사진","반려동물"]', '["Sunset","Terrace","Brunch","Open Air","Pet Friendly"]'),

-- 15. 딥 포레스트 (노원 숨은명소)
(15, 3.8, 3.5, 3.5, 3.0, 4.0, 15, 60, 80, 'Ambient', 20, true, true, true, '["원목테이블","소파","정원석"]', '["자연친화","숨은명소","고요한","명상"]', '["힐링","독서","혼카페","명상"]', '["Hidden Gem","Forest","Meditation","Quiet","Organic"]');
