"""
Author: ywl-ops 2644984438@qq.com
Date: 2026-01-19
LastEditors: ywl-ops 2644984438@qq.com
LastEditTime: 2026-02-04
FilePath: /test/read_toml.py
Description: 
"""
import tomli as tomllib
# 读取TOML文件
def read_toml(file_path):
    """
    读取并解析 TOML 配置文件
    
    Args:
        file_path (str): TOML 文件路径
        
    Returns:
        dict: 解析后的配置数据，出错时返回 None
    """
    try:
        with open(file_path, 'rb') as f:
            data = tomllib.load(f)
        return data
    except FileNotFoundError:
        print(f"配置文件不存在：{file_path}")
        return {"error": "file_not_found", "path": file_path}
    except tomllib.TOMLDecodeError as e:
        print(f"TOML解析失败：{e}")
        return {"error": "parse_error", "message": str(e)}
    except PermissionError:
        print(f"无权限访问配置文件：{file_path}")
        return {"error": "permission_denied", "path": file_path}
    except Exception as e:
        print(f"读取TOML失败：{e}")
        return {"error": "unknown", "message": str(e)}
    