# -*- coding: utf-8 -*-
"""给 daily-report.html 加 cache-bust meta"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

FILE = Path("D:/MINIMAX/phoenix-live/daily-report.html")
text = FILE.read_text(encoding="utf-8")

OLD = '<meta charset="UTF-8">\n\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n\n<title>市场日报'
NEW = '''<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">

<title>市场日报'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    FILE.write_text(text, encoding="utf-8")
    print("[OK] cache-bust meta added")
else:
    print("[ERR] pattern not found")
