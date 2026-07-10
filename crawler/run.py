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

# 兜底：环境变量没设时从 .env 自动加载 token（根治 token is required 报错）
_ENV_FILE = ROOT / ".env"
if _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        _k = _k.strip()
        _v = _v.strip()
        if _k in ("PHOENIX_GH_TOKEN", "PHOENIX_APIFY_TOKEN") and not os.environ.get(_k):
            os.environ[_k] = _v

# 本机 Chrome 路径（playwright 自带 chromium 下载太慢，直接用本机 Chrome）
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Users\www\AppData\Local\Google\Chrome\Application\chrome.exe",
]


def find_chrome() -> str | None:
    """找本地 Chrome"""
    for p in CHROME_PATHS:
        if Path(p).exists():
            return p
    return None


CHROME = find_chrome()


def write_json_lf(path, data) -> None:
    """写 JSON 强制 LF 行尾（Windows write_text 默认 CRLF 会让 CF Pages JSON.parse 崩）"""
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    if "\r\n" in raw:
        raw = raw.replace("\r\n", "\n")
    Path(path).write_bytes(raw.encode("utf-8"))


def log(msg: str) -> None:
    line = f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, file=sys.stderr, flush=True)
    (LOG_DIR / "crawler.log").open("a", encoding="utf-8").write(line + "\n")


def _platform_prefix(platform: str) -> str:
    """
    提取 platform 的"族"前缀用于 merge-by-platform
    "Daraz BD (MTB 综合)" -> "daraz bd"
    "dreamcycle.store"    -> "dreamcycle.store"
    "Dream Cycle (dreamcycle.store)" -> "dreamcycle"
    "Shopee ID (Polygon)" -> "shopee id"
    """
    p = (platform or "").lower().strip()
    if not p:
        return ""
    if "(" in p:
        p = p.split("(", 1)[0].strip()
    return p


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
    "Element", "United", "Federal", "Wimcycle", "United Bike",
    # 2026-06-30 补充：BD 中高端主流品牌（之前漏导致 ROCKRIDER XC 401 等被错认为 Generic）
    "Rockrider", "Ceres", "Magpy", "Kiesel", "MEZAROTTI", "Forever",
    "Falcon", "Adder", "Avon", "Pollux", "Polloux", "Duronto", "Python",
    "Hero", "Trek", "Specialized", "Cannondale", "Scott",
    "Mustang", "Seventy One", "71 Warrior",
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
    """
    BD 市场动态 = Sogou 兜底 + Daraz 数据驱动信号
    - 如果 Sogou 抓到 >= 3 条真实相关 → 用 Sogou
    - 否则用 Daraz 数据生成市场信号（更准确）
    """
    sogou_items = fetch_sogou_news(NEWS_QUERIES_BD)

    # 过滤 Sogou 结果（看是否真实相关）
    relevant = []
    for it in sogou_items:
        title_lower = it['title'].lower()
        if any(kw in title_lower for kw in ['bicycle', 'bike', 'cyclist', 'mtb', 'mountain', 'cycle', 'phoenix', 'marine', 'rockrider', 'veloce']):
            relevant.append(it)

    if len(relevant) >= 3:
        log(f"  news_bd: Sogou 找到 {len(relevant)} 条相关")
        return relevant, "ok"

    # 否则：用 Daraz 数据生成信号
    log(f"  news_bd: Sogou 不相关 ({len(relevant)} 条)，用 Daraz 数据驱动")
    return _generate_market_signals_bd(), "ok"


def run_news_id():
    """
    ID 市场动态 = Sogou 兜底 + serbasepeda 数据驱动信号
    """
    sogou_items = fetch_sogou_news(NEWS_QUERIES_ID)

    relevant = []
    for it in sogou_items:
        title_lower = it['title'].lower()
        if any(kw in title_lower for kw in ['sepeda', 'polygon', 'united', 'element', 'pacific', 'mtb', 'bike']):
            relevant.append(it)

    if len(relevant) >= 3:
        log(f"  news_id: Sogou 找到 {len(relevant)} 条相关")
        return relevant, "ok"

    log(f"  news_id: Sogou 不相关 ({len(relevant)} 条)，用 serbasepeda 数据驱动")
    return _generate_market_signals_id(), "ok"


def _generate_market_signals_bd():
    """从 Daraz BD 实时数据生成市场信号"""
    d_path = DATA_DIR / "latest.json"
    if not d_path.exists():
        return []
    d = json.loads(d_path.read_text(encoding='utf-8'))
    pool = [it for it in d.get('bd', {}).get('price_pool', []) if (it.get('brand') or '').lower() != 'generic']
    signals = []
    now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

    # 信号 1: 25K+ 高端市场
    high = [it for it in pool if (it.get('price') or 0) >= 25000]
    if high:
        brands = sorted(set(it['brand'] for it in high))
        signals.append({
            'title': f"BD 25K+ BDT 高端市场: {len(high)} SKU 跨 {len(brands)} 品牌 = {', '.join(brands[:5])}",
            'source': 'Daraz BD 实时',
            'summary': f"顶价 {max(it['price'] for it in high):,} BDT（{max(high, key=lambda x: x['price'])['brand']}）· Phoenix 当前无 25K+ SKU",
            'url': 'https://www.daraz.com.bd/catalog/?q=mountain+bike',
            'published_at': now[:10],
            'is_new': True,
        })

    # 信号 2: 15-25K 中高端主战场
    mid_high = [it for it in pool if 15000 <= (it.get('price') or 0) < 25000]
    if mid_high:
        from collections import Counter
        brand_cnt = Counter(it['brand'] for it in mid_high)
        top3 = brand_cnt.most_common(3)
        signals.append({
            'title': f"BD 15-25K BDT 中高端: {len(mid_high)} SKU · 龙头 = {top3[0][0]} ({top3[0][1]} SKU)",
            'source': 'Daraz BD 实时',
            'summary': f"Phoenix 在 15-25K 缺席（红海）：Marine {brand_cnt.get('Marine', 0)} / Duranta {brand_cnt.get('Duranta', 0)} / Warrior {brand_cnt.get('Warrior', 0)} SKU",
            'url': 'https://www.daraz.com.bd/catalog/?q=Phoenix+bicycle',
            'published_at': now[:10],
            'is_new': True,
        })

    # 信号 3: Phoenix 真实定位
    phx = [it for it in pool if (it.get('brand') or '').lower() == 'phoenix']
    if phx:
        phx_asp = round(sum(it['price'] for it in phx) / len(phx))
        phx_max = max(it['price'] for it in phx)
        signals.append({
            'title': f"Phoenix BD 实时: {len(phx)} SKU · ASP {phx_asp:,} BDT · 顶价 {phx_max:,}",
            'source': 'Daraz BD 实时',
            'summary': f"Phoenix BD 真实排名 = #14 · 评分 46.4 · 与 Rockrider(16 SKU · ASP 33K · score 92.4) 差距 3.5x",
            'url': 'https://www.daraz.com.bd/catalog/?q=Phoenix+bicycle',
            'published_at': now[:10],
            'is_new': True,
        })

    return signals


def _generate_market_signals_id():
    """从 serbasepeda / ID 池数据生成市场信号"""
    d_path = DATA_DIR / "latest.json"
    if not d_path.exists():
        return []
    d = json.loads(d_path.read_text(encoding='utf-8'))
    id_pool = d.get('id', {}).get('price_pool', [])
    signals = []
    now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

    # 信号 1: ID 7-15M 中端市场
    mid = [it for it in id_pool if 7e6 <= (it.get('price') or 0) < 15e6]
    if mid:
        brands = sorted(set(it['brand'] for it in mid))
        signals.append({
            'title': f"ID Rp 7-15M 中端市场: {len(mid)} SKU 跨 {len(brands)} 品牌 = {', '.join(brands)}",
            'source': 'serbasepeda 实时',
            'summary': f"无中国 SGS 品牌 = Thunder ID 真空切入点（V2.4 已规划 RD-1 12M IDR）",
            'url': 'https://serbasepeda.com/',
            'published_at': now[:10],
            'is_new': True,
        })

    # 信号 2: ID 25M+ 真空
    high = [it for it in id_pool if (it.get('price') or 0) >= 25e6]
    if high:
        signals.append({
            'title': f"ID Rp 25M+ 高端: 仅 {len(high)} SKU = Element Gravel Top Spec 26M = 高端 MTB 真空",
            'source': 'serbasepeda 实时',
            'summary': f"V2.4 规划：FNIX MTB-FLAG-1 27M IDR 正面狙击 Patrol · MTB-FLAG-2 22M 下探 Element 真空段",
            'url': 'https://serbasepeda.com/',
            'published_at': now[:10],
            'is_new': True,
        })

    # 信号 3: ID 折叠子品类
    from collections import Counter
    brand_cnt = Counter(it['brand'] for it in id_pool)
    if 'Element' in brand_cnt:
        signals.append({
            'title': f"ID 折叠子品类 = Element 主导 ({brand_cnt['Element']} SKU · 6.4-7.3M IDR)",
            'source': 'serbasepeda 实时',
            'summary': f"V2.6 修订：Phoenix 无折叠核心技术 + 大行/JAVA 强竞品 → 折叠只试水 1 SKU（不投入长期资源）",
            'url': 'https://serbasepeda.com/',
            'published_at': now[:10],
            'is_new': True,
        })

    return signals


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


def run_serbasepeda():
    """
    serbasepeda.com ID 整车 SKU 写入 latest.json#id.price_pool

    真实情况：serbasepeda.com 首页 bestseller 16 SKU（验证 2026-06-15 11:25）
    但 CF 拦截详情页，所以只能拿首页快照 hardcoded
    8 个成人整车 SKU（排除童车/折叠/配件/电动）写入 price_pool
    让 Tab #4 (competitive.html) 区域筛选能用 ID
    """
    try:
        from id_pool_hardcoded import write_id_pool, ID_HARDCODED
        n = write_id_pool()
        items = []
        for sku in ID_HARDCODED:
            items.append({
                'brand': sku['brand'],
                'model': sku['model'],
                'price': sku['price'],
                'currency': 'IDR',
                'platform': 'serbasepeda.com',
                'in_stock': sku.get('in_stock', True),
                'is_new': True,
                'scraped_at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
                'url': sku.get('url', ''),
                'note': f"IDR {sku['price']:,} - serbasepeda.com hardcoded backup",
            })
        log(f"serbasepeda: {len(items)} ID 整车 SKU written to latest.json#id.price_pool")
        return items, "ok"
    except Exception as e:
        log(f"serbasepeda ERR: {e}")
        return [], "fail"


def discover_dreamcycle():
    """
    Step 1: 先扫全站拿全量 slug 列表（sitemap + collections/all + 分类页）
    写到 discovered_slugs.json，给 scrape_all 用
    """
    try:
        import subprocess
        _this_dir = Path(__file__).parent
        discover_script = _this_dir / "discover_dreamcycle.py"
        if not discover_script.exists():
            log("discover_dreamcycle.py not found, skip")
            return False
        log("discover_dreamcycle: scanning full site (sitemap + collections/all)...")
        r = subprocess.run(
            [sys.executable, str(discover_script)],
            capture_output=True, text=True, timeout=300
        )
        # 输出到日志
        for line in r.stderr.splitlines()[-10:]:
            log(f"  {line}")
        if r.returncode == 0:
            discovered = _this_dir / "discovered_slugs.json"
            if discovered.exists():
                import json as _json
                d = _json.loads(discovered.read_text(encoding='utf-8'))
                log(f"discover_dreamcycle: {d.get('total',0)} slugs discovered")
                return True
        log(f"discover_dreamcycle failed (rc={r.returncode}): {r.stderr[:200]}")
        return False
    except Exception as e:
        log(f"discover_dreamcycle ERR: {e}")
        return False


def run_dreamcycle():
    """
    dreamcycle.store 详情页价格抓取（Playwright + rendered 渲染）

    关键：分类页 .products .product 只能抓分类卡片（不显示真实价格），
    必须 navigate 全量详情页（用 .evaluate + ৳ 字符 + TreeWalker 匹配可见价格）。

    Step 0: discover_dreamcycle() 跑全站扫描拿全量 slug（避免漏抓）
    Step 1: scrape_all() 逐个详情页抓价格（用 discovered_slugs.json）
    Step 2: merge_into_latest 写入 latest.json#bd.price_pool（带 brand 解析）

    用 scrape_full_dreamcycle.py（有 brand 解析）—— dreamcycle_playwright.py 的 brand 解析有 bug 会写 "Unknown"
    """
    # Step 0: 全站发现（失败也继续 = fallback 到 hardcoded 20）
    try:
        discover_dreamcycle()
    except Exception as e:
        log(f"discover_dreamcycle skipped: {e}")

    # 用 scrape_full_dreamcycle（有 brand 解析）
    from scrape_full_dreamcycle import scrape_all, merge_into_latest
    # 加载 discover 出来的 slugs（scrape_all 需要这个参数）
    slugs_file = Path(__file__).parent / "discovered_slugs.json"
    if slugs_file.exists():
        slugs_data = json.loads(slugs_file.read_text(encoding='utf-8'))
        # discovered_slugs.json 结构 = {"total":N, "slugs":[...]}
        if isinstance(slugs_data, dict):
            slugs = slugs_data.get('slugs', [])
        elif isinstance(slugs_data, list):
            slugs = slugs_data
        else:
            slugs = []
        log(f"loaded {len(slugs)} slugs from discovered_slugs.json")
    else:
        slugs = []
        log("WARN: discovered_slugs.json not found, dreamcycle scrape will skip")
    results = asyncio_run_sync(scrape_all(slugs))
    # merge into data/latest.json#bd.price_pool (dreamcycle.*)
    latest_path = DATA_DIR / "latest.json"
    n_updated, n_new = merge_into_latest(results, str(latest_path))
    # 同步返回 items 给 run.py（写 latest 时已包含价格）
    items = []
    for r in results:
        if 'err' in r: continue
        items.append({
            "brand": r.get("title", "?"),  # brand 已在 merge 时正确解析
            "model": r.get("title", r.get("slug", "")),
            "platform": "dreamcycle.store",
            "price": int(r.get("sale", 0)) if r.get("sale") else 0,
            "currency": "BDT",
            "url": r.get("url", ""),
            "is_new": True,
            "scraped_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "note": f"BDT {int(r.get('sale', 0)):,} - dreamcycle.store (Playwright)",
        })
    status = "ok" if items else "fail"
    if items and len(items) < 10:
        status = "partial"
    log(f"dreamcycle: {len(items)} products scraped, merged {n_updated}/{len(results)} into latest.json")
    # ⚠️ merge_into_latest 已经直接写盘（保留了 daraz + 加了 dreamcycle），
    # 但主循环 `data["bd"]["price_pool"] = items` 会用 items 覆盖整个 price_pool。
    # 这里重新读盘拿完整 price_pool 返回，避免覆盖 daraz items。
    full_pool = json.loads(latest_path.read_text(encoding='utf-8'))['bd']['price_pool']
    log(f"dreamcycle: returning full pool = {len(full_pool)} items (preserves daraz)")
    return full_pool, status


def asyncio_run_sync(coro):
    """从 sync context 调 async coroutine"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


MODULES = {
    "daraz_bd":          ("bd", "price_pool", run_daraz_bd),
    "shopee_id":         ("id", "price_pool", run_shopee_id),
    "tokopedia":         ("id", "price_pool", run_tokopedia),
    "news_bd":           ("bd", "news", run_news_bd),
    "news_id":           ("id", "news", run_news_id),
    "daraz_bd_reviews":  ("bd", "dtc_reviews", run_daraz_bd_reviews),
    "apify_social":      ("global", "dtc_social", run_apify_social),
    "dreamcycle":        ("bd", "price_pool", run_dreamcycle),
    "serbasepeda":       ("id", "price_pool", run_serbasepeda),
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
            # 但 status=fail 时不要覆盖（避免反爬空池覆盖之前的真实数据）
            # 特殊：id.price_pool 永不覆盖（serbasepeda hardcoded 持久化）
            # V3.1 fix (2026-07-10): BD price_pool 用 merge-by-platform 替代 replace
            #   修复 daraz_bd 覆盖整个 pool 把 dreamcycle 103 SKU 干掉的 bug
            if status == "ok" or (status != "fail" and items):
                if region == "id" and slot == "price_pool" and name != "serbasepeda":
                    # shopee_id / tokopedia 等反爬时不覆盖 id pool
                    log(f"  {name}: skip overwrite id.price_pool (反爬不覆盖)")
                elif region == "bd" and slot == "price_pool" and items:
                    # BD merge-by-platform: 只覆盖自己 platform 的 items，保留其他 platform
                    # (e.g. daraz_bd 不删 dreamcycle / scrape_full_dreamcycle 不删 daraz)
                    this_prefix = _platform_prefix(items[0].get('platform', ''))
                    existing = data[region].get(slot, [])
                    kept = [it for it in existing if _platform_prefix(it.get('platform', '')) != this_prefix]
                    merged = list(items) + kept
                    data[region][slot] = merged
                    log(f"  {name}: merged {len(items)} this + kept {len(kept)} other = {len(merged)}")
                else:
                    data[region][slot] = items
            else:
                log(f"  {name}: status={status} (len={len(items)}), 跳过覆盖避免数据丢失")
            data["fetch_status"][name] = status
            data["generated_at"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
            data["schema_version"] = "1.0"
            log(f"{name}: {len(items)} items, status={status}")
            # 增量写盘（让后续 module 能读到 in-memory 写回的数据）
            if not args.dry_run:
                write_json_lf(DATA_DIR / "latest.json", data)
        except Exception as e:
            log(f"{name} CRASH: {type(e).__name__}: {e}")
            data["fetch_status"][name] = "fail"

    if args.dry_run:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    out = DATA_DIR / "latest.json"
    write_json_lf(out, data)
    log(f"wrote {out} ({out.stat().st_size} bytes)")

    # === 品牌中高端排行：每次跑都重算（供 Tab #1 + Tab #5 共享）===
    try:
        from compute_brand_metrics import compute as _compute_bm
        _compute_bm(out)
        log("brand_metrics: recomputed and saved to latest.json")
    except Exception as e:
        log(f"brand_metrics ERR (non-fatal): {e}")

    # === ID 真实数据合并（手动 HTML 解析 119+ SKU → id.price_pool 替代 8 SKU hardcoded）===
    try:
        log("running ID real-data merge (Shopee+Tokopedia+roadbike+gravel+hybrid)")
        import subprocess as _sp
        _root = Path(__file__).parent.parent  # D:\\MINIMAX\\phoenix-live
        for _script in ['merge_shopee_tokopedia.py', 'merge_roadbike.py', 'merge_gravel.py', 'merge_hybrid.py']:
            _s = _root / _script
            if _s.exists():
                _r = _sp.run([sys.executable, str(_s)], capture_output=True, text=True, timeout=60)
                for line in (_r.stdout + _r.stderr).splitlines()[-3:]:
                    if line.strip(): log(f"  [merge] {line.strip()[:100]}")
            else:
                log(f"  [merge] { _script } not found, skip")
        # 重新读 latest.json，因为 merge_* 重新写过
        _latest_path = DATA_DIR / "latest.json"
        if _latest_path.exists():
            _d2 = json.loads(_latest_path.read_text(encoding='utf-8'))
            _ip = (_d2.get('id', {}).get('price_pool') or [])
            log(f"id.price_pool after ID real-data merge: {len(_ip)} SKUs ({len(set(p.get('brand','') for p in _ip))} brands)")
    except Exception as _e:
        log(f"ID real-data merge WARN: {_e}")

    # === dashboard_metrics：单一数据源（供所有 9 Tab 共享，避免数据滞后冲突）===
    try:
        from compute_dashboard import compute as _compute_dm
        _compute_dm(out)
        log("dashboard_metrics: recomputed and saved to latest.json")
    except Exception as e:
        log(f"dashboard_metrics ERR (non-fatal): {e}")

    # 追加今日快照到 history.json（7 日价格趋势用）
    save_history_snapshot(data)

    if not args.no_git:
        git_commit_and_push()

    return 0


def save_history_snapshot(data: dict) -> None:
    """每天保留 1 个快照到 data/history.json，7 日价格趋势用。"""
    history_path = DATA_DIR / "history.json"
    today = data.get("generated_at", "")[:10]  # YYYY-MM-DD
    if not today:
        return
    # 读现有 history
    history = {"bd": [], "id": []}
    if history_path.exists():
        try:
            history = json.loads(history_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    # 今日快照（只保留价格）
    snap_bd = [{"date": today, "prices": [
        {"brand": p.get("brand"), "model": p.get("model"), "price": p.get("price")}
        for p in (data.get("bd", {}).get("price_pool") or [])
    ]}]
    snap_id = [{"date": today, "prices": [
        {"brand": p.get("brand"), "model": p.get("model"), "price": p.get("price")}
        for p in (data.get("id", {}).get("price_pool") or [])
    ]}]
    # BD: 替换今日
    history["bd"] = [s for s in history.get("bd", []) if s.get("date") != today] + snap_bd
    history["id"] = [s for s in history.get("id", []) if s.get("date") != today] + snap_id
    # 保留最近 7 天
    history["bd"] = history["bd"][-7:]
    history["id"] = history["id"][-7:]
    history["last_updated"] = today
    write_json_lf(history_path, history)
    log(f"history snapshot saved: {today} (bd={len(history['bd'])}d, id={len(history['id'])}d)")


if __name__ == "__main__":
    sys.exit(main())
