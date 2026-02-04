"""
获取当前日期和时间的工具函数
"""
from datetime import datetime
import sys


def get_current_date(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    获取当前日期和时间
    
    Args:
        format_str: 日期格式字符串，默认为 "%Y-%m-%d %H:%M:%S"
    
    Returns:
        格式化后的当前日期时间字符串
        
    Raises:
        ValueError: 当格式字符串无效时
    """
    if not isinstance(format_str, str):
        raise TypeError("Format string must be a string")
    
    try:
        return datetime.now().strftime(format_str)
    except ValueError as e:
        raise ValueError(f"Invalid date format '{format_str}': {str(e)}")


def main():
    """主函数，处理命令行调用"""
    default_format = "%Y-%m-%d %H:%M:%S"
    format_arg = sys.argv[1] if len(sys.argv) > 1 else default_format
    
    try:
        result = get_current_date(format_arg)
        print(result)
    except (ValueError, TypeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Usage: python get_date.py [date_format]", file=sys.stderr)
        print("Example: python get_date.py '%Y-%m-%d'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()