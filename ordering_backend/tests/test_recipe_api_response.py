#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试菜谱API返回的数据
"""

import requests
import json

def test_recipe_api():
    """测试菜谱API"""
    
    print("=== 测试菜谱API ===")
    
    # 测试获取菜谱列表
    try:
        response = requests.get("http://127.0.0.1:8000/api/recipes/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API返回状态: {data.get('success')}")
            print(f"菜谱数量: {len(data.get('data', []))}")
            
            print("\nAPI返回的菜谱列表:")
            for i, recipe in enumerate(data.get('data', [])):
                print(f"{i+1}. ID: {recipe['id']}, 名称: {recipe['name']}")
                print(f"   描述: {recipe['description']}")
                print(f"   作者: {recipe['author']['nickname']}")
                print(f"   创建时间: {recipe['created_at']}")
                print("-" * 40)
                
        else:
            print(f"API请求失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试获取特定菜谱详情
    print("\n=== 测试菜谱详情API ===")
    
    test_ids = [1, 2, 3, 4, 5]
    for recipe_id in test_ids:
        try:
            response = requests.get(f"http://127.0.0.1:8000/api/recipes/{recipe_id}/")
            
            if response.status_code == 200:
                data = response.json()
                recipe = data.get('data')
                print(f"\n菜谱ID {recipe_id} 详情:")
                print(f"名称: {recipe['name']}")
                print(f"描述: {recipe['description']}")
                print(f"食材数量: {len(recipe['ingredients'])}")
                print(f"步骤数量: {len(recipe['steps'])}")
                if recipe['ingredients']:
                    print(f"第一个食材: {recipe['ingredients'][0]['name']}")
                if recipe['steps']:
                    print(f"第一个步骤: {recipe['steps'][0]['description'][:30]}...")
            else:
                print(f"\n菜谱ID {recipe_id} 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"获取菜谱ID {recipe_id} 失败: {e}")

if __name__ == "__main__":
    test_recipe_api()
