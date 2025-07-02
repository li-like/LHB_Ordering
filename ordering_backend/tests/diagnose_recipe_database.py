#!/usr/bin/env python
"""
菜谱数据库诊断脚本
检查数据完整性和一致性问题
"""

import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from recipes.models import Recipe, RecipeIngredient, RecipeStep, RecipeNote
from wechat_auth.models import WeChatUser, Family
from django.db.models import Count, Q

def diagnose_database():
    """诊断数据库问题"""
    print("=" * 60)
    print("📊 菜谱数据库诊断报告")
    print("=" * 60)
    
    # 1. 基本统计信息
    print("\n1️⃣ 基本统计信息:")
    print(f"   📝 菜谱总数: {Recipe.objects.count()}")
    print(f"   🥕 食材总数: {RecipeIngredient.objects.count()}")
    print(f"   📝 步骤总数: {RecipeStep.objects.count()}")
    print(f"   📋 笔记总数: {RecipeNote.objects.count()}")
    print(f"   👥 用户总数: {WeChatUser.objects.count()}")
    print(f"   👨‍👩‍👧‍👦 家庭总数: {Family.objects.count()}")
    
    # 2. 检查孤立菜谱（没有食材或步骤的菜谱）
    print("\n2️⃣ 检查数据完整性:")
    recipes_without_ingredients = Recipe.objects.annotate(
        ingredient_count=Count('ingredients')
    ).filter(ingredient_count=0)
    print(f"   ⚠️  没有食材的菜谱: {recipes_without_ingredients.count()}")
    
    recipes_without_steps = Recipe.objects.annotate(
        step_count=Count('steps')
    ).filter(step_count=0)
    print(f"   ⚠️  没有步骤的菜谱: {recipes_without_steps.count()}")
    
    # 3. 检查重复名称
    print("\n3️⃣ 检查重复名称:")
    duplicate_names = Recipe.objects.values('author', 'name').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    print(f"   ⚠️  重复名称的菜谱: {duplicate_names.count()}")
    
    # 4. 检查步骤序号问题
    print("\n4️⃣ 检查步骤序号:")
    recipes_with_step_issues = []
    for recipe in Recipe.objects.all():
        steps = recipe.steps.all().order_by('step_number')
        if steps.exists():
            step_numbers = [step.step_number for step in steps]
            expected_numbers = list(range(1, len(step_numbers) + 1))
            if step_numbers != expected_numbers:
                recipes_with_step_issues.append(recipe)
    print(f"   ⚠️  步骤序号有问题的菜谱: {len(recipes_with_step_issues)}")
    
    # 5. 检查作者关联问题
    print("\n5️⃣ 检查关联问题:")
    recipes_without_author = Recipe.objects.filter(author__isnull=True)
    print(f"   ⚠️  没有作者的菜谱: {recipes_without_author.count()}")
    
    # 6. 详细报告问题菜谱
    print("\n6️⃣ 问题菜谱详情:")
    
    if recipes_without_ingredients.exists():
        print("   📋 没有食材的菜谱:")
        for recipe in recipes_without_ingredients[:5]:  # 只显示前5个
            print(f"      - ID: {recipe.id}, 名称: {recipe.name}, 作者: {recipe.author.nickname}")
    
    if recipes_without_steps.exists():
        print("   📋 没有步骤的菜谱:")
        for recipe in recipes_without_steps[:5]:  # 只显示前5个
            print(f"      - ID: {recipe.id}, 名称: {recipe.name}, 作者: {recipe.author.nickname}")
    
    if duplicate_names:
        print("   📋 重复名称的菜谱:")
        for dup in duplicate_names[:5]:  # 只显示前5个
            author = WeChatUser.objects.get(id=dup['author'])
            recipes = Recipe.objects.filter(author=author, name=dup['name'])
            print(f"      - 作者: {author.nickname}, 名称: {dup['name']}, 数量: {dup['count']}")
            for recipe in recipes:
                print(f"        * ID: {recipe.id}, 创建时间: {recipe.created_at}")
    
    if recipes_with_step_issues:
        print("   📋 步骤序号有问题的菜谱:")
        for recipe in recipes_with_step_issues[:5]:  # 只显示前5个
            steps = recipe.steps.all().order_by('step_number')
            step_numbers = [step.step_number for step in steps]
            print(f"      - ID: {recipe.id}, 名称: {recipe.name}")
            print(f"        步骤序号: {step_numbers}")
            print(f"        应该是: {list(range(1, len(step_numbers) + 1))}")
    
    # 7. 数据库约束检查
    print("\n7️⃣ 数据库约束检查:")
    
    # 检查是否有同一菜谱的重复步骤序号
    duplicate_steps = RecipeStep.objects.values('recipe', 'step_number').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    print(f"   ⚠️  重复步骤序号: {duplicate_steps.count()}")
    
    # 检查JSON字段
    invalid_tags = Recipe.objects.exclude(tags__isnull=True).exclude(tags__exact=[])
    valid_tags_count = 0
    for recipe in invalid_tags:
        try:
            if isinstance(recipe.tags, list):
                valid_tags_count += 1
        except:
            print(f"   ⚠️  无效标签数据: 菜谱ID {recipe.id}")
    
    print("\n=" * 60)
    print("✅ 诊断完成！")
    print("=" * 60)
    
    return {
        'recipes_without_ingredients': recipes_without_ingredients.count(),
        'recipes_without_steps': recipes_without_steps.count(),
        'duplicate_names': duplicate_names.count(),
        'step_issues': len(recipes_with_step_issues),
        'duplicate_steps': duplicate_steps.count()
    }

def suggest_fixes(diagnosis_result):
    """建议修复方案"""
    print("\n🔧 建议修复方案:")
    
    if diagnosis_result['recipes_without_ingredients'] > 0:
        print("   1. 删除没有食材的菜谱，或为其添加默认食材")
    
    if diagnosis_result['recipes_without_steps'] > 0:
        print("   2. 删除没有步骤的菜谱，或为其添加默认步骤")
    
    if diagnosis_result['duplicate_names'] > 0:
        print("   3. 处理重复名称的菜谱（删除重复或重命名）")
    
    if diagnosis_result['step_issues'] > 0:
        print("   4. 修复步骤序号（重新编号）")
    
    if diagnosis_result['duplicate_steps'] > 0:
        print("   5. 删除重复的步骤记录")
    
    print("\n💡 运行修复脚本:")
    print("   python fix_recipe_data.py")

if __name__ == '__main__':
    diagnosis_result = diagnose_database()
    suggest_fixes(diagnosis_result)
