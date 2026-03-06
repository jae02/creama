# -*- coding: utf-8 -*-
import urllib.request, json

url = "http://localhost:8081/api/cafes"
with urllib.request.urlopen(url) as res:
    data = json.loads(res.read())

has_score = [c for c in data if c.get("creamaScore") is not None]
no_score = [c for c in data if c.get("creamaScore") is None]

print(f"전체: {len(data)}개")
print(f"점수 있음: {len(has_score)}개")
print(f"점수 없음: {len(no_score)}개")
print()

scores = [c["creamaScore"] for c in has_score]
print(f"점수 범위: {min(scores):.1f} ~ {max(scores):.1f}")
print(f"평균: {sum(scores)/len(scores):.1f}")
print()

# 상위 5개
top5 = sorted(has_score, key=lambda c: c["creamaScore"], reverse=True)[:5]
print("TOP 5:")
for c in top5:
    print(f"  {c['creamaScore']:.1f} | {c['name']} | {c['address']}")

print()
# 하위 5개
bottom5 = sorted(has_score, key=lambda c: c["creamaScore"])[:5]
print("BOTTOM 5:")
for c in bottom5:
    print(f"  {c['creamaScore']:.1f} | {c['name']} | {c['address']}")
