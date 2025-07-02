#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
清理重复的菜谱数据并修复数据混乱问题
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

def clean_duplicate_recipes():
    """清理重复的菜谱数据"""
    
    print("=== 清理重复菜谱数据 ===")
    
    # 查找所有菜谱
    recipes = Recipe.objects.all().order_by('id')
    
    print("清理前的菜谱:")
    for recipe in recipes:
        print(f"ID: {recipe.id}, 名称: {recipe.name}, 作者: {recipe.author.nickname}")
        print(f"  食材: {recipe.ingredients.count()}, 步骤: {recipe.steps.count()}")
    
    # 找出重复的鸡蛋葱油饼
    egg_pancake_recipes = Recipe.objects.filter(name__icontains="鸡蛋葱油饼")
    
    if len(egg_pancake_recipes) > 1:
        print(f"\n发现 {len(egg_pancake_recipes)} 个鸡蛋葱油饼菜谱:")
        
        for recipe in egg_pancake_recipes:
            print(f"ID: {recipe.id}, 创建时间: {recipe.created_at}")
            print(f"  食材数: {recipe.ingredients.count()}, 步骤数: {recipe.steps.count()}")
            print(f"  作者: {recipe.author.nickname}")
        
        # 保留有完整数据的那个，删除空的
        recipes_to_delete = []
        
        for recipe in egg_pancake_recipes:
            if recipe.ingredients.count() == 0 and recipe.steps.count() == 0:
                recipes_to_delete.append(recipe)
        
        if recipes_to_delete:
            print(f"\n将删除 {len(recipes_to_delete)} 个空的菜谱:")
            for recipe in recipes_to_delete:
                print(f"  删除: ID {recipe.id} - {recipe.name}")
                recipe.delete()
            
            print("✅ 清理完成")
        else:
            print("所有鸡蛋葱油饼菜谱都有数据，需要手动检查")
    
    # 再次检查数据
    print("\n清理后的菜谱:")
    recipes = Recipe.objects.all().order_by('id')
    for recipe in recipes:
        print(f"ID: {recipe.id}, 名称: {recipe.name}, 作者: {recipe.author.nickname}")
        print(f"  食材: {recipe.ingredients.count()}, 步骤: {recipe.steps.count()}")

def verify_recipe_data_integrity():
    """验证菜谱数据完整性"""
    
    print("\n=== 验证数据完整性 ===")
    
    recipes = Recipe.objects.all()
    
    for recipe in recipes:
        print(f"\n菜谱: {recipe.name} (ID: {recipe.id})")
        
        # 检查食材
        ingredients = recipe.ingredients.all()
        print(f"  食材 ({len(ingredients)} 个):")
        for ing in ingredients:
            print(f"    - {ing.name} {ing.amount} {ing.unit}")
        
        # 检查步骤
        steps = recipe.steps.all().order_by('step_number')
        print(f"  步骤 ({len(steps)} 个):")
        for step in steps:
            print(f"    {step.step_number}. {step.description[:50]}...")

if __name__ == "__main__":
    clean_duplicate_recipes()
    verify_recipe_data_integrity()
