# -*- coding: utf-8 -*-
"""修 daily-report.html:
1. renderBuckets ID 段位: 4 -> 3 (删空段位)
2. renderOpportunities: 加 ID 洞察
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
FILE = Path("D:/MINIMAX/phoenix-live/daily-report.html")
text = FILE.read_text(encoding="utf-8")

# ===================== 1. renderBuckets ID 段位修正 =====================
old_buckets = """    // IDR (印尼盾) - serbasepeda 真实数据：Rp 265K-26.2M

    buckets = [

      { name: '配件 &lt; Rp 1M', lo: 0, hi: 1e6 },

      { name: '入门 Rp 1-7M', lo: 1e6, hi: 7e6 },

      { name: '中端 Rp 7-15M', lo: 7e6, hi: 15e6 },

      { name: '高端 Rp 15M+', lo: 15e6, hi: 9999999 },

    ];"""

new_buckets = """    // V2.9.26 修正: 3 段位 (删空'配件 < 1M'段位, 因为 isMidHighAdult 已 filter 1e6+)
    // IDR (印尼盾) - serbasepeda 真实数据：Rp 1M-30M
    buckets = [

      { name: '入门 Rp 1-7M', lo: 1e6, hi: 7e6 },

      { name: '中端 Rp 7-15M', lo: 7e6, hi: 15e6 },

      { name: '高端 Rp 15M+', lo: 15e6, hi: 9999999 },

    ];"""

if old_buckets in text:
    text = text.replace(old_buckets, new_buckets)
    print("[OK] renderBuckets ID buckets: 4 -> 3 segments")
else:
    print("[ERR] renderBuckets ID buckets: pattern not found")
    # show context
    idx = text.find("IDR (印尼盾)")
    if idx > 0:
        print(f"   found 'IDR (印尼盾)' at offset {idx}")
        print(f"   surrounding 200 chars: {text[idx-50:idx+300]!r}")

# ===================== 2. renderOpportunities 加 ID 洞察 =====================
# 在 "社媒声量" 注释前插入 ID 段
old_social = """  // 社媒声量

  if (social.length) {"""

new_social_with_id = """  // ID 缺口价位 + 缺品牌 (V2.9.26 补)
  const idPrices = id.map(p => p.price).filter(x => x > 0);
  if (idPrices.length) {
    const idBands = {
      '入门 (1-7M)': id.filter(p => p.price >= 1e6 && p.price < 7e6).length,
      '中端 (7-15M)': id.filter(p => p.price >= 7e6 && p.price < 15e6).length,
      '中高端 (15-25M)': id.filter(p => p.price >= 15e6 && p.price < 25e6).length,
      '高端 (25M+)': id.filter(p => p.price >= 25e6).length
    };
    const densestID = Object.entries(idBands).sort((a,b) => b[1] - a[1])[0];
    const idDensestRatio = densestID[1] / idPrices.length;
    // 红海提示
    if (idDensestRatio > 0.3) {
      html.push(`<div class="opp"><strong>🔴 ID 红海价位：</strong>${densestID[0]} 有 ${densestID[1]} SKU（占总数 ${(idDensestRatio*100).toFixed(0)}%），竞品最密集。凤凰需差异化避免价格战。</div>`);
    }
    // 蓝海: 15M+ = 战略蓝海 (高端切入, Phoenix 12-15M / FNIX 18M 主推)
    const id15MPlus = id.filter(p => p.price >= 15e6);
    if (id15MPlus.length > 0 && id15MPlus.length < densestID[1] / 4) {
      const id15Brands = [...new Set(id15MPlus.map(p => p.brand))];
      const id15MaxP = Math.max(...id15MPlus.map(p => p.price || 0));
      html.push(`<div class="opp" style="background:rgba(46,125,50,.1);border-left:3px solid #2e7d32;color:#1b5e20"><strong>💎 ID 蓝海价位：</strong>15M+ 有 ${id15MPlus.length} SKU · ${id15Brands.length} 品牌 · 顶价 ${id15MaxP.toLocaleString()} IDR = <b>FNIX 18M IDR 主战场</b></div>`);
    }
    // ID 缺品牌
    const idKnownBrands = ['Trek', 'Giant', 'Polygon', 'Pacific', 'United', 'Element', 'Polygon'];
    const idBrands = new Set(id.map(p => p.brand));
    const idMissing = idKnownBrands.filter(b => !idBrands.has(b));
    if (idMissing.length) {
      html.push(`<div class="opp warn"><strong>ID 未监测到品牌：</strong>${idMissing.join('、')}。可能市场份额小或不在 Shopee/Tokopedia。</div>`);
    }
  }

  // 社媒声量

  if (social.length) {"""

if old_social in text:
    text = text.replace(old_social, new_social_with_id)
    print("[OK] renderOpportunities: added ID insights")
else:
    print("[ERR] renderOpportunities social marker not found")
    idx = text.find("社媒声量")
    if idx > 0:
        print(f"   found '社媒声量' at offset {idx}")
        print(f"   surrounding 100 chars: {text[idx-50:idx+100]!r}")

FILE.write_text(text, encoding="utf-8")
print(f"\n[OK] daily-report.html updated, size: {FILE.stat().st_size} bytes")
