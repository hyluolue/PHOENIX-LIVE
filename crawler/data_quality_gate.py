"""Phoenix 数据质量门 (Data Quality Gate) V2.7.2

V2.7.2 修订：模块分级 — 核心 vs 高级 vs 永久挂
- 核心模块（daraz_bd / serbasepeda / news_bd / daraz_bd_reviews）：必通，否则 RED
- 高级模块（dreamcycle_vpn / apify_social）：可选，失败仅 YELLOW
- 企业反爬（shopee_id / tokopedia）：永久挂，不计入评估

阈值（用户验证过的基线）：
- BD 池：完整 ≥ 150（74 daraz + 113 dreamcycle）/ 中等 ≥ 60（仅 daraz）
- ID 池：≥ 4（serbasepeda 8 SKU 持久化）
- Phoenix SKU：≥ 15 完整 / ≥ 5 中等
- 25K+ 高端：≥ 10 完整 / ≥ 1 中等

输出到 latest.json#data_quality 块
"""
import json
import datetime
from pathlib import Path

DATA_LATEST = Path(__file__).parent.parent / "data" / "latest.json"


# ===== 模块分级（V2.7.2）=====
# 核心模块：必通，否则 RED
CORE_MODULES = {
    'daraz_bd':         'BD 主数据源 · Phoenix + Rockrider + Marine + 5 品牌池',
    'serbasepeda':      'ID 整车 8 SKU 持久化 + 印尼真蓝海数据',
    'news_bd':          'BD 市场动态（Sogou news）',
    'daraz_bd_reviews': 'Phoenix BD 用户真实评价（差评驱动 R&D）',
}

# 高级模块：可选，失败降级 YELLOW
PREMIUM_MODULES = {
    'dreamcycle_vpn':   'BD 高端品牌（Rockrider/Veloce/Core/Ceres/Magpy 等）· 需 VPN',
    'apify_social':     '社媒数据（FB/IG 竞品）· 偶发 5xx',
    'news_id':          'ID 市场动态（Sogou news ID）· 偶发失败',
}

# 永久反爬：不计入评估
BLOCKED_MODULES = {
    'shopee_id':        '企业反爬 (PerimeterX)',
    'tokopedia':        '企业反爬 (DataDome)',
}


# ===== 数据规模阈值 =====
POOL_THRESHOLDS = {
    'bd_pool_min_green': 150,
    'bd_pool_min_yellow': 60,
    'id_pool_min_green': 4,
    'id_pool_min_yellow': 4,
    'phoenix_sku_min_green': 15,
    'phoenix_sku_min_yellow': 5,
    'gt_25k_sku_min_green': 10,
    'gt_25k_sku_min_yellow': 1,
}


def evaluate_quality(latest_data):
    """返回 (level, reasons, recommendations, stats)

    V2.7.2 判定逻辑：
    - 核心模块任意一个失败 = RED（致命）
    - 高级模块失败但核心全通 = YELLOW（降级显示）
    - 核心+高级全通 = GREEN（完整）
    """
    fs = latest_data.get('fetch_status', {})

    core_status = {k: ('ok' in str(fs.get(k, '')).lower()) for k in CORE_MODULES}
    premium_status = {k: ('ok' in str(fs.get(k, '')).lower()) for k in PREMIUM_MODULES}

    core_failed = [k for k, v in core_status.items() if not v]
    premium_failed = [k for k, v in premium_status.items() if not v]

    # pool 数量统计
    bd_pool = latest_data.get('bd', {}).get('price_pool', [])
    id_pool = latest_data.get('id', {}).get('price_pool', [])

    bd_count = len(bd_pool)
    id_count = len(id_pool)

    # Phoenix SKU
    bm = latest_data.get('brand_metrics', {})
    rankings = bm.get('rankings', [])
    phx = [b for b in rankings if b.get('brand', '').lower() == 'phoenix']
    phx_count = phx[0].get('sku_count', 0) if phx else 0

    # 25K+ SKU
    dm = latest_data.get('dashboard_metrics', {})
    gt_25k_count = dm.get('gt_25k_brands', {})
    gt_25k_total = sum(gt_25k_count.values()) if isinstance(gt_25k_count, dict) else 0

    # 评估每个问题
    core_reasons = []         # 核心问题（触发 RED）
    premium_reasons = []      # 高级问题（触发 YELLOW）
    recommendations = []

    # 核心模块
    for k in core_failed:
        core_reasons.append(f"❌ 核心模块失败: {k} — {CORE_MODULES[k]}")
        recommendations.append(f"检查 {k} 网络连接 + 重启 cron")

    # 高级模块
    for k in premium_failed:
        premium_reasons.append(f"⚠️ 高级模块失败: {k} — {PREMIUM_MODULES[k]}")

    # pool 数量
    if bd_count < POOL_THRESHOLDS['bd_pool_min_yellow']:
        core_reasons.append(f"BD 池只有 {bd_count} SKU（致命，应 ≥ 60）")
    elif bd_count < POOL_THRESHOLDS['bd_pool_min_green']:
        premium_reasons.append(f"BD 池 {bd_count} SKU（缺 dreamcycle，建议 ≥ 150）")

    if id_count < POOL_THRESHOLDS['id_pool_min_yellow']:
        core_reasons.append(f"ID 池只有 {id_count} SKU（致命，应 ≥ 4）")

    if phx_count < POOL_THRESHOLDS['phoenix_sku_min_yellow']:
        premium_reasons.append(f"Phoenix SKU {phx_count}（dreamcycle 没抓到 = 高端品牌不可见）")
    elif phx_count < POOL_THRESHOLDS['phoenix_sku_min_green']:
        premium_reasons.append(f"Phoenix SKU {phx_count}（建议 ≥ 15）")

    if gt_25k_total < POOL_THRESHOLDS['gt_25k_sku_min_yellow']:
        premium_reasons.append(f"25K+ 高端 SKU {gt_25k_total}（高端市场分析残缺）")

    # ===== 判定级别（V2.7.2 分级）=====
    all_reasons = core_reasons + premium_reasons

    if core_reasons:
        level = 'red'
    elif premium_reasons:
        level = 'yellow'
    else:
        level = 'green'

    return level, all_reasons, recommendations, {
        'core_modules': core_status,
        'premium_modules': premium_status,
        'core_failed': core_failed,
        'premium_failed': premium_failed,
        'bd_count': bd_count,
        'id_count': id_count,
        'phoenix_sku': phx_count,
        'gt_25k_total': gt_25k_total,
    }


def main():
    if not DATA_LATEST.exists():
        print(f"[ERR] latest.json not found: {DATA_LATEST}")
        return

    d = json.loads(DATA_LATEST.read_text(encoding='utf-8'))
    level, reasons, recommendations, stats = evaluate_quality(d)

    emoji = {'green': '🟢', 'yellow': '🟡', 'red': '🔴'}[level]
    print(f"\n{emoji} Data Quality: {level.upper()}")
    print(f"   BD pool: {stats['bd_count']} SKU")
    print(f"   ID pool: {stats['id_count']} SKU")
    print(f"   Phoenix: {stats['phoenix_sku']} SKU")
    print(f"   25K+ SKU: {stats['gt_25k_total']}")
    print(f"   核心模块: {stats['core_failed'] or '全部 OK'}")
    print(f"   高级模块: {stats['premium_failed'] or '全部 OK'}")

    if reasons:
        print(f"\n   问题:")
        for r in reasons:
            print(f"      {r}")

    if recommendations:
        print(f"\n   💡 建议:")
        for r in recommendations:
            print(f"      {r}")

    # 写入 latest.json#data_quality
    d['data_quality'] = {
        'level': level,
        'emoji': emoji,
        'evaluated_at': datetime.datetime.now().isoformat(timespec='seconds'),
        'reasons': reasons,
        'recommendations': recommendations,
        'stats': stats,
        'thresholds': POOL_THRESHOLDS,
        'version': 'V2.7.2',  # 模块分级版
    }

    DATA_LATEST.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n[OK] latest.json#data_quality 已写入 → {level.upper()}")


if __name__ == "__main__":
    main()