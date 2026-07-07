// Phoenix V2.7.3 数据质量指示器（紧凑版 · 只显示小图标）
// 依赖：latest.json#data_quality 块（由 crawler/data_quality_gate.py 写入）
//
// 使用：
//   <script src="./render_quality_gate.js"></script>
//   <script>renderQualityGate(data);</script>
//
// V2.7.3 修订：只显示一个右上角小圆点 + tooltip，hover 才看详情（不占空间）

(function() {
  const GATE_LEVEL = {
    green:  { dot: '🟢', label: '数据完整 · 可信',  color: '#2e7d32' },
    yellow: { dot: '🟡', label: '数据部分 · 降级',  color: '#e65100' },
    red:    { dot: '🔴', label: '数据失真 · 不可信', color: '#c8102e' }
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

    // === 紧凑指示器（右上角悬浮小圆点 + tooltip）===
    const indicator = document.createElement('div');
    indicator.className = 'quality-indicator ' + level;
    indicator.id = 'quality-indicator';
    indicator.setAttribute('data-quality-level', level);
    indicator.innerHTML = `
      <span class="qi-dot">${cfg.dot}</span>
      <span class="qi-label">${cfg.label}</span>
      <div class="qi-tooltip">
        <div class="qi-tip-header">
          <b>${cfg.dot} ${cfg.label}</b>
          <small>${evaluatedAt}</small>
        </div>
        <div class="qi-tip-body">
          <b>📊 数据规模:</b>
          · BD ${stats.bd_count || 0} / ID ${stats.id_count || 0} / Phoenix ${stats.phoenix_sku || 0} / 25K+ ${stats.gt_25k_total || 0}
          ${stats.core_failed && stats.core_failed.length ? '<br><b>❌ 核心模块失败:</b><br>' + stats.core_failed.map(k => '· ' + k).join('<br>') : ''}
          ${stats.premium_failed && stats.premium_failed.length ? '<br><b>⚠️ 高级模块失败:</b><br>' + stats.premium_failed.map(k => '· ' + k).join('<br>') : ''}
          ${reasons.length ? '<br><b>问题详情:</b><br>' + reasons.slice(0, 5).map(r => '· ' + esc(r)).join('<br>') : ''}
          ${recommendations.length ? '<br><b>💡 建议:</b><br>' + recommendations.slice(0, 3).map(r => '· ' + esc(r)).join('<br>') : ''}
        </div>
      </div>
    `;

    // 插到 body（绝对定位右上角，不占文档流）
    document.body.appendChild(indicator);

    // === 数据失真模块降级处理（仅 RED 时启用）===
    if (level === 'red') {
      const degrades = ['dashboard-totals', 'gt-25k-top5', 'phx-gap-analysis', 'competitive-rankings', 'id-vacuum-analysis'];
      degrades.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('dq-degraded');
      });

      // 一次性警告弹窗
      if (!window.sessionStorage.getItem('dq-warn-shown')) {
        const warn = document.createElement('div');
        warn.style.cssText = 'position:fixed;top:50px;right:20px;background:#c8102e;color:#fff;padding:10px 14px;border-radius:6px;z-index:9999;max-width:280px;font-size:12px;box-shadow:0 4px 12px rgba(0,0,0,.3);line-height:1.5';
        warn.innerHTML = `<b>🚨 数据失真</b> · 核心模块挂了<br><span style="opacity:.9">别用此 dashboard 做营销判断 · 修好核心模块后刷新</span><div style="text-align:right;margin-top:4px"><a href="#" onclick="this.parentNode.parentNode.remove();return false" style="color:#fff;font-size:11px">×</a></div>`;
        document.body.appendChild(warn);
        window.sessionStorage.setItem('dq-warn-shown', '1');
        setTimeout(() => warn.remove(), 8000);
      }
    }
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  window.renderQualityGate = render;
})();