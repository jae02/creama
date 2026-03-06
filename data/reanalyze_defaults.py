# -*- coding: utf-8 -*-
"""
Creama - Re-analyze cafes that got English fallback defaults from failed Gemini JSON parsing.
These cafes have vibe_keywords = 'normal' or NULL, indicating a failed analysis.

Usage:
  python reanalyze_defaults.py
  python reanalyze_defaults.py --max-calls 20 --batch-size 100
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
from models import Base, Cafe, SensoryData, get_engine, get_session
from sqlalchemy import text

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY")

for key, name in [(NAVER_CLIENT_ID, "NAVER_CLIENT_ID"),
                  (NAVER_CLIENT_SECRET, "NAVER_CLIENT_SECRET"),
                  (GEMINI_API_KEY, "GEMINI_API_KEY")]:
    if not key:
        print(f"[ERROR] Missing: {name}")
        sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

NAVER_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"
BASE_DIR = os.path.dirname(__file__)

naver_call_count = 0

DEFAULT_ENGLISH_VIBE = {"normal", "cozy", "general", "cafe", "table", "unknown"}

BATCH_PROMPT_HEADER = """\
You are a cafe review analyst. Analyze the blog review snippets for each cafe and extract structured sensory data.
Return ONLY a valid JSON array, no explanation.

For each cafe output:
{
  "cafe_index": 0,
  "analysis": {
    "acidity": 3.0,
    "body": 3.0,
    "sweetness": 3.0,
    "bitterness": 3.0,
    "aroma": 3.0,
    "noise_level": 50,
    "lighting": 60,
    "comfort": 60,
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
- Taste values: 0.0 to 5.0, Vibe values: 0 to 100
- vibe_keywords and recommended_for: USE KOREAN words
- If no reviews: use reasonable defaults but Korean words for text fields
- Output ONLY the JSON array

[Cafe Data]
"""


def fetch_blog_descriptions(cafe_name, district):
    global naver_call_count
    query = f"{cafe_name} {district} \uce74\ud398 \ub9ac\ubdf0"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": 10, "sort": "sim"}
    try:
        naver_call_count += 1
        resp = requests.get(NAVER_BLOG_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except Exception as e:
        print(f"    [WARN] Naver error: {e}")
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


def validate_analysis(analysis):
    for f in ["acidity", "body", "sweetness", "bitterness", "aroma"]:
        v = analysis.get(f, 3.0)
        analysis[f] = max(0.0, min(5.0, float(v) if isinstance(v, (int, float)) else 3.0))
    for f in ["noise_level", "lighting", "comfort", "crowdedness"]:
        v = analysis.get(f, 50)
        analysis[f] = max(0, min(100, int(v) if isinstance(v, (int, float)) else 50))
    for f in ["seat_types", "vibe_keywords", "recommended_for", "keywords"]:
        if not isinstance(analysis.get(f), list):
            analysis[f] = []
    if not isinstance(analysis.get("music_genre"), str):
        analysis["music_genre"] = "unknown"
    for f in ["has_wifi", "has_concent", "has_parking"]:
        if not isinstance(analysis.get(f), bool):
            analysis[f] = True if f in ["has_wifi", "has_concent"] else False
    return analysis


def arr_to_str(val):
    if isinstance(val, list):
        return ",".join(str(v) for v in val)
    return val or ""


def analyze_batch(cafes_batch, gemini_call_count, max_calls):
    if gemini_call_count[0] >= max_calls:
        return None  # None = quota reached, stop calling

    cafe_entries = []
    for item in cafes_batch:
        reviews = "\n".join(f"  - {d}" for d in item["descriptions"]) if item["descriptions"] else "  - (no reviews)"
        cafe_entries.append(
            f"--- Cafe #{item['index']} ---\n"
            f"Name: {item['name']}\nAddress: {item['address']}\nReviews:\n{reviews}\n"
        )

    prompt = BATCH_PROMPT_HEADER + "\n".join(cafe_entries)
    results = {}

    # Retry up to 3 times on 429 errors
    for attempt in range(3):
        try:
            print(f"    [Gemini #{gemini_call_count[0]+1}] Analyzing {len(cafes_batch)} cafes (attempt {attempt+1})...", flush=True)
            response = model.generate_content(prompt)
            raw = response.text.strip()
            json_match = re.search(r'\[.*\]', raw, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                for entry in parsed:
                    idx = entry.get("cafe_index")
                    if idx is not None:
                        results[idx] = validate_analysis(entry.get("analysis", {}))
            gemini_call_count[0] += 1  # Only count successful calls
            return results
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "quota" in err_str.lower():
                wait_time = 60 * (attempt + 1)  # 60s, 120s, 180s
                print(f"    [WARN] Quota error, waiting {wait_time}s... (attempt {attempt+1}/3)", flush=True)
                time.sleep(wait_time)
            else:
                print(f"    [ERROR] Gemini failed: {e}", flush=True)
                gemini_call_count[0] += 1
                return results

    print(f"    [STOP] Quota exhausted after retries. Stopping.", flush=True)
    return None  # Signal to stop


def run(batch_size=100, max_calls=20):
    engine = get_engine()
    session = get_session(engine)

    # Find cafes with English default vibe_keywords
    target_cafes = session.execute(text("""
        SELECT c.id, c.name, c.address, sd.id as sd_id
        FROM cafes c
        JOIN sensory_data sd ON sd.cafe_id = c.id
        WHERE sd.vibe_keywords IS NULL
           OR sd.vibe_keywords = ''
           OR LOWER(sd.vibe_keywords) = 'normal'
           OR LOWER(sd.vibe_keywords) = 'cozy'
           OR LOWER(sd.vibe_keywords) = 'general'
           OR LOWER(sd.vibe_keywords) = 'cafe'
        ORDER BY c.id
    """)).fetchall()

    print(f"[INFO] Found {len(target_cafes)} cafes with default/English vibe_keywords", flush=True)
    print(f"[INFO] Batch size: {batch_size}, Max Gemini calls: {max_calls}", flush=True)
    print(f"[INFO] Max cafes this run: {batch_size * max_calls}", flush=True)
    print("=" * 60, flush=True)

    gemini_call_count = [0]
    updated_total = 0

    cafe_list = [{"id": r[0], "name": r[1], "address": r[2] or "", "sd_id": r[3]} for r in target_cafes]
    pending = cafe_list[:batch_size * max_calls]

    for batch_start in range(0, len(pending), batch_size):
        if gemini_call_count[0] >= max_calls:
            print(f"\n[STOP] Daily Gemini limit reached ({max_calls}). Run again tomorrow.", flush=True)
            break

        batch = pending[batch_start:batch_start + batch_size]
        print(f"\n--- Batch {gemini_call_count[0]+1} ({len(batch)} cafes) starting at #{batch_start} ---", flush=True)

        # Collect Naver blog descriptions
        cafe_data = []
        for i, cafe in enumerate(batch):
            district = ""
            addr = cafe["address"]
            if addr:
                parts = addr.split()
                district = parts[1] if len(parts) > 1 else ""
            descs = fetch_blog_descriptions(cafe["name"], district)
            cafe_data.append({
                "index": i,
                "name": cafe["name"],
                "address": cafe["address"],
                "descriptions": descs,
            })
            if (i + 1) % 20 == 0:
                print(f"    Naver: {i+1}/{len(batch)}", flush=True)

        print(f"    Naver complete (total calls: {naver_call_count})", flush=True)

        results = analyze_batch(cafe_data, gemini_call_count, max_calls)

        # None means quota exhausted - stop everything
        if results is None:
            print(f"    [STOP] Gemini quota exhausted. Stopping.", flush=True)
            break

        # Update DB
        updated_batch = 0
        for i, cafe in enumerate(batch):
            analysis = results.get(i)
            if analysis is None:
                continue
            sd = session.query(SensoryData).filter_by(id=cafe["sd_id"]).first()
            if sd:
                sd.acidity = analysis.get("acidity", 3.0)
                sd.body = analysis.get("body", 3.0)
                sd.sweetness = analysis.get("sweetness", 3.0)
                sd.bitterness = analysis.get("bitterness", 3.0)
                sd.aroma = analysis.get("aroma", 3.0)
                sd.noise_level = analysis.get("noise_level", 50)
                sd.lighting = analysis.get("lighting", 60)
                sd.comfort = analysis.get("comfort", 60)
                sd.crowdedness = analysis.get("crowdedness", 50)
                sd.music_genre = analysis.get("music_genre", "unknown")
                sd.has_wifi = analysis.get("has_wifi", True)
                sd.has_concent = analysis.get("has_concent", True)
                sd.has_parking = analysis.get("has_parking", False)
                sd.seat_types = arr_to_str(analysis.get("seat_types", []))
                sd.vibe_keywords = arr_to_str(analysis.get("vibe_keywords", []))
                sd.recommended_for = arr_to_str(analysis.get("recommended_for", []))
                sd.keywords = arr_to_str(analysis.get("keywords", []))
                updated_batch += 1

        session.commit()
        updated_total += updated_batch
        print(f"    Updated {updated_batch} cafes in DB. Total updated: {updated_total}", flush=True)
        if gemini_call_count[0] < max_calls:
            print(f"    Cooling down 65s before next batch...", flush=True)
            time.sleep(65)

    remaining = len(target_cafes) - updated_total
    print("\n" + "=" * 60, flush=True)
    print(f"[DONE] Re-analysis complete!", flush=True)
    print(f"   Updated this run: {updated_total}", flush=True)
    print(f"   Remaining (needs next run): {remaining}", flush=True)
    print(f"   Gemini calls used: {gemini_call_count[0]} / {max_calls}", flush=True)
    print("=" * 60, flush=True)
    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reanalyze cafes with English fallback data")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--max-calls", type=int, default=20)
    args = parser.parse_args()
    run(args.batch_size, args.max_calls)
