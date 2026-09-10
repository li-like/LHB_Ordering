#!/usr/bin/env python3
"""
完整的前后端菜谱展示测试
"""

import os
import sys
import django
import requests

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from recipes.models import Recipe

def test_complete_flow():
    """完整测试菜谱展示流程"""
    print("============================================================")
    print("🔍 完整的前后端菜谱展示测试")
    print("============================================================")
    
    base_url = "http://192.168.189.240:8000"
    test_user = "ocYjt6oIJsFk2RgC7duPZVScsBV8"  # 冷汉堡
    
    # 1. 数据库状态检查
    print("1. 数据库状态检查:")
    recipes = Recipe.objects.all().order_by('-created_at')
    for recipe in recipes:
        print(f"   ID:{recipe.id} - {recipe.name} by {recipe.author.nickname} (公开:{recipe.is_public})")
    
    # 2. 模拟首页菜谱大全访问（无mode参数）
    print("\n2. 模拟首页菜谱大全访问:")
    print("   URL: /pages/recipe/index")
    print("   预期行为: pageMode='all', showUserRecipes=false")
    
    try:
        # 模拟前端调用（未登录）
        response = requests.get(f"{base_url}/api/recipes/?mode=all", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   未登录API结果: {len(data.get('data', []))} 个菜谱")
            for recipe in data.get('data', []):
                print(f"     - {recipe['name']} by {recipe['author']['nickname']} (公开:{recipe['is_public']})")
        
        # 模拟前端调用（已登录）
        response = requests.get(f"{base_url}/api/recipes/?mode=all&current_user={test_user}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   已登录API结果: {len(data.get('data', []))} 个菜谱")
            for recipe in data.get('data', []):
                can_edit = recipe.get('can_edit', False)
                print(f"     - {recipe['name']} by {recipe['author']['nickname']} (公开:{recipe['is_public']}, 可编辑:{can_edit})")
    except Exception as e:
        print(f"   API测试失败: {e}")
    
    # 3. 模拟我的菜谱访问
    print("\n3. 模拟我的菜谱访问:")
    print("   URL: /pages/recipe/index?mode=user")
    print("   预期行为: pageMode='user', showUserRecipes=true")
    
    try:
        response = requests.get(f"{base_url}/api/recipes/?mode=user&author={test_user}&current_user={test_user}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   我的菜谱API结果: {len(data.get('data', []))} 个菜谱")
            for recipe in data.get('data', []):
                can_edit = recipe.get('can_edit', False)
                print(f"     - {recipe['name']} by {recipe['author']['nickname']} (公开:{recipe['is_public']}, 可编辑:{can_edit})")
    except Exception as e:
        print(f"   API测试失败: {e}")
    
    # 4. 前端逻辑检查
    print("\n4. 前端逻辑检查:")
    print("   菜谱大全模式:")
    print("     - 页面标题: '菜谱大全'")
    print("     - 显示作者信息: 是")
    print("     - 显示创建按钮: 否")
    print("     - 显示可编辑标识: 仅对自己的菜谱")
    
    print("   我的菜谱模式:")
    print("     - 页面标题: '我的菜谱'")
    print("     - 显示作者信息: 否（因为都是自己的）")
    print("     - 显示创建按钮: 是")
    print("     - 显示可编辑标识: 是")
    
    # 5. 总结
    print("\n5. 问题诊断:")
    if Recipe.objects.filter(is_public=True).count() == 2:
        print("   ✅ 公开菜谱数量正确 (2个)")
    else:
        print("   ❌ 公开菜谱数量异常")
    
    if Recipe.objects.filter(author__openid=test_user).count() == 3:
        print("   ✅ 测试用户菜谱数量正确 (3个)")
    else:
        print("   ❌ 测试用户菜谱数量异常")
    
    print("\n6. 建议检查项:")
    print("   - 前端小程序是否已重新编译？")
    print("   - 小程序开发者工具是否已刷新？")
    print("   - 网络请求是否正常？")
    print("   - 浏览器控制台是否有错误信息？")

if __name__ == '__main__':
    test_complete_flow()
