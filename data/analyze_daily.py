# -*- coding: utf-8 -*-
"""
Creama - Daily batch analysis script

Collects Naver blog descriptions for cafes and analyzes them with Gemini AI.
Tracks progress in progress.json to resume across days.

Usage:
  python analyze_daily.py
  python analyze_daily.py --batch-size 100 --max-calls 20
  python analyze_daily.py --input output/metro_cafes_latest.json
  python analyze_daily.py --dry-run  # preview without calling Gemini
"""

import os
import sys
import json
import time
import re
import argparse
import requests
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY")

missing = []
if not NAVER_CLIENT_ID:     missing.append("NAVER_CLIENT_ID")
if not NAVER_CLIENT_SECRET: missing.append("NAVER_CLIENT_SECRET")
if not GEMINI_API_KEY:      missing.append("GEMINI_API_KEY")
if missing:
    print(f"[ERROR] Missing in .env: {', '.join(missing)}")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

BASE_DIR   = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

NAVER_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"

MAX_NAVER_CALLS = 25000
naver_call_count = 0
gemini_call_count = 0

DEFAULT_ANALYSIS = {
    "acidity": 3.0, "body": 3.0, "sweetness": 3.0,
    "bitterness": 3.0, "aroma": 3.0,
    "noise_level": 50, "lighting": 60, "comfort": 60, "crowdedness": 50,
    "music_genre": "unknown",
    "has_wifi": True, "has_concent": True, "has_parking": False,
    "seat_types": ["table"],
    "vibe_keywords": ["normal"],
    "recommended_for": ["general"],
    "keywords": ["cafe"],
}

PROGRESS_FILE = os.path.join(OUTPUT_DIR, "progress.json")
ANALYZED_FILE = os.path.join(OUTPUT_DIR, "daily_analyzed.json")


# ========================================
# Progress tracking
# ========================================
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"analyzed_ids": [], "last_run": None}


def save_progress(progress):
    progress["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def load_analyzed():
    if os.path.exists(ANALYZED_FILE):
        with open(ANALYZED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_analyzed(data):
    with open(ANALYZED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========================================
# Step 1: Naver blog description collection
# ========================================
def fetch_blog_descriptions(cafe_name, district):
    global naver_call_count

    if naver_call_count >= MAX_NAVER_CALLS:
        return []

    query = f"{cafe_name} {district} \uce74\ud398 \ub9ac\ubdf0"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {
        "query": query,
        "display": 10,
        "sort": "sim",
    }

    try:
        naver_call_count += 1
        resp = requests.get(NAVER_BLOG_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except requests.RequestException as e:
        print(f"    [WARN] Naver API error: {e}")
        return []

    descriptions = []
    seen = set()
    for item in items:
        raw = item.get("description", "")
        clean = re.sub(r"<[^>]+>", "", raw).strip()
        if clean and clean not in seen:
            seen.add(clean)
            descriptions.append(clean)

    return descriptions


# ========================================
# Step 2: Gemini AI batch analysis
# ========================================
BATCH_PROMPT_HEADER = """\
You are a cafe review analyst. Given blog review snippets for multiple cafes,
extract structured data for each cafe. Return ONLY a valid JSON array.

For each cafe, output:
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
    "music_genre": "unknown",
    "has_wifi": true,
    "has_concent": true,
    "has_parking": false,
    "seat_types": ["table"],
    "vibe_keywords": ["cozy"],
    "recommended_for": ["study"],
    "keywords": ["specialty"]
  }
}

Rules:
- Taste values (acidity, body, sweetness, bitterness, aroma): 0.0 to 5.0
- Vibe values (noise_level, lighting, comfort, crowdedness): 0 to 100
- noise_level: 0=very quiet, 100=very noisy
- lighting: 0=dark/mood, 100=bright
- comfort: 0=hard chair, 100=very comfortable sofa
- music_genre: one of [jazz, lo-fi, acoustic, k-pop, indie, classical, none, unknown]
- vibe_keywords: Korean words like ["aaa", "bbb", "ccc"]
- recommended_for: Korean words like ["ddd", "eee"]
- keywords: Korean words describing the cafe
- If no review info available, use reasonable defaults

Output ONLY the JSON array, no explanation.

[Cafe Data]
"""


def validate_analysis(analysis):
    """Validate and clamp values to valid ranges"""
    taste_fields = ["acidity", "body", "sweetness", "bitterness", "aroma"]
    vibe_fields = ["noise_level", "lighting", "comfort", "crowdedness"]

    for f in taste_fields:
        v = analysis.get(f, 3.0)
        if not isinstance(v, (int, float)):
            v = 3.0
        analysis[f] = max(0.0, min(5.0, float(v)))

    for f in vibe_fields:
        v = analysis.get(f, 50)
        if not isinstance(v, (int, float)):
            v = 50
        analysis[f] = max(0, min(100, int(v)))

    for f in ["seat_types", "vibe_keywords", "recommended_for", "keywords"]:
        if not isinstance(analysis.get(f), list):
            analysis[f] = DEFAULT_ANALYSIS[f]

    if not isinstance(analysis.get("music_genre"), str):
        analysis["music_genre"] = "unknown"

    for f in ["has_wifi", "has_concent", "has_parking"]:
        if not isinstance(analysis.get(f), bool):
            analysis[f] = DEFAULT_ANALYSIS[f]

    return analysis


def get_confidence(desc_count):
    if desc_count == 0:
        return "low"
    elif desc_count <= 3:
        return "medium"
    else:
        return "high"


def analyze_batch_with_gemini(cafes_batch, max_gemini_calls, dry_run=False):
    global gemini_call_count

    results = {}

    if dry_run or gemini_call_count >= max_gemini_calls:
        if gemini_call_count >= max_gemini_calls:
            print(f"\n    [STOP] Gemini daily limit reached ({max_gemini_calls}). Using defaults.")
        for item in cafes_batch:
            results[item["index"]] = DEFAULT_ANALYSIS.copy()
        return results

    # Build prompt
    cafe_entries = []
    for item in cafes_batch:
        reviews_text = "\n".join(f"  - {d}" for d in item["descriptions"]) if item["descriptions"] else "  - (no reviews found)"
        cafe_entries.append(
            f"--- Cafe #{item['index']} ---\n"
            f"Name: {item['name']}\n"
            f"Address: {item['address']}\n"
            f"Reviews:\n{reviews_text}\n"
        )

    prompt = BATCH_PROMPT_HEADER + "\n".join(cafe_entries)

    try:
        gemini_call_count += 1
        print(f"    [Gemini #{gemini_call_count}] Analyzing {len(cafes_batch)} cafes...")
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Extract JSON from response
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
        else:
            print(f"    [WARN] Could not parse Gemini response, using defaults")
            for item in cafes_batch:
                results[item["index"]] = DEFAULT_ANALYSIS.copy()
            return results

        for entry in parsed:
            idx = entry.get("cafe_index")
            analysis = entry.get("analysis", {})
            if idx is not None:
                results[idx] = validate_analysis(analysis)

    except Exception as e:
        print(f"    [ERROR] Gemini call failed: {e}")
        for item in cafes_batch:
            if item["index"] not in results:
                results[item["index"]] = DEFAULT_ANALYSIS.copy()

    # Fill missing
    for item in cafes_batch:
        if item["index"] not in results:
            results[item["index"]] = DEFAULT_ANALYSIS.copy()

    return results


# ========================================
# Main pipeline
# ========================================
def run_daily(input_file, batch_size, max_calls, dry_run=False):
    global gemini_call_count, naver_call_count
    gemini_call_count = 0
    naver_call_count = 0

    # Load cafe list
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file not found: {input_file}")
        print(f"  Run: python collect_kakao.py  first")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        all_cafes = json.load(f)
    print(f"[INFO] Loaded {len(all_cafes)} cafes from {input_file}")

    # Load progress
    progress = load_progress()
    analyzed_set = set(progress.get("analyzed_ids", []))
    analyzed_results = load_analyzed()

    # Filter out already analyzed cafes
    pending = [c for c in all_cafes if c["kakao_id"] not in analyzed_set]
    print(f"[INFO] Already analyzed: {len(analyzed_set)}, Pending: {len(pending)}")

    if not pending:
        print("[DONE] All cafes have been analyzed!")
        return

    print(f"[INFO] Batch size: {batch_size}, Max Gemini calls: {max_calls}")
    print(f"[INFO] Max cafes this run: {batch_size * max_calls}")
    if dry_run:
        print("[INFO] DRY RUN mode - no Gemini calls will be made")

    print("\n" + "=" * 60)
    print(f"[START] Daily analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Process in batches
    batch_num = 0
    processed = 0

    for batch_start in range(0, len(pending), batch_size):
        if gemini_call_count >= max_calls:
            print(f"\n[STOP] Gemini call limit reached ({max_calls}). Resume tomorrow.")
            break

        batch = pending[batch_start:batch_start + batch_size]
        batch_num += 1

        print(f"\n--- Batch {batch_num} ({len(batch)} cafes) ---")

        # Step 1: Collect Naver blog descriptions
        cafe_data_for_gemini = []
        for i, cafe in enumerate(batch):
            district = cafe.get("district", "")
            descs = fetch_blog_descriptions(cafe["name"], district)
            cafe_data_for_gemini.append({
                "index": i,
                "name": cafe["name"],
                "address": cafe.get("road_address") or cafe.get("address", ""),
                "descriptions": descs,
            })

            if (i + 1) % 20 == 0:
                print(f"    Naver blog search: {i+1}/{len(batch)} done")

        print(f"    Naver blog search complete (API calls: {naver_call_count})")

        # Step 2: Gemini batch analysis
        analysis_results = analyze_batch_with_gemini(cafe_data_for_gemini, max_calls, dry_run)

        # Step 3: Merge results
        for i, cafe in enumerate(batch):
            analysis = analysis_results.get(i, DEFAULT_ANALYSIS.copy())
            desc_count = len(cafe_data_for_gemini[i]["descriptions"])

            result_entry = {
                "kakao_id": cafe["kakao_id"],
                "name": cafe["name"],
                "address": cafe.get("address", ""),
                "road_address": cafe.get("road_address", ""),
                "latitude": cafe.get("latitude"),
                "longitude": cafe.get("longitude"),
                "phone": cafe.get("phone", ""),
                "district": cafe.get("district", ""),
                "region": cafe.get("region", ""),
                "sensory_analysis": analysis,
                "confidence": get_confidence(desc_count),
                "blog_desc_count": desc_count,
                "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            analyzed_results.append(result_entry)
            analyzed_set.add(cafe["kakao_id"])
            processed += 1

        # Save progress after each batch
        progress["analyzed_ids"] = list(analyzed_set)
        save_progress(progress)
        save_analyzed(analyzed_results)

        print(f"    Batch {batch_num} saved. Total analyzed: {len(analyzed_set)}")

        # Rate limit cooldown between batches
        if gemini_call_count < max_calls:
            time.sleep(2)

    # Final summary
    remaining = len(all_cafes) - len(analyzed_set)
    print("\n" + "=" * 60)
    print(f"[DONE] Daily analysis complete!")
    print(f"   Processed this run: {processed}")
    print(f"   Total analyzed: {len(analyzed_set)} / {len(all_cafes)}")
    print(f"   Remaining: {remaining}")
    print(f"   Gemini calls used: {gemini_call_count} / {max_calls}")
    print(f"   Naver calls used: {naver_call_count}")
    print(f"   Output: {ANALYZED_FILE}")
    print(f"   Progress: {PROGRESS_FILE}")
    if remaining > 0:
        est_days = (remaining + batch_size * max_calls - 1) // (batch_size * max_calls)
        print(f"   Estimated days remaining: {est_days}")
    print("=" * 60)

    # Confidence stats
    conf_stats = {"low": 0, "medium": 0, "high": 0}
    for r in analyzed_results:
        c = r.get("confidence", "low")
        conf_stats[c] = conf_stats.get(c, 0) + 1
    print(f"\n[QUALITY] Confidence distribution:")
    for level, count in conf_stats.items():
        pct = count / len(analyzed_results) * 100 if analyzed_results else 0
        print(f"   {level}: {count} ({pct:.1f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creama daily batch analysis")
    parser.add_argument("--input", default=os.path.join(OUTPUT_DIR, "metro_cafes_latest.json"),
                        help="Input cafe JSON file")
    parser.add_argument("--batch-size", type=int, default=100,
                        help="Cafes per Gemini call (default: 100)")
    parser.add_argument("--max-calls", type=int, default=20,
                        help="Max Gemini calls per day (default: 20)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without calling Gemini")
    args = parser.parse_args()

    run_daily(args.input, args.batch_size, args.max_calls, args.dry_run)
