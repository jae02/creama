import urllib.request, json

url = "http://localhost:8081/api/cafes"
with urllib.request.urlopen(url) as res:
    data = json.loads(res.read())

keywords = ["키즈", "kids", "pc", "인터넷", "노래", "코인", "방탈출", "찜질", "보드게임", "독서실", "스터디카페"]
found = []
for c in data:
    name_lower = c["name"].lower()
    for kw in keywords:
        if kw in name_lower:
            found.append(f"{kw:12s}| {c['name']}")
            break

print(f"총 {len(data)}개 중 필터 후보 {len(found)}개:")
for f in found:
    print(f)
