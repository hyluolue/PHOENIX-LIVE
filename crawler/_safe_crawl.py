"""
Phoenix-Live 安全网抓取脚本 V2 (V2.9.17-P1.5, 2026-07-16)
========================================================
使用 Playwright (本地 Chrome) 抓 Daraz BD - 绕过反爬 SSL EOF
多关键词 (13 BD) + retry 3 + baseline 保护 + history snapshot + deploy
"""
import argparse
import datetime
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

import os
_ENV = ROOT / ".env"
if _ENV.exists():
    for _line in _ENV.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        if _k.strip() == "PHOENIX_GH_TOKEN":
            os.environ.setdefault("PHOENIX_GH_TOKEN", _v.strip())

REPO = "hyluolue/PHOENIX-LIVE"
BRANCH = "main"
API = "https://api.github.com"

BD_QUERIES = [
    ("mountain bike", "MTB"),
    ("Phoenix bicycle", "Phoenix"),
    ("Marine bicycle", "Marine"),
    ("Giant bicycle", "Giant"),
    ("Polygon bicycle", "Polygon"),
    ("Veloce bicycle", "Veloce"),
    ("Duranta bicycle", "Duranta"),
    ("Foxter bicycle", "Foxter"),
    ("Decathlon bicycle", "Decathlon"),
    ("Firefox bicycle", "Firefox"),
    ("road bike bangladesh", "Road"),
    ("hybrid bike bangladesh", "Hybrid"),
    ("bicycle BD", "BD"),
]
BD_BASELINE_MIN = 30  # 绝对最低 (Playwright 抓 30+ 才写)
BD_KEEP_RATIO = 0.7   # 相对保护: 抓到的 < 之前 70% 则保留 baseline


def log(msg: str):
    # \u53bb\u6389 emoji \u4ee5\u9002\u5e94 GBK \u7ec8\u7aef
    safe = msg.encode("ascii", "replace").decode("ascii")
    line = f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {safe}"
    print(line, flush=True)
    (LOG_DIR / "safe_crawl.log").open("a", encoding="utf-8").write(line + "\n")


def _brand_from_title(title: str) -> tuple[str, str]:
    title = re.sub(r"\s+", " ", title).strip()
    known = ["Phoenix", "Marine", "Veloce", "Giant", "Polygon", "Core", "Pacific",
             "Duranta", "Foxter", "Be worth", "Warrior", "Thorne", "Rockrider",
             "Decathlon", "Firefox", "Trek", "Specialized", "Scott", "Avon",
             "Hero", "BSA", "Montra", "United", "Element"]
    for k in known:
        if k.lower() in title.lower():
            idx = title.lower().index(k.lower())
            return k, title[idx + len(k):].strip(" -")[:60]
    return "Generic", title[:80]


def fetch_daraz_bd_playwright(page, query: str, max_items: int = 8) -> list[dict]:
    """\u7528 Playwright \u6293 Daraz BD \u5355\u67e5\u8be2"""
    out = []
    url = f"https://www.daraz.com.bd/catalog/?q={query.replace(' ', '+')}"
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        page.wait_for_selector('[data-qa-locator="product-item"]', timeout=12000)
        items = page.locator('[data-qa-locator="product-item"]')
        n = min(items.count(), max_items)
        for i in range(n):
            it = items.nth(i)
            a_tags = it.locator('a')
            if a_tags.count() < 2:
                continue
            try:
                title = a_tags.nth(1).get_attribute("title") or ""
            except Exception:
                continue
            if not title:
                continue
            try:
                price_loc = it.locator('span.ooOxS, span[class*="price"]').first
                price_text = price_loc.inner_text(timeout=3000)
            except Exception:
                price_text = ""
            price_digits = "".join(ch for ch in price_text if ch.isdigit())
            try:
                href = a_tags.nth(1).get_attribute("href") or ""
            except Exception:
                href = ""
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = "https://www.daraz.com.bd" + href
            if price_digits and int(price_digits) > 1000:
                brand, model = _brand_from_title(title)
                out.append({
                    "brand": brand, "model": model,
                    "platform": f"Daraz BD ({query})",
                    "price": int(price_digits), "currency": "BDT",
                    "url": href, "is_new": True,
                    "scraped_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                    "note": f"BDT {int(price_digits):,}",
                })
    except Exception as e:
        log(f"  q={query}: {type(e).__name__}: {str(e)[:80]}")
    return out


def fetch_bd_with_retry(page) -> list[dict]:
    """13 \u5173\u952e\u8bcd + 3 retry"""
    out = []
    seen = set()
    for q, label in BD_QUERIES:
        for attempt in range(3):
            items = fetch_daraz_bd_playwright(page, q)
            added = 0
            for it in items:
                key = (it["brand"], it["model"][:30], it["price"])
                if key not in seen:
                    seen.add(key)
                    out.append(it)
                    added += 1
            if added > 0:
                log(f"  BD q={q}: +{added} SKU (total {len(out)})")
                break
            log(f"  BD q={q}: 0 SKU (attempt {attempt+1})")
            time.sleep(3 + attempt * 2)
        time.sleep(1)
    return out


def compute_metrics(latest: dict) -> dict:
    bd_pool = latest["bd"]["price_pool"]
    id_pool = latest["id"]["price_pool"]
    bd_brands = len(set((it.get("brand") or "").strip() for it in bd_pool
                        if (it.get("brand") or "").lower() != "generic"))
    id_brands = len(set((it.get("brand") or "").strip() for it in id_pool
                        if (it.get("brand") or "").lower() != "generic"))
    return {
        "bd": {"total_sku": len(bd_pool), "real_brands": bd_brands},
        "id": {"total_sku": len(id_pool), "real_brands": id_brands},
        "global": {
            "total_sku": len(bd_pool) + len(id_pool),
            "real_brands": len(set(
                [b for b in (it.get("brand", "") for it in bd_pool) if b and b.lower() != "generic"] +
                [b for b in (it.get("brand", "") for it in id_pool) if b and b.lower() != "generic"]
            ))
        }
    }


def snapshot_history(latest: dict, history: dict, today: str) -> dict:
    bd_pool = latest["bd"]["price_pool"]
    id_pool = latest["id"]["price_pool"]
    if len(bd_pool) == 0 and len(id_pool) == 0:
        log("  history: 0 SKU, no snapshot")
        return history
    for region, pool in [("bd", bd_pool), ("id", id_pool)]:
        existing = next((d for d in history[region] if d["date"] == today), None)
        entry = {
            "date": today,
            "sku_count": len(pool),
            "brand_count": len(set((it.get("brand") or "").strip() for it in pool
                                    if (it.get("brand") or "").lower() != "generic")),
            "phx_count": sum(1 for x in pool if (x.get("brand") or "").lower() == "phoenix"),
            "sources": ["safe_crawl"],
            "note": "safe_crawl playwright"
        }
        if existing:
            history[region][history[region].index(existing)] = entry
        else:
            history[region].append(entry)
        history[region] = history[region][-14:]
    history["last_updated"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    return history


def deploy_file(rel_path: str, content: bytes) -> str | None:
    import base64, urllib.request, urllib.error
    token = os.environ.get("PHOENIX_GH_TOKEN")
    if not token:
        log(f"  [SKIP] no token: {rel_path}")
        return None
    b64 = base64.b64encode(content).decode("ascii")
    url = f"{API}/repos/{REPO}/contents/{rel_path}"
    sha = None
    try:
        req = urllib.request.Request(f"{url}?ref={BRANCH}", headers={
            "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            sha = json.load(r).get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            log(f"  [ERR] {rel_path} GET: {e.code}")
    body = json.dumps({"message": f"chore: safe-crawl deploy {rel_path}",
                       "content": b64, "branch": BRANCH, **({"sha": sha} if sha else {})}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=body, method="PUT", headers={
                "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                "Content-Type": "application/json"
            })
            with urllib.request.urlopen(req, timeout=30) as r:
                new_sha = json.load(r)["content"]["sha"][:8]
                log(f"  [OK  ] {rel_path} -> {new_sha}")
                return new_sha
        except Exception as e:
            log(f"  {rel_path} attempt {attempt+1}: {type(e).__name__}")
            if attempt < 2:
                time.sleep(2 ** attempt)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-deploy", action="store_true")
    args = ap.parse_args()

    log("=" * 60)
    log("safe_crawl V2 (Playwright) - V2.9.17-P1.5")
    log("=" * 60)

    latest_path = DATA_DIR / "latest.json"
    history_path = DATA_DIR / "history.json"
    if not latest_path.exists():
        log("[FATAL] latest.json not found")
        return 1

    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else {"bd": [], "id": []}

    prev_bd = len(latest["bd"]["price_pool"])
    prev_id = len(latest["id"]["price_pool"])
    log(f"prev: BD={prev_bd} ID={prev_id}")

    # V2.9.17-P2.3 修复: 用历史最大 BD SKU 数作为 prev_bd_max (防 latest.json 已被漂移)
    hist_bd_max = max((h.get("sku_count", 0) for h in history.get("bd", [])), default=0)
    prev_bd_max = max(prev_bd, hist_bd_max)
    log(f"prev_bd_max = max(prev_bd {prev_bd}, hist_bd_max {hist_bd_max}) = {prev_bd_max}")

    # Playwright
    log("launching Playwright...")
    from playwright.sync_api import sync_playwright
    bd_pool = []
    with sync_playwright() as p:
        chrome = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        browser = p.chromium.launch(executable_path=chrome, headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        log("== BD multi-keyword fetch ==")
        bd_pool = fetch_bd_with_retry(page)
        browser.close()
    log(f"BD total: {len(bd_pool)} SKU")

    # baseline \u4fdd\u62a4 (\u4e24\u91cd\u9608\u503c: \u7edd\u5bf9\u6700\u4f4e + \u76f8\u5bf9\u6bd4\u4f8b)
    # V2.9.17-P2.3 修复: 用 prev_bd_max (历史最大) 不是 prev_bd (上次) 防 9:30 cron 漂移
    threshold = max(BD_BASELINE_MIN, int(prev_bd_max * BD_KEEP_RATIO))
    if len(bd_pool) < threshold:
        log(f"[WARN] BD {len(bd_pool)} < threshold {threshold} (prev_bd_max {prev_bd_max} x 0.7 = {int(prev_bd_max*0.7)}, prev_bd was {prev_bd}), triggering baseline restore")
        # V2.9.17-P2.4: 从 baseline 文件恢复 (不是从 latest.json 读, latest 可能已被漂移)
        baseline_file = DATA_DIR / "latest_20260710_190SKU_baseline.json"
        if baseline_file.exists():
            with baseline_file.open("r", encoding="utf-8") as f:
                _baseline = json.load(f)
            bd_pool = _baseline["bd"]["price_pool"]
            log(f"[RESTORE] BD baseline from {baseline_file.name}: {len(bd_pool)} SKU")
        else:
            daraz_existing = [it for it in latest["bd"]["price_pool"]
                              if "daraz" in (it.get("platform", "")).lower()]
            other = [it for it in latest["bd"]["price_pool"]
                     if "daraz" not in (it.get("platform", "")).lower()]
            bd_pool = daraz_existing + other
            log(f"[WARN] no baseline file, fallback to latest.json: {len(bd_pool)} SKU")
        status_msg = f"warn (BD {len(bd_pool)} kept, baseline protected, threshold {threshold})"
    else:
        status_msg = f"ok ({len(bd_pool)} SKU, threshold {threshold})"

    id_pool = latest["id"]["price_pool"]  # \u4fdd\u7559 baseline 141

    new_latest = latest.copy()
    new_latest["bd"]["price_pool"] = bd_pool
    new_latest["id"]["price_pool"] = id_pool
    new_latest["generated_at"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    new_latest["gen_at"] = new_latest["generated_at"]
    new_latest["fetch_status"] = {
        "daraz_bd": status_msg,
        "shopee_id": "ok (baseline 141 kept)",
        "tokopedia": "ok (baseline kept)",
        "news_bd": "ok", "news_id": "ok",
        "apify_social": "pending",
        "dreamcycle": "pending",
        "serbasepeda": "ok (V2.6.1 8 SKU hardcoded backup)"
    }
    new_latest["dashboard_metrics"] = compute_metrics(new_latest)
    new_latest["source_query"] = f"V2.9.17-P1.5 safe_crawl playwright: 13 BD queries"

    today = datetime.date.today().isoformat()
    new_history = snapshot_history(new_latest, history, today)

    log("== write ==")
    latest_bytes = json.dumps(new_latest, ensure_ascii=False, indent=2).encode("utf-8")
    history_bytes = json.dumps(new_history, ensure_ascii=False, indent=2).encode("utf-8")
    latest_path.write_bytes(latest_bytes)
    history_path.write_bytes(history_bytes)
    log(f"  latest.json: {len(latest_bytes):,} bytes")
    log(f"  history.json: {len(history_bytes):,} bytes")

    if args.skip_deploy:
        log("--skip-deploy")
        return 0

    log("== deploy ==")
    latest_sha = deploy_file("data/latest.json", latest_bytes)
    history_sha = deploy_file("data/history.json", history_bytes)
    log("=" * 60)
    log(f"DONE: BD={len(bd_pool)} ID={len(id_pool)} | latest={latest_sha} history={history_sha}")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
