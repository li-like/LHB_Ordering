#!/usr/bin/env python3
"""
简单的点餐API测试脚本
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def test_api():
    print("开始测试点餐API...")
    
    # 测试获取分类
    print("\n=== 测试获取分类 ===")
    try:
        response = requests.get(f'{BASE_URL}/api/ordering/categories/')
        print(f"分类接口状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"获取到 {len(data.get('results', []))} 个分类")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试获取餐品
    print("\n=== 测试获取餐品 ===")
    try:
        response = requests.get(f'{BASE_URL}/api/ordering/items/')
        print(f"餐品接口状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"获取到 {len(data.get('results', []))} 个餐品")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试简化分类接口
    print("\n=== 测试简化分类接口 ===")
    try:
        response = requests.get(f'{BASE_URL}/api/ordering/categories/simple_list/')
        print(f"简化分类接口状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"简化分类数据: {data}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == '__main__':
    test_api()
