#!/usr/bin/env python3
"""
测试第二个用户加入家庭
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/wechat"
INVITE_CODE = "515200"  # 从前面的测试获得的邀请码

def print_response(response, title="API Response"):
    """格式化打印响应"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except:
        print(f"Response Text: {response.text}")
    print(f"{'='*50}")

def test_join_family():
    """测试第二个用户加入家庭"""
    print("🧪 测试: 第二个用户加入家庭")
    
    url = f"{BASE_URL}/families/join/"
    data = {
        "openid": "test_user_003",  # 使用第三个测试用户
        "invite_code": INVITE_CODE,
        "display_name": "儿子"
    }
    
    response = requests.post(url, json=data)
    print_response(response, "加入家庭")
    
    if response.status_code == 201:
        print("✅ 加入家庭成功")
        return True
    else:
        print("❌ 加入家庭失败")
        return False

def test_family_members_after_join(family_id=2):
    """测试加入后的家庭成员列表"""
    print("\n🧪 测试: 查看加入后的家庭成员")
    
    url = f"{BASE_URL}/families/{family_id}/members/"
    response = requests.get(url, params={"openid": "test_user_001"})
    print_response(response, "家庭成员列表")
    
    if response.status_code == 200:
        members = response.json().get('members', [])
        print(f"✅ 当前家庭共有 {len(members)} 个成员")
        for member in members:
            print(f"  - {member['user_info']['nickname']} ({member['display_name']}) - {member['permission_level']}")
        return True
    else:
        print("❌ 获取家庭成员失败")
        return False

def main():
    print("🚀 测试第二个用户加入家庭")
    print(f"邀请码: {INVITE_CODE}")
    
    # 测试加入家庭
    if test_join_family():
        # 测试加入后的成员列表
        test_family_members_after_join()
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()
