#!/usr/bin/env python
"""
快速创建测试数据脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from django.utils import timezone
from wechat_auth.models import WeChatUser, Family, FamilyMembership
from ordering.models import MealCategory, MealItem, MealRequest

def create_test_data():
    print("开始创建测试数据...")

    # 1. 创建测试用户
    user1, created = WeChatUser.objects.get_or_create(
        openid='test_user_001',
        defaults={
            'session_key': 'test_session_001',
            'nickname': '小明',
            'avatar_url': 'https://example.com/avatar1.jpg'
        }
    )
    if created:
        print(f"创建用户: {user1.nickname}")

    user2, created = WeChatUser.objects.get_or_create(
        openid='test_user_002',
        defaults={
            'session_key': 'test_session_002',
            'nickname': '小红',
            'avatar_url': 'https://example.com/avatar2.jpg'
        }
    )
    if created:
        print(f"创建用户: {user2.nickname}")

    # 2. 创建测试家庭
    import random
    invite_code = f"{random.randint(100000, 999999)}"
    
    family, created = Family.objects.get_or_create(
        name='温馨家庭',
        defaults={
            'invite_code': invite_code,
            'max_members': 10
        }
    )
    if created:
        print(f"创建家庭: {family.name}")

    # 3. 创建家庭成员关系
    membership1, created = FamilyMembership.objects.get_or_create(
        user=user1,
        family=family,
        defaults={
            'display_name': '爸爸',
            'permission_level': 'admin'
        }
    )

    membership2, created = FamilyMembership.objects.get_or_create(
        user=user2,
        family=family,
        defaults={
            'display_name': '妈妈',
            'permission_level': 'member'
        }
    )

    # 4. 创建餐品分类
    categories_data = [
        {'name': '家常菜', 'icon': '🥩', 'description': '日常家庭料理', 'sort_order': 1},
        {'name': '汤品', 'icon': '🍲', 'description': '营养汤类', 'sort_order': 2},
        {'name': '主食', 'icon': '🍚', 'description': '米饭面条等主食', 'sort_order': 3},
        {'name': '素菜', 'icon': '🥬', 'description': '健康蔬菜', 'sort_order': 4},
        {'name': '小食', 'icon': '🥟', 'description': '小点心零食', 'sort_order': 5}
    ]

    categories = []
    for cat_data in categories_data:
        category, created = MealCategory.objects.get_or_create(
            family=family,
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'icon': cat_data['icon'],
                'sort_order': cat_data['sort_order'],
                'created_by': user1
            }
        )
        categories.append(category)
        if created:
            print(f"创建分类: {category.name}")

    # 5. 创建餐品
    meals_data = [
        {
            'name': '红烧肉',
            'category': categories[0],  # 家常菜
            'description': '香甜软糯的红烧肉，肥瘦相间',
            'meal_type': 'lunch',
            'difficulty': 'medium',
            'prep_time': 60,
            'ingredients': ['五花肉', '生抽', '老抽', '冰糖', '料酒', '葱', '姜'],
            'cooking_steps': ['切肉块', '焯水去腥', '炒糖色', '炖煮1小时'],
            'tags': ['下饭', '荤菜', '传统'],
            'popularity': 8
        },
        {
            'name': '番茄鸡蛋',
            'category': categories[0],  # 家常菜
            'description': '简单快手的番茄炒蛋',
            'meal_type': 'lunch',
            'difficulty': 'easy',
            'prep_time': 15,
            'ingredients': ['鸡蛋', '番茄', '盐', '糖', '葱花'],
            'cooking_steps': ['打散鸡蛋', '炒蛋盛起', '炒番茄', '混合炒制'],
            'tags': ['快手菜', '下饭', '经典'],
            'popularity': 10
        },
        {
            'name': '紫菜蛋花汤',
            'category': categories[1],  # 汤品
            'description': '清淡营养的汤品',
            'meal_type': 'dinner',
            'difficulty': 'easy',
            'prep_time': 10,
            'ingredients': ['紫菜', '鸡蛋', '香油', '盐', '葱花'],
            'cooking_steps': ['水开放紫菜', '打入蛋花', '调味出锅'],
            'tags': ['清汤', '营养', '简单'],
            'popularity': 6
        },
        {
            'name': '白米饭',
            'category': categories[2],  # 主食
            'description': '香喷喷的大米饭',
            'meal_type': 'lunch',
            'difficulty': 'easy',
            'prep_time': 30,
            'ingredients': ['大米', '水'],
            'cooking_steps': ['淘米', '加水', '电饭煲蒸煮'],
            'tags': ['主食', '必备'],
            'popularity': 5
        },
        {
            'name': '清炒小白菜',
            'category': categories[3],  # 素菜
            'description': '清爽的素菜',
            'meal_type': 'lunch',
            'difficulty': 'easy',
            'prep_time': 10,
            'ingredients': ['小白菜', '蒜', '盐', '油'],
            'cooking_steps': ['洗菜切段', '爆炒蒜蓉', '下菜炒制'],
            'tags': ['素菜', '清淡', '健康'],
            'popularity': 4
        }
    ]

    meals = []
    for meal_data in meals_data:
        meal, created = MealItem.objects.get_or_create(
            family=family,
            name=meal_data['name'],
            defaults={
                'category': meal_data['category'],
                'description': meal_data['description'],
                'meal_type': meal_data['meal_type'],
                'difficulty': meal_data['difficulty'],
                'prep_time': meal_data['prep_time'],
                'ingredients': meal_data['ingredients'],
                'cooking_steps': meal_data['cooking_steps'],
                'tags': meal_data['tags'],
                'popularity': meal_data['popularity'],
                'created_by': user1
            }
        )
        meals.append(meal)
        if created:
            print(f"创建餐品: {meal.name}")

    # 6. 创建一些点餐需求
    requests_data = [
        {
            'meal': meals[0],  # 红烧肉
            'requester': user2,
            'quantity': 1,
            'priority': 'normal',
            'special_requests': '请少放糖'
        },
        {
            'meal': meals[1],  # 番茄鸡蛋
            'requester': user2,
            'quantity': 1,
            'priority': 'high',
            'special_requests': '多放点番茄'
        },
        {
            'meal': meals[3],  # 白米饭
            'requester': user1,
            'quantity': 2,
            'priority': 'normal',
            'special_requests': '要软糯一点'
        }
    ]

    for req_data in requests_data:
        request, created = MealRequest.objects.get_or_create(
            family=family,
            requester=req_data['requester'],
            meal_item=req_data['meal'],
            defaults={
                'quantity': req_data['quantity'],
                'priority': req_data['priority'],
                'special_requests': req_data['special_requests'],
                'preferred_time': timezone.now() + timezone.timedelta(hours=2)
            }
        )
        if created:
            print(f"创建点餐需求: {request.requester.nickname} 点了 {request.meal_item.name}")

    print("\n✅ 测试数据创建完成！")
    print(f"📊 数据统计:")
    print(f"   - 用户: {WeChatUser.objects.count()} 个")
    print(f"   - 家庭: {Family.objects.count()} 个")
    print(f"   - 餐品分类: {MealCategory.objects.filter(family=family).count()} 个")
    print(f"   - 餐品: {MealItem.objects.filter(family=family).count()} 个")
    print(f"   - 点餐需求: {MealRequest.objects.filter(family=family).count()} 个")

if __name__ == '__main__':
    create_test_data()
