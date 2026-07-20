"""中高端品牌加权得分（V2.9.47 · 跟前端 V2.9.42 跨 Tab 统一）

公式（V2.9.47 = V2.9.42 跨 Tab 统一）:
score = (sku_count * 0.20) + (asp/30K * 100 * 0.30)
      + (high_tier_pct * 100 * 0.20)
      + (max_price/50K * 100 * 0.20)
      + (in_stock_rate * 100 * 0.10)

- SKU 数量 20%: 覆盖宽度
- ASP 30%: 品牌真实定位（核心权重）
- 高端占比 20%: ≥15K BDT SKU 比例
- 顶价 20%: 价格天花板高度
- 有货率 10%: 市场认可度代理

排除规则（V2.9.42 跟前端一致 = 不限价 + ADULT_KW 黑名单）:
- 不限价 (含 Rockrider 65K / Magpy 38K / Ceres 37K = 行业真实顶价 = 评分用)
- 排除 Generic + 童车 (kid/baby/child/folding/bmx/stunt/16"/20"/boys/girls) + 周边
"""
import json
import datetime
from pathlib import Path

# V2.9.42 跟前端一致的 EXCLUDED (含 16"/20"/boys/girls 童车关键词)
EXCLUDED = [
    # 童车
    'kid', 'kids', 'baby', 'child', 'children', 'boys', 'girls',
    '16"', '20"',
    # 折叠
    'folding', 'foldable',
    # BMX
    'bmx', 'stunt',
    # 周边
    'helmet', 'lamp', 'light', 'bracket', 'fender', 'bell',
    'lock', 'bottle', 'bag', 'carrier', 'pump', 'sticker',
    'seat post', 'chain', 'pedal', 'grip', 'saddle',
    'tire', 'tyre', 'tube', 'spoke', 'handle', 'bar end',
    'glove', 'wear', 'jacket', 'mirror', 'pannier', 'rack',
    # 电动
    'electric', 'e-bike', 'ebike',
]

GENERIC_KEYWORDS = ['sepeda', 'sepada', 'mtb', 'generic', 'bike', 'bicycle', 'bikes',
                    'toko', 'official', 'fixie', 'road', 'roadbike', 'mountain',
                    'gravel', 'hybrid']


def is_generic_brand(b):
    """判断是否为通用/无品牌条目（V2.9.42 跟前端的 isGenericBd 一致）"""
    if not b:
        return True
    return any(kw in b.lower() for kw in GENERIC_KEYWORDS)


def is_adult_bike(it):
    """判断是否为成人整车（V2.9.42 跟前端 isAdultBike 一致）

    跟 is_mid_high 的区别:
    - 不限价 (含 30K+ 高端 = Rockrider 65K = 评分用)
    - 用 ADULT_KW 黑名单过滤童车 (kid/baby/child/folding/bmx/stunt/16"/20"/boys/girls)
    - 排除 Generic 品牌
    """
    brand = (it.get('brand') or '').strip()
    if is_generic_brand(brand):
        return False
    p = it.get('price') or 0
    if p <= 0:
        return False
    m = ((it.get('model') or '') + ' ' + brand).lower()
    return not any(kw in m for kw in EXCLUDED)


def compute(latest_path: str | Path) -> dict:
    """重算 brand_metrics 并写回 latest.json，返回 metrics 字典

    V2.9.47 跟前端 V2.9.42 公式一致:
    - 评分公式 0.20/0.30/0.20/0.20/0.10
    - 不限价（含 30K+ 高端）
    - 过滤 Generic + 童车
    - 行业真实顶价用于评分 (Rockrider 65K)
    """
    latest_path = Path(latest_path)
    d = json.loads(latest_path.read_text(encoding='utf-8'))
    pool = d['bd']['price_pool']

    # 过滤 = 成人整车 (V2.9.42 跟前端一致)
    adult = [it for it in pool if is_adult_bike(it)]

    # 品牌聚合
    brands = {}
    for it in adult:
        b = (it.get('brand') or '').strip()
        if not b:
            continue
        if b not in brands:
            brands[b] = {'skus': [], 'in_stock': 0, 'oos': 0}
        p = it.get('price') or 0
        if p > 0:
            brands[b]['skus'].append(p)
        if it.get('in_stock'):
            brands[b]['in_stock'] += 1
        else:
            brands[b]['oos'] += 1

    # 计算指标 (V2.9.47 跟前端 V2.9.42 公式一致)
    metrics = []
    for b, dd in brands.items():
        skus = dd['skus']
        sku_count = len(skus)
        if sku_count == 0:
            continue
        asp = sum(skus) / sku_count
        max_price = max(skus)
        high_tier_count = sum(1 for p in skus if p >= 15000)
        high_tier_pct = high_tier_count / sku_count
        in_stock_rate = dd['in_stock'] / sku_count

        # V2.9.47 新公式 (跟 V2.9.42 前端 5 Tab 一致)
        sku_score = min(sku_count / 20, 1) * 100 * 0.20
        asp_score = min(asp / 30000, 1) * 100 * 0.30
        high_score = high_tier_pct * 100 * 0.20
        max_score = min(max_price / 50000, 1) * 100 * 0.20
        in_stock_score = in_stock_rate * 100 * 0.10
        score = sku_score + asp_score + high_score + max_score + in_stock_score

        metrics.append({
            'brand': b,
            'sku_count': sku_count,
            'asp': round(asp),
            'max_price': max_price,
            'high_tier_count': high_tier_count,
            'high_tier_pct': round(high_tier_pct * 100),
            'in_stock_rate': round(in_stock_rate * 100),
            'sku_score': round(sku_score, 1),
            'asp_score': round(asp_score, 1),
            'high_score': round(high_score, 1),
            'max_score': round(max_score, 1),
            'in_stock_score': round(in_stock_score, 1),
            'score': round(score, 1)
        })

    # 写回（V2.9.47 公式描述）
    d['brand_metrics'] = {
        'computed_at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
        'method': 'V2.9.47 (跟 V2.9.42 前端 5 Tab 跨 Tab 统一): score = (min(sku/20,1)*100*0.20) + (min(asp/30K,1)*100*0.30) + (high_tier_pct*100*0.20) + (min(max/50K,1)*100*0.20) + (in_stock_rate*100*0.10)',
        'excluded_keywords': EXCLUDED,
        'generic_keywords': GENERIC_KEYWORDS,
        'price_range': '不限价（含 30K+ 高端 = Rockrider 65K / Magpy 38K / Ceres 37K 真实顶价 = 评分用）',
        'total_brands': len(metrics),
        'rankings': sorted(metrics, key=lambda x: -x['score']),
    }
    d['gen_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    d['generated_at'] = d['gen_at']

    raw = json.dumps(d, ensure_ascii=False, indent=2)
    if '\r\n' in raw:
        raw = raw.replace('\r\n', '\n')
    latest_path.write_bytes(raw.encode('utf-8'))
    return d['brand_metrics']


if __name__ == '__main__':
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else 'data/latest.json'
    m = compute(p)
    print(f'V2.9.47 brand_metrics: {m["total_brands"]} brands (跟 V2.9.42 前端 5 Tab 跨 Tab 统一)')
    print('Top 10:')
    for r in m['rankings'][:10]:
        print(f'  {r["brand"]:<14} {r["sku_count"]:>3} SKU · ASP {r["asp"]:>6,} · top {r["max_price"]:>6,} · score {r["score"]}')
