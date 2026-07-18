# -*- coding: utf-8 -*-
"""统一所有 bd/ + id/ 子目录 HTML 的 nav 为 9 个 Tab (跟 index.html 一致)"""
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path("D:/MINIMAX/phoenix-live")

# 9-Tab 标准 nav 模板 (bd/ 路径, 自己 active)
NAV_BD_TEMPLATE = '''<div class="nav">
      <a href="./index.html">🏠 总览</a>
      <a href="../daily-report.html">📅 市场日报</a>
      <a href="./competitive.html">🏆 竞品监控</a>
      <a href="./matrix.html">💎 产品矩阵</a>
      <a href="./index.html" class="active">🇧🇩 孟加拉</a>
      <a href="../id/index.html">🇮🇩 印尼</a>
      <a href="./tasks.html">🎯 任务 OKR</a>
      <a href="./dtc.html">💬 DTC 差评</a>
      <a href="./strategy.html">🧠 策略迭代</a>
    </div>'''

NAV_ID_TEMPLATE = '''<div class="nav">
      <a href="./index.html">🏠 总览</a>
      <a href="../daily-report.html">📅 市场日报</a>
      <a href="./competitive.html">🏆 竞品监控</a>
      <a href="./matrix.html">💎 产品矩阵</a>
      <a href="../bd/index.html">🇧🇩 孟加拉</a>
      <a href="./index.html" class="active">🇮🇩 印尼</a>
      <a href="./tasks.html">🎯 任务 OKR</a>
      <a href="./dtc.html">💬 DTC 差评</a>
      <a href="./strategy.html">🧠 策略迭代</a>
    </div>'''

# bd 子目录中各文件对应的 active 类名
BD_ACTIVE_MAP = {
    "bd/competitive.html": ("competitive.html", "🏆 竞品监控"),
    "bd/matrix.html": ("matrix.html", "💎 产品矩阵"),
    "bd/market.html": ("index.html", "🇧🇩 孟加拉"),
    "bd/tasks.html": ("tasks.html", "🎯 任务 OKR"),
    "bd/dtc.html": ("dtc.html", "💬 DTC 差评"),
    "bd/strategy.html": ("strategy.html", "🧠 策略迭代"),
    "bd/daily.html": (None, None),  # daily.html 是 old, 不动
}

ID_ACTIVE_MAP = {
    "id/competitive.html": ("competitive.html", "🏆 竞品监控"),
    "id/matrix.html": ("matrix.html", "💎 产品矩阵"),
    "id/market.html": ("index.html", "🇮🇩 印尼"),
    "id/tasks.html": ("tasks.html", "🎯 任务 OKR"),
    "id/dtc.html": ("dtc.html", "💬 DTC 差评"),
    "id/strategy.html": ("strategy.html", "🧠 策略迭代"),
    "id/daily.html": (None, None),
}

def make_nav(template_base, active_href, active_label):
    """根据 active 替换模板里的 active 类"""
    nav = template_base
    # 先去掉所有 class="active"
    nav = re.sub(r' class="active"', '', nav)
    # 在 active 项加上 class="active"
    if active_href and active_label:
        # 找到 <a href="...">label</a> 替换
        pattern = f'<a href="./{active_href}">{active_label}</a>'
        replacement = f'<a href="./{active_href}" class="active">{active_label}</a>'
        nav = nav.replace(pattern, replacement)
        # 跨目录 active (../id/index.html 等)
        pattern2 = f'<a href="../{active_href}">{active_label}</a>'
        replacement2 = f'<a href="../{active_href}" class="active">{active_label}</a>'
        nav = nav.replace(pattern2, replacement2)
    return nav

# 修复 bd/
print("=== bd/ ===")
for relpath, (active_href, active_label) in BD_ACTIVE_MAP.items():
    f = ROOT / relpath
    if not f.exists() or active_href is None:
        continue
    text = f.read_text(encoding="utf-8")
    # 找 nav 块
    m = re.search(r'(<div class="nav">.*?</div>)', text, re.DOTALL)
    if not m:
        print(f"  [{relpath}] NO nav block found, skip")
        continue
    old_nav = m.group(1)
    new_nav = make_nav(NAV_BD_TEMPLATE, active_href, active_label)
    if old_nav.strip() == new_nav.strip():
        print(f"  [{relpath}] already correct")
        continue
    new_text = text.replace(old_nav, new_nav, 1)
    f.write_text(new_text, encoding="utf-8")
    print(f"  [{relpath}] nav updated (active={active_label})")

# 修复 id/
print("\n=== id/ ===")
for relpath, (active_href, active_label) in ID_ACTIVE_MAP.items():
    f = ROOT / relpath
    if not f.exists() or active_href is None:
        continue
    text = f.read_text(encoding="utf-8")
    m = re.search(r'(<div class="nav">.*?</div>)', text, re.DOTALL)
    if not m:
        print(f"  [{relpath}] NO nav block found, skip")
        continue
    old_nav = m.group(1)
    new_nav = make_nav(NAV_ID_TEMPLATE, active_href, active_label)
    if old_nav.strip() == new_nav.strip():
        print(f"  [{relpath}] already correct")
        continue
    new_text = text.replace(old_nav, new_nav, 1)
    f.write_text(new_text, encoding="utf-8")
    print(f"  [{relpath}] nav updated (active={active_label})")

print("\n[OK] nav 9-Tab 统一完成")
