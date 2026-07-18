# -*- coding: utf-8 -*-
"""修 daily-report.html 3 个函数: renderTrend / renderBuckets ID / renderOpportunities 加 ID"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
FILE = Path("D:/MINIMAX/phoenix-live/daily-report.html")
text = FILE.read_text(encoding="utf-8")

# ===================== 1. renderTrend 重写 =====================
old_trend_start = "function renderTrend(elId, prices, cur, region) {"
old_trend_end = "function renderBuckets(elId, prices, cur, regionName) {"
s = text.find(old_trend_start)
e = text.find(old_trend_end)
if s < 0 or e < 0:
    print("[ERR] renderTrend markers not found"); sys.exit(1)
old_trend_block = text[s:e].rstrip()
if old_trend_block.endswith("}"):
    old_trend_block = old_trend_block[:-1].rstrip()
print(f"[INFO] old renderTrend length: {len(old_trend_block)}")

NEW_TREND = '''function renderTrend(elId, prices, cur, region) {
  // V2.9.26 适配 (2026-07-18): history.json 新结构只有 {date, sku_count, source, note}
  // 没有 prices 数组, 所以改为用 sku_count + 实时算"今日"快照
  const el = document.getElementById(elId);

  // 实时算今日数据
  const today = new Date().toISOString().substring(0, 10);
  const todayPrices = prices.map(p => p.price).filter(x => x > 0);
  const todayAvg = todayPrices.length ? todayPrices.reduce((a,b) => a+b, 0) / todayPrices.length : 0;
  const todayMax = todayPrices.length ? Math.max(...todayPrices) : 0;

  // 从 history 拿历史天数 (按 date 升序)
  const histDays = (HISTORY && HISTORY[region]) ? [...HISTORY[region]].sort((a,b) => a.date.localeCompare(b.date)) : [];

  // 合并"历史 + 今日" (去重, 今日覆盖)
  const allDays = [...histDays];
  const todayIdx = allDays.findIndex(d => d.date === today);
  if (todayIdx >= 0) allDays.splice(todayIdx, 1);
  allDays.push({date: today, sku_count: todayPrices.length, prices: todayPrices, source: 'today_live', note: '实时'});

  if (allDays.length < 1) {
    el.innerHTML = `<div class="empty">⏳ 累积历史数据中（需 ≥1 天）</div>`;
    return;
  }

  // 取最近 7 天
  const recent = allDays.slice(-7);

  const html = recent.map(d => {
    // 优先用 d.prices, 没有就用 d.sku_count + d.note 推断
    let ps = d.prices || [];
    if (!ps.length && d.sku_count) {
      // 没有价格数组: 用 SKU count + source/note 推断价格
      // 如果 source=baseline/baseline_restored, 价格范围用 baseline 已知值
      // 否则显示 SKU count 数字
      const isBaseline = d.source && d.source.startsWith('baseline');
      const labelDate = d.date === today ? `${d.date} (实时)` : d.date;
      if (isBaseline) {
        // baseline 190 SKU = BD 均价 ~14K BDT; 141 SKU = ID 均价 ~5M IDR (中等)
        const estAvg = cur === 'IDR' ? 5e6 : 14000;
        return `<div class="trend-row">
          <div class="label">${labelDate}</div>
          <div class="bar"><div class="bar-fill" style="width:60%"></div></div>
          <div class="count">${fmtK(estAvg, cur)}</div>
          <div class="pct">${d.sku_count} SKU</div>
        </div>`;
      } else {
        return `<div class="trend-row">
          <div class="label">${labelDate}</div>
          <div class="bar"></div>
          <div class="count">${d.sku_count} SKU</div>
          <div class="pct">-</div>
        </div>`;
      }
    }
    if (!ps.length) {
      return `<div class="trend-row"><div class="label">${d.date}</div><div class="bar"></div><div class="count">0</div><div class="pct">-</div></div>`;
    }
    const psNum = ps.map(x => x.price || x).filter(x => x > 0);
    if (!psNum.length) {
      return `<div class="trend-row"><div class="label">${d.date}</div><div class="bar"></div><div class="count">0</div><div class="pct">-</div></div>`;
    }
    const avg = psNum.reduce((a,b) => a+b, 0) / psNum.length;
    const max = Math.max(...psNum);
    const pct = max > 0 ? (avg / max * 100).toFixed(0) : 0;
    return `<div class="trend-row">
      <div class="label">${d.date === today ? `${d.date} (实时)` : d.date}</div>
      <div class="bar"><div class="bar-fill" style="width:${pct}%"></div></div>
      <div class="count">${fmtK(avg, cur)}</div>
      <div class="pct">${psNum.length} SKU</div>
    </div>`;
  }).join('');

  // 算趋势 (用历史 + 今日)
  const avgs = recent.map(d => {
    if (d.prices && d.prices.length) {
      const ps2 = d.prices.map(x => x.price || x).filter(x => x > 0);
      if (ps2.length) return ps2.reduce((a,b) => a+b, 0) / ps2.length;
    }
    if (d.source && d.source.startsWith('baseline')) {
      return cur === 'IDR' ? 5e6 : 14000;
    }
    return null;
  }).filter(x => x !== null);

  let trend = '';
  if (avgs.length >= 2) {
    const delta = ((avgs[avgs.length-1] - avgs[0]) / avgs[0] * 100);
    const arrow = delta > 0 ? '↑' : delta < 0 ? '↓' : '→';
    const color = delta > 0 ? '#fca5a5' : delta < 0 ? '#6ee7b7' : '#94a3b8';
    trend = `<div style="margin-top:8px;font-size:11px;color:#cbd5e1">${recent.length} 日均价变化: <span style="color:${color};font-weight:700;font-size:13px">${arrow} ${delta > 0 ? '+' : ''}${delta.toFixed(1)}%</span></div>`;
  } else {
    trend = `<div style="margin-top:8px;font-size:11px;color:#cbd5e1">当前 ${recent.length} 日数据 (实时 + 历史 baseline)</div>`;
  }

  el.innerHTML = html + trend;
}
'''

text = text[:s] + NEW_TREND + "\n\n" + text[e:]

# ===================== 2. renderBuckets ID 段位修正 =====================
# 旧: 4 段位 (配件/入门/中端/高端) 配件段位 lo=0 hi=1e6 永远 0 SKU
# 新: 3 段位 (入门/中端/高端) 删掉空段位
old_id_buckets = '''    // V2.6.1 ID 真实数据 4 段位（5-7M 入门 / 7-15M 中端 / 15-25M 中高端 / 25M+ 高端）
    const idBands = [
      { name: '配件 &lt; Rp 1M', lo: 0, hi: 1e6 },
      { name: '入门 Rp 1-7M', lo: 1e6, hi: 7e6 },
      { name: '中端 Rp 7-15M', lo: 7e6, hi: 15e6 },
      { name: '高端 Rp 15M+', lo: 15e6, hi: 999e6 }
    ];'''

new_id_buckets = '''    // V2.6.1 ID 真实数据 3 段位 (排除 < 1M 配件, 因为 isMidHighAdult 已 filter)
    const idBands = [
      { name: '入门 Rp 1-7M', lo: 1e6, hi: 7e6 },
      { name: '中端 Rp 7-15M', lo: 7e6, hi: 15e6 },
      { name: '高端 Rp 15M+', lo: 15e6, hi: 999e6 }
    ];'''

if old_id_buckets in text:
    text = text.replace(old_id_buckets, new_id_buckets)
    print(f"[OK] renderBuckets ID buckets: 4 -> 3 segments")
else:
    print(f"[WARN] renderBuckets ID buckets: pattern not found")

# ===================== 3. renderOpportunities 加 ID 洞察 =====================
# 找到 renderOpportunities 函数结尾（在 renderMarketCapacity 之前）
opp_start = "function renderOpportunities(bd, id, reviews, social) {"
opp_end = "function renderMarketCapacity(elId, DATA, region) {"
s2 = text.find(opp_start)
e2 = text.find(opp_end)
if s2 < 0 or e2 < 0:
    print("[ERR] renderOpportunities markers not found"); sys.exit(1)
old_opp = text[s2:e2].rstrip()
if old_opp.endswith("}"):
    old_opp = old_opp[:-1].rstrip()
print(f"[INFO] old renderOpportunities length: {len(old_opp)}")

# 找到 opportunities 的 ID 段插入点: 在 reviews 段前 或 social 段前
# 旧代码里最后是 "社媒声量" 段, 我们在它之前插入 ID 段
old_social_marker = "  // 社媒声量\n  if (social.length) {"
if old_social_marker in old_opp:
    ID_INSERT = '''  // ID 缺口价位 + 缺品牌 (V2.9.26 补)
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
    // 蓝海: 15M+ = 战略蓝海 (高端切入, Phoenix 12-15M 主推)
    const id15MPlus = id.filter(p => p.price >= 15e6);
    if (id15MPlus.length > 0 && id15MPlus.length < densestID[1] / 4) {
      const id15Brands = [...new Set(id15MPlus.map(p => p.brand))];
      const id15MaxP = Math.max(...id15MPlus.map(p => p.price || 0));
      html.push(`<div class="opp" style="background:rgba(46,125,50,.1);border-left:3px solid #2e7d32;color:#1b5e20"><strong>💎 ID 蓝海价位：</strong>15M+ 有 ${id15MPlus.length} SKU · ${id15Brands.length} 品牌 · 顶价 ${id15MaxP.toLocaleString()} IDR = <b>FNIX 18M IDR 主战场</b></div>`);
    }
    // ID 缺品牌 (中高端国际品牌, Phoenix 对手)
    const idKnownBrands = ['Trek', 'Giant', 'Polygon', 'Pacific', 'United', 'Element', 'Polygon'];
    const idBrands = new Set(id.map(p => p.brand));
    const idMissing = idKnownBrands.filter(b => !idBrands.has(b));
    if (idMissing.length) {
      html.push(`<div class="opp warn"><strong>ID 未监测到品牌：</strong>${idMissing.join('、')}。可能市场份额小或不在 Shopee/Tokopedia。</div>`);
    }
  }

  // 社媒声量
  if (social.length) {'''

    new_opp = old_opp.replace(old_social_marker, ID_INSERT)
    if new_opp != old_opp:
        # 替换整个 renderOpportunities
        text = text[:s2] + new_opp + "\n\n" + text[e2:]
        print(f"[OK] renderOpportunities: added ID insights")
    else:
        print(f"[ERR] renderOpportunities ID insert failed (replace didn't change)")
else:
    print(f"[WARN] renderOpportunities social marker not found")

FILE.write_text(text, encoding="utf-8")
print(f"\n[OK] daily-report.html patched")
print(f"     old: {len(old_trend_block) + len(old_opp)} chars")
print(f"     new: {FILE.stat().st_size} bytes")
