#!/usr/bin/env python3
"""
修复菜谱图片路径问题的脚本
处理微信临时文件路径等不可用的图片路径
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from recipes.models import Recipe, RecipeStep
from django.db import transaction
from django.utils import timezone
import json

def fix_recipe_image_paths():
    """修复菜谱图片路径"""
    print("============================================================")
    print("🔧 开始修复菜谱图片路径")
    print("============================================================")
    
    # 需要修复的图片路径模式
    invalid_path_patterns = [
        'wxfile://',  # 微信临时文件
        'tmp_',       # 临时文件
    ]
    
    # 默认替换图片
    default_cover_image = '/static/food-decoration.png'
    
    fixed_count = 0
    total_recipes = Recipe.objects.count()
    
    print(f"📊 检查 {total_recipes} 个菜谱的图片路径...")
    
    with transaction.atomic():
        # 修复菜谱封面图片
        recipes_to_fix = []
        for recipe in Recipe.objects.all():
            needs_fix = False
            original_image = recipe.cover_image
            
            if recipe.cover_image:
                for pattern in invalid_path_patterns:
                    if pattern in recipe.cover_image:
                        needs_fix = True
                        break
            
            if needs_fix:
                recipes_to_fix.append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'original_image': original_image,
                    'recipe': recipe
                })
        
        # 批量修复菜谱封面
        for item in recipes_to_fix:
            recipe = item['recipe']
            
            # 根据菜谱类别选择默认图片
            category_images = {
                'meat': '/static/dishes/meat_default.jpg',
                'vegetable': '/static/dishes/vegetable_default.jpg',
                'soup': '/static/dishes/soup_default.jpg',
                'staple': '/static/dishes/staple_default.jpg',
                'snack': '/static/dishes/snack_default.jpg',
                'dessert': '/static/dishes/dessert_default.jpg',
                'other': default_cover_image
            }
            
            new_image = category_images.get(recipe.category, default_cover_image)
            recipe.cover_image = new_image
            recipe.save(update_fields=['cover_image'])
            
            print(f"✅ 修复菜谱 [{item['id']}] {item['name']}")
            print(f"   原图片: {item['original_image']}")
            print(f"   新图片: {new_image}")
            print()
            
            fixed_count += 1
        
        # 修复步骤图片
        print("🔍 检查步骤图片...")
        steps_to_fix = []
        
        for step in RecipeStep.objects.all():
            if step.images:
                try:
                    images = step.images if isinstance(step.images, list) else json.loads(step.images)
                    needs_fix = False
                    
                    for image_path in images:
                        if isinstance(image_path, str):
                            for pattern in invalid_path_patterns:
                                if pattern in image_path:
                                    needs_fix = True
                                    break
                    
                    if needs_fix:
                        steps_to_fix.append({
                            'id': step.id,
                            'recipe_name': step.recipe.name,
                            'step_title': step.title,
                            'original_images': images.copy(),
                            'step': step
                        })
                        
                except (json.JSONDecodeError, TypeError):
                    # 图片数据格式错误，清空
                    steps_to_fix.append({
                        'id': step.id,
                        'recipe_name': step.recipe.name,
                        'step_title': step.title,
                        'original_images': step.images,
                        'step': step
                    })
        
        # 批量修复步骤图片
        for item in steps_to_fix:
            step = item['step']
            
            # 清空无效图片
            step.images = []
            step.save(update_fields=['images'])
            
            print(f"✅ 修复步骤 [{item['id']}] {item['recipe_name']} - {item['step_title']}")
            print(f"   原图片: {item['original_images']}")
            print(f"   新图片: []")
            print()
            
            fixed_count += 1
    
    print("============================================================")
    print(f"✅ 修复完成! 共修复 {fixed_count} 项")
    print("============================================================")

def create_default_image_files():
    """创建默认图片文件提示"""
    print("\n💡 建议创建以下默认图片文件:")
    print("   static/dishes/meat_default.jpg")
    print("   static/dishes/vegetable_default.jpg") 
    print("   static/dishes/soup_default.jpg")
    print("   static/dishes/staple_default.jpg")
    print("   static/dishes/snack_default.jpg")
    print("   static/dishes/dessert_default.jpg")
    print("\n   或者复制现有的 food-decoration.png 作为通用默认图片")

def verify_fix():
    """验证修复结果"""
    print("\n🔍 验证修复结果...")
    
    invalid_recipes = []
    invalid_steps = []
    
    # 检查菜谱封面
    for recipe in Recipe.objects.all():
        if recipe.cover_image:
            for pattern in ['wxfile://', 'tmp_']:
                if pattern in recipe.cover_image:
                    invalid_recipes.append(f"菜谱 {recipe.id}: {recipe.cover_image}")
    
    # 检查步骤图片
    for step in RecipeStep.objects.all():
        if step.images:
            try:
                images = step.images if isinstance(step.images, list) else json.loads(step.images)
                for image_path in images:
                    if isinstance(image_path, str):
                        for pattern in ['wxfile://', 'tmp_']:
                            if pattern in image_path:
                                invalid_steps.append(f"步骤 {step.id}: {image_path}")
            except:
                invalid_steps.append(f"步骤 {step.id}: JSON格式错误")
    
    if not invalid_recipes and not invalid_steps:
        print("✅ 验证通过! 所有无效图片路径已修复")
    else:
        print("⚠️  仍有问题需要处理:")
        for item in invalid_recipes:
            print(f"   {item}")
        for item in invalid_steps:
            print(f"   {item}")

if __name__ == '__main__':
    try:
        fix_recipe_image_paths()
        create_default_image_files()
        verify_fix()
        
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
