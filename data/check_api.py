# -*- coding: utf-8 -*-
import urllib.request, json

# 군자역 좌표 기준 nearby 테스트
# 군자역: 37.5488, 127.0877
lat, lng = 37.5488, 127.0877

url = f"http://localhost:8081/api/cafes/nearby?lat={lat}&lng={lng}&limit=20"
with urllib.request.urlopen(url) as res:
    data = json.loads(res.read())

print(f"군자역 근처 카페 (limit=20): {len(data)}개")
for c in data:
    dist = c.get("distance", "?")
    print(f"  [{c['id']}] {c['name']} | {c['address']} | {dist}km")

print()
print("=> 전체 목록(/api/cafes)에서 광진구 ID 범위:")
url2 = "http://localhost:8081/api/cafes"
with urllib.request.urlopen(url2) as res:
    all_data = json.loads(res.read())

gwangjin_ids = [c["id"] for c in all_data if "광진" in (c.get("address") or "") or "군자" in (c.get("address") or "")]
print(f"  광진구 ID 목록: {gwangjin_ids[:10]}...")
print(f"  위도/경도 샘플:")
for c in all_data:
    if "광진" in (c.get("address") or ""):
        print(f"    {c['name']}: lat={c.get('latitude')}, lng={c.get('longitude')}")
        break
