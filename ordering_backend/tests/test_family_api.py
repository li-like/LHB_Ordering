#!/usr/bin/env python3
"""
家庭功能API测试脚本
测试刚刚创建的家庭相关API接口
"""

import requests
import json
import time

# 配置
BASE_URL = "http://127.0.0.1:8000/api/wechat"
TEST_OPENID = "test_user_001"  # 测试用的openid

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

def test_user_creation():
    """测试创建用户"""
    print("\n🧪 测试1: 创建测试用户")
    
    # 模拟微信登录创建用户
    url = f"{BASE_URL}/login/"
    data = {
        "code": "test_code_001",
        "userInfo": {
            "nickName": "测试用户001",
            "avatarUrl": "https://example.com/avatar.jpg"
        }
    }
    
    # 由于我们没有真实的微信服务器，这个请求会失败
    # 我们直接通过数据库或用户信息API来创建/获取用户
    
    # 先尝试获取用户信息
    url = f"{BASE_URL}/user-info/"
    response = requests.get(url, params={"openid": TEST_OPENID})
    
    if response.status_code == 404:
        print("用户不存在，需要先在数据库中创建测试用户")
        return False
    
    print_response(response, "获取用户信息")
    return response.status_code == 200

def test_family_creation():
    """测试创建家庭"""
    print("\n🧪 测试2: 创建家庭")
    
    url = f"{BASE_URL}/families/create/"
    data = {
        "openid": TEST_OPENID,
        "name": "测试家庭001",
        "display_name": "爸爸"
    }
    
    response = requests.post(url, json=data)
    print_response(response, "创建家庭")
    
    if response.status_code == 201:
        family_data = response.json().get('family', {})
        return family_data.get('id'), family_data.get('invite_code')
    
    return None, None

def test_family_list():
    """测试获取家庭列表"""
    print("\n🧪 测试3: 获取家庭列表")
    
    url = f"{BASE_URL}/families/"
    response = requests.get(url, params={"openid": TEST_OPENID})
    print_response(response, "获取家庭列表")
    
    return response.status_code == 200

def test_join_family(invite_code):
    """测试加入家庭"""
    print("\n🧪 测试4: 加入家庭")
    
    # 使用另一个测试用户
    test_openid_2 = "test_user_002"
    
    url = f"{BASE_URL}/families/join/"
    data = {
        "openid": test_openid_2,
        "invite_code": invite_code,
        "display_name": "妈妈"
    }
    
    response = requests.post(url, json=data)
    print_response(response, "加入家庭")
    
    return response.status_code == 201

def test_family_members(family_id):
    """测试获取家庭成员"""
    print("\n🧪 测试5: 获取家庭成员")
    
    url = f"{BASE_URL}/families/{family_id}/members/"
    response = requests.get(url, params={"openid": TEST_OPENID})
    print_response(response, "获取家庭成员")
    
    return response.status_code == 200

def test_family_detail(family_id):
    """测试获取家庭详情"""
    print("\n🧪 测试6: 获取家庭详情")
    
    url = f"{BASE_URL}/families/{family_id}/"
    response = requests.get(url, params={"openid": TEST_OPENID})
    print_response(response, "获取家庭详情")
    
    return response.status_code == 200

def test_family_settings(family_id):
    """测试修改家庭设置"""
    print("\n🧪 测试7: 修改家庭设置")
    
    url = f"{BASE_URL}/families/{family_id}/settings/"
    data = {
        "openid": TEST_OPENID,
        "name": "更新后的家庭名称",
        "max_members": 8
    }
    
    response = requests.put(url, json=data)
    print_response(response, "修改家庭设置")
    
    return response.status_code == 200

def main():
    """主测试函数"""
    print("🚀 开始测试家庭功能API")
    print(f"测试服务器: {BASE_URL}")
    print(f"测试用户: {TEST_OPENID}")
    
    # 测试1: 用户相关
    if not test_user_creation():
        print("❌ 用户创建/获取失败，请先确保数据库中有测试用户")
        print("请手动创建测试用户或运行微信登录接口")
        return
    
    # 测试2: 创建家庭
    family_id, invite_code = test_family_creation()
    if not family_id:
        print("❌ 家庭创建失败")
        return
    
    print(f"✅ 家庭创建成功 - ID: {family_id}, 邀请码: {invite_code}")
    
    # 测试3: 获取家庭列表
    if test_family_list():
        print("✅ 获取家庭列表成功")
    
    # 测试4: 加入家庭（这个可能会失败，因为需要另一个用户）
    if invite_code:
        print(f"⚠️  加入家庭测试需要第二个用户，邀请码: {invite_code}")
    
    # 测试5: 获取家庭成员
    if test_family_members(family_id):
        print("✅ 获取家庭成员成功")
    
    # 测试6: 获取家庭详情
    if test_family_detail(family_id):
        print("✅ 获取家庭详情成功")
    
    # 测试7: 修改家庭设置
    if test_family_settings(family_id):
        print("✅ 修改家庭设置成功")
    
    print("\n🎉 API测试完成！")
    print(f"创建的测试家庭ID: {family_id}")
    print(f"邀请码: {invite_code}")

if __name__ == "__main__":
    main()
