# -*- coding: utf-8 -*-
import os, sys, json, time, re, requests
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

BASE_DIR   = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
BATCH_SIZE  = 10
BATCH_DELAY = 65
NAVER_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"

DEFAULT = {
    "acidity": 3.0, "body": 3.0, "sweetness": 3.0, "bitterness": 3.0, "aroma": 3.0,
    "noise_level": 50, "lighting": 60, "comfort": 60, "crowdedness": 50,
    "music_genre": "none", "has_wifi": True, "has_concent": True, "has_parking": False,
    "seat_types": ["table"], "vibe_keywords": ["modern", "simple"],
    "recommended_for": ["cafe tour"], "keywords": ["coffee", "cafe"],
}

def fetch_naver(name, loc):
    h = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    p = {"query": f"{name} {loc}", "display": 10, "sort": "sim"}
    try:
        r = requests.get(NAVER_BLOG_URL, headers=h, params=p, timeout=10)
        r.raise_for_status()
        return [re.sub(r"<[^>]+>", "", i.get("description","")).strip()
                for i in r.json().get("items",[]) if i.get("description")]
    except Exception as e:
        print(f"    [WARN] {e}"); return []

def build_prompt(batch):
    lines = [
        "아래 카페들을 분석하세요. 반드시 JSON 배열만 반환하고 다른 텍스트는 없어야 합니다.",
        "중요: vibe_keywords, recommended_for, keywords, seat_types, music_genre 의 값은 반드시 한국어로 작성하세요. 영어 금지.",
        "예시 형식: [{\"cafe_index\":0,\"analysis\":{\"acidity\":3.0,\"body\":3.0,\"sweetness\":3.0,\"bitterness\":3.0,\"aroma\":3.0,\"noise_level\":50,\"lighting\":50,\"comfort\":50,\"crowdedness\":50,\"music_genre\":\"재즈\",\"has_wifi\":true,\"has_concent\":true,\"has_parking\":false,\"seat_types\":[\"테이블\",\"소파\"],\"vibe_keywords\":[\"아늑한\",\"감성적\"],\"recommended_for\":[\"데이트\",\"카공\"],\"keywords\":[\"커피\",\"디저트\"]}}]",
        "", "[카페 목록]"
    ]
    for item in batch:
        revs = "\n".join(f"  - {d}" for d in item["descriptions"]) if item["descriptions"] else "  - (리뷰 없음)"
        lines.append(f"카페 #{item['index']} 이름: {item['name']}")
        lines.append(f"위치: {item['address']}")
        lines.append(f"리뷰:\n{revs}\n---")
    return "\n".join(lines)

def run_gemini(batch, bnum, total):
    print(f"  [GEMINI {bnum}/{total}] {len(batch)} cafes...", end="", flush=True)
    res = {}
    for attempt in range(3):
        try:
            raw = gemini_model.generate_content(build_prompt(batch)).text.strip()
            raw = re.sub(r"^```json\s*","",raw); raw=re.sub(r"^```\s*","",raw); raw=re.sub(r"\s*```$","",raw)
            for e in json.loads(raw):
                if e.get("cafe_index") is not None:
                    res[e["cafe_index"]] = e.get("analysis", DEFAULT.copy())
            for item in batch:
                if item["index"] not in res: res[item["index"]] = DEFAULT.copy()
            print(f" OK {len(res)}/{len(batch)}")
            return res
        except json.JSONDecodeError:
            print("\n    [WARN] JSON parse failed"); break
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                w = 60*(attempt+1); print(f"\n    [WAIT] quota. wait {w}s..."); time.sleep(w)
            else:
                print(f"\n    [WARN] {e}"); break
    for item in batch: res[item["index"]] = DEFAULT.copy()
    return res

def main():
    src = os.path.join(OUTPUT_DIR, "군자역_analyzed.json")
    if not os.path.exists(src):
        print("[ERROR] 군자역_analyzed.json not found."); sys.exit(1)
    cafes = json.load(open(src, "r", encoding="utf-8"))
    print(f"Cafes: {len(cafes)} | Batch: {BATCH_SIZE} | Delay: {BATCH_DELAY}s")
    print(f"Model: gemini-2.5-flash")

    collected = []
    print(f"\n[Phase 1] Naver blog review collection ({len(cafes)} cafes)")
    for i, c in enumerate(cafes):
        name = c.get("name","")
        print(f"  [{i+1:2d}/{len(cafes)}] {name}", end="", flush=True)
        descs = fetch_naver(name, "군자역 광진구 카페")
        time.sleep(0.3); print(f" -> {len(descs)} reviews")
        collected.append({"index":i,"name":name,"address":c.get("address",""),"descriptions":descs,"cafe_data":c})

    total = (len(collected)+BATCH_SIZE-1)//BATCH_SIZE
    print(f"\n[Phase 2] Gemini batch analysis ({BATCH_SIZE}/req, {total} batches)")
    amap = {}
    for b, start in enumerate(range(0, len(collected), BATCH_SIZE), 1):
        batch = collected[start:start+BATCH_SIZE]
        amap.update(run_gemini(batch, b, total))
        if start+BATCH_SIZE < len(collected):
            print(f"  [WAIT] {BATCH_DELAY}s...", end="", flush=True)
            time.sleep(BATCH_DELAY); print(" done")

    results = []
    for item in collected:
        a = amap.get(item["index"], DEFAULT.copy())
        results.append({**item["cafe_data"], "sensory_analysis":a,
            "review_source":"naver_blog" if item["descriptions"] else "default",
            "analyzed_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    for p in [os.path.join(OUTPUT_DIR,"군자역_analyzed.json"),
              os.path.join(OUTPUT_DIR,f"군자역_analyzed_{ts}.json")]:
        json.dump(results, open(p,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

    ok = sum(1 for r in results if r["sensory_analysis"].get("vibe_keywords") not in [["modern","simple"],["모던","심플"]])
    print(f"\nDone! Gemini analyzed: {ok}/{len(results)}")

if __name__ == "__main__":
    main()
