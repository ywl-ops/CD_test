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
    try:
        with open(file_path, "rb") as f:  # 注意用rb模式（二进制）
            data = tomllib.load(f)
        return data
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在")
        return None
    except Exception as e:
        print(f"读取TOML失败：{e}")
        return None