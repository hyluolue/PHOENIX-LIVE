// Phoenix V2.7 数据质量门渲染器（共享 JS · 所有 9 Tab 引用）
// 依赖：latest.json#data_quality 块（由 crawler/data_quality_gate.py 写入）
//
// 使用：
//   <script src="./render_quality_gate.js"></script>
//   <script>renderQualityGate(data);</script>  // data 是 latest.json 解析后对象

(function() {
  const GATE_LEVEL = {
    green:  { emoji: '🟢', label: '数据完整 · 可信',        color: '#2e7d32', bg: '#e8f5e9' },
    yellow: { emoji: '🟡', label: '数据部分 · 部分降级',    color: '#e65100', bg: '#fff8e1' },
    red:    { emoji: '🔴', label: '数据失真 · 不可信',      color: '#c8102e', bg: '#ffebee' }
  };

  const SAFE_TIPS = {
    green:  '所有 VPN 依赖模块已通 · 数据规模达预期 · 可放心基于 dashboard 决策',
    yellow: '部分数据失真 · 数据驱动模块已降级显示 · 建议打开 VPN 后刷新',
    red:    'VPN 未开或核心模块失败 · BD pool/ID pool/Phoenix SKU 严重残缺 · 不要基于此 dashboard 做营销判断'
  };

  function render(data) {
    const dq = (data && data.data_quality) || null;
    if (!dq) {
      console.warn('[quality-gate] data_quality 块缺失，请先跑 data_quality_gate.py');
      return;
    }

    const level = dq.level || 'red';
    const cfg = GATE_LEVEL[level] || GATE_LEVEL.red;
    const reasons = (dq.reasons || []);
    const recommendations = (dq.recommendations || []);
    const stats = dq.stats || {};
    const evaluatedAt = dq.evaluated_at || '';

    // === 信号灯 banner ===
    const banner = document.createElement('div');
    banner.className = 'quality-gate ' + level;
    banner.id = 'quality-gate-' + level;
    banner.setAttribute('data-quality-level', level);
    banner.innerHTML = `
      <div class="qg-emoji">${cfg.emoji}</div>
      <div class="qg-text">
        <strong>数据质量门: ${cfg.label}</strong> · ${SAFE_TIPS[level]}
        <small>评估时间: ${evaluatedAt}</small>
        <div class="qg-detail" id="qg-detail-${level}">
          <b>📊 当前数据规模:</b>
          · BD pool: ${stats.bd_count || 0} SKU
          · ID pool: ${stats.id_count || 0} SKU
          · Phoenix: ${stats.phoenix_sku || 0} SKU
          · 25K+ 高端: ${stats.gt_25k_total || 0} SKU
          · VPN 模块: dreamcycle_vpn=${stats.vpn_modules?.dreamcycle_vpn ? '✅' : '❌'}, serbasepeda=${stats.vpn_modules?.serbasepeda ? '✅' : '❌'}
          ${reasons.length ? '<br><b>❌ 问题:</b><br>' + reasons.map(r => '· ' + esc(r)).join('<br>') : ''}
          ${recommendations.length ? '<br><b>💡 建议:</b><br>' + recommendations.map(r => '· ' + esc(r)).join('<br>') : ''}
        </div>
      </div>
      <span class="qg-toggle" onclick="document.getElementById('qg-detail-${level}').classList.toggle('open')">详情 ▾</span>
    `;

    // 插到 body 最前面（每个 Tab 顶部都看得到）
    document.body.insertBefore(banner, document.body.firstChild);

    // === 数据失真模块降级处理 ===
    if (level === 'red' || level === 'yellow') {
      // 1. 标记关键数据驱动模块降级
      const degrades = [
        'dashboard-totals',        // BD pool 总量
        'gt-25k-top5',              // 25K+ 高端榜
        'phx-gap-analysis',         // Phoenix 差距分析
        'competitive-rankings',     // 竞品品牌排行
        'id-vacuum-analysis',       // ID 真空分析
      ];
      degrades.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('dq-degraded');
      });

      // 2. 弹一次性警告（仅 RED 时弹，yellow 不弹）
      if (level === 'red' && !window.sessionStorage.getItem('dq-warn-shown')) {
        const warn = document.createElement('div');
        warn.style.cssText = 'position:fixed;top:60px;right:20px;background:#c8102e;color:#fff;padding:14px 18px;border-radius:8px;z-index:9999;max-width:320px;font-size:13px;box-shadow:0 4px 12px rgba(0,0,0,.3);line-height:1.6';
        warn.innerHTML = `
          <b>🚨 数据失真警告</b><br>
          当前数据严重残缺（VPN 未开）<br>
          <span style="font-size:11.5px;opacity:.9">已为数据驱动模块加红框蒙版 · 不要基于此 dashboard 做营销判断 · 打开 VPN 后重启跑</span>
          <div style="text-align:right;margin-top:6px"><a href="#" onclick="this.parentNode.parentNode.remove();return false" style="color:#fff;text-decoration:underline;font-size:12px">知道了</a></div>
        `;
        document.body.appendChild(warn);
        window.sessionStorage.setItem('dq-warn-shown', '1');
        setTimeout(() => warn.remove(), 12000);
      }
    }
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  window.renderQualityGate = render;
})();