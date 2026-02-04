"""
Author: ywl-ops 2644984438@qq.com
Date: 2026-02-04
LastEditors: ywl-ops 2644984438@qq.com
LastEditTime: 2026-02-04
FilePath: /test/codereviewskill/scripts/get_date.py
Description: 
"""
#!/usr/bin/env python3
"""获取当前日期和时间"""

from datetime import datetime
import sys

def get_current_date(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    return datetime.now().strftime(format_str)

if __name__ == "__main__":
    format_arg = sys.argv[1] if len(sys.argv) > 1 else "%Y-%m-%d %H:%M:%S"
    print(get_current_date(format_arg))