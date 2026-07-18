# -*- coding: utf-8 -*-
"""替换 daily-report.html 的 renderMarketCapacity 函数"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
FILE = Path("D:/MINIMAX/phoenix-live/daily-report.html")
text = FILE.read_text(encoding="utf-8")

START = "function renderMarketCapacity(elId, DATA, region) {"
# 找匹配的结束：下一个 } 在 renderSocial 之前的 }
# 简单办法：从 START 开始，按行扫描直到 "function renderSocial"
END = "function renderSocial(posts) {"

start_idx = text.find(START)
if start_idx < 0:
    print("[ERR] START not found"); sys.exit(1)
end_idx = text.find(END, start_idx)
if end_idx < 0:
    print("[ERR] END not found"); sys.exit(1)
# end_idx 指向 "function renderSocial" — 我们要替换到 end_idx 之前
# 旧函数最后是 "}\n\n" — 找最后一个 }
# 简单：从 end_idx 往前找 "}"
# 但更稳：找 "}\n\n" 或 "}\n" 然后往前
old_section = text[start_idx:end_idx].rstrip()
# 去掉结尾的 }
if old_section.endswith("}"):
    old_section = old_section[:-1].rstrip()
print(f"[INFO] old section length: {len(old_section)}")
print(f"[INFO] first 200: {old_section[:200]}")
print(f"[INFO] last 200: {old_section[-200:]}")

NEW_FUNC = '''function renderMarketCapacity(elId, DATA, region) {

  // V2.9.x 兼容 (2026-07-18): dashboard_metrics 结构从 V2.7.2 的 totals/bands/phx_gap
  // 简化为 bd/id/global. 实时从 price_pool 数组计算所需字段 (不再依赖缺失的 dm.totals).
  const dm = DATA.dashboard_metrics || {};
  const isBD = region === 'BD';

  // V2.9.x 新字段优先, 老字段 fallback
  const dmBD = dm.bd || {};
  const dmID = dm.id || {};
  const totalsOld = dm.totals || {};
  const bandsOld = dm.bands || {};
  const phxGapOld = dm.phx_gap || {};
  const idInfoOld = dm.id_7_15m || {};

  const pool = isBD
    ? ((DATA.bd && DATA.bd.price_pool) || [])
    : ((DATA.id && DATA.id.price_pool) || []);

  // 实时计算 brand_metrics (fallback)
  const realBrands = dmBD.real_brands || dmID.real_brands
    || [...new Set(pool.map(p => (p.brand || '').trim()).filter(b => b && b.toLowerCase() !== 'generic'))].length;
  const totalSku = dmBD.total_sku || dmID.total_sku || pool.length;

  // 实时计算 Phoenix 占比 (BD)
  const phxItems = pool.filter(p => (p.brand || '').toLowerCase() === 'phoenix');
  const phxSku = phxItems.length;
  const phxAsp = phxItems.length ? Math.round(phxItems.reduce((s, p) => s + (p.price || 0), 0) / phxItems.length) : 0;
  const phxMaxPrice = phxItems.length ? Math.max(...phxItems.map(p => p.price || 0)) : 0;

  // 实时计算 bands (BD 价位带)
  const bdBands = isBD ? {
    bd_lt_10k: { count: pool.filter(p => p.price >= 5000 && p.price < 10000).length },
    bd_10_15k: { count: pool.filter(p => p.price >= 10000 && p.price < 15000).length },
    bd_15_25k: { count: pool.filter(p => p.price >= 15000 && p.price < 25000).length },
    bd_gt_25k: { count: pool.filter(p => p.price >= 25000).length },
  } : {};
  // 合并 V2.7.2 老 bands 字段 (如果有)
  ['bd_lt_10k', 'bd_10_15k', 'bd_15_25k', 'bd_gt_25k'].forEach(k => {
    if (bandsOld[k]) bdBands[k] = Object.assign({}, bdBands[k], bandsOld[k]);
  });

  // 实时计算 phx_gap
  const allPrices = pool.map(p => p.price).filter(x => x > 0);
  const industryMax = allPrices.length ? Math.max(...allPrices) : 0;
  const phxGap = {
    industry_max_price: phxGapOld.industry_max_price || industryMax,
    industry_max_brand: phxGapOld.industry_max_brand || 'N/A',
    phx_max_price: phxGapOld.phx_max_price || phxMaxPrice,
  };

  // 实时计算 ID 7-15M
  const id7to15Items = pool.filter(p => p.price >= 7e6 && p.price < 15e6);
  const id7to15Brands = [...new Set(id7to15Items.map(p => p.brand))];
  const idInfo = {
    count: idInfoOld.count || id7to15Items.length,
    brands: idInfoOld.brands || id7to15Brands,
  };

  // 总数 (KPI 用) - 兼容老字段
  const totalSkuDisplay = totalsOld.bd_pool_total || (isBD ? totalSku : totalsOld.id_pool_total) || totalSku;
  const realBrandsDisplay = totalsOld.bd_pool_brands || (isBD ? realBrands : totalsOld.id_pool_brands) || realBrands;
  const phxSkuDisplay = totalsOld.phx_bd_mid_high || phxSku;
  const phxAspDisplay = totalsOld.phx_bd_asp || phxAsp;

  // KPI 顶部
  let kpiHtml = '';
  if (isBD) {
    kpiHtml = `<div class="kpi-grid" style="margin-bottom:10px">
      <div class="kpi"><div class="label">总 SKU</div><div class="value cyan">${totalSkuDisplay}</div><div class="delta">含 Generic 已剔除</div></div>
      <div class="kpi"><div class="label">真品牌数</div><div class="value green">${realBrandsDisplay}</div><div class="delta">不含白牌</div></div>
      <div class="kpi"><div class="label">Phoenix BD</div><div class="value yellow">${phxSkuDisplay} SKU</div><div class="delta">${phxAspDisplay.toLocaleString()} ASP</div></div>
      <div class="kpi"><div class="label">Phoenix 顶价</div><div class="value">${phxMaxPrice.toLocaleString()}</div><div class="delta">行业顶价 ${industryMax.toLocaleString()}</div></div>
    </div>`;
  } else {
    kpiHtml = `<div class="kpi-grid" style="margin-bottom:10px">
      <div class="kpi"><div class="label">ID 整车 SKU</div><div class="value cyan">${totalSkuDisplay}</div><div class="delta">Shopee+Tokopedia+4 子品类合并</div></div>
      <div class="kpi"><div class="label">ID 真品牌数</div><div class="value">${realBrandsDisplay}</div><div class="delta">${realBrandsDisplay} 真品牌</div></div>
      <div class="kpi"><div class="label">7-15M 中端</div><div class="value green">${idInfo.count} SKU</div><div class="delta">${(idInfo.brands || []).slice(0, 5).join(' / ')}</div></div>
      <div class="kpi"><div class="label">SGS 中国品牌</div><div class="value yellow" style="color:#c8102e">0</div><div class="delta">真空 = 凤凰切入点</div></div>
    </div>`;
  }

  // 价位带分布
  let bandRows = '';
  if (isBD) {
    const order = ['bd_lt_10k', 'bd_10_15k', 'bd_15_25k', 'bd_gt_25k'];
    const labels = {'bd_lt_10k': '入门 5-10K', 'bd_10_15k': '中端 10-15K', 'bd_15_25k': '中高端 15-25K', 'bd_gt_25k': '高端 25K+'};
    const maxB = Math.max(bdBands.bd_15_25k ? bdBands.bd_15_25k.count : 0, 1);
    order.forEach(k => {
      const b = bdBands[k];
      if (b && b.count > 0) {
        const pct = (b.count / maxB * 100).toFixed(0);
        bandRows += `<div class="trend-row">
          <div class="label">${labels[k]}</div>
          <div class="bar"><div class="bar-fill" style="width:${pct}%"></div></div>
          <div class="count">${b.count} SKU</div>
          <div class="pct">${b.brands_count || '-'} 品牌</div>
        </div>`;
      }
    });
  } else {
    // V2.6.1 ID 真实数据 4 段位
    const idBands = [
      { name: 'Rp 1-7M 入门', lo: 1e6, hi: 7e6 },
      { name: 'Rp 7-15M 中端', lo: 7e6, hi: 15e6 },
      { name: 'Rp 15-25M 中高端', lo: 15e6, hi: 25e6 },
      { name: 'Rp 25M+ 高端', lo: 25e6, hi: 999e6 }
    ];
    const idAll = pool
      .filter(x => x.price > 0)
      .filter(x => x.currency === 'IDR' || x._region === 'ID')
      .filter(x => x.price >= 1e6 && x.price <= 3e7);
    const idMax = Math.max(...idBands.map(b => idAll.filter(p => p.price >= b.lo && p.price < b.hi).length), 1);
    bandRows = idBands.map(b => {
      const inB = idAll.filter(p => p.price >= b.lo && p.price < b.hi);
      const brands = [...new Set(inB.map(p => p.brand))];
      const pct = (inB.length / idMax * 100).toFixed(0);
      return `<div class="trend-row">
      <div class="label">${b.name}</div>
      <div class="bar"><div class="bar-fill" style="width:${pct}%"></div></div>
      <div class="count">${inB.length} SKU</div>
      <div class="pct">${brands.length} 品牌</div>
    </div>`;
    }).join('');
  }

  // 战略洞察
  let insight = '';
  if (isBD) {
    const phxV25 = bdBands.bd_15_25k ? bdBands.bd_15_25k.count : 0;
    const gt25 = bdBands.bd_gt_25k ? bdBands.bd_gt_25k.count : 0;
    const ratio = totalSkuDisplay > 0 ? (phxV25 / totalSkuDisplay * 100).toFixed(0) : 0;
    insight = `<div style="margin-top:10px;padding:10px;background:rgba(46,125,50,.08);border-left:3px solid #2e7d32;font-size:11px;line-height:1.6;color:#1b5e20">
      <b>💎 BD 市场容量关键洞察:</b><br>
      · 15-25K 中高端 ${phxV25} SKU (占总数 ${ratio}%) = 红海集中<br>
      · 25K+ 高端 ${gt25} SKU = <b>真蓝海</b> (行业顶价 ${phxGap.industry_max_price.toLocaleString()} BDT / ${phxGap.industry_max_brand})<br>
      · Phoenix 顶价仅 ${phxMaxPrice.toLocaleString()} BDT, <b>缺席高端 25K+</b>
    </div>`;
  } else {
    const idId25mPlus = pool.filter(x => x.price >= 25e6).length;
    const id7to15 = idInfo.count;
    const id7to15Brands = (idInfo.brands || []).join(' / ') || '本土品牌';
    insight = `<div style="margin-top:10px;padding:10px;background:rgba(46,125,50,.08);border-left:3px solid #2e7d32;font-size:11px;line-height:1.6;color:#1b5e20">
      <b>💎 ID 市场容量关键洞察 (V2.6.1 真实数据):</b><br>
      · <b>${totalSkuDisplay} SKU / ${realBrandsDisplay} 真品牌</b> (Shopee + Tokopedia + roadbike + gravel + hybrid 合并)<br>
      · <b>7-15M 中端 ${id7to15} SKU / ${id7to15Brands}</b> = <b style="color:#2e7d32">V2.6.1 公路+平把+砾石三蓝海切入点 (Phoenix 12-15M 主推)</b><br>
      · 25M+ 高端 <b>${idId25mPlus} SKU</b> = <b style="color:#c8102e">V2.6.1 客户判断 = MTB/折叠/童车 4% 毛利红海 = 永不参与</b> (即使真空也不进)<br>
      · 客户双重身份防火墙: Pacific (客户自有) + Phoenix + FNIX (SNI) 永不直接同品
    </div>`;
  }

  document.getElementById(elId).innerHTML = kpiHtml + bandRows + insight;
}
'''

# 替换
new_text = text[:start_idx] + NEW_FUNC + text[end_idx:]
FILE.write_text(new_text, encoding="utf-8")

print(f"[OK] renderMarketCapacity replaced")
print(f"     old: {len(text)} chars")
print(f"     new: {len(new_text)} chars")
print(f"     diff: {len(new_text) - len(text):+d} chars")
