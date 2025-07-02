#!/usr/bin/env python3
"""
测试移除家庭成员功能
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/wechat"

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

def test_remove_member():
    """测试移除成员功能"""
    print("🧪 测试: 管理员移除家庭成员")
    
    family_id = 2  # 之前创建的测试家庭
    admin_openid = "test_user_001"  # 管理员
    target_openid = "test_user_003"  # 要移除的成员
    
    url = f"{BASE_URL}/families/{family_id}/remove-member/"
    data = {
        "openid": admin_openid,
        "target_user_openid": target_openid
    }
    
    response = requests.post(url, json=data)
    print_response(response, "移除家庭成员")
    
    if response.status_code == 200:
        print("✅ 移除成员成功")
        return True
    else:
        print("❌ 移除成员失败")
        return False

def test_family_members_after_removal(family_id=2):
    """测试移除后的家庭成员列表"""
    print("\n🧪 测试: 查看移除后的家庭成员")
    
    url = f"{BASE_URL}/families/{family_id}/members/"
    response = requests.get(url, params={"openid": "test_user_001"})
    print_response(response, "移除后的家庭成员列表")
    
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
    print("🚀 测试移除家庭成员功能")
    
    # 测试移除成员
    if test_remove_member():
        # 测试移除后的成员列表
        test_family_members_after_removal()
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()
