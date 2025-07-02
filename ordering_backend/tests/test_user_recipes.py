#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试"我的菜谱"功能
"""

import requests
import json

# 配置
BASE_URL = "http://127.0.0.1:8000"
TEST_OPENID = "ocYjt6oIJsFk2RgC7duPZVScsBV8"

def test_user_recipes():
    """测试用户菜谱获取功能"""
    
    print("=== 测试我的菜谱功能 ===")
    
    # 1. 测试获取所有菜谱
    print("\n1. 获取所有菜谱...")
    response = requests.get(f"{BASE_URL}/api/recipes/")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ 获取所有菜谱成功，共 {len(data.get('data', []))} 条")
            # 显示前3条菜谱
            for i, recipe in enumerate(data.get('data', [])[:3]):
                print(f"   {i+1}. {recipe['name']} (作者: {recipe['author']['nickname']})")
        else:
            print(f"❌ 获取所有菜谱失败: {data}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    # 2. 测试获取特定用户的菜谱
    print(f"\n2. 获取用户 {TEST_OPENID} 的菜谱...")
    response = requests.get(f"{BASE_URL}/api/recipes/", params={
        'author': TEST_OPENID
    })
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            user_recipes = data.get('data', [])
            print(f"✅ 获取用户菜谱成功，共 {len(user_recipes)} 条")
            if user_recipes:
                for i, recipe in enumerate(user_recipes):
                    print(f"   {i+1}. {recipe['name']} (创建时间: {recipe['created_at'][:10]})")
            else:
                print("   该用户还没有创建菜谱")
        else:
            print(f"❌ 获取用户菜谱失败: {data}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    # 3. 测试按分类获取用户菜谱
    print(f"\n3. 获取用户 {TEST_OPENID} 的荤菜菜谱...")
    response = requests.get(f"{BASE_URL}/api/recipes/", params={
        'author': TEST_OPENID,
        'category': 'meat'
    })
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            meat_recipes = data.get('data', [])
            print(f"✅ 获取用户荤菜菜谱成功，共 {len(meat_recipes)} 条")
            for i, recipe in enumerate(meat_recipes):
                print(f"   {i+1}. {recipe['name']} (分类: {recipe['category']})")
        else:
            print(f"❌ 获取用户荤菜菜谱失败: {data}")
    else:
        print(f"❌ 请求失败: {response.status_code}")

if __name__ == "__main__":
    test_user_recipes()
