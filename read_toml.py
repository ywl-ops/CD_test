"""
Author: ywl-ops 2644984438@qq.com
Date: 2026-01-19
LastEditors: ywl-ops 2644984438@qq.com
LastEditTime: 2026-01-19
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
# 调用示例
config_data = read_toml("config.toml")
if config_data:
    print("数据库主机：", config_data["data"]["host"],type(config_data["data"]["host"]))
    print("应用名称：", config_data["data"]["port"],type(config_data["data"]["port"]))
    print("功能列表：", config_data["data"]["username"],type(config_data["data"]["username"]))
    print("功能列表：", config_data["data"]["password"],type(config_data["data"]["password"]))
    print("功能列表：", config_data["data"]["enabled"],type(config_data["data"]["enabled"]))