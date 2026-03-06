# -*- coding: utf-8 -*-
"""
Creama - ?¹ì  ??ì§??ì£¼ë? ì¹´í ?ì§ + AI ë¶ì ?ì´?ë¼??

êµ°ì??ì£¼ë? ì¹´íë¥?ì¹´ì¹´??API ì¢í ê¸°ë°?¼ë¡ ?ì§ ??
?¤ì´ë²?ë¸ë¡ê·?+ Gemini AIë¡??¼ê´ ë¶ì?©ë??

?¬ì©ë²?
  python collect_and_analyze_nearby.py
  python collect_and_analyze_nearby.py --lat 37.5484 --lng 127.0864 --radius 1000 --label êµ°ì??
"""

import os
import sys
import json
import time
import re
import math
import argparse
import requests
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ?? API ????
KAKAO_API_KEY       = os.getenv("KAKAO_API_KEY")
NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY")

for key, name in [(KAKAO_API_KEY,"KAKAO_API_KEY"),(NAVER_CLIENT_ID,"NAVER_CLIENT_ID"),
                  (NAVER_CLIENT_SECRET,"NAVER_CLIENT_SECRET"),(GEMINI_API_KEY,"GEMINI_API_KEY")]:
    if not key:
        print(f"[ERROR] .env??{name}???ìµ?ë¤.")
        sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# ?? ê²½ë¡ ??
BASE_DIR   = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

KAKAO_COORD_URL = "https://dapi.kakao.com/v2/local/search/category.json"
NAVER_BLOG_URL  = "https://openapi.naver.com/v1/search/blog.json"

# ?? [SAFE] ?ë ë¦¬ë° ??
MAX_NAVER_CALLS  = 25000   # ?¤ì´ë²??¼ì¼ ?ë
MAX_GEMINI_CALLS = 5       # ë°°ì¹ ?¨ì
BATCH_SIZE       = 50      # ì¹´í 50ê°???Gemini 1ë²??ì²­

naver_call_count  = 0
gemini_call_count = 0


# ?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â??
# STEP 1: ì¹´ì¹´??API - ì¢í ê¸°ë° ì¹´í ?ì§
# ?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â??
def collect_cafes_nearby(lat: float, lng: float, radius: int, label: str) -> list[dict]:
    """ì¹´ì¹´??ì¹´íê³ ë¦¬ ê²?ì¼ë¡?ì¢í ë°ê²½ ??ì¹´í ?ì§"""
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    cafes = {}

    print(f"\n[STEP 1] ì¹´ì¹´??API - {label} ë°ê²½ {radius}m ì¹´í ?ì§")

    for page in range(1, 46):
        params = {
            "category_group_code": "CE7",  # ì¹´í
            "x": lng,
            "y": lat,
            "radius": radius,
            "size": 15,
            "page": page,
            "sort": "distance",
        }
        try:
            resp = requests.get(KAKAO_COORD_URL, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            print(f"  [WARN] ì¹´ì¹´??API ?¤í¨ (page {page}): {e}")
            break

        documents = data.get("documents", [])
        if not documents:
            break

        for doc in documents:
            kid = doc.get("id")
            if kid and kid not in cafes:
                cafes[kid] = {
                    "kakao_id": kid,
                    "name": doc.get("place_name"),
                    "address": doc.get("address_name"),
                    "road_address": doc.get("road_address_name", ""),
                    "latitude": float(doc.get("y", 0)),
                    "longitude": float(doc.get("x", 0)),
                    "phone": doc.get("phone", ""),
                    "category": doc.get("category_name", ""),
                    "place_url": doc.get("place_url", ""),
                    "district": label,
                    "distance_m": int(doc.get("distance", 0)),
                }

        if data.get("meta", {}).get("is_end", True):
            break
        time.sleep(0.2)

    result = sorted(cafes.values(), key=lambda c: c["distance_m"])
    print(f"  ??{len(result)}ê°?ì¹´í ?ì§ ?ë£")
    for c in result[:5]:
        print(f"     {c['distance_m']}m - {c['name']}")
    if len(result) > 5:
        print(f"     ... ??{len(result)-5}ê°?)
    return result


# ?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â??
# STEP 2: ?¤ì´ë²?ë¸ë¡ê·?ê²??
# ?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â??
def fetch_blog_descriptions(cafe_name: str, location_hint: str) -> list[str]:
    global naver_call_count
    if naver_call_count >= MAX_NAVER_CALLS:
        return []

    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": f"{cafe_name} {location_hint} ì¹´í", "display": 10, "sort": "sim"}

    try:
        naver_call_count += 1
        resp = requests.get(NAVER_BLOG_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except requests.RequestException as e:
        print(f"    [WARN] ?¤ì´ë²?API ?¤í¨: {e}")
        return []

    return [re.sub(r"<[^>]+>", "", item.get("description","")).strip()
            for item in items if item.get("description")]


# ?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â??
# STEP 3: Gemini AI ë°°ì¹ ë¶ì
# ?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â??
DEFAULT_ANALYSIS = {
    "acidity": 3.0, "body": 3.0, "sweetness": 3.0, "bitterness": 3.0, "aroma": 3.0,
    "noise_level": 50, "lighting": 60, "comfort": 60, "crowdedness": 50,
    "music_genre": "?ì", "has_wifi": True, "has_concent": True, "has_parking": False,
    "seat_types": ["?ì´ë¸?], "vibe_keywords": ["ëª¨ë", "?¬í"],
    "recommended_for": ["ì¹´í?¬ì´"], "keywords": ["ì»¤í¼", "ì¹´í"],
}

BATCH_PROMPT_HEADER = """\
?¤ì? ?¬ë¬ ì¹´í?????ë¸ë¡ê·?ë¦¬ë·° ?ì½ ëª©ë¡?´ì¼.
ê°?ì¹´íë¥?ë¶ì?´ì ?ë JSON ë°°ì´ ?ì?¼ë¡ë§??ëµ?´ì¤. ?¤ë¥¸ ?ì¤???ì´ JSON ë°°ì´ë§?

ê°??ì ?ì:
{"cafe_index": 0, "analysis": {"acidity":3.0,"body":3.0,"sweetness":3.0,"bitterness":3.0,"aroma":3.0,
"noise_level":50,"lighting":50,"comfort":50,"crowdedness":50,"music_genre":"?ì",
"has_wifi":true,"has_concent":true,"has_parking":false,
"seat_types":["?ì´ë¸?],"vibe_keywords":["ëª¨ë"],"recommended_for":["ì¹´í?¬ì´"],"keywords":["ì»¤í¼"]}}

ë¦¬ë·°?ì ?¸ê¸ ?ë ??ª©? ì¹´í ? íÂ·?ì¹ë¥?ê³ ë ¤???©ë¦¬?ì¼ë¡?ì¶ì ?´ì¤.

[ì¹´í ëª©ë¡]
"""

def analyze_batch(cafes_batch: list[dict]) -> dict:
    global gemini_call_count
    results = {}

    if gemini_call_count >= MAX_GEMINI_CALLS:
        for item in cafes_batch:
            results[item["index"]] = DEFAULT_ANALYSIS.copy()
        return results

    entries = []
    for item in cafes_batch:
        reviews = "\n".join(f"  - {d}" for d in item["descriptions"]) if item["descriptions"] else "  - (ë¸ë¡ê·?ë¦¬ë·° ?ì)"
        entries.append(f"ì¹´í #{item['index']} ?´ë¦: {item['name']}\n?ì¹: {item['address']}\në¸ë¡ê·?ë¦¬ë·°:\n{reviews}")

    prompt = BATCH_PROMPT_HEADER + "\n\n---\n\n".join(entries)

    try:
        gemini_call_count += 1
        print(f"\n  [GEMINI ë°°ì¹ #{gemini_call_count}] {len(cafes_batch)}ê°?ì¹´í ?¼ê´ ë¶ì ì¤?..", end="", flush=True)

        response = None
        for attempt in range(3):
            try:
                response = gemini_model.generate_content(prompt)
                break
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    wait = 30 * (attempt+1)
                    print(f"\n    [WAIT] ì¿¼í° ì´ê³¼. {wait}ì´??ê¸?..", end="")
                    time.sleep(wait)
                else:
                    raise e

        raw = response.text.strip()
        raw = re.sub(r"^```json\s*","",raw); raw = re.sub(r"^```\s*","",raw); raw = re.sub(r"\s*```$","",raw)

        parsed = json.loads(raw)
        for entry in parsed:
            idx = entry.get("cafe_index")
            if idx is not None:
                results[idx] = entry.get("analysis", DEFAULT_ANALYSIS.copy())

        for item in cafes_batch:
            if item["index"] not in results:
                results[item["index"]] = DEFAULT_ANALYSIS.copy()

        print(f" ??[OK] {len(results)}/{len(cafes_batch)}ê°??ë£")

    except json.JSONDecodeError:
        print(f"\n    [WARN] JSON ?ì± ?¤í¨. ê¸°ë³¸ê°??¬ì©.")
        for item in cafes_batch:
            results[item["index"]] = DEFAULT_ANALYSIS.copy()
    except Exception as e:
        print(f"\n    [WARN] ?¤ë¥: {e}. ê¸°ë³¸ê°??¬ì©.")
        for item in cafes_batch:
            results[item["index"]] = DEFAULT_ANALYSIS.copy()

    return results


# ?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â??
# ë©ì¸
# ?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â?â??
def main():
    global naver_call_count, gemini_call_count
    naver_call_count = gemini_call_count = 0

    parser = argparse.ArgumentParser(description="??ì§??ì£¼ë? ì¹´í ?ì§ + AI ë¶ì")
    parser.add_argument("--lat",    type=float, default=37.5484,  help="ì¤ì¬ ?ë (ê¸°ë³¸: êµ°ì??")
    parser.add_argument("--lng",    type=float, default=127.0864, help="ì¤ì¬ ê²½ë (ê¸°ë³¸: êµ°ì??")
    parser.add_argument("--radius", type=int,   default=1000,     help="ë°ê²½ (ë¯¸í°, ê¸°ë³¸: 1000)")
    parser.add_argument("--label",  type=str,   default="êµ°ì??, help="ì§???ì´ë¸?(?ì¼ëªÂ·ê??ì´ ?¬ì©)")
    args = parser.parse_args()

    print("=" * 60)
    print("[INFO] Creama ì§??ì¹´í ?ì§ + AI ë¶ì ?ì")
    print(f"   ?ê°: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   ?ì¹: {args.label} (?ë:{args.lat}, ê²½ë:{args.lng})")
    print(f"   ë°ê²½: {args.radius}m")
    print("=" * 60)

    # ?? 1. ì¹´ì¹´???ì§ ??
    cafes = collect_cafes_nearby(args.lat, args.lng, args.radius, args.label)
    if not cafes:
        print("[ERROR] ?ì§??ì¹´íê° ?ìµ?ë¤.")
        sys.exit(1)

    # ?? 2. ?¤ì´ë²?ë¸ë¡ê·??ì§ ??
    print(f"\n[STEP 2] ?¤ì´ë²?ë¸ë¡ê·?ë¦¬ë·° ?ì§ ({len(cafes)}ê°?ì¹´í)")
    collected = []
    for i, cafe in enumerate(cafes):
        print(f"  [{i+1:2d}/{len(cafes)}] {cafe['name']}", end="", flush=True)
        descs = fetch_blog_descriptions(cafe["name"], args.label)
        time.sleep(0.3)
        print(f" ??{len(descs)}ê°?ë¦¬ë·°")
        collected.append({"index": i, "name": cafe["name"], "address": cafe["address"],
                          "descriptions": descs, "cafe_data": cafe})

    # ?? 3. Gemini ë°°ì¹ ë¶ì ??
    print(f"\n[STEP 3] Gemini AI ë°°ì¹ ë¶ì ({BATCH_SIZE}ê°??ì²­)")
    analysis_map = {}
    for start in range(0, len(collected), BATCH_SIZE):
        if gemini_call_count >= MAX_GEMINI_CALLS:
            for item in collected[start:]:
                analysis_map[item["index"]] = DEFAULT_ANALYSIS.copy()
            break
        batch = collected[start:start+BATCH_SIZE]
        analysis_map.update(analyze_batch(batch))
        if start + BATCH_SIZE < len(collected):
            print("  [WAIT] 12ì´??ê¸?..")
            time.sleep(12)

    # ?? 4. ê²°ê³¼ ë³í© ë°??????
    results = []
    for item in collected:
        cafe_data = item["cafe_data"]
        analysis  = analysis_map.get(item["index"], DEFAULT_ANALYSIS.copy())
        results.append({
            **cafe_data,
            "sensory_analysis": analysis,
            "review_source": "naver_blog" if item["descriptions"] else "default",
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    safe_label = args.label.replace(" ", "_")
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_ts   = os.path.join(OUTPUT_DIR, f"{safe_label}_analyzed_{timestamp}.json")
    out_latest = os.path.join(OUTPUT_DIR, f"{safe_label}_analyzed.json")

    for path in [out_ts, out_latest]:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    success = sum(1 for r in results if r["review_source"] == "naver_blog")
    print("\n" + "=" * 60)
    print("[OK] ?ë£!")
    print(f"   ?ì§ ì¹´í: {len(results)}ê°?)
    print(f"   ë¦¬ë·° ê¸°ë° ë¶ì: {success}ê°?/ ê¸°ë³¸ê°? {len(results)-success}ê°?)
    print(f"   [SAFE] ?¤ì´ë²? {naver_call_count}/{MAX_NAVER_CALLS}ê±? Gemini ë°°ì¹: {gemini_call_count}/{MAX_GEMINI_CALLS}ê±?)
    print(f"   ê²°ê³¼ ?ì¼: {out_latest}")
    print("=" * 60)
    print("\n?¤ì ëªë ¹?¼ë¡ DB???í¬?¸í?¸ì:")
    print(f"   python import_analyzed.py --file {out_latest}")


if __name__ == "__main__":
    main()
