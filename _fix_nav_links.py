# -*- coding: utf-8 -*-
"""修复 bd/id 子目录 HTML 的 nav 链接: ./daily.html -> ../daily-report.html"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path("D:/MINIMAX/phoenix-live")

files = [
    "bd/competitive.html", "bd/dtc.html", "bd/matrix.html",
    "bd/strategy.html", "bd/tasks.html",
    "id/competitive.html", "id/dtc.html", "id/matrix.html",
    "id/strategy.html", "id/tasks.html",
]

total_replaced = 0
for relpath in files:
    f = ROOT / relpath
    if not f.exists():
        print(f"[SKIP] {relpath} not found")
        continue
    text = f.read_text(encoding="utf-8")
    # 仅替换 nav 里 ./daily.html 链接
    new_text = text.replace('href="./daily.html"', 'href="../daily-report.html"')
    count = text.count('href="./daily.html"') - new_text.count('href="./daily.html"')
    if count > 0:
        f.write_text(new_text, encoding="utf-8")
        total_replaced += count
        print(f"[OK] {relpath}: {count} link(s) fixed")
    else:
        print(f"[--] {relpath}: no match")

print(f"\nTotal: {total_replaced} link(s) fixed")
