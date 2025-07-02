#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地测试菜谱API功能（不需要启动服务器）
"""

import os
import sys
import django
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from django.test import RequestFactory
from recipes.views import RecipeListView, RecipeDetailView
from recipes.models import Recipe

def test_recipe_list_api():
    """测试菜谱列表API"""
    
    print("=== 测试菜谱列表API ===")
    
    factory = RequestFactory()
    view = RecipeListView()
    
    # 模拟GET请求
    request = factory.get('/api/recipes/')
    response = view.get(request)
    
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {response.data}")
    
    if response.data.get('success'):
        recipes = response.data.get('data', [])
        print(f"\n返回的菜谱列表 ({len(recipes)} 个):")
        for i, recipe in enumerate(recipes):
            print(f"{i+1}. ID: {recipe['id']}, 名称: {recipe['name']}")
            print(f"   作者: {recipe['author']['nickname']}")
    
    return response.data

def test_recipe_detail_api():
    """测试菜谱详情API"""
    
    print("\n=== 测试菜谱详情API ===")
    
    factory = RequestFactory()
    view = RecipeDetailView()
    
    # 测试所有现有菜谱的详情
    recipes = Recipe.objects.all()
    
    for recipe in recipes:
        print(f"\n测试菜谱ID {recipe.id} ({recipe.name}):")
        
        request = factory.get(f'/api/recipes/{recipe.id}/')
        response = view.get(request, recipe_id=recipe.id)
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200 and response.data.get('success'):
            recipe_data = response.data.get('data')
            print(f"  返回名称: {recipe_data['name']}")
            print(f"  返回描述: {recipe_data['description'][:50]}...")
            print(f"  食材数量: {len(recipe_data['ingredients'])}")
            print(f"  步骤数量: {len(recipe_data['steps'])}")
            
            if recipe_data['ingredients']:
                print(f"  第一个食材: {recipe_data['ingredients'][0]['name']}")
            if recipe_data['steps']:
                print(f"  第一个步骤: {recipe_data['steps'][0]['description'][:30]}...")
        else:
            print(f"  ❌ 错误: {response.data}")

def verify_id_consistency():
    """验证ID一致性"""
    
    print("\n=== 验证ID一致性 ===")
    
    recipes = Recipe.objects.all().order_by('id')
    
    print("数据库中的菜谱:")
    for recipe in recipes:
        print(f"ID: {recipe.id}, 名称: {recipe.name}")
    
    # 测试前端可能遇到的情况
    print("\n模拟前端请求:")
    
    # 模拟前端获取列表
    factory = RequestFactory()
    list_view = RecipeListView()
    list_request = factory.get('/api/recipes/')
    list_response = list_view.get(list_request)
    
    if list_response.data.get('success'):
        api_recipes = list_response.data.get('data', [])
        print(f"API返回的菜谱列表:")
        for recipe in api_recipes:
            print(f"ID: {recipe['id']}, 名称: {recipe['name']}")
        
        # 检查每个ID的详情
        detail_view = RecipeDetailView()
        for api_recipe in api_recipes:
            recipe_id = api_recipe['id']
            detail_request = factory.get(f'/api/recipes/{recipe_id}/')
            detail_response = detail_view.get(detail_request, recipe_id=recipe_id)
            
            if detail_response.data.get('success'):
                detail_data = detail_response.data.get('data')
                list_name = api_recipe['name']
                detail_name = detail_data['name']
                
                if list_name == detail_name:
                    print(f"✅ ID {recipe_id}: 列表和详情数据一致 ({list_name})")
                else:
                    print(f"❌ ID {recipe_id}: 数据不一致!")
                    print(f"    列表中: {list_name}")
                    print(f"    详情中: {detail_name}")

if __name__ == "__main__":
    test_recipe_list_api()
    test_recipe_detail_api()
    verify_id_consistency()
