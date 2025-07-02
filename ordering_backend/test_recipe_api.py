#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试菜谱API是否正常工作
"""

import requests
import json

# 配置
BASE_URL = "http://192.168.10.4:8000"
TEST_OPENID = "ocYjt6oIJsFk2RgC7duPZVScsBV8"

def test_recipe_api():
    """测试菜谱API"""
    
    print("=== 测试菜谱API ===")
    
    # 1. 测试获取所有菜谱
    print("\n1. 测试获取所有菜谱...")
    try:
        response = requests.get(f"{BASE_URL}/api/recipes/", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
    
    # 2. 测试带参数的请求
    print("\n2. 测试带参数的菜谱请求...")
    try:
        params = {
            'mode': 'all',
            'current_user': TEST_OPENID
        }
        response = requests.get(f"{BASE_URL}/api/recipes/", params=params, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 带参数请求成功")
            print(f"菜谱数量: {len(data.get('data', []))}")
            for recipe in data.get('data', [])[:3]:  # 只显示前3个
                print(f"  - {recipe['name']} by {recipe['author']['nickname']}")
        else:
            print(f"❌ 带参数请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    test_recipe_api()
