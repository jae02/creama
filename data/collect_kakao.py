# -*- coding: utf-8 -*-
"""
Creama - Kakao API based metro area cafe collection

Usage:
  python collect_kakao.py
  python collect_kakao.py --seoul-only
"""

import os
import json
import csv
import time
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
if not KAKAO_API_KEY:
    print("[ERROR] KAKAO_API_KEY not set in .env")
    exit(1)

SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
HEADERS = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

MAX_API_CALLS = 3000
api_call_count = 0

SEOUL_DISTRICTS = [
    "\uac15\ub0a8\uad6c", "\uac15\ub3d9\uad6c", "\uac15\ubd81\uad6c", "\uac15\uc11c\uad6c", "\uad00\uc545\uad6c",
    "\uad11\uc9c4\uad6c", "\uad6c\ub85c\uad6c", "\uae08\ucc9c\uad6c", "\ub178\uc6d0\uad6c", "\ub3c4\ubd09\uad6c",
    "\ub3d9\ub300\ubb38\uad6c", "\ub3d9\uc791\uad6c", "\ub9c8\ud3ec\uad6c", "\uc11c\ub300\ubb38\uad6c", "\uc11c\ucd08\uad6c",
    "\uc131\ub3d9\uad6c", "\uc131\ubd81\uad6c", "\uc1a1\ud30c\uad6c", "\uc591\ucc9c\uad6c", "\uc601\ub4f1\ud3ec\uad6c",
    "\uc6a9\uc0b0\uad6c", "\uc740\ud3c9\uad6c", "\uc885\ub85c\uad6c", "\uc911\uad6c", "\uc911\ub791\uad6c",
]

GYEONGGI_CITIES = [
    "\uc131\ub0a8\uc2dc", "\uc218\uc6d0\uc2dc", "\uc6a9\uc778\uc2dc", "\uace0\uc591\uc2dc", "\ubd80\ucc9c\uc2dc",
    "\uc548\uc591\uc2dc", "\uc548\uc0b0\uc2dc", "\ud3c9\ud0dd\uc2dc", "\uc758\uc815\ubd80\uc2dc", "\ud30c\uc8fc\uc2dc",
    "\ud558\ub0a8\uc2dc", "\uad11\uba85\uc2dc", "\uae40\ud3ec\uc2dc", "\uad11\uc8fc\uc2dc", "\ub0a8\uc591\uc8fc\uc2dc",
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def search_cafes(region, prefix="Seoul"):
    global api_call_count
    results = []
    if prefix == "Seoul":
        query = f"\uc11c\uc6b8 {region} \uce74\ud398"
    else:
        query = f"\uacbd\uae30\ub3c4 {region} \uce74\ud398"

    for page in range(1, 46):
        if api_call_count >= MAX_API_CALLS:
            print(f"    [STOP] API limit reached ({api_call_count}/{MAX_API_CALLS})")
            return results

        params = {
            "query": query,
            "category_group_code": "CE7",
            "size": 15,
            "page": page,
        }

        try:
            api_call_count += 1
            resp = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            print(f"    [WARN] API error (page {page}): {e}")
            break

        documents = data.get("documents", [])
        if not documents:
            break

        for doc in documents:
            results.append({
                "kakao_id": doc.get("id"),
                "name": doc.get("place_name"),
                "address": doc.get("address_name"),
                "road_address": doc.get("road_address_name"),
                "latitude": float(doc.get("y", 0)),
                "longitude": float(doc.get("x", 0)),
                "phone": doc.get("phone", ""),
                "category": doc.get("category_name", ""),
                "place_url": doc.get("place_url", ""),
                "district": region,
                "region": prefix,
            })

        meta = data.get("meta", {})
        if meta.get("is_end", True):
            break

        time.sleep(0.2)

    return results


def collect_all(seoul_only=False):
    global api_call_count
    api_call_count = 0

    regions = []
    for d in SEOUL_DISTRICTS:
        regions.append(("Seoul", d))
    if not seoul_only:
        for c in GYEONGGI_CITIES:
            regions.append(("Gyeonggi", c))

    total = len(regions)

    print("=" * 60)
    print(f"[INFO] Creama metro cafe collection start")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Regions: {total}")
    print(f"   [SAFE] API call limit: {MAX_API_CALLS}")
    print("=" * 60)

    all_cafes = {}

    for i, (prefix, region) in enumerate(regions, 1):
        label = "\uc11c\uc6b8" if prefix == "Seoul" else "\uacbd\uae30"
        print(f"\n[{i:2d}/{total}] {label} {region} ...")
        cafes = search_cafes(region, prefix)

        new_count = 0
        for cafe in cafes:
            kid = cafe["kakao_id"]
            if kid not in all_cafes:
                all_cafes[kid] = cafe
                new_count += 1

        print(f"    Found {len(cafes)} -> New {new_count} (Total: {len(all_cafes)})")
        time.sleep(0.3)

    cafe_list = list(all_cafes.values())

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = os.path.join(OUTPUT_DIR, f"metro_cafes_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cafe_list, f, ensure_ascii=False, indent=2)

    csv_path = os.path.join(OUTPUT_DIR, f"metro_cafes_{timestamp}.csv")
    if cafe_list:
        fieldnames = cafe_list[0].keys()
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cafe_list)

    latest_json = os.path.join(OUTPUT_DIR, "metro_cafes_latest.json")
    with open(latest_json, "w", encoding="utf-8") as f:
        json.dump(cafe_list, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"[DONE] Metro cafe collection complete!")
    print(f"   Total cafes: {len(cafe_list)} (deduplicated)")
    print(f"   [SAFE] API usage: {api_call_count} / {MAX_API_CALLS}")
    print(f"   JSON: {json_path}")
    print(f"   CSV:  {csv_path}")
    print(f"   Latest: {latest_json}")
    print("=" * 60)

    print(f"\n[STAT] Cafes per region:")
    region_counts = {}
    for cafe in cafe_list:
        r = cafe.get("region", "?")
        label = "\uc11c\uc6b8" if r == "Seoul" else "\uacbd\uae30"
        key = f"{label} {cafe['district']}"
        region_counts[key] = region_counts.get(key, 0) + 1
    for k in sorted(region_counts.keys()):
        print(f"   {k}: {region_counts[k]}")

    return cafe_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creama metro cafe collection")
    parser.add_argument("--seoul-only", action="store_true", help="Seoul only (no Gyeonggi)")
    args = parser.parse_args()
    collect_all(seoul_only=args.seoul_only)
