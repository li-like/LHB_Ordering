#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
诊断菜谱数据混乱问题
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from recipes.models import Recipe, RecipeIngredient, RecipeStep
from wechat_auth.models import WeChatUser

def diagnose_recipe_data():
    """诊断菜谱数据问题"""
    
    print("=== 菜谱数据诊断 ===")
    
    # 1. 检查所有菜谱
    print("\n1. 当前数据库中的所有菜谱:")
    recipes = Recipe.objects.all().order_by('id')
    
    for recipe in recipes:
        print(f"ID: {recipe.id}")
        print(f"名称: {recipe.name}")
        print(f"描述: {recipe.description[:50]}..." if len(recipe.description) > 50 else f"描述: {recipe.description}")
        print(f"作者: {recipe.author.nickname}")
        print(f"创建时间: {recipe.created_at}")
        print(f"食材数量: {recipe.ingredients.count()}")
        print(f"步骤数量: {recipe.steps.count()}")
        print("-" * 50)
    
    # 2. 检查是否有ID重复或者关联错误
    print("\n2. 检查数据一致性:")
    
    for recipe in recipes:
        # 检查食材关联
        ingredients = recipe.ingredients.all()
        print(f"\n菜谱 '{recipe.name}' (ID: {recipe.id}) 的食材:")
        for ing in ingredients:
            print(f"  - {ing.name} {ing.amount} {ing.unit}")
        
        # 检查步骤关联
        steps = recipe.steps.all().order_by('step_number')
        print(f"菜谱 '{recipe.name}' (ID: {recipe.id}) 的步骤:")
        for step in steps:
            print(f"  {step.step_number}. {step.description[:30]}...")
    
    # 3. 检查最近创建的菜谱
    print("\n3. 最近创建的菜谱:")
    recent_recipes = Recipe.objects.all().order_by('-created_at')[:3]
    for recipe in recent_recipes:
        print(f"- {recipe.name} (ID: {recipe.id}, 创建时间: {recipe.created_at})")

if __name__ == "__main__":
    diagnose_recipe_data()
