"""模拟 fix 后的主循环，验证 merge-by-platform 不覆盖"""
import json
from pathlib import Path

LATEST = Path(r'D:\MINIMAX\phoenix-live\data\latest.json')

def _platform_prefix(platform: str) -> str:
    p = (platform or "").lower().strip()
    if not p:
        return ""
    if "(" in p:
        p = p.split("(", 1)[0].strip()
    return p

# Load baseline (190 SKU)
d = json.loads(LATEST.read_text(encoding='utf-8'))
print(f"Baseline BD pool: {len(d['bd']['price_pool'])} SKU")

# 模拟 daraz_bd 跑: 假设抓到 20 个 daraz items
mock_daraz_items = [
    {"brand": "Marine", "model": "Marine X1", "platform": "Daraz BD (MTB)", "price": 18000, "url": "https://daraz.test/marine_x1", "currency": "BDT", "in_stock": True, "is_new": True, "scraped_at": "2026-07-10T09:00:00", "note": "test"},
    {"brand": "Phoenix", "model": "Phoenix 26er", "platform": "Daraz BD (Phoenix)", "price": 14000, "url": "https://daraz.test/phx", "currency": "BDT", "in_stock": True, "is_new": True, "scraped_at": "2026-07-10T09:00:00", "note": "test"},
]

# 应用 fix: merge-by-platform
items = mock_daraz_items
this_prefix = _platform_prefix(items[0].get('platform', ''))
existing = d['bd']['price_pool']
kept = [it for it in existing if _platform_prefix(it.get('platform', '')) != this_prefix]
merged = list(items) + kept
print(f"After daraz_bd mock: {len(items)} new + {len(kept)} kept = {len(merged)}")
# 验证 dreamcycle 仍保留
dreamcycle_kept = [it for it in merged if 'dreamcycle' in (it.get('platform') or '').lower()]
print(f"Dreamcycle items preserved: {len(dreamcycle_kept)}")
assert len(dreamcycle_kept) == 116, f"❌ FAIL: dreamcycle should be 116, got {len(dreamcycle_kept)}"
print("✅ TEST PASSED: daraz_bd merge preserves dreamcycle 116 items")

# 模拟 dreamcycle 跑: 假设抓到 0
mock_dreamcycle_items = [
    {"brand": "Dream", "model": "Dream Test", "platform": "dreamcycle.store", "price": 16000, "url": "https://dreamcycle.test/x", "currency": "BDT", "in_stock": True, "is_new": True, "scraped_at": "2026-07-10T09:00:00", "note": "test"},
]
items = mock_dreamcycle_items
this_prefix = _platform_prefix(items[0].get('platform', ''))
existing = d['bd']['price_pool']
kept = [it for it in existing if _platform_prefix(it.get('platform', '')) != this_prefix]
merged = list(items) + kept
print(f"\nAfter dreamcycle mock: {len(items)} new + {len(kept)} kept = {len(merged)}")
daraz_kept = [it for it in merged if (it.get('platform') or '').startswith('Daraz BD')]
print(f"Daraz items preserved: {len(daraz_kept)}")
assert len(daraz_kept) == 74, f"❌ FAIL: daraz should be 74, got {len(daraz_kept)}"
print("✅ TEST PASSED: dreamcycle merge preserves daraz 74 items")
