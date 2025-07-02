#!/usr/bin/env python3
"""
测试菜谱编辑功能
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

def test_recipe_edit():
    """测试菜谱编辑功能"""
    print("=== 测试菜谱编辑功能 ===")
    
    recipe_id = 1  # 使用第一个菜谱进行测试
    
    # 1. 获取原始菜谱数据
    print("\n1. 获取原始菜谱数据...")
    try:
        response = requests.get(f'{BASE_URL}/api/recipes/{recipe_id}/')
        print(f"获取菜谱状态码: {response.status_code}")
        
        if response.status_code == 200:
            original_recipe = response.json()['data']
            print(f"✅ 原始菜谱: {original_recipe['name']}")
            print(f"   制作时间: {original_recipe.get('cook_time', 0)} 分钟")
            print(f"   步骤数量: {len(original_recipe.get('steps', []))}")
            print(f"   食材数量: {len(original_recipe.get('ingredients', []))}")
        else:
            print("❌ 获取菜谱失败")
            return
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 2. 构造编辑数据
    print("\n2. 构造编辑数据...")
    updated_data = {
        'name': original_recipe['name'] + ' (编辑测试)',
        'description': original_recipe.get('description', '') + ' - 通过API编辑测试',
        'cook_time': original_recipe.get('cook_time', 30) + 10,
        'servings': original_recipe.get('servings', 2),
        'difficulty': original_recipe.get('difficulty', 1),
        'category': original_recipe.get('category', 'meat'),
        'tags': original_recipe.get('tags', []) + ['API测试'],
        'ingredients': [
            {'name': '测试食材1', 'amount': '200', 'unit': '克'},
            {'name': '测试食材2', 'amount': '1', 'unit': '个'},
            {'name': '调料', 'amount': '适量', 'unit': ''}
        ],
        'steps': [
            {
                'description': '第一步：准备所有食材，清洗干净',
                'time_required': 5,
                'temperature': '',
                'tips': '食材要新鲜'
            },
            {
                'description': '第二步：开始制作，注意火候控制',
                'time_required': 15,
                'temperature': '中火',
                'tips': '要不断翻炒'
            },
            {
                'description': '第三步：最后调味，装盘即可',
                'time_required': 5,
                'temperature': '',
                'tips': '可以撒上葱花装饰'
            }
        ]
    }
    
    print(f"准备更新: {updated_data['name']}")
    print(f"新的制作时间: {updated_data['cook_time']} 分钟")
    print(f"新的步骤数量: {len(updated_data['steps'])}")
    print(f"新的食材数量: {len(updated_data['ingredients'])}")
    
    # 3. 提交更新
    print("\n3. 提交更新...")
    try:
        response = requests.put(
            f'{BASE_URL}/api/recipes/{recipe_id}/',
            json=updated_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"更新状态码: {response.status_code}")
        print(f"更新响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 菜谱更新成功")
        else:
            print("❌ 菜谱更新失败")
            return
            
    except Exception as e:
        print(f"❌ 更新请求失败: {e}")
        return
    
    # 4. 验证更新结果
    print("\n4. 验证更新结果...")
    try:
        response = requests.get(f'{BASE_URL}/api/recipes/{recipe_id}/')
        if response.status_code == 200:
            updated_recipe = response.json()['data']
            print(f"✅ 更新后菜谱名称: {updated_recipe['name']}")
            print(f"✅ 更新后制作时间: {updated_recipe.get('cook_time', 0)} 分钟")
            print(f"✅ 更新后步骤数量: {len(updated_recipe.get('steps', []))}")
            print(f"✅ 更新后食材数量: {len(updated_recipe.get('ingredients', []))}")
            
            # 验证步骤内容
            print("\n步骤详情:")
            for i, step in enumerate(updated_recipe.get('steps', []), 1):
                print(f"  {i}. {step.get('description', '')[:30]}...")
                
            # 验证食材内容
            print("\n食材详情:")
            for ingredient in updated_recipe.get('ingredients', []):
                print(f"  - {ingredient.get('name', '')}: {ingredient.get('amount', '')}{ingredient.get('unit', '')}")
                
        else:
            print("❌ 验证获取失败")
            
    except Exception as e:
        print(f"❌ 验证请求失败: {e}")

if __name__ == '__main__':
    test_recipe_edit()
