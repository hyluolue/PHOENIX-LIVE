# -*- coding: utf-8 -*-
"""
重写 strategy.html 第 8 节：从"产品策略落地"改为"价值主张决策方法论"
- 删除 8.1-8.7 的所有产品策略细节
- 改为方法论 + 指向 matrix.html 7 节
"""
import io
import re
from pathlib import Path

ROOT = Path("D:/MINIMAX/phoenix-live")
STRATEGY = ROOT / "bd" / "strategy.html"

# 强制 UTF-8 读
text = STRATEGY.read_text(encoding="utf-8")

# 第 8 节起始标志
START = "<!-- V2.9.18-V2.9.23 (2026-07-17): 8. 价值主张迭代 + 4 国差异化 (BD V1+V3+V4 三轴场景差异化) -->"
# 第 8 节结束后的标志（用作切分点）
END_AFTER = "<!-- 4 框架交叉验证（V1 → V2 gap） -->"

# 检查
if START not in text:
    raise SystemExit("[ERR] START not found")
if END_AFTER not in text:
    raise SystemExit("[ERR] END_AFTER not found")

# 切：START 之前 + START 到 END_AFTER 之间的旧 8 节 + END_AFTER 之后
parts = text.split(START, 1)
before, rest = parts[0], parts[1]
end_parts = rest.split(END_AFTER, 1)
# end_parts[0] = 旧 8 节内容（含 START 之后到 END_AFTER 之前）= 要替换
# end_parts[1] = END_AFTER 之后
old_section_body = end_parts[0]  # 整段 8 节 HTML
after_marker = end_parts[1]

# 新 8 节内容（方法论版）
NEW_SECTION = """<!-- V2.9.18-V2.9.23 (2026-07-17): 8. 价值主张决策方法论（理论框架实战 · 6 个方法） -->
<div class="section" style="background:linear-gradient(135deg,rgba(94,234,212,.05) 0%,rgba(33,150,243,.04) 50%,rgba(255,87,34,.04) 100%);border:1px solid rgba(94,234,212,.3);border-left:4px solid #5eead4">
  <h2><span class="flag">🧭</span>8. 价值主张决策方法论 <span class="badge green">理论框架实战 · 2026-07-17</span></h2>
  <div style="font-size:12px;color:#cbd5e1;margin-bottom:14px;line-height:1.7">
    <b style="color:#5eead4">📌 本节定位：</b>理论框架的实战方法论 · 6 个决策方法从 V2.9.18-V2.9.23 提炼<br>
    <b style="color:#fbbf24">📌 产品策略落地（具体选了什么）请看 →</b> <a href="./matrix.html" style="color:#fbbf24">产品矩阵 Tab · 7. 价值主张 V2.9.23</a><br>
    7 天里 Phoenix BD 价值主张从 V1-V5 5 候选 → V1+V3+V4 三轴场景差异化 = 6 个核心方法论共同作用
  </div>

  <!-- 8.1 5 维价值主张评估法 (V5 方法论) -->
  <h3 style="color:#5eead4;font-size:15px;margin:18px 0 10px">🔍 8.1 5 维价值主张评估法 (V2.9.11 V5 升维方法论)</h3>
  <div style="background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.1);padding:12px;border-radius:8px;margin-bottom:12px">
    <div style="font-size:11px;color:#cbd5e1;margin-bottom:10px"><b style="color:#5eead4">方法论：</b>不只看"功能价值"，从 <b>5 个维度</b> 评估每个候选</div>
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:10px">
      <div style="background:rgba(233,30,99,.1);padding:10px;border-radius:6px;border-left:3px solid #e91e63;text-align:center">
        <div style="font-size:11px;font-weight:800;color:#c2185b">1. 情绪价值</div>
        <div style="font-size:10px;color:#cbd5e1;margin-top:2px">千金难买我喜欢</div>
      </div>
      <div style="background:rgba(156,39,176,.1);padding:10px;border-radius:6px;border-left:3px solid #9c27b0;text-align:center">
        <div style="font-size:11px;font-weight:800;color:#6a1b9a">2. 品牌主张</div>
        <div style="font-size:10px;color:#cbd5e1;margin-top:2px">百年民族品牌</div>
      </div>
      <div style="background:rgba(123,31,162,.1);padding:10px;border-radius:6px;border-left:3px solid #7b1fa2;text-align:center">
        <div style="font-size:11px;font-weight:800;color:#4a148c">3. 品牌调性</div>
        <div style="font-size:10px;color:#cbd5e1;margin-top:2px">文化自信</div>
      </div>
      <div style="background:rgba(206,147,216,.1);padding:10px;border-radius:6px;border-left:3px solid #ce93d8;text-align:center">
        <div style="font-size:11px;font-weight:800;color:#6a1b9a">4. 品牌差异</div>
        <div style="font-size:10px;color:#cbd5e1;margin-top:2px">护城河</div>
      </div>
      <div style="background:rgba(251,191,36,.1);padding:10px;border-radius:6px;border-left:3px solid #fbbf24;text-align:center">
        <div style="font-size:11px;font-weight:800;color:#fbbf24">5. 产品溢价</div>
        <div style="font-size:10px;color:#cbd5e1;margin-top:2px">闪电龙年 10万+</div>
      </div>
    </div>
    <div style="background:rgba(94,234,212,.06);border:1px solid rgba(94,234,212,.3);padding:10px;border-radius:6px;margin-bottom:10px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#5eead4">📐 评分公式：</b><br>
        · 5 维各打 0-2 分（0=无/1=弱/2=强）= 总分 0-10<br>
        · ≥7 分 = 立项 · 5-7 分 = 条件性立项 · ≤5 分 = 弃用<br>
        · V1 质性价比 = 7/10（基础强 + 短期落地）<br>
        · V4 沃尔沃 = 4/10（0 用户提到"安全" → 弃用）<br>
        · V5 文化美学 = 9/10（情绪/主张/调性/差异/溢价都满分 + 短期落地难 = 长期 P0）
      </div>
    </div>
    <div style="background:rgba(255,87,34,.08);border:1px solid rgba(255,87,34,.3);padding:10px;border-radius:6px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#ff8a65">🎯 实战应用：</b>V2.9.18 用此方法评估 V1-V5 → V1 短期 P0 · V4 抽象 4/10 不选 · V5 9/10 长期 · V3 8/10 重做
      </div>
    </div>
  </div>

  <!-- 8.2 真实消费者心智验证法 -->
  <h3 style="color:#5eead4;font-size:15px;margin:18px 0 10px">🗣️ 8.2 真实消费者心智验证法 (V2.9.18 决策方法)</h3>
  <div style="background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.1);padding:12px;border-radius:8px;margin-bottom:12px">
    <div style="font-size:11px;color:#cbd5e1;margin-bottom:10px"><b style="color:#5eead4">方法论核心：</b>不靠分析推论，靠 <b>真实消费者原话</b> 验证 · 客户掏钱 > 分析推论</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
      <div style="background:rgba(239,68,68,.08);padding:10px;border-radius:6px;border-left:3px solid #ef4444">
        <div style="font-size:11px;color:#ef4444;font-weight:800">❌ 反例：分析推论陷阱</div>
        <div style="font-size:11px;color:#cbd5e1;margin:6px 0;line-height:1.5">
          · "沃尔沃 = 安全" = 概念完美<br>
          · "中国文化出海" = 概念完美<br>
          · 完美概念 ≠ 用户真实心智<br>
          · 0 用户提到"安全" → V4 4/10 弃用
        </div>
      </div>
      <div style="background:rgba(46,125,50,.08);padding:10px;border-radius:6px;border-left:3px solid #2e7d32">
        <div style="font-size:11px;color:#2e7d32;font-weight:800">✅ 正例：真实心智</div>
        <div style="font-size:11px;color:#cbd5e1;margin:6px 0;line-height:1.5">
          · bicyclebd.com 真实评论<br>
          · DreamCycle 116 SKU 价格分层<br>
          · "因为便宜才买" = Phoenix 真实定位<br>
          · V4 重新定义 = 夜间安全骑行专家
        </div>
      </div>
    </div>
    <div style="background:rgba(94,234,212,.06);border:1px solid rgba(94,234,212,.3);padding:10px;border-radius:6px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#5eead4">📋 6 步验证法：</b><br>
        ① 拉 1-2 个月 DTC 差评+好评+客服对话（IG + Daraz/Shopee + 客服）<br>
        ② 关键词提取 = <b>消费者用什么词</b>（不是我们想的）<br>
        ③ 对比 5 候选 vs 消费者原话词频（"安全"/"可靠"/"不掉色"/"放心"/"10年" 哪个出现最多）<br>
        ④ 看竞品差评：Rockrider/Veloce/Pacific 的"安全"相关差评<br>
        ⑤ 看竞品好评：Polygon/Element 涂装相关的"高溢价/收藏/限定"评价<br>
        ⑥ 投票决策 → 5 候选哪个胜出 → 改 dashboard 研发方向
      </div>
    </div>
  </div>

  <!-- 8.3 抽象 → 具体 重新定义法 -->
  <h3 style="color:#5eead4;font-size:15px;margin:18px 0 10px">🎯 8.3 抽象 → 具体 重新定义法 (V2.9.23 V4 升维方法论)</h3>
  <div style="background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.1);padding:12px;border-radius:8px;margin-bottom:12px">
    <div style="font-size:11px;color:#cbd5e1;margin-bottom:10px"><b style="color:#5eead4">方法论核心：</b>抽象概念如果用户无感，就找"概念背后最有触感的具体场景"</div>
    <div style="background:rgba(255,87,34,.08);border:1px solid rgba(255,87,34,.3);padding:10px;border-radius:6px;margin-bottom:10px">
      <table style="width:100%;font-size:11px;border-collapse:collapse;color:#cbd5e1">
        <tr style="background:rgba(255,87,34,.2);color:#fff">
          <th style="text-align:left;padding:6px;width:25%">维度</th>
          <th style="text-align:left;padding:6px;width:37%">抽象版本（不选）</th>
          <th style="text-align:left;padding:6px;width:38%">重新定义版（选）</th>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,.08)">
          <td style="padding:6px;font-weight:700">概念</td>
          <td style="padding:6px;color:#ff8a80">"自行车界沃尔沃"</td>
          <td style="padding:6px;color:#a5d6a7">"夜间安全骑行专家"</td>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,.08)">
          <td style="padding:6px;font-weight:700">抽象度</td>
          <td style="padding:6px;color:#ff8a80">抽象品牌定位</td>
          <td style="padding:6px;color:#a5d6a7">具体产品功能</td>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,.08)">
          <td style="padding:6px;font-weight:700">真实场景</td>
          <td style="padding:6px;color:#ff8a80">无</td>
          <td style="padding:6px;color:#a5d6a7">BD 夜间通勤（8 点高峰）</td>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,.08)">
          <td style="padding:6px;font-weight:700">真实产品</td>
          <td style="padding:6px;color:#ff8a80">无</td>
          <td style="padding:6px;color:#a5d6a7">反光/夜光/夜光漆</td>
        </tr>
        <tr>
          <td style="padding:6px;font-weight:700">评分</td>
          <td style="padding:6px;color:#ff8a80">4/10 ❌</td>
          <td style="padding:6px;color:#a5d6a7"><b>8/10 ✓</b></td>
        </tr>
      </table>
    </div>
    <div style="background:rgba(94,234,212,.06);border:1px solid rgba(94,234,212,.3);padding:10px;border-radius:6px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#5eead4">📋 重新定义 3 步法：</b><br>
        ① 找出抽象概念（"安全" "可靠" "耐用"）→ 用 5 维法评估（V4 4/10 弃用）<br>
        ② 找概念背后 <b>最有触感</b> 的具体场景（晚 8 点通勤 + 交通混乱 + 夜光 LOGO 看不见）<br>
        ③ 找 <b>真实产品</b> 对应这个具体场景（夜光 LOGO + 反光贴标 + 智能尾灯）<br>
        → 抽象概念 → 具体场景 → 真实产品 = V4 4/10 → 8/10 重新升级 P0
      </div>
    </div>
  </div>

  <!-- 8.4 战略简化判断法 -->
  <h3 style="color:#5eead4;font-size:15px;margin:18px 0 10px">⚖️ 8.4 战略简化判断法 (V2.9.19 → V2.9.20 简化原则)</h3>
  <div style="background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.1);padding:12px;border-radius:8px;margin-bottom:12px">
    <div style="font-size:11px;color:#cbd5e1;margin-bottom:10px"><b style="color:#5eead4">方法论核心：</b>概念完美 ≠ 可执行 · 复杂战略需要先验证"组织能否承接"</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
      <div style="background:rgba(255,193,7,.08);padding:10px;border-radius:6px;border-left:3px solid #ffc107">
        <div style="font-size:11px;color:#ffc107;font-weight:800">❌ 双品牌线（已弃用）</div>
        <div style="font-size:11px;color:#cbd5e1;margin:6px 0;line-height:1.5">
          · 借鉴小米 Mi + Redmi + MIX<br>
          · 主品牌升级中高端 + 副品牌守 30% 份额<br>
          · FNIX 旗舰 + 飞鸟副品牌<br>
          · <b style="color:#ff8a80">问题：组织阻力大 + 资源分散</b>
        </div>
      </div>
      <div style="background:rgba(76,175,80,.08);padding:10px;border-radius:6px;border-left:3px solid #4caf50">
        <div style="font-size:11px;color:#4caf50;font-weight:800">✅ 单线 V1+V3 双轴（采用）</div>
        <div style="font-size:11px;color:#cbd5e1;margin:6px 0;line-height:1.5">
          · 主品牌 Phoenix 直接做 V1+V3 双轴<br>
          · 15-25K BDT 中端价位<br>
          · V1 质价比（基础）+ V3 耐候性（差异化）<br>
          · <b style="color:#a5d6a7">简化：不需副品牌分离</b>
        </div>
      </div>
    </div>
    <div style="background:rgba(94,234,212,.06);border:1px solid rgba(94,234,212,.3);padding:10px;border-radius:6px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#5eead4">📋 简化判断 3 问：</b><br>
        ① <b>组织能力：</b>现有团队能否承接多品牌运营？（BD 团队小 = 否）<br>
        ② <b>资源效率：</b>双品牌是否分散资源导致两边都做不好？（V1+V3 单线 = 集中）<br>
        ③ <b>心智成本：</b>消费者能否同时理解 2 个品牌？（BD 消费心智 1 个品牌 = 集中）<br>
        → 3 问全 Yes 才用双品牌 · 否则单线 V1+V3 双轴更稳
      </div>
    </div>
  </div>

  <!-- 8.5 资源/能力评估法（集团全产业链护城河识别） -->
  <h3 style="color:#5eead4;font-size:15px;margin:18px 0 10px">🏭 8.5 资源/能力评估法 (V2.9.22 护城河识别)</h3>
  <div style="background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.1);padding:12px;border-radius:8px;margin-bottom:12px">
    <div style="font-size:11px;color:#cbd5e1;margin-bottom:10px"><b style="color:#5eead4">方法论核心：</b>独家护城河 = "别人学不来"的能力 · 不只是产品参数</div>
    <div style="background:rgba(255,193,7,.08);border:1px solid rgba(255,193,7,.3);padding:10px;border-radius:6px;margin-bottom:10px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#fbbf24">📋 护城河识别 4 问：</b><br>
        ① 我们的核心资源是什么？（内部 vs 外部采购）<br>
        ② 竞品是否拥有同样资源？（是否唯一）<br>
        ③ 资源能否支撑长期差异化？（耐候性 3 阶段 18 月+）<br>
        ④ 资源能否内部协同放大？（5 公司联合专利）
      </div>
    </div>
    <div style="background:rgba(94,234,212,.06);border:1px solid rgba(94,234,212,.3);padding:10px;border-radius:6px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#5eead4">🎯 V2.9.22 实战：</b>Phoenix = 凤凰集团（华久+美乐+凤曜+凤驰+凤凰）<br>
        · ① 内部全产业链 = 辐条厂+链条厂+车架厂+管材厂+整车厂<br>
        · ② 竞品（Veloce/Marine/Foxter）= 单一品牌 · 外部采购所有零件 → 学不来<br>
        · ③ 18 月内分 3 阶段做（达克锈→氟碳漆→集团专利）<br>
        · ④ 5 公司联合申请 5+ 集团专利 = 内部协同放大<br>
        → 4 问全 Yes = 凤凰集团全产业链 = 独家护城河
      </div>
    </div>
  </div>

  <!-- 8.6 时间场景差异化法（V3+V4 时间轴） -->
  <h3 style="color:#5eead4;font-size:15px;margin:18px 0 10px">⏰ 8.6 时间场景差异化法 (V2.9.23 V3+V4 共同点提炼)</h3>
  <div style="background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.1);padding:12px;border-radius:8px;margin-bottom:12px">
    <div style="font-size:11px;color:#cbd5e1;margin-bottom:10px"><b style="color:#5eead4">方法论核心：</b>差异化维度 = 时间 / 空间 / 人群 · 同一个维度下不同子场景 = 强协同</div>
    <div style="background:rgba(94,234,212,.06);border:1px solid rgba(94,234,212,.3);padding:10px;border-radius:6px;margin-bottom:10px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#5eead4">🌅 V3 雨季 + V4 夜间 = 时间场景差异化的 2 个子场景：</b><br>
        · V3 雨季 = 6-10 月 + 白天 + 潮湿场景<br>
        · V4 夜间 = 全年 + 晚上 8 点通勤 + 黑暗场景<br>
        · 共同点 = <b>都是"时间维度"差异化的子场景</b> = 强协同<br>
        · 差异点 = V3 防锈 / V4 夜光 = 不冲突<br>
        · 整合价值 = <b>24 小时全场景守护</b> = 凤凰品牌核心
      </div>
    </div>
    <div style="background:rgba(255,87,34,.08);border:1px solid rgba(255,87,34,.3);padding:10px;border-radius:6px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#ff8a65">📋 时间场景差异化 3 步：</b><br>
        ① 列出目标市场的<b>所有真实使用时间</b>（早/中/晚 + 雨季/旱季 + 工作日/周末）<br>
        ② 找出每个时间段下的<b>真实痛点</b>（雨季生锈 / 夜间看不见）<br>
        ③ 把不同时间段痛点 = 不同子场景 = 整合为 1 个品牌承诺（24h 全场景守护）<br>
        → 3 个子场景 < 1 个品牌承诺 = 战略协同 ≠ 战略分散
      </div>
    </div>
  </div>

  <!-- 8.7 跨市场差异化框架（4 国 = L1+L2+L3+L4） -->
  <h3 style="color:#5eead4;font-size:15px;margin:18px 0 10px">🌍 8.7 跨市场差异化框架 (V2.9.14 4 国分层法)</h3>
  <div style="background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.1);padding:12px;border-radius:8px;margin-bottom:12px">
    <div style="font-size:11px;color:#cbd5e1;margin-bottom:10px"><b style="color:#5eead4">方法论核心：</b>不同市场 = 不同资源/不同购买力/不同文化 → 不可能 1 个策略打所有</div>
    <div style="background:rgba(94,234,212,.06);border:1px solid rgba(94,234,212,.3);padding:10px;border-radius:6px;margin-bottom:10px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#5eead4">📋 跨市场分层 4 步：</b><br>
        ① <b>购买力分层：</b>BD 25-40K / ID 15M-50M IDR / EG-IN 5K-50K<br>
        ② <b>场景分层：</b>BD 雨季+夜间真实痛 / ID 华人圈 + 穆斯林圈 / EG 阿拉伯健身 / IN 印度教<br>
        ③ <b>资源分层：</b>L1 主力 (70%) / L2 复制 (5%) / L3 观察 / L4 跳过<br>
        ④ <b>心智分层：</b>BD 短期不用 V5 文化美学（购买力不够）/ ID/EG/IN 长期 L1+L2 用 V5
      </div>
    </div>
    <div style="background:rgba(76,175,80,.08);border:1px solid rgba(76,175,80,.3);padding:10px;border-radius:6px">
      <div style="font-size:11px;color:#cbd5e1;line-height:1.7">
        <b style="color:#a5d6a7">🎯 4 国差异化实战（V2.9.23）：</b><br>
        · 🇧🇩 BD = V1+V3+V4 雨季+夜间 / 18-35K BDT / L1 / 70%<br>
        · 🇮🇩 ID = V5 文化美学 + 华人圈 / 15M-50M IDR / L1 / 20%<br>
        · 🇪🇬 EG = V5 + 阿拉伯书法 / 5K-50K EGP / L2 复制 / 5%<br>
        · 🇮🇳 IN = V5 + 莲花图腾 / 5K-50K INR / L2 复制 / 5%
      </div>
    </div>
  </div>

  <!-- 8.8 决策方法论汇总 -->
  <h3 style="color:#5eead4;font-size:15px;margin:18px 0 10px">📋 8.8 6 个决策方法论汇总 (V2.9.18-V2.9.23 提炼)</h3>
  <div style="background:linear-gradient(135deg,rgba(94,234,212,.08),rgba(33,150,243,.05));border:1px solid rgba(94,234,212,.3);padding:12px;border-radius:8px;margin-bottom:12px">
    <table style="width:100%;font-size:11px;border-collapse:collapse;color:#cbd5e1">
      <tr style="background:rgba(94,234,212,.2);color:#fff">
        <th style="text-align:left;padding:8px;width:8%">#</th>
        <th style="text-align:left;padding:8px;width:24%">方法论</th>
        <th style="text-align:left;padding:8px;width:30%">核心问题</th>
        <th style="text-align:left;padding:8px;width:20%">实战应用</th>
        <th style="text-align:center;padding:8px;width:18%">最终结论</th>
      </tr>
      <tr style="border-bottom:1px solid rgba(255,255,255,.08)">
        <td style="padding:6px;font-weight:700;color:#5eead4">8.1</td>
        <td style="padding:6px">5 维价值主张评估法</td>
        <td style="padding:6px">5 个维度打分 ≥ 7 才立项？</td>
        <td style="padding:6px">V1 7/V4 4/V5 9/V3 8</td>
        <td style="padding:6px;text-align:center;color:#a5d6a7">V1+V3+V5 立项</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(255,255,255,.08)">
        <td style="padding:6px;font-weight:700;color:#5eead4">8.2</td>
        <td style="padding:6px">真实消费者心智验证</td>
        <td style="padding:6px">用户原话 vs 我们想的？</td>
        <td style="padding:6px">bicyclebd + DreamCycle</td>
        <td style="padding:6px;text-align:center;color:#a5d6a7">客户掏钱 > 推论</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(255,255,255,.08)">
        <td style="padding:6px;font-weight:700;color:#5eead4">8.3</td>
        <td style="padding:6px">抽象 → 具体 重新定义</td>
        <td style="padding:6px">抽象概念找具体场景 + 产品？</td>
        <td style="padding:6px">V4 沃尔沃 4/10 → 夜间安全 8/10</td>
        <td style="padding:6px;text-align:center;color:#a5d6a7">V4 重新定义 P0</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(255,255,255,.08)">
        <td style="padding:6px;font-weight:700;color:#5eead4">8.4</td>
        <td style="padding:6px">战略简化判断法</td>
        <td style="padding:6px">复杂战略先验组织承接？</td>
        <td style="padding:6px">双品牌线 → 单线 V1+V3</td>
        <td style="padding:6px;text-align:center;color:#a5d6a7">简化更稳</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(255,255,255,.08)">
        <td style="padding:6px;font-weight:700;color:#5eead4">8.5</td>
        <td style="padding:6px">资源/能力评估法</td>
        <td style="padding:6px">护城河别人学得来？</td>
        <td style="padding:6px">凤凰集团全产业链 = 独家</td>
        <td style="padding:6px;text-align:center;color:#a5d6a7">集团护城河</td>
      </tr>
      <tr style="border-bottom:1px solid rgba(255,255,255,.08)">
        <td style="padding:6px;font-weight:700;color:#5eead4">8.6</td>
        <td style="padding:6px">时间场景差异化法</td>
        <td style="padding:6px">同一维度下找子场景？</td>
        <td style="padding:6px">V3 雨季 + V4 夜间 = 24h 全场景</td>
        <td style="padding:6px;text-align:center;color:#a5d6a7">1 品牌承诺</td>
      </tr>
      <tr>
        <td style="padding:6px;font-weight:700;color:#5eead4">8.7</td>
        <td style="padding:6px">跨市场分层框架</td>
        <td style="padding:6px">1 策略打所有？</td>
        <td style="padding:6px">BD V1+V3+V4 / ID/EG/IN V5</td>
        <td style="padding:6px;text-align:center;color:#a5d6a7">4 国差异化</td>
      </tr>
    </table>
    <div style="background:rgba(245,158,11,.08);border:1px solid #f59e0b;padding:10px;border-radius:6px;margin-top:10px">
      <div style="font-size:12px;color:#fff;line-height:1.7">
        <b style="color:#fcd34d">📌 跨 Tab 引用：</b><br>
        · <b style="color:#5eead4">方法论</b>（怎么判断）= <a href="./strategy.html" style="color:#5eead4">strategy.html 8 节（本节）</a><br>
        · <b style="color:#c8102e">产品策略</b>（具体选了什么）= <a href="./matrix.html" style="color:#ff9cae">matrix.html 7. 价值主张 V2.9.23</a><br>
        · <b style="color:#fbbf24">理论框架</b>（5 看/4P/SWOT/爆品）= strategy.html 1-7 节
      </div>
    </div>
  </div>
</div>

"""

# 重建
new_text = before + NEW_SECTION + END_AFTER + after_marker
STRATEGY.write_text(new_text, encoding="utf-8")

# 报告
old_len = len(text)
new_len = len(new_text)
print(f"[OK] strategy.html 第 8 节重写")
print(f"     旧: {old_len} chars / 估算 {old_len//1024}KB")
print(f"     新: {new_len} chars / 估算 {new_len//1024}KB")
print(f"     diff: {new_len - old_len:+d} chars")
