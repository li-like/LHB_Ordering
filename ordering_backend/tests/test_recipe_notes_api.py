#!/usr/bin/env python3
"""
测试菜谱笔记相关API的脚本
"""
import os
import sys
import django
import requests
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

BASE_URL = 'http://127.0.0.1:8000'

def test_recipe_notes_api():
    """测试菜谱笔记API"""
    print("=== 测试菜谱笔记API ===")
    
    # 1. 先获取一个菜谱ID（假设存在ID为1的菜谱）
    recipe_id = 1
    
    # 2. 测试创建笔记
    print("\n1. 测试创建笔记...")
    note_data = {
        'content': '这道菜做得很成功！味道很好，家人都很喜欢。',
        'rating': 5,
        'success': True,
        'modifications': '下次可以稍微多放一点盐',
        'cooking_date': '2024-01-15T10:30:00Z',
        'author_openid': 'test_user_123'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/recipes/{recipe_id}/notes/',
            json=note_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            note_id = result['data']['id']
            print(f"✅ 笔记创建成功，ID: {note_id}")
        else:
            print(f"❌ 笔记创建失败")
            return
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 3. 测试获取笔记列表
    print("\n2. 测试获取笔记列表...")
    try:
        response = requests.get(f'{BASE_URL}/api/recipes/{recipe_id}/notes/')
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            notes = result['data']
            print(f"✅ 获取笔记列表成功，共 {len(notes)} 条笔记")
        else:
            print(f"❌ 获取笔记列表失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_recipe_detail():
    """测试菜谱详情API"""
    print("\n=== 测试菜谱详情API ===")
    
    recipe_id = 1
    try:
        response = requests.get(f'{BASE_URL}/api/recipes/{recipe_id}/')
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            recipe = result['data']
            print(f"✅ 获取菜谱详情成功: {recipe.get('name', 'Unknown')}")
        else:
            print(f"❌ 获取菜谱详情失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == '__main__':
    # 首先测试菜谱详情API
    test_recipe_detail()
    
    # 然后测试笔记API
    test_recipe_notes_api()
