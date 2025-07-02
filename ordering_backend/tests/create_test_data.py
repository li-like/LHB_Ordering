#!/usr/bin/env python3
"""
创建家庭功能测试数据
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from wechat_auth.models import WeChatUser, Family, FamilyMembership

def create_test_users():
    """创建测试用户"""
    print("创建测试用户...")
    
    # 创建测试用户1
    user1, created1 = WeChatUser.objects.get_or_create(
        openid='test_user_001',
        defaults={
            'session_key': 'test_session_001',
            'nickname': '测试用户001',
            'avatar': 'https://example.com/avatar1.jpg'
        }
    )
    print(f"用户1: {user1.nickname} ({'新创建' if created1 else '已存在'})")
    
    # 创建测试用户2
    user2, created2 = WeChatUser.objects.get_or_create(
        openid='test_user_002',
        defaults={
            'session_key': 'test_session_002',
            'nickname': '测试用户002',
            'avatar': 'https://example.com/avatar2.jpg'
        }
    )
    print(f"用户2: {user2.nickname} ({'新创建' if created2 else '已存在'})")
    
    # 创建测试用户3
    user3, created3 = WeChatUser.objects.get_or_create(
        openid='test_user_003',
        defaults={
            'session_key': 'test_session_003',
            'nickname': '测试用户003',
            'avatar': 'https://example.com/avatar3.jpg'
        }
    )
    print(f"用户3: {user3.nickname} ({'新创建' if created3 else '已存在'})")
    
    return user1, user2, user3

def create_test_family():
    """创建测试家庭"""
    print("\n创建测试家庭...")
    
    user1, user2, user3 = create_test_users()
    
    # 创建测试家庭
    family, created = Family.objects.get_or_create(
        name='李家大院',
        defaults={
            'invite_code': '123456',
            'code_enabled': True,
            'max_members': 10
        }
    )
    print(f"家庭: {family.name} ({'新创建' if created else '已存在'})")
    print(f"邀请码: {family.invite_code}")
    
    # 创建家庭成员关系
    membership1, created1 = FamilyMembership.objects.get_or_create(
        user=user1,
        family=family,
        defaults={
            'display_name': '爸爸',
            'permission_level': 'admin'
        }
    )
    print(f"成员1: {user1.nickname} - {membership1.display_name} ({'新创建' if created1 else '已存在'})")
    
    membership2, created2 = FamilyMembership.objects.get_or_create(
        user=user2,
        family=family,
        defaults={
            'display_name': '妈妈',
            'permission_level': 'member'
        }
    )
    print(f"成员2: {user2.nickname} - {membership2.display_name} ({'新创建' if created2 else '已存在'})")
    
    return family

def show_test_data():
    """显示测试数据"""
    print("\n=== 当前测试数据 ===")
    
    print("\n用户列表:")
    for user in WeChatUser.objects.filter(openid__startswith='test_user'):
        print(f"  - {user.nickname} ({user.openid})")
    
    print("\n家庭列表:")
    for family in Family.objects.all():
        print(f"  - {family.name} (邀请码: {family.invite_code})")
        members = FamilyMembership.objects.filter(family=family, is_active=True)
        for member in members:
            print(f"    └─ {member.user.nickname} ({member.display_name}) - {member.permission_level}")

def main():
    print("🚀 创建家庭功能测试数据")
    
    try:
        # 创建测试用户
        create_test_users()
        
        # 创建测试家庭
        create_test_family()
        
        # 显示测试数据
        show_test_data()
        
        print("\n✅ 测试数据创建完成！")
        print("\n可以运行以下命令测试API:")
        print("python test_family_api.py")
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
