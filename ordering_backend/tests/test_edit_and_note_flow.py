#!/usr/bin/env python3
"""
测试菜谱编辑和笔记功能的完整流程
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

def test_recipe_edit_flow():
    """测试菜谱编辑完整流程"""
    print("=== 测试菜谱编辑流程 ===")
    
    recipe_id = 1  # 假设存在ID为1的菜谱
    
    # 1. 获取菜谱详情
    print("\n1. 获取菜谱详情...")
    try:
        response = requests.get(f'{BASE_URL}/api/recipes/{recipe_id}/')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            recipe_data = response.json()['data']
            print(f"✅ 获取菜谱成功: {recipe_data.get('name', 'Unknown')}")
            
            # 2. 修改菜谱数据
            print("\n2. 测试菜谱更新...")
            updated_data = {
                'name': recipe_data['name'] + ' (已编辑)',
                'description': recipe_data.get('description', '') + ' - 编辑测试',
                'cook_time': recipe_data.get('cook_time', 30) + 5,
                'servings': recipe_data.get('servings', 2),
                'difficulty': recipe_data.get('difficulty', 1),
                'category': recipe_data.get('category', 'meat'),
                'ingredients': recipe_data.get('ingredients', []),
                'steps': recipe_data.get('steps', []),
                'tags': recipe_data.get('tags', []) + ['编辑测试']
            }
            
            # 3. 提交更新
            response = requests.put(
                f'{BASE_URL}/api/recipes/{recipe_id}/',
                json=updated_data,
                headers={'Content-Type': 'application/json'}
            )
            print(f"更新状态码: {response.status_code}")
            print(f"更新响应: {response.text}")
            
            if response.status_code == 200:
                print("✅ 菜谱更新成功")
                
                # 4. 验证更新结果
                print("\n3. 验证更新结果...")
                response = requests.get(f'{BASE_URL}/api/recipes/{recipe_id}/')
                if response.status_code == 200:
                    updated_recipe = response.json()['data']
                    print(f"✅ 更新后的菜谱名称: {updated_recipe.get('name', 'Unknown')}")
                    print(f"✅ 更新后的制作时间: {updated_recipe.get('cook_time', 0)} 分钟")
                else:
                    print("❌ 验证更新结果失败")
            else:
                print("❌ 菜谱更新失败")
                
        else:
            print("❌ 获取菜谱详情失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_recipe_note_flow():
    """测试菜谱笔记完整流程"""
    print("\n=== 测试菜谱笔记流程 ===")
    
    recipe_id = 1  # 假设存在ID为1的菜谱
    
    # 1. 创建笔记
    print("\n1. 创建制作笔记...")
    note_data = {
        'content': '这是一个测试笔记，验证前后端同步功能是否正常。',
        'rating': 4,
        'success': True,
        'modifications': '下次可以稍微多加一点调料',
        'cooking_date': '2024-01-20T14:30:00Z',
        'author_openid': 'test_user_edit_flow'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/recipes/{recipe_id}/notes/',
            json=note_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"创建笔记状态码: {response.status_code}")
        print(f"创建笔记响应: {response.text}")
        
        if response.status_code == 201:
            note_result = response.json()['data']
            note_id = note_result['id']
            print(f"✅ 笔记创建成功，ID: {note_id}")
            
            # 2. 获取菜谱详情，验证笔记是否显示
            print("\n2. 验证菜谱详情中是否包含新笔记...")
            response = requests.get(f'{BASE_URL}/api/recipes/{recipe_id}/')
            if response.status_code == 200:
                recipe_data = response.json()['data']
                notes = recipe_data.get('notes', [])
                print(f"✅ 菜谱包含 {len(notes)} 条笔记")
                
                # 查找我们刚创建的笔记
                created_note = None
                for note in notes:
                    if note.get('id') == note_id:
                        created_note = note
                        break
                
                if created_note:
                    print(f"✅ 找到新创建的笔记: {created_note.get('content', '')[:20]}...")
                else:
                    print("❌ 未找到新创建的笔记")
            else:
                print("❌ 获取更新后的菜谱详情失败")
        else:
            print("❌ 笔记创建失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == '__main__':
    print("开始测试菜谱编辑和笔记功能...")
    
    # 测试菜谱编辑流程
    test_recipe_edit_flow()
    
    # 测试菜谱笔记流程
    test_recipe_note_flow()
    
    print("\n测试完成!")
