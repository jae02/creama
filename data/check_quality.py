# -*- coding: utf-8 -*-
import json

data = json.load(open("output/군자역_analyzed.json", encoding="utf-8"))
has_korean = 0
has_english = 0
has_default = 0

for c in data:
    vk = c.get("sensory_analysis", {}).get("vibe_keywords", [])
    vk_str = ",".join(vk) if isinstance(vk, list) else str(vk)
    if not vk_str or vk_str in ["modern,simple", "모던,심플"]:
        has_default += 1
    elif all(ch.isascii() for ch in vk_str.replace(",", "").replace(" ", "")):
        has_english += 1
    else:
        has_korean += 1

print(f"한글 분석: {has_korean}개")
print(f"영문 분석: {has_english}개")
print(f"기본값: {has_default}개")
print()
print("샘플 5개:")
for c in data[:5]:
    vk = c.get("sensory_analysis", {}).get("vibe_keywords", [])
    rf = c.get("sensory_analysis", {}).get("recommended_for", [])
    print(f"  {c['name']}: vibe={vk}, rec={rf}")
