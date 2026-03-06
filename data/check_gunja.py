# -*- coding: utf-8 -*-
import json, os

OUTPUT_DIR = "output"

# 각 군자역 파일의 분석 품질 비교
files = sorted([f for f in os.listdir(OUTPUT_DIR) if "군자역" in f])
print("=== 군자역 파일 분석 품질 비교 ===\n")

for fname in files:
    data = json.load(open(f"{OUTPUT_DIR}/{fname}", encoding="utf-8"))
    total = len(data)
    
    # 기본값/실패 분류
    default_vibe = ["modern,simple", "모던,심플", ["modern", "simple"], ["모던", "심플"]]
    unknown_vibe = ["unknown"]
    
    has_real = 0
    has_english = 0
    has_default = 0
    has_unknown = 0
    
    for c in data:
        sa = c.get("sensory_analysis", {})
        vk = sa.get("vibe_keywords", [])
        
        if isinstance(vk, list):
            vk_str = ",".join(vk).lower()
        else:
            vk_str = str(vk).lower()
        
        if not vk or vk_str in ["modern,simple", "모던,심플"]:
            has_default += 1
        elif "unknown" in vk_str:
            has_unknown += 1
        elif all(c.isascii() for c in vk_str.replace(",", "").replace(" ", "")):
            has_english += 1
        else:
            has_real += 1
    
    print(f"[FILE] {fname}")
    print(f"   총 {total}개 | 한글 분석: {has_real}개 | 영문 분석: {has_english}개 | default: {has_default}개 | unknown: {has_unknown}개")
    
    # 샘플 vibe 몇 개
    samples = []
    for c in data[:5]:
        vk = c.get("sensory_analysis", {}).get("vibe_keywords", [])
        samples.append(f"{c['name']}: {vk}")
    for s in samples[:3]:
        print(f"   - {s}")
    print()
