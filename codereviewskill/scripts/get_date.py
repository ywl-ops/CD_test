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
    try:
        return datetime.now().strftime(format_str)
    except ValueError as e:
        print(f"Error: Invalid date format '{format_str}'", file=sys.stderr)
        raise

if __name__ == "__main__":
    default_format = "%Y-%m-%d %H:%M:%S"
    format_arg = sys.argv[1] if len(sys.argv) > 1 else default_format
    try:
        print(get_current_date(format_arg))
    except ValueError:
        print("Usage: python get_date.py [date_format]", file=sys.stderr)
        print(f"Example: python get_date.py '%Y-%m-%d'", file=sys.stderr)
        sys.exit(1)