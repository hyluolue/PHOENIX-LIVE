"""
Phoenix-Live 完整爬虫（阶段 2）
===============================

跑在**本机**（Windows），每天 9:00 触发一次：
1. 抓 Daraz BD 实时价格 → data/latest.json#bd.price_pool
2. 抓 Shopee ID 实时价格 → data/latest.json#id.price_pool
3. 抓 Tokopedia 实时价格 → data/latest.json#id.price_pool (追加)
4. 抓 Google News RSS 孟加拉 MTB → data/latest.json#bd.news
5. 抓 Google News RSS 印尼 MTB   → data/latest.json#id.news
6. 写完 git commit + push（如果 git 已配）

**安装**:
    python -m pip install playwright requests beautifulsoup4 lxml
    python -m playwright install chromium
    git init  (一次性，仓库配好后)

**用法**:
    python run.py                 # 全量跑
    python run.py --module daraz_bd
    python run.py --dry-run
    python run.py --no-git        # 写 json 但不 push
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# 本机 Chrome 路径（playwright 自带 chromium 下载太慢，直接用本机 Chrome）
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Users\www\AppData\Local\Google\Chrome\Application\chrome.exe",
]


def find_chrome() -> str | None:
    """找本机 Chrome"""
    for p in CHROME_PATHS:
        if Path(p).exists():
            return p
    return None


CHROME = find_chrome()


def log(msg: str) -> None:
    line = f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, file=sys.stderr, flush=True)
    (LOG_DIR / "crawler.log").open("a", encoding="utf-8").write(line + "\n")


# ============================================================
# Daraz BD（已验证可用，阶段 1 跑过）
# ============================================================

DARAZ_QUERIES = [
    {"q": "mountain bike", "label": "MTB 综合"},
    {"q": "Phoenix bicycle", "label": "Phoenix 凤凰"},
    {"q": "Marine bicycle", "label": "Marine"},
    {"q": "Giant bicycle", "label": "Giant"},
    {"q": "Polygon bicycle", "label": "Polygon"},
    {"q": "Veloce bicycle", "label": "Veloce"},
    {"q": "Pacific bicycle", "label": "Pacific"},
    {"q": "Duranta bicycle", "label": "Duranta"},
    {"q": "Foxter bicycle", "label": "Foxter"},
    {"q": "Warrior bicycle", "label": "Warrior 71"},
]


def fetch_daraz_bd(page) -> list[dict]:
    """在已打开的 page 上抓 Daraz 搜索结果（多次搜索）"""
    out = []
    for q in DARAZ_QUERIES:
        url = f"https://www.daraz.com.bd/catalog/?q={q['q'].replace(' ', '+')}"
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_selector('[data-qa-locator="product-item"]', timeout=10000)
            items = page.locator('[data-qa-locator="product-item"]')
            for i in range(min(items.count(), 8)):
                it = items.nth(i)
                a_tags = it.locator('a')
                if a_tags.count() < 2:
                    continue
                title = a_tags.nth(1).get_attribute("title") or ""
                if not title:
                    continue
                price_text = it.locator('span.ooOxS, span[class*="price"]').first.inner_text(timeout=3000) if it.locator('span.ooOxS, span[class*="price"]').count() else ""
                price_digits = "".join(ch for ch in price_text if ch.isdigit())
                href = a_tags.nth(1).get_attribute("href") or ""
                if href.startswith("//"):
                    href = "https:" + href
                elif href.startswith("/"):
                    href = "https://www.daraz.com.bd" + href
                if price_digits:
                    out.append({
                        "brand": _brand_from_title(title),
                        "model": title[:100],
                        "platform": f"Daraz BD ({q['label']})",
                        "price": int(price_digits),
                        "currency": "BDT",
                        "url": href,
                        "is_new": True,
                        "scraped_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                        "note": f"BDT {int(price_digits):,}",
                    })
            time.sleep(2)
        except Exception as e:
            log(f"  daraz_bd q={q['q']}: {type(e).__name__}: {str(e)[:100]}")
    return out


# ============================================================
# Shopee Indonesia
# ============================================================

SHOPEE_QUERIES = [
    {"q": "sepeda gunung", "label": "MTB 综合"},
    {"q": "Polygon Sepeda", "label": "Polygon"},
    {"q": "Element Sepeda", "label": "Element"},
    {"q": "United Sepeda", "label": "United"},
    {"q": "Pacific Sepeda", "label": "Pacific"},
    {"q": "Giant Sepeda", "label": "Giant"},
]


def fetch_shopee_id(page) -> list[dict]:
    """Shopee 用 data-testid 或 shopee-search-item-result-item 选择器"""
    out = []
    for q in SHOPEE_QUERIES:
        url = f"https://shopee.co.id/search?keyword={q['q'].replace(' ', '%20')}"
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector('[data-sqe="item"]', timeout=15000)
            items = page.locator('[data-sqe="item"]')
            for i in range(min(items.count(), 8)):
                it = items.nth(i)
                # 标题在 data-sqe="name" 或 [class*="name"]
                name_el = it.locator('[data-sqe="name"], div[class*="name"]').first
                title = name_el.inner_text(timeout=2000) if name_el.count() else ""
                # 价格在 [class*="price"]
                price_el = it.locator('[class*="price"]').first
                price_text = price_el.inner_text(timeout=2000) if price_el.count() else ""
                price_digits = "".join(ch for ch in price_text if ch.isdigit())
                # 链接
                link = it.locator('a').first.get_attribute("href") or ""
                if link.startswith("/"):
                    link = "https://shopee.co.id" + link
                if price_digits and title:
                    out.append({
                        "brand": _brand_from_title(title),
                        "model": title[:100],
                        "platform": f"Shopee ID ({q['label']})",
                        "price": int(price_digits),
                        "currency": "IDR",
                        "url": link,
                        "is_new": True,
                        "scraped_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                        "note": f"Rp {int(price_digits):,}",
                    })
            time.sleep(3)  # Shopee 反爬重，多等
        except Exception as e:
            log(f"  shopee_id q={q['q']}: {type(e).__name__}: {str(e)[:100]}")
    return out


# ============================================================
# Tokopedia
# ============================================================

TOKOPEDIA_QUERIES = [
    {"q": "sepeda gunung", "label": "MTB 综合"},
    {"q": "Polygon sepeda", "label": "Polygon"},
    {"q": "Giant sepeda", "label": "Giant"},
    {"q": "Element sepeda", "label": "Element"},
]


def fetch_tokopedia(page) -> list[dict]:
    """Tokopedia 用 css- 选择器（哈希化），从 data-testid 找更稳"""
    out = []
    for q in TOKOPEDIA_QUERIES:
        url = f"https://www.tokopedia.com/search?q={q['q'].replace(' ', '+')}"
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector('[data-testid="master-product-card"]', timeout=15000)
            items = page.locator('[data-testid="master-product-card"]')
            for i in range(min(items.count(), 8)):
                it = items.nth(i)
                # 标题
                title_el = it.locator('[data-testid="spnSRPProdTitle"], [class*="title"]').first
                title = title_el.inner_text(timeout=2000) if title_el.count() else ""
                # 价格
                price_el = it.locator('[data-testid="spnSRPProdPrice"], [class*="price"]').first
                price_text = price_el.inner_text(timeout=2000) if price_el.count() else ""
                price_digits = "".join(ch for ch in price_text if ch.isdigit())
                # 链接
                link = it.locator('a').first.get_attribute("href") or ""
                if price_digits and title:
                    out.append({
                        "brand": _brand_from_title(title),
                        "model": title[:100],
                        "platform": f"Tokopedia ({q['label']})",
                        "price": int(price_digits),
                        "currency": "IDR",
                        "url": link,
                        "is_new": True,
                        "scraped_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                        "note": f"Rp {int(price_digits):,}",
                    })
            time.sleep(3)
        except Exception as e:
            log(f"  tokopedia q={q['q']}: {type(e).__name__}: {str(e)[:100]}")
    return out


# ============================================================
# News via Sogou 搜索（国内可访问，无 playwright）
# ============================================================

import urllib.parse
import re
from html import unescape as _unescape

NEWS_QUERIES_BD = [
    "MTB Bangladesh market 2026",
    "bicycle industry Bangladesh",
    "Phoenix bicycle Bangladesh",
]
NEWS_QUERIES_ID = [
    "Polygon MTB Indonesia",
    "sepeda gunung pasar Indonesia",
    "bicycle market Indonesia 2026",
]


def fetch_sogou_news(queries: list[str]) -> list[dict]:
    """用 Sogou 网页搜索代替新闻 RSS（国内可访问）"""
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    out = []
    for q in queries:
        url = "https://www.sogou.com/web?query=" + urllib.parse.quote(q)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as r:
                html = r.read().decode("utf-8", errors="replace")
            # 提取标题
            results = re.findall(
                r'<h3[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                html, re.DOTALL,
            )
            for href, title_html in results[:6]:
                title = re.sub(r'<[^>]+>', '', title_html).strip()
                title = _unescape(title)
                if not title or len(title) < 8:
                    continue
                # 过滤低质源
                if any(s in href.lower() for s in ["bilibili.com", "baike.baidu", "zhidao.baidu"]):
                    continue
                out.append({
                    "title": title[:200],
                    "source": "Sogou",
                    "summary": "",
                    "url": href,
                    "published_at": "",
                    "is_new": True,
                })
            time.sleep(1.5)
        except Exception as e:
            log(f"  news q={q}: {type(e).__name__}: {str(e)[:100]}")
    return out


# ============================================================
# Helpers
# ============================================================

KNOWN_BRANDS = [
    "Phoenix", "Marine", "Veloce", "Giant", "Polygon", "Core", "Pacific",
    "Duranta", "Foxter", "Be worth", "Warrior", "Thorne",
    "Element", "United", "Federal", "Wimcycle", "Polygon", "United Bike",
]


def _brand_from_title(title: str) -> str:
    for k in KNOWN_BRANDS:
        if k.lower() in title.lower():
            return k
    return "Generic"


# ============================================================
# Module registry
# ============================================================

def run_daraz_bd():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        kwargs = {"headless": True}
        if CHROME:
            kwargs["executable_path"] = CHROME
        b = p.chromium.launch(**kwargs)
        ctx = b.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = ctx.new_page()
        items = fetch_daraz_bd(page)
        b.close()
    status = "ok" if items else "fail"
    if items and len(items) < 5:
        status = "partial"
    return items, status


def run_shopee_id():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        kwargs = {"headless": True}
        if CHROME:
            kwargs["executable_path"] = CHROME
        b = p.chromium.launch(**kwargs)
        ctx = b.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="id-ID",
        )
        page = ctx.new_page()
        items = fetch_shopee_id(page)
        b.close()
    status = "ok" if items else "fail"
    return items, status


def run_tokopedia():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        kwargs = {"headless": True}
        if CHROME:
            kwargs["executable_path"] = CHROME
        b = p.chromium.launch(**kwargs)
        ctx = b.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="id-ID",
        )
        page = ctx.new_page()
        items = fetch_tokopedia(page)
        b.close()
    status = "ok" if items else "fail"
    return items, status


def run_news_bd():
    items = fetch_sogou_news(NEWS_QUERIES_BD)
    status = "ok" if items else "fail"
    return items, status


def run_news_id():
    items = fetch_sogou_news(NEWS_QUERIES_ID)
    status = "ok" if items else "fail"
    return items, status


# ============================================================
# Tab #7: DTC 差评采集 — Daraz BD 评论 + Apify (TK/Reels/FB/Ins)
# ============================================================

DARAZ_REVIEW_API = "https://my.daraz.com.bd/pdp/review/getReviewList"
DARAZ_REVIEW_PAGE_SIZE = 5  # 每个商品最多拉前 5 条
DARAZ_REVIEW_STAR_THRESHOLD = 3  # 只保留 1-3 星差评 + 5 星好评（按需可改）


def fetch_daraz_reviews_for_item(item_id: str, item_meta: dict) -> list[dict]:
    """抓单个商品的评论：分页取前 5 条"""
    out = []
    try:
        u = f"{DARAZ_REVIEW_API}?itemId={item_id}&pageSize={DARAZ_REVIEW_PAGE_SIZE}&pageNo=1"
        req = urllib.request.Request(u, headers={"User-Agent": "phoenix-live-dtc/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            j = json.loads(r.read().decode("utf-8"))
        m = j.get("model") or {}
        ratings = m.get("ratings") or {}
        reviews = (m.get("items") or [])
        if not reviews:
            return []
        for rv in reviews:
            out.append({
                "item_id": item_id,
                "item_title": item_meta.get("title", ""),
                "item_url": item_meta.get("url", ""),
                "brand": item_meta.get("brand", ""),
                "platform": "daraz_bd",
                "review_id": str(rv.get("reviewId", "")),
                "buyer_name": rv.get("user", {}).get("nickName", "Anonymous"),
                "buyer_country": "BD",
                "rating": int(rv.get("rating", 0)),
                "review_text": (rv.get("reviewContent") or "").strip(),
                "review_time": rv.get("reviewTime", ""),
                "has_image": bool(rv.get("images")),
                "scraped_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            })
    except Exception as e:
        log(f"daraz review {item_id} error: {type(e).__name__}: {e}")
    return out


def run_daraz_bd_reviews():
    """
    抓 data/latest.json#bd.price_pool 里所有商品的 Daraz 评论
    只对 Daraz BD 平台的商品做评论抓取
    """
    data = load_existing()
    price_pool = data.get("bd", {}).get("price_pool", [])

    # 收集 daraz 商品（unique by item_id）
    seen = set()
    items = []
    for p in price_pool:
        if p.get("platform", "").startswith("Daraz"):
            url = p.get("url", "")
            m = re.search(r'i(\d+)\.html', url)
            if m:
                iid = m.group(1)
                if iid not in seen:
                    seen.add(iid)
                    items.append({
                        "item_id": iid,
                        "title": p.get("model", ""),
                        "url": url,
                        "brand": p.get("brand", ""),
                    })

    if not items:
        log("daraz_bd_reviews: no Daraz items in price_pool")
        return [], "fail"

    all_reviews = []
    for it in items:
        reviews = fetch_daraz_reviews_for_item(it["item_id"], it)
        all_reviews.extend(reviews)
        time.sleep(0.3)  # 礼貌

    status = "ok" if all_reviews else "fail"
    if all_reviews and len(all_reviews) < 5:
        status = "partial"
    log(f"daraz_bd_reviews: {len(items)} items -> {len(all_reviews)} reviews")
    return all_reviews, status


# Apify 4 平台 - 已验证 actId
APIFY_ACTS = {
    # platform -> (actId, payload_constructor)
    "tiktok":    ("GdWCkxBtKWOsKjdch",   "clockworks/tiktok-scraper"),
    "instagram": ("SB6AtxpxHLYCx2HEj",  "apify/instagram-hashtag-scraper"),  # placeholder, will validate
    "facebook":  ("d4rlKFnQ7M0qKEZuf",  "apify/facebook-posts-scraper"),
    "reels":     ("hCbsZH9TdSwTCqAP6",  "apify/instagram-reel-scraper"),
}

# 已验证 4 个 actId
APIFY_VERIFIED = {
    "tiktok":   "GdWCkxBtKWOsKjdch",  # clockworks/tiktok-scraper  ✓
    "instagram":"apify~instagram-hashtag-scraper",  # ✓
    "facebook": "apify~facebook-posts-scraper",  # ✓
    "reels":    "apify~instagram-reel-scraper",  # ✓
}

APIFY_HASHTAGS = {
    "bd": ["phoenixbicycle", "phoenixbike", "phoenixcycle", "phoenixmtb", "phoenixbikereview", "71warrior", "dreamcycle"],
    "id": ["phoenixbike", "phoenixbicycleid", "phoenixbikereview", "phoenixcycle", "sepedaphoenix", "phoenixbikesmtb"],
}

# 已知的 phoenix BD/ID 官方 IG/TK username（用于 reels 抓）
APIFY_USERNAMES = {
    "bd": ["dreamcyclestorebd", "phoenix_bd", "phoenixbikebd"],
    "id": ["phoenixbikeofficial", "phoenixbikeid", "phoenix_bike_id"],
}


def _apify_run(act_id: str, token: str, payload: dict, wait_secs: int = 60) -> list[dict]:
    """异步跑 apify actor (start + poll + fetch dataset)，避免长 timeout"""
    # 1) start run
    start_url = f"https://api.apify.com/v2/acts/{act_id}/runs?token={token}"
    req = urllib.request.Request(
        start_url, data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "phoenix-live/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            run = json.loads(r.read().decode("utf-8"))
        run_id = run.get("data", {}).get("id")
        if not run_id:
            log(f"apify start failed: {run}")
            return []
    except Exception as e:
        log(f"apify start error: {type(e).__name__}: {e}")
        return []

    # 2) poll status
    poll_url = f"https://api.apify.com/v2/acts/{act_id}/runs/{run_id}?token={token}"
    deadline = time.time() + wait_secs
    while time.time() < deadline:
        time.sleep(3)
        try:
            with urllib.request.urlopen(poll_url, timeout=10) as r:
                run = json.loads(r.read().decode("utf-8"))
            status = run.get("data", {}).get("status")
            if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                break
        except Exception as e:
            log(f"apify poll error: {e}")
            continue
    else:
        log(f"apify {act_id} timeout after {wait_secs}s")
        return []

    if status != "SUCCEEDED":
        log(f"apify {act_id} status={status}")
        return []

    # 3) fetch dataset
    dataset_id = run.get("data", {}).get("defaultDatasetId")
    if not dataset_id:
        return []
    ds_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}&limit=50"
    try:
        with urllib.request.urlopen(ds_url, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        log(f"apify dataset fetch error: {e}")
        return []


def _norm_post(item: dict, platform: str, kw: str) -> dict | None:
    """normalize 不同平台的 item 到统一 schema"""
    pid = str(item.get("id") or item.get("postId") or item.get("videoId") or "")
    if not pid:
        return None
    return {
        "platform": platform,
        "post_id": pid,
        "url": item.get("url") or item.get("postUrl") or item.get("videoUrl") or item.get("shareUrl") or "",
        "author": (item.get("authorMeta") or {}).get("name") or item.get("ownerUsername") or (item.get("user") or {}).get("name") or (item.get("pageName")) or "",
        "caption": (item.get("text") or item.get("caption") or item.get("message") or "").strip()[:500],
        "likes": item.get("likesCount") or item.get("likes") or item.get("likeCount") or 0,
        "comments": item.get("commentsCount") or item.get("comments") or item.get("commentCount") or 0,
        "shares": item.get("sharesCount") or item.get("shares") or item.get("shareCount") or 0,
        "views": item.get("playCount") or item.get("videoViewCount") or item.get("views") or 0,
        "region": kw.split(":")[0] if ":" in kw else "global",
        "keyword": kw,
        "scraped_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    }


def run_apify_social():
    """
    走 Apify 4 平台: TikTok + Reels + Facebook + Instagram
    需要环境变量 PHOENIX_APIFY_TOKEN
    """
    token = os.environ.get("PHOENIX_APIFY_TOKEN")
    if not token:
        log("apify_social: PHOENIX_APIFY_TOKEN not set, skip")
        return [], "skipped"

    out = []
    seen = set()

    # 1) TikTok 搜 hashtags (BD + ID) - 每区 1 个高频 tag (省额度)
    for region, tags in APIFY_HASHTAGS.items():
        items = _apify_run(APIFY_VERIFIED["tiktok"], token, {
            "searchQueries": [tags[0]],
            "resultsPerPage": 8,
        }, wait_secs=60)
        for it in items[:8]:
            p = _norm_post(it, "tiktok", f"{region}:{tags[0]}")
            if p and p["post_id"] not in seen:
                seen.add(p["post_id"])
                out.append(p)

    # 2) Reels 抓已知 phoenix IG 账号 (优先 ID 官方)
    items = _apify_run(APIFY_VERIFIED["reels"], token, {
        "username": APIFY_USERNAMES["id"][:2],  # 印尼 phoenix 官方号
        "resultsLimit": 8,
    }, wait_secs=60)
    for it in items[:8]:
        p = _norm_post(it, "reels", "id:phoenix_official")
        if p and p["post_id"] not in seen:
            seen.add(p["post_id"])
            out.append(p)

    # 3) Instagram hashtag 抓
    items = _apify_run(APIFY_VERIFIED["instagram"], token, {
        "hashtags": ["phoenixbicycle"],
        "resultsLimit": 8,
    }, wait_secs=60)
    for it in items[:8]:
        p = _norm_post(it, "instagram", "global:phoenixbicycle")
        if p and p["post_id"] not in seen:
            seen.add(p["post_id"])
            out.append(p)

    # 4) Facebook posts
    items = _apify_run(APIFY_VERIFIED["facebook"], token, {
        "startUrls": [{"url": "https://www.facebook.com/search/posts/?q=phoenix+bicycle"}],
        "resultsLimit": 5,
    }, wait_secs=60)
    for it in items[:5]:
        p = _norm_post(it, "facebook", "global:phoenix+bicycle")
        if p and p["post_id"] not in seen:
            seen.add(p["post_id"])
            out.append(p)

    status = "ok" if out else "fail"
    log(f"apify_social: {len(out)} social posts")
    return out, status


# ============================================================
# BD 本土电商: dreamcycle.store (WordPress + WooCommerce)
# ============================================================

DREAMCYCLE_CATEGORY_URLS = [
    "https://www.dreamcycle.store/product-category/bicycle/",
]


def fetch_dreamcycle_products(page) -> list[dict]:
    """从 dreamcycle.store 抓商品价格（BD 9,800-12,000 BDT MTB 段）"""
    out = []
    for cat_url in DREAMCYCLE_CATEGORY_URLS:
        try:
            page.goto(cat_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            # WooCommerce 产品卡片选择器
            items = page.evaluate("""() => {
                const out = [];
                const cards = document.querySelectorAll('.products .product, li.product');
                cards.forEach(c => {
                    const title = c.querySelector('.woocommerce-loop-product__title, h2');
                    const priceEl = c.querySelector('.price');
                    const link = c.querySelector('a.woocommerce-loop-product__link, a[href*="/shop/"]');
                    if (title && priceEl && link) {
                        out.push({
                            title: title.innerText.trim(),
                            price: priceEl.innerText.trim(),
                            href: link.href
                        });
                    }
                });
                return out;
            }""")
            for it in items:
                # 抽价格数字
                m = re.findall(r'([\d,]+(?:\.\d+)?)\s*৳', it["price"])
                if not m:
                    continue
                prices = [float(x.replace(',', '')) for x in m]
                # 取最大（划线/原价/现价）
                pmax = max(prices)
                # 品牌识别
                t = it["title"].lower()
                brand = "Unknown"
                for b in ["phoenix", "duranta", "veloce", "foster", "polloux", "uctocifu", "giant", "trek", "specialized"]:
                    if b in t:
                        brand = b.capitalize()
                        break
                out.append({
                    "brand": brand,
                    "model": it["title"],
                    "platform": "Dream Cycle (dreamcycle.store)",
                    "price": int(pmax),
                    "currency": "BDT",
                    "url": it["href"],
                    "is_new": True,
                    "scraped_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                    "note": f"BDT {pmax:,.0f} (dreamcycle.store)",
                })
        except Exception as e:
            log(f"dreamcycle category {cat_url} error: {type(e).__name__}: {e}")
    return out


def run_dreamcycle():
    from playwright.sync_api import sync_playwright
    if not CHROME:
        log("dreamcycle: no Chrome, skip")
        return [], "skipped"
    items = []
    try:
        with sync_playwright() as p:
            kwargs = {"headless": True}
            kwargs["executable_path"] = CHROME
            b = p.chromium.launch(**kwargs)
            ctx = b.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US",
            )
            page = ctx.new_page()
            items = fetch_dreamcycle_products(page)
            b.close()
    except Exception as e:
        log(f"dreamcycle CRASH: {type(e).__name__}: {e}")
    status = "ok" if items else "fail"
    if items and len(items) < 3:
        status = "partial"
    log(f"dreamcycle: {len(items)} products")
    return items, status


MODULES = {
    "daraz_bd":          ("bd", "price_pool", run_daraz_bd),
    "shopee_id":         ("id", "price_pool", run_shopee_id),
    "tokopedia":         ("id", "price_pool", run_tokopedia),
    "news_bd":           ("bd", "news", run_news_bd),
    "news_id":           ("id", "news", run_news_id),
    "daraz_bd_reviews":  ("bd", "dtc_reviews", run_daraz_bd_reviews),
    "apify_social":      ("global", "dtc_social", run_apify_social),
    "dreamcycle":        ("bd", "price_pool", run_dreamcycle),
}


# ============================================================
# Main
# ============================================================

def load_existing() -> dict:
    p = DATA_DIR / "latest.json"
    if p.exists():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log("warn: latest.json 损坏，重写")
            d = {}
    else:
        d = {}
    # 兜底补齐所有 region / slot
    d.setdefault("schema_version", "1.0")
    d.setdefault("generated_at", None)
    d.setdefault("fetch_status", {})
    d.setdefault("bd", {})
    d["bd"].setdefault("price_pool", [])
    d["bd"].setdefault("price_tracker", [])
    d["bd"].setdefault("news", [])
    d["bd"].setdefault("dtc_reviews", [])
    d.setdefault("id", {})
    d["id"].setdefault("price_pool", [])
    d["id"].setdefault("price_tracker", [])
    d["id"].setdefault("news", [])
    d.setdefault("global", {})
    d["global"].setdefault("dtc_social", [])
    return d


def git_commit_and_push():
    """把最新 data/latest.json 推送到 GitHub —— 用 API（避免 git rebase 冲突）"""
    token = os.environ.get("PHOENIX_GH_TOKEN")
    if not token:
        log("git push skipped: PHOENIX_GH_TOKEN not set")
        return False
    try:
        import base64
        import urllib.request
        import urllib.error
        import json as _json

        local = DATA_DIR / "latest.json"
        if not local.exists():
            log("git push skipped: latest.json not found")
            return False
        b64 = base64.b64encode(local.read_bytes()).decode("ascii")
        url = "https://api.github.com/repos/hyluolue/PHOENIX-LIVE/contents/data/latest.json"
        # 先 GET 拿当前 sha（如果存在）
        sha = None
        try:
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "phoenix-live-deployer",
            })
            with urllib.request.urlopen(req, timeout=15) as r:
                j = _json.load(r)
                sha = j.get("sha")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise

        body = _json.dumps({
            "message": f"chore: data update {datetime.datetime.now().astimezone().isoformat(timespec='seconds')}",
            "content": b64,
            "branch": "main",
            **({"sha": sha} if sha else {}),
        }).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="PUT", headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "phoenix-live-deployer",
            "Content-Type": "application/json",
        })
        with urllib.request.urlopen(req, timeout=30) as r:
            j = _json.load(r)
            log(f"API upload OK: data/latest.json sha={j['content']['sha'][:8]}")
        return True
    except Exception as e:
        log(f"API upload error: {type(e).__name__}: {str(e)[:300]}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", help="逗号分隔要跑的模块名")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-git", action="store_true", help="不 git push")
    args = ap.parse_args()

    targets = list(MODULES.keys())
    if args.module:
        targets = [m.strip() for m in args.module.split(",") if m.strip() in MODULES]
        if not targets:
            log(f"error: --module 无效，可用: {list(MODULES.keys())}")
            return 2

    data = load_existing()
    for name in targets:
        log(f"=== {name} ===")
        try:
            region, slot, fn = MODULES[name]
            items, status = fn()
            # price_pool/news: 覆盖（每日是新数据，不是累积）
            data[region][slot] = items
            data["fetch_status"][name] = status
            log(f"{name}: {len(items)} items, status={status}")
        except Exception as e:
            log(f"{name} CRASH: {type(e).__name__}: {e}")
            data["fetch_status"][name] = "fail"

    data["generated_at"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    data["schema_version"] = "1.0"

    if args.dry_run:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    out = DATA_DIR / "latest.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"wrote {out} ({out.stat().st_size} bytes)")

    if not args.no_git:
        git_commit_and_push()

    return 0


if __name__ == "__main__":
    sys.exit(main())
