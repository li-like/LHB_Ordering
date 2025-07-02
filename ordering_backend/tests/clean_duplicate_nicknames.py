#!/usr/bin/env python
"""
数据库迁移和数据清理脚本
用于处理昵称唯一性约束相关的数据库问题

运行步骤：
1. 首先运行此脚本清理重复昵称
2. 然后运行 python manage.py makemigrations
3. 最后运行 python manage.py migrate
"""

import os
import sys
import django
from collections import defaultdict

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from wechat_auth.models import WeChatUser

def clean_duplicate_nicknames():
    """清理重复的昵称数据"""
    print("开始清理重复昵称数据...")
    
    # 统计昵称重复情况
    nickname_count = defaultdict(list)
    users = WeChatUser.objects.all()
    
    for user in users:
        if user.nickname:
            nickname_count[user.nickname].append(user)
    
    # 找出重复的昵称
    duplicates = {nick: users for nick, users in nickname_count.items() if len(users) > 1}
    
    if not duplicates:
        print("没有发现重复的昵称，可以安全添加唯一性约束。")
        return
    
    print(f"发现 {len(duplicates)} 个重复昵称:")
    
    for nickname, duplicate_users in duplicates.items():
        print(f"\n昵称 '{nickname}' 被 {len(duplicate_users)} 个用户使用:")
        
        # 按创建时间排序，保留最早创建的用户
        duplicate_users.sort(key=lambda u: u.created_at if hasattr(u, 'created_at') else u.id)
        
        # 保留第一个用户，其他用户修改昵称
        keep_user = duplicate_users[0]
        print(f"  保留用户: {keep_user.openid} (创建于: {getattr(keep_user, 'created_at', '未知')})")
        
        for i, user in enumerate(duplicate_users[1:], 1):
            new_nickname = f"{nickname}_{i}"
            print(f"  修改用户 {user.openid} 的昵称: '{nickname}' -> '{new_nickname}'")
            user.nickname = new_nickname
            user.save()
    
    print(f"\n清理完成！修改了 {sum(len(users) - 1 for users in duplicates.values())} 个用户的昵称。")

def check_final_status():
    """检查最终状态"""
    print("\n检查最终状态...")
    
    nickname_count = defaultdict(int)
    users = WeChatUser.objects.all()
    
    for user in users:
        if user.nickname:
            nickname_count[user.nickname] += 1
    
    duplicates = {nick: count for nick, count in nickname_count.items() if count > 1}
    
    if duplicates:
        print("警告：仍然存在重复昵称:")
        for nick, count in duplicates.items():
            print(f"  '{nick}': {count} 个用户")
        return False
    else:
        print("✓ 所有昵称都是唯一的，可以安全应用数据库迁移。")
        return True

if __name__ == '__main__':
    try:
        clean_duplicate_nicknames()
        success = check_final_status()
        
        if success:
            print("\n接下来请运行以下命令:")
            print("1. python manage.py makemigrations")
            print("2. python manage.py migrate")
        else:
            print("\n请手动解决剩余的重复昵称问题后再运行数据库迁移。")
            
    except Exception as e:
        print(f"脚本执行失败: {e}")
        sys.exit(1)
