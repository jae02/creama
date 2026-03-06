# -*- coding: utf-8 -*-
"""
Creama - ?¤ì´ë²?ë¸ë¡ê·?ê²??API + Gemini AI ì¹´í ë¶ì ?ì´?ë¼??(ë°°ì¹ ë²ì )

?ë¦:
  1. seoul_cafes_latest.json ?ì ì§??êµ?ì¹´í ë¡ë
  2. ?¤ì´ë²?ë¸ë¡ê·?ê²??APIë¡?ì¹´íëª?ê²??-> description(?ì½) ?ì§ (?ë¬¸ ????í¨)
  3. Gemini AIë¡?ìµë? 50ê°?ì¹´íë¥???ë²ì ?ì²­?¼ë¡ ?¼ê´ ë¶ì
  4. ë¶ì ê²°ê³¼ë§?{district}_analyzed.json?????

[SAFE] ?ì¹:
  - ë¸ë¡ê·??ë¬¸/ë¦¬ë·° ?ë¬¸ ?ë? ????í¨
  - ?¤ì´ë²?API ?ë ë¦¬ë°: 100ê±?
  - Gemini API ?ë ë¦¬ë° (ë°°ì¹ ?¨ì): MAX_GEMINI_CALLS = 5
    => ë°°ì¹??ìµë? 50ì¹´í x 5??= ìµë? 250ì¹´í ì²ë¦¬ ê°??

?¬ì©ë²?
  python analyze_reviews.py                  # ê¸°ë³¸: ê°ë¨êµ?
  python analyze_reviews.py --district ë§í¬êµ?
  python analyze_reviews.py --district ?¡íêµ?--max-cafes 100
"""

import os
import json
import time
import re
import argparse
import requests
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# .env ë¡ë
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ?? API ????
NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY")

missing = []
if not NAVER_CLIENT_ID:     missing.append("NAVER_CLIENT_ID")
if not NAVER_CLIENT_SECRET: missing.append("NAVER_CLIENT_SECRET")
if not GEMINI_API_KEY:      missing.append("GEMINI_API_KEY")
if missing:
    print(f"[ERROR] .env???¤ì ?¤ê? ?ìµ?ë¤: {', '.join(missing)}")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ?? [SAFE] ?ë ë¦¬ë° ??
MAX_NAVER_CALLS  = 25000   # ?¤ì´ë²?ë¸ë¡ê·?ê²??API ?¼ì¼ ?ë (ê³µì: 25,000ê±?
MAX_GEMINI_CALLS = 5        # ë°°ì¹ ?¨ì (ë°°ì¹??ìµë? 50ì¹´í)
BATCH_SIZE       = 50       # ??ë²ì Gemini ?ì²­??ë¬¶ë ì¹´í ??

naver_call_count  = 0
gemini_call_count = 0

# ?? ê²½ë¡ ??
BASE_DIR   = os.path.dirname(__file__)
INPUT_FILE = os.path.join(BASE_DIR, "output", "seoul_cafes_latest.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

NAVER_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"


# ????????????????????????????????????????
# Step 1: ?¤ì´ë²?ë¸ë¡ê·?ê²??
# ????????????????????????????????????????
def fetch_blog_descriptions(cafe_name: str, district: str) -> list[str]:
    """
    ?¤ì´ë²?ë¸ë¡ê·?ê²??APIë¡?ì¹´í ê´??ë¸ë¡ê·??ì½(description)ë§??ì§.
    ?ë¬¸ URL? ë¬´ì?ê³  description ?¤ë?«ë§ ë°í.
    """
    global naver_call_count

    if naver_call_count >= MAX_NAVER_CALLS:
        print(f"    [STOP] ?¤ì´ë²?API ë¦¬ë° ?ë¬ ({MAX_NAVER_CALLS}ê±?. ?ì§ ì¤ë¨.")
        return []

    query = f"{cafe_name} {district} ì¹´í"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {
        "query":   query,
        "display": 10,
        "sort":    "sim",
    }

    try:
        naver_call_count += 1
        resp = requests.get(NAVER_BLOG_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except requests.RequestException as e:
        print(f"    [WARN] ?¤ì´ë²?API ?¤í¨: {e}")
        return []

    # descriptionë§?ì¶ì¶ (HTML ?ê·¸ ?ê±°), ?ë¬¸ ë§í¬/?ëª©? ë¬´ì
    descriptions = []
    for item in items:
        raw = item.get("description", "")
        clean = re.sub(r"<[^>]+>", "", raw).strip()
        if clean:
            descriptions.append(clean)

    return descriptions  # ?ë¬¸ URL/?ì¤?¸ë ë°í?ì? ?ì


# ????????????????????????????????????????
# Step 2: Gemini AI ë°°ì¹ ë¶ì
# ????????????????????????????????????????
DEFAULT_ANALYSIS = {
    "acidity": 3.0, "body": 3.0, "sweetness": 3.0,
    "bitterness": 3.0, "aroma": 3.0,
    "noise_level": 50, "lighting": 60, "comfort": 60, "crowdedness": 50,
    "music_genre": "?ì",
    "has_wifi": True, "has_concent": True, "has_parking": False,
    "seat_types": ["?ì´ë¸?],
    "vibe_keywords": ["ëª¨ë", "?¬í"],
    "recommended_for": ["ì¹´í?¬ì´"],
    "keywords": ["ì»¤í¼", "ì¹´í"],
}

BATCH_PROMPT_HEADER = """\
?¤ì? ?¬ë¬ ì¹´í?????ë¸ë¡ê·?ë¦¬ë·° ?ì½ ëª©ë¡?´ì¼.
ê°?ì¹´íë¥?ë¶ì?´ì ?ë JSON ë°°ì´ ?ì?¼ë¡ ?ëµ?´ì¤.
ë°ë??? í¨??JSON ë°°ì´ë§?ì¶ë ¥?? ?¤ë¥¸ ?ì¤?? ë§í¬?¤ì´ ì½ëë¸ë¡ ?ì´ JSON ë°°ì´ë§?

ê°??ì???ì:
{
  "cafe_index": 0,
  "analysis": {
    "acidity": 3.0,
    "body": 3.0,
    "sweetness": 3.0,
    "bitterness": 3.0,
    "aroma": 3.0,
    "noise_level": 50,
    "lighting": 50,
    "comfort": 50,
    "crowdedness": 50,
    "music_genre": "?ì",
    "has_wifi": true,
    "has_concent": true,
    "has_parking": false,
    "seat_types": ["?ì´ë¸?],
    "vibe_keywords": ["ëª¨ë"],
    "recommended_for": ["ì¹´í?¬ì´"],
    "keywords": ["ì»¤í¼"]
  }
}

ë¦¬ë·°?ì ?¸ê¸?ì? ?ì? ??ª©? ì¹´í ? íê³??ì¹ë¥?ê³ ë ¤?´ì ?©ë¦¬?ì¼ë¡?ì¶ì ?´ì¤.

[ì¹´í ëª©ë¡]
"""


def analyze_with_gemini_batch(cafes_batch: list[dict]) -> list[dict]:
    """
    ìµë? BATCH_SIZEê°ì ì¹´íë¥???ë²ì Gemini ?ì²­?¼ë¡ ?¼ê´ ë¶ì.

    cafes_batch ?ì: {
        "index": int,          # ?ë³¸ ë°°ì´?ì???¸ë±??
        "name": str,
        "address": str,
        "descriptions": list[str]
    }

    ë°í: { index: int -> analysis: dict } ?ì?ë¦¬
    """
    global gemini_call_count

    results = {}
    if gemini_call_count >= MAX_GEMINI_CALLS:
        print(f"\n    [STOP] Gemini API ë°°ì¹ ë¦¬ë° ?ë¬ ({MAX_GEMINI_CALLS}ê±?. ê¸°ë³¸ê°??¬ì©.")
        for item in cafes_batch:
            results[item["index"]] = DEFAULT_ANALYSIS.copy()
        return results

    # ?ë¡¬?í¸ êµ¬ì±: ê°?ì¹´í???ë³´ë¥??ì´
    cafe_entries = []
    for item in cafes_batch:
        reviews_text = "\n".join(f"  - {d}" for d in item["descriptions"]) if item["descriptions"] else "  - (ë¸ë¡ê·?ë¦¬ë·° ?ì)"
        entry = (
            f"ì¹´í #{item['index']} ?´ë¦: {item['name']}\n"
            f"?ì¹: {item['address']}\n"
            f"ë¸ë¡ê·?ë¦¬ë·° ?ì½:\n{reviews_text}"
        )
        cafe_entries.append(entry)

    prompt = BATCH_PROMPT_HEADER + "\n\n---\n\n".join(cafe_entries)

    try:
        gemini_call_count += 1
        batch_num = gemini_call_count
        print(f"\n  [GEMINI ë°°ì¹ #{batch_num}] {len(cafes_batch)}ê°?ì¹´í ë¶ì ?ì²­ ì¤?..", end="", flush=True)

        # 429 ?¬ì??ë¡ì§ (ìµë? 3ë²?
        response = None
        for attempt in range(3):
            try:
                response = model.generate_content(prompt)
                break
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    wait = 30 * (attempt + 1)
                    print(f"\n    [WAIT] Gemini ì¿¼í° ì´ê³¼. {wait}ì´??ê¸????¬ì??.. ({attempt+1}/3)")
                    time.sleep(wait)
                else:
                    raise e

        raw = response.text.strip()

        # ì½ëë¸ë¡ ?í¼ ?ê±°
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"^```\s*",     "", raw)
        raw = re.sub(r"\s*```$",     "", raw)

        parsed = json.loads(raw)
        # parsed: [{"cafe_index": 0, "analysis": {...}}, ...]
        for entry in parsed:
            idx = entry.get("cafe_index")
            analysis = entry.get("analysis", {})
            if idx is not None:
                results[idx] = analysis

        # ?ë½???¸ë±?¤ë ê¸°ë³¸ê°?ì±ì?
        for item in cafes_batch:
            if item["index"] not in results:
                results[item["index"]] = DEFAULT_ANALYSIS.copy()

        print(f" -> [OK] {len(results)}/{len(cafes_batch)}ê°?ë¶ì ?ë£")

    except json.JSONDecodeError as e:
        print(f"\n    [WARN] Gemini ë°°ì¹ JSON ?ì± ?¤í¨: {e}. ê¸°ë³¸ê°??¬ì©.")
        for item in cafes_batch:
            results[item["index"]] = DEFAULT_ANALYSIS.copy()
    except Exception as e:
        print(f"\n    [WARN] Gemini ë°°ì¹ ?¤ë¥: {e}. ê¸°ë³¸ê°??¬ì©.")
        for item in cafes_batch:
            results[item["index"]] = DEFAULT_ANALYSIS.copy()

    return results


# ????????????????????????????????????????
# ë©ì¸
# ????????????????????????????????????????
def main():
    global naver_call_count, gemini_call_count
    naver_call_count = 0
    gemini_call_count = 0

    parser = argparse.ArgumentParser(description="Creama ?¤ì´ë²?ë¸ë¡ê·?+ Gemini AI ë¶ì (ë°°ì¹ ì²ë¦¬)")
    parser.add_argument("--district", "-d", default="ê°ë¨êµ?, help="ë¶ì??êµ??´ë¦ (ê¸°ë³¸ê°? ê°ë¨êµ?")
    parser.add_argument("--max-cafes", "-n", type=int, default=0, help="ìµë? ì²ë¦¬ ì¹´í ??(0=?ì²´)")
    args = parser.parse_args()

    district = args.district
    max_cafes = args.max_cafes

    # ?? ?ë ¥ ?ì¼ ë¡ë ??
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] ?ë ¥ ?ì¼ ?ì: {INPUT_FILE}")
        print("       ë¨¼ì? collect_kakao.py ë¥??¤í?ì¸??")
        exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        all_cafes = json.load(f)

    # êµ??í°ë§?
    cafes = [c for c in all_cafes if c.get("district") == district]
    if max_cafes > 0:
        cafes = cafes[:max_cafes]

    print("=" * 60)
    print("[INFO] Creama ?¤ì´ë²?ë¸ë¡ê·?+ Gemini AI ë°°ì¹ ë¶ì ?ì")
    print(f"   ?ê°: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   ??? {district} ì¹´í {len(cafes)}ê°?)
    print(f"   ë°°ì¹ ?¬ê¸°: {BATCH_SIZE}ê°??ì²­")
    print(f"   [SAFE] ?¤ì´ë²?ë¦¬ë°: {MAX_NAVER_CALLS}ê±? Gemini ë°°ì¹ ë¦¬ë°: {MAX_GEMINI_CALLS}ê±?)
    print("=" * 60)

    # ?? Step 1: ëª¨ë  ì¹´í??????¤ì´ë²?ë¸ë¡ê·??ì§ ??
    print("\n[Phase 1] ?¤ì´ë²?ë¸ë¡ê·?ë¦¬ë·° ?ì§ ì¤?..")
    collected_cafes = []  # {"index", "name", "address", "descriptions", "cafe_data"}

    for i, cafe in enumerate(cafes):
        name    = cafe.get("name", "")
        address = cafe.get("address", "")

        if naver_call_count >= MAX_NAVER_CALLS:
            print(f"  [STOP] ?¤ì´ë²?API ë¦¬ë° ?ë¬. {i}ë²ì§¸ ì¹´íë¶??ê±´ë?.")
            # ë¦¬ë° ?´í ì¹´í??ë¹?descriptionsë¡?ì¶ê?
            for j in range(i, len(cafes)):
                collected_cafes.append({
                    "index": j,
                    "name": cafes[j].get("name", ""),
                    "address": cafes[j].get("address", ""),
                    "descriptions": [],
                    "cafe_data": cafes[j],
                })
            break

        print(f"  [{i+1:3d}/{len(cafes)}] {name}", end="", flush=True)
        descriptions = fetch_blog_descriptions(name, district)
        time.sleep(0.5)
        print(f" -> {len(descriptions)}ê°?ë¦¬ë·° ?ì§")

        collected_cafes.append({
            "index": i,
            "name": name,
            "address": address,
            "descriptions": descriptions,
            "cafe_data": cafe,
        })

    # ?? Step 2: 50ê°ì© ë°°ì¹ë¡?Gemini ë¶ì ??
    print(f"\n[Phase 2] Gemini AI ë°°ì¹ ë¶ì ({BATCH_SIZE}ê°??ì²­)...")

    analysis_map = {}  # index -> analysis dict

    for batch_start in range(0, len(collected_cafes), BATCH_SIZE):
        if gemini_call_count >= MAX_GEMINI_CALLS:
            print(f"  [STOP] Gemini ë°°ì¹ ë¦¬ë° ?ë¬ ({MAX_GEMINI_CALLS}ê±?. ?ë¨¸ì§??ê¸°ë³¸ê°?ì²ë¦¬.")
            for item in collected_cafes[batch_start:]:
                analysis_map[item["index"]] = DEFAULT_ANALYSIS.copy()
            break

        batch = collected_cafes[batch_start:batch_start + BATCH_SIZE]
        batch_results = analyze_with_gemini_batch(batch)
        analysis_map.update(batch_results)

        # ë°°ì¹ ê°??ë ??(?¤ì ë°°ì¹ê° ?ì ?ë§)
        if batch_start + BATCH_SIZE < len(collected_cafes):
            print(f"  [WAIT] ?¤ì ë°°ì¹ê¹ì? 12ì´??ê¸?..")
            time.sleep(12.0)

    # ?? Step 3: ê²°ê³¼ ë³í© (?ë¬¸? ë²ë¦¬ê³?ë¶ì ê²°ê³¼ë§???? ??
    results = []
    for item in collected_cafes:
        cafe_data = item["cafe_data"]
        analysis = analysis_map.get(item["index"], DEFAULT_ANALYSIS.copy())
        review_source = "naver_blog" if item["descriptions"] else "default"

        cafe_result = {
            **cafe_data,
            "sensory_analysis": analysis,
            "review_source": review_source,
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        results.append(cafe_result)

    # ?? ê²°ê³¼ ?????
    safe_district = district.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"{safe_district}_analyzed_{timestamp}.json")
    latest_path = os.path.join(OUTPUT_DIR, f"{safe_district}_analyzed.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # ê°ë¨êµ¬ì ê²½ì° ê¸°ì¡´ gangnam_analyzed.json???ë°?´í¸
    if district == "ê°ë¨êµ?:
        gangnam_path = os.path.join(OUTPUT_DIR, "gangnam_analyzed.json")
        with open(gangnam_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    success = sum(1 for r in results if r.get("review_source") == "naver_blog")
    default_cnt = sum(1 for r in results if r.get("review_source") == "default")

    print("\n" + "=" * 60)
    print("[OK] ë¶ì ?ë£!")
    print(f"   ???êµ? {district}")
    print(f"   ë¶ì ?±ê³µ (ë¦¬ë·° ?ì): {success}ê°?)
    print(f"   ê¸°ë³¸ê°?ì²ë¦¬ (ë¦¬ë·° ?ì): {default_cnt}ê°?)
    print(f"   [SAFE] ?¤ì´ë²?API: {naver_call_count}ê±?/ {MAX_NAVER_CALLS}ê±?)
    print(f"   [SAFE] Gemini ë°°ì¹: {gemini_call_count}ê±?/ {MAX_GEMINI_CALLS}ê±?)
    print(f"   ê²°ê³¼: {latest_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
