#!/usr/bin/env python3
"""
测试当前API返回的数据结构和前端展示问题
"""

import os
import sys
import django
import requests
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from recipes.models import Recipe, RecipeIngredient, RecipeStep
from wechat_auth.models import WeChatUser

def test_current_api():
    """测试当前API的实际表现"""
    print("============================================================")
    print("🧪 测试当前API表现")
    print("============================================================")
    
    # 1. 直接查询数据库
    print("📊 数据库中的菜谱:")
    recipes = Recipe.objects.all().order_by('-created_at')
    
    for recipe in recipes:
        print(f"ID: {recipe.id}")
        print(f"名称: {recipe.name}")
        print(f"作者: {recipe.author.nickname} ({recipe.author.openid})")
        print(f"是否公开: {recipe.is_public}")
        print(f"创建时间: {recipe.created_at}")
        print("-" * 40)
    
    # 2. 测试API调用
    print("\n🌐 测试API调用:")
    base_url = "http://192.168.189.240:8000"
    
    # 测试所有菜谱
    print("\n1. 测试获取所有菜谱 (无参数):")
    try:
        response = requests.get(f"{base_url}/api/recipes/", timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数量: {len(data.get('data', []))}")
            for recipe in data.get('data', [])[:2]:  # 只显示前2个
                print(f"  - {recipe['name']} by {recipe['author']['nickname']}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"API调用失败: {e}")
    
    # 测试按作者筛选
    print("\n2. 测试按作者筛选:")
    test_openid = "ocYjt6oIJsFk2RgC7duPZVScsBV8"  # 冷汉堡的openid
    try:
        response = requests.get(f"{base_url}/api/recipes/?author={test_openid}", timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数量: {len(data.get('data', []))}")
            for recipe in data.get('data', []):
                print(f"  - {recipe['name']} by {recipe['author']['nickname']}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"API调用失败: {e}")
    
    # 3. 分析问题
    print("\n🔍 问题分析:")
    
    # 检查用户菜谱数量
    user_recipes = Recipe.objects.filter(author__openid="ocYjt6oIJsFk2RgC7duPZVScsBV8")
    print(f"冷汉堡的菜谱数量: {user_recipes.count()}")
    
    all_recipes = Recipe.objects.all()
    print(f"所有菜谱数量: {all_recipes.count()}")
    
    public_recipes = Recipe.objects.filter(is_public=True)
    print(f"公开菜谱数量: {public_recipes.count()}")
    
    private_recipes = Recipe.objects.filter(is_public=False)
    print(f"私有菜谱数量: {private_recipes.count()}")

if __name__ == '__main__':
    test_current_api()
