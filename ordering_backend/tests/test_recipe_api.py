#!/usr/bin/env python
"""
菜谱API测试脚本
用于测试前后端菜谱相关API的连通性
"""

import os
import sys
import django
import requests
import json

# 添加Django项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')

# 初始化Django
django.setup()

from recipes.models import Recipe, RecipeIngredient, RecipeStep
from wechat_auth.models import WeChatUser, Family

# API基础URL - 需要根据实际情况修改
BASE_URL = 'http://127.0.0.1:8000'

def test_recipe_apis():
    """测试菜谱相关API"""
    
    print("=" * 50)
    print("开始测试菜谱API连通性")
    print("=" * 50)
    
    # 1. 测试获取菜谱列表
    print("\n1. 测试获取菜谱列表...")
    try:
        response = requests.get(f'{BASE_URL}/api/recipes/')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试获取菜谱详情
    print("\n2. 测试获取菜谱详情...")
    try:
        # 获取第一个菜谱的ID
        recipes = Recipe.objects.all()
        if recipes.exists():
            recipe_id = recipes.first().id
            response = requests.get(f'{BASE_URL}/api/recipes/{recipe_id}/')
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"错误响应: {response.text}")
        else:
            print("数据库中没有菜谱数据")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 测试创建菜谱
    print("\n3. 测试创建菜谱...")
    try:
        # 获取一个用户
        user = WeChatUser.objects.first()
        if user:
            recipe_data = {
                'name': 'API测试菜谱',
                'description': '这是通过API创建的测试菜谱',
                'category': 'meat',
                'cook_time': 30,
                'servings': 2,
                'difficulty': 2,
                'author_openid': user.openid,
                'ingredients': [
                    {'name': '测试食材1', 'amount': '100', 'unit': '克'},
                    {'name': '测试食材2', 'amount': '1', 'unit': '个'}
                ],
                'steps': [
                    {'description': '第一步：准备食材'},
                    {'description': '第二步：开始制作'}
                ],
                'tags': ['测试', 'API']
            }
            
            response = requests.post(
                f'{BASE_URL}/api/recipes/',
                json=recipe_data,
                headers={'Content-Type': 'application/json'}
            )
            print(f"状态码: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"创建成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return data.get('id')  # 返回创建的菜谱ID
            else:
                print(f"错误响应: {response.text}")
        else:
            print("数据库中没有用户数据")
    except Exception as e:
        print(f"请求失败: {e}")
    
    return None

def test_database_status():
    """测试数据库状态"""
    
    print("\n" + "=" * 50)
    print("数据库状态检查")
    print("=" * 50)
    
    # 检查用户数据
    user_count = WeChatUser.objects.count()
    print(f"用户数量: {user_count}")
    
    # 检查家庭数据
    family_count = Family.objects.count()
    print(f"家庭数量: {family_count}")
    
    # 检查菜谱数据
    recipe_count = Recipe.objects.count()
    print(f"菜谱数量: {recipe_count}")
    
    if recipe_count > 0:
        print("\n菜谱列表:")
        for recipe in Recipe.objects.all()[:5]:  # 显示前5个
            print(f"- ID: {recipe.id}, 名称: {recipe.name}, 作者: {recipe.author.nickname}")
    
    # 检查食材数据
    ingredient_count = RecipeIngredient.objects.count()
    print(f"食材记录数量: {ingredient_count}")
    
    # 检查步骤数据
    step_count = RecipeStep.objects.count()
    print(f"步骤记录数量: {step_count}")

def create_test_user_and_family():
    """创建测试用户和家庭"""
    
    print("\n" + "=" * 50)
    print("创建测试数据")
    print("=" * 50)
    
    # 创建测试用户
    test_user, created = WeChatUser.objects.get_or_create(
        openid='test_api_user_001',
        defaults={
            'nickname': 'API测试用户',
            'avatar': '',
            'phone': '13800138000'
        }
    )
    
    if created:
        print(f"创建测试用户: {test_user.nickname} ({test_user.openid})")
    else:
        print(f"使用现有测试用户: {test_user.nickname} ({test_user.openid})")
    
    # 创建测试家庭
    test_family, created = Family.objects.get_or_create(
        name='API测试家庭',
        defaults={
            'creator': test_user,
            'description': '用于API测试的家庭'
        }
    )
    
    if created:
        print(f"创建测试家庭: {test_family.name}")
        # 将创建者添加为家庭成员
        test_family.members.add(test_user)
    else:
        print(f"使用现有测试家庭: {test_family.name}")
    
    return test_user, test_family

def main():
    """主函数"""
    
    print("菜谱API测试工具")
    print("确保Django服务已启动 (python manage.py runserver)")
    
    # 创建测试数据
    test_user, test_family = create_test_user_and_family()
    
    # 检查数据库状态
    test_database_status()
    
    # 测试API
    new_recipe_id = test_recipe_apis()
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)
    
    if new_recipe_id:
        print(f"新创建的菜谱ID: {new_recipe_id}")
        print("可以在前端使用这个ID进行详情页测试")

if __name__ == '__main__':
    main()
