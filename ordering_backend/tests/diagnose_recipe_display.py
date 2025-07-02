#!/usr/bin/env python
"""
菜谱显示问题详细诊断脚本
检查API返回数据和前端显示的一致性
"""

import os
import sys
import django
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from recipes.models import Recipe, RecipeIngredient, RecipeStep, RecipeNote
from wechat_auth.models import WeChatUser, Family
from django.core.serializers.json import DjangoJSONEncoder

def check_recipe_display_issues():
    """检查菜谱显示问题"""
    print("=" * 60)
    print("🔍 菜谱显示问题详细诊断")
    print("=" * 60)
    
    # 获取所有菜谱
    recipes = Recipe.objects.all()
    print(f"\n📊 总共检查 {recipes.count()} 个菜谱")
    
    for recipe in recipes:
        print(f"\n{'='*40}")
        print(f"📝 菜谱: {recipe.name} (ID: {recipe.id})")
        print(f"👤 作者: {recipe.author.nickname} ({recipe.author.openid})")
        print(f"📅 创建时间: {recipe.created_at}")
        print(f"🏷️ 分类: {recipe.category}")
        
        # 检查食材
        ingredients = recipe.ingredients.all().order_by('order')
        print(f"\n🥕 食材 ({ingredients.count()}个):")
        for i, ingredient in enumerate(ingredients, 1):
            print(f"   {i}. {ingredient.name} - {ingredient.amount} {ingredient.unit}")
        
        # 检查步骤
        steps = recipe.steps.all().order_by('step_number')
        print(f"\n📝 步骤 ({steps.count()}个):")
        for step in steps:
            print(f"   {step.step_number}. {step.title or '(无标题)'}")
            print(f"      描述: {step.description[:50]}...")
            if step.time_required:
                print(f"      时间: {step.time_required}分钟")
            if step.temperature:
                print(f"      温度: {step.temperature}")
            if step.tips:
                print(f"      提示: {step.tips[:30]}...")
            print(f"      图片: {len(step.images)}张")
        
        # 检查数据完整性
        issues = []
        if not ingredients.exists():
            issues.append("❌ 没有食材")
        if not steps.exists():
            issues.append("❌ 没有步骤")
        
        # 检查步骤序号连续性
        if steps.exists():
            step_numbers = [step.step_number for step in steps]
            expected_numbers = list(range(1, len(step_numbers) + 1))
            if step_numbers != expected_numbers:
                issues.append(f"❌ 步骤序号不连续: {step_numbers} (应该是: {expected_numbers})")
        
        # 检查JSON字段
        try:
            if not isinstance(recipe.tags, list):
                issues.append("❌ 标签字段格式错误")
        except:
            issues.append("❌ 标签字段无法解析")
        
        for step in steps:
            try:
                if not isinstance(step.images, list):
                    issues.append(f"❌ 步骤{step.step_number}图片字段格式错误")
            except:
                issues.append(f"❌ 步骤{step.step_number}图片字段无法解析")
        
        if issues:
            print(f"\n⚠️  发现问题:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print(f"\n✅ 数据完整性良好")

def simulate_api_response():
    """模拟API响应，检查数据格式"""
    print(f"\n{'='*60}")
    print("🌐 模拟API响应数据格式检查")
    print("=" * 60)
    
    recipes = Recipe.objects.all()
    
    for recipe in recipes:
        print(f"\n📝 菜谱: {recipe.name} (ID: {recipe.id})")
        
        # 模拟列表API响应格式
        list_data = {
            'id': recipe.id,
            'name': recipe.name,
            'description': recipe.description,
            'category': recipe.category,
            'difficulty': recipe.difficulty,
            'cook_time': recipe.cook_time,
            'servings': recipe.servings,
            'cover_image': recipe.cover_image,
            'tags': recipe.tags,
            'author': {
                'openid': recipe.author.openid,
                'nickname': recipe.author.nickname,
                'avatar': recipe.author.avatar
            },
            'family': {
                'id': recipe.family.id,
                'name': recipe.family.name
            } if recipe.family else None,
            'is_public': recipe.is_public,
            'success_rate': recipe.success_rate,
            'rating': recipe.rating,
            'likes': recipe.likes,
            'created_at': recipe.created_at.isoformat(),
            'updated_at': recipe.updated_at.isoformat()
        }
        
        print("📊 列表API数据:")
        print(json.dumps(list_data, ensure_ascii=False, indent=2, cls=DjangoJSONEncoder))
        
        # 模拟详情API响应格式
        ingredients = []
        for ingredient in recipe.ingredients.all():
            ingredients.append({
                'id': ingredient.id,
                'name': ingredient.name,
                'amount': ingredient.amount,
                'unit': ingredient.unit,
                'category': ingredient.category,
                'notes': ingredient.notes,
                'order': ingredient.order
            })
        
        steps = []
        for step in recipe.steps.all():
            steps.append({
                'id': step.id,
                'step_number': step.step_number,
                'title': step.title,
                'description': step.description,
                'images': step.images,
                'time_required': step.time_required,
                'temperature': step.temperature,
                'tips': step.tips
            })
        
        detail_data = {
            **list_data,
            'first_try_date': recipe.first_try_date.isoformat() if recipe.first_try_date else None,
            'success_count': recipe.success_count,
            'total_attempts': recipe.total_attempts,
            'ingredients': ingredients,
            'steps': steps,
            'notes': []  # 简化显示
        }
        
        print(f"\n📋 详情API数据:")
        print(json.dumps(detail_data, ensure_ascii=False, indent=2, cls=DjangoJSONEncoder))
        
        print(f"\n{'='*40}")

def check_data_consistency():
    """检查数据一致性"""
    print(f"\n{'='*60}")
    print("🔄 检查数据一致性")
    print("=" * 60)
    
    recipes = Recipe.objects.all()
    
    for recipe in recipes:
        print(f"\n📝 菜谱: {recipe.name} (ID: {recipe.id})")
        
        # 检查模型字段是否与API字段一致
        required_fields = ['name', 'description', 'category', 'difficulty', 'cook_time', 'servings']
        missing_fields = []
        
        for field in required_fields:
            value = getattr(recipe, field, None)
            if value is None or value == '':
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   ⚠️  缺少必填字段: {missing_fields}")
        else:
            print(f"   ✅ 所有必填字段完整")
        
        # 检查关联数据
        ingredient_count = recipe.ingredients.count()
        step_count = recipe.steps.count()
        
        print(f"   📊 食材数量: {ingredient_count}")
        print(f"   📊 步骤数量: {step_count}")
        
        if ingredient_count == 0:
            print(f"   ❌ 没有食材数据")
        if step_count == 0:
            print(f"   ❌ 没有步骤数据")

if __name__ == '__main__':
    check_recipe_display_issues()
    simulate_api_response()
    check_data_consistency()
