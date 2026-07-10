"""dashboard_metrics 单一数据源计算器
所有 9 Tab 都从这里读 KPI/真空/品牌排行
避免 Tab 间数据滞后冲突

输出到 latest.json#dashboard_metrics
"""
import json
import datetime
from pathlib import Path

DATA_LATEST = Path(__file__).parent.parent / "data" / "latest.json"

EXCLUDED = ['kid','baby','child','folding','bmx','stunt','helmet','lamp','light','bracket','fender','bell','lock','bottle','bag','carrier','pump','sticker','seat post','chain','pedal','grip','saddle','tire','tyre','tube','spoke','handle','bar end','glove','wear','jacket','mirror','pannier','rack','spinning','statif','treadmill','kardio','elliptical','recumbent','latis','fitnes','sepeda statis','orbitrack','treadmil']


def is_mid_high(it):
    """中高端整车：BD ≥ 5K BDT + 排除白牌/童车/折叠/电动/配件
    注意：不限 30K 上限 —— 真实顶价（Rockrider 65K / Magpy 38K）保留
    """
    if (it.get('brand') or '').lower() == 'generic': return False
    p = it.get('price') or 0
    if p < 5000: return False
    m = ((it.get('model') or '') + ' ' + (it.get('brand') or '')).lower()
    return not any(kw in m for kw in EXCLUDED)


def compute(latest_path=DATA_LATEST):
    p = Path(latest_path)
    d = json.loads(p.read_text(encoding='utf-8'))

    # 合并所有 BD 数据源：bd.price_pool (daraz) + dreamcycle_vpn + reviews
    pool = list(d['bd']['price_pool'])  # daraz 主池
    # 加入 dreamcycle_vpn 抓的数据（藏在哪里？看实际路径）
    # 关键：用户验证过 dreamcycle_vpn 抓到 113 SKU，必须并入
    if d.get('bd', {}).get('dreamcycle_pool'):
        pool.extend(d['bd']['dreamcycle_pool'])

    # ID 池：id.price_pool + serbasepeda（serbasepeda 不在 id.price_pool 里？查一下）
    id_pool = list(d.get('id', {}).get('price_pool', []))
    # 如果 id.brand_pool 或 id.serbasepeda_pool 存在，也并入
    if d.get('id', {}).get('serbasepeda_pool'):
        id_pool.extend(d['id']['serbasepeda_pool'])

    # === 1. 中高端池（统一口径）===
    mh = [it for it in pool if is_mid_high(it)]

    # === 2. 价段分布 ===
    bands = {
        'bd_lt_10k': [it for it in mh if (it.get('price') or 0) < 10000],
        'bd_10_15k': [it for it in mh if 10000 <= (it.get('price') or 0) < 15000],
        'bd_15_25k': [it for it in mh if 15000 <= (it.get('price') or 0) < 25000],
        'bd_25_30k': [it for it in mh if 25000 <= (it.get('price') or 0) < 30000],
    }
    bands['bd_gt_25k'] = [it for it in pool if (it.get('price') or 0) >= 25000 and is_mid_high(it)]
    bands['bd_gt_30k'] = [it for it in pool if (it.get('price') or 0) > 30000 and is_mid_high(it)]

    from collections import Counter

    def band_summary(items):
        brands = Counter(it.get('brand', '?') for it in items)
        return {
            'count': len(items),
            'brands_count': len(brands),
            'brands': dict(brands.most_common()),
            'top_5_brands': [b for b, _ in brands.most_common(5)],
        }

    # === 3. Phoenix BD 真实定位 ===
    phx = [it for it in mh if (it.get('brand') or '').lower() == 'phoenix']
    phx_all = [it for it in pool if (it.get('brand') or '').lower() == 'phoenix' and (it.get('price') or 0) > 0]
    phx_asp = round(sum(it['price'] for it in phx) / len(phx)) if phx else 0
    phx_max = max((it['price'] for it in phx), default=0)
    phx_min = min((it['price'] for it in phx), default=0)
    phx_in_15_25 = sum(1 for it in phx if it['price'] >= 15000)
    phx_in_gt_25 = sum(1 for it in phx if it['price'] >= 25000)

    # === 4. 行业顶价 + 对比（排除 Generic 白牌 + 只算中高端）===
    real_pool = [it for it in pool if (it.get('brand') or '').lower() != 'generic']
    industry_top = max((it['price'] for it in real_pool), default=0)
    industry_top_brand = next((it.get('brand') for it in real_pool if it.get('price') == industry_top), '?')
    industry_top_model = next((it.get('model') for it in real_pool if it.get('price') == industry_top), '?')

    # === 5. 行业 ≥ 25K 品牌分布（多品牌）===
    gt_25k_brands = Counter(it.get('brand', '?') for it in bands['bd_gt_25k'])
    gt_25k_top_brands = dict(gt_25k_brands.most_common(10))

    # === 6. 行业 ≥ 25K 顶价 TOP 5 ===
    gt_25k_top_items = sorted(bands['bd_gt_25k'], key=lambda x: -x['price'])[:5]
    gt_25k_top5 = [{'brand': it.get('brand'), 'model': it.get('model'), 'price': it.get('price')} for it in gt_25k_top_items]

    # === 7. Phoenix 真空/缺席判断 ===
    phx_gap = {
        'phx_max_price': phx_max,
        'phx_min_price': phx_min,
        'phx_asp': phx_asp,
        'phx_count': len(phx),
        'phx_in_15_25': phx_in_15_25,
        'phx_in_gt_25': phx_in_gt_25,
        'industry_max_price': industry_top,
        'industry_max_brand': industry_top_brand,
        'industry_max_model': industry_top_model,
        'phx_vs_industry_ratio': round(industry_top / phx_max, 1) if phx_max > 0 else 0,
        # 真空判断
        'gt_25k_count': len(bands['bd_gt_25k']),
        'gt_25k_brand_count': len(gt_25k_brands),
        'gt_25k_brands': list(gt_25k_brands.keys()),
        'gt_25k_phx_present': phx_in_gt_25 > 0,
        'gt_15_25k_count': len(bands['bd_15_25k']),
        'gt_15_25k_phx_present': phx_in_15_25 > 0,
    }

    # === 8. ID 真空判断 ===
    id_mid_high = [it for it in id_pool if 7e6 <= (it.get('price') or 0) < 15e6]
    id_brands = [it.get('brand') for it in id_mid_high]

    # === 8.1 V2.6.1 ID 品类 × 价段 真空判断 (修复 dashboard 失真, 2026-07-10) ===
    # 品类分类 (与 id/matrix.html#catOf 完全一致, 避免跨 Tab 数据失真)
    def _id_cat(it):
        m = ((it.get('model') or '') + ' ' + (it.get('brand') or '')).lower()
        if 'gravel' in m or 'frc' in m: return 'gravel'
        if 'hybrid' in m or 'city' in m or 'rochester' in m or 'junior' in m: return 'hybrid'
        if 'road' in m or 'racer' in m or 'balap' in m: return 'road'
        return 'mtb'

    # 排除健身车 (与 index.html JS 一致)
    def _is_bicycle(it):
        t = ((it.get('model') or '') + ' ' + (it.get('brand') or '')).lower()
        return not any(kw in t for kw in ['sepeda statis', 'treadmill', 'spinning', 'kardio', 'elliptical', 'recumbent'])

    id_bicycles = [it for it in id_pool if _is_bicycle(it) and (it.get('price') or 0) > 0]

    # ID 全价段 (4 段, 含品牌清单, 用于 dashboard 透明度)
    id_bands_full = {
        'id_lt_1m':  [it for it in id_bicycles if (it.get('price') or 0) < 1e6],
        'id_1_7m':   [it for it in id_bicycles if 1e6 <= (it.get('price') or 0) < 7e6],
        'id_7_15m':  [it for it in id_bicycles if 7e6 <= (it.get('price') or 0) < 15e6],
        'id_15_20m': [it for it in id_bicycles if 15e6 <= (it.get('price') or 0) < 20e6],
        'id_gt_20m': [it for it in id_bicycles if (it.get('price') or 0) >= 20e6],
    }

    # 品类 × 价段 (V2.6.1 三蓝海 + 高端)
    id_cat_x_band = {}
    for cat in ['road', 'gravel', 'hybrid', 'mtb']:
        cat_items = [it for it in id_bicycles if _id_cat(it) == cat]
        id_cat_x_band[cat] = {
            'count': len(cat_items),
            '1_7m':  [it for it in cat_items if 1e6 <= (it.get('price') or 0) < 7e6],
            '7_15m': [it for it in cat_items if 7e6 <= (it.get('price') or 0) < 15e6],
            'gt_20m': [it for it in cat_items if (it.get('price') or 0) >= 20e6],
        }
    # Roadbike 12-15M 段单独 (V2.6.1 主推价位)
    id_cat_x_band['road']['12_15m'] = [it for it in id_bicycles if _id_cat(it) == 'road' and 12e6 <= (it.get('price') or 0) < 15e6]

    def _cat_band_summary(items):
        return {
            'count': len(items),
            'brands': list(set((it.get('brand') or '?') for it in items)),
        }

    # === 9. V2 战略大单品数据支撑 ===
    strategy_v2 = {
        'bd_22k_uci_mtb': {
            'rationale': f'BD 15-25K {len(bands["bd_15_25k"])} SKU {band_summary(bands["bd_15_25k"])["brands_count"]} 品牌，Phoenix 缺席；> 25K {len(bands["bd_gt_25k"])} SKU {len(gt_25k_brands)} 品牌 = Rockrider/Veloce/Core 主导',
            'target_price': '22K-25K BDT',
            'top_competitors_gt_25k': gt_25k_top5,
        },
        'id_thunder_id_mtb': {
            'rationale': f'ID 7-15M {len(id_mid_high)} SKU 品牌 {id_brands}，无 SGS 中国品牌',
            'target_price': 'Rp 9.5M',
            'id_competitors': list(set(id_brands)),
        },
        'bd_road_bike': {
            'rationale': 'BD 17 品牌 公路车品类仅 Hero 1 SKU = 真空',
            'target_price': '13K-15K BDT',
        },
    }

    # === 10. totals ===
    totals = {
        'bd_pool_total': len(pool),
        'bd_pool_priced': sum(1 for it in pool if (it.get('price') or 0) > 0),
        'bd_pool_mid_high': len(mh),
        'bd_pool_brands': len(set(it.get('brand', '?') for it in pool if (it.get('brand') or '').lower() != 'generic')),
        'id_pool_total': len(id_pool),
        'id_pool_brands': len(set(it.get('brand', '?') for it in id_pool)),
        'phx_bd_total': len(phx_all),
        'phx_bd_mid_high': len(phx),
        'phx_bd_asp': phx_asp,
        'phx_bd_max': phx_max,
        'phx_bd_min': phx_min,
    }

    dashboard = {
        'computed_at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
        'totals': totals,
        'bands': {k: band_summary(v) for k, v in bands.items() if k in ('bd_lt_10k', 'bd_10_15k', 'bd_15_25k', 'bd_gt_25k')},
        'gt_25k_brands': gt_25k_top_brands,
        'gt_25k_top5': gt_25k_top5,
        'phx_gap': phx_gap,
        'id_7_15m': {
            'count': len(id_mid_high),
            'brands': list(set(id_brands)),
        },
        # V2.6.1 ID 全价段分布 (用于 dashboard 透明度 - 不再 "1 SKU 完全真空" 失真)
        'id_bands_full': {
            band: {
                'count': len(items),
                'brands': list(set((it.get('brand') or '?') for it in items)),
            }
            for band, items in id_bands_full.items()
        },
        # V2.6.1 ID 品类 × 价段 (三蓝海品类 真空识别, 修复 dashboard 失真)
        'id_cat_x_band': {
            cat: {
                'count': info['count'],
                '1_7m_count': len(info['1_7m']),
                '7_15m_count': len(info['7_15m']),
                'gt_20m_count': len(info['gt_20m']),
                '7_15m_brands': list(set((it.get('brand') or '?') for it in info['7_15m'])),
                'gt_20m_brands': list(set((it.get('brand') or '?') for it in info['gt_20m'])),
                **({'12_15m_count': len(info['12_15m'])} if cat == 'road' else {}),
            }
            for cat, info in id_cat_x_band.items()
        },
        # V2.6.1 简洁别名 (Tab 展示用)
        'id_road_bike_12_15m': {
            'count': len(id_cat_x_band['road']['12_15m']),
            'brands': list(set((it.get('brand') or '?') for it in id_cat_x_band['road']['12_15m'])),
        },
        'id_gravel_7_15m': {
            'count': len(id_cat_x_band['gravel']['7_15m']),
            'brands': list(set((it.get('brand') or '?') for it in id_cat_x_band['gravel']['7_15m'])),
        },
        'id_hybrid_7_15m': {
            'count': len(id_cat_x_band['hybrid']['7_15m']),
            'brands': list(set((it.get('brand') or '?') for it in id_cat_x_band['hybrid']['7_15m'])),
        },
        'id_road_bike_gt_20m': {
            'count': len(id_cat_x_band['road']['gt_20m']),
            'brands': list(set((it.get('brand') or '?') for it in id_cat_x_band['road']['gt_20m'])),
        },
        'id_top10_brands': d.get('id', {}).get('brand_pool', []),
        'id_channels': d.get('id', {}).get('channels', []),
        'id_high_end_competitors': [
            {'brand': 'Patrol', 'note': '高端 MTB · 8M-30M+ · V2 25K+ 真竞品', 'roda_link': False},
            {'brand': 'Polygon', 'note': '国际品牌 · 5M-30M+ · MTB/公路/电助力全覆盖', 'roda_link': True},
            {'brand': 'Element', 'note': '折叠/城市休闲/砾石 · 5M-26M · 折叠子品类可切入', 'roda_link': True},
        ],
        'strategy_v2': strategy_v2,
        'data_consistency': {
            'source': 'data/latest.json#bd.price_pool + id.price_pool + brand_metrics',
            'excluded_keywords': EXCLUDED,
            'mid_high_filter': 'BD 5K-30K BDT + 排除童车/折叠/电动/配件',
            'gt_25k_definition': 'price >= 25000 BDT (含中高端池外)',
        },
    }

    d['dashboard_metrics'] = dashboard
    d['gen_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    d['generated_at'] = d['gen_at']

    raw = json.dumps(d, ensure_ascii=False, indent=2)
    if '\r\n' in raw: raw = raw.replace('\r\n', '\n')
    p.write_bytes(raw.encode('utf-8'))
    return dashboard


if __name__ == '__main__':
    m = compute()
    print(f'dashboard_metrics computed:')
    print(f'  totals: {m["totals"]}')
    print(f'  phx_gap: phx_max={m["phx_gap"]["phx_max_price"]} | industry_max={m["phx_gap"]["industry_max_price"]} ({m["phx_gap"]["industry_max_brand"]})')
    print(f'  > 25K: {m["phx_gap"]["gt_25k_count"]} SKU {m["phx_gap"]["gt_25k_brand_count"]} brands: {m["phx_gap"]["gt_25k_brands"]}')
    print(f'  bands.bd_15_25k: {m["bands"]["bd_15_25k"]["count"]} SKU {m["bands"]["bd_15_25k"]["brands_count"]} brands')
    print(f'  bands.bd_gt_25k: {m["bands"]["bd_gt_25k"]["count"]} SKU {m["bands"]["bd_gt_25k"]["brands_count"]} brands')
