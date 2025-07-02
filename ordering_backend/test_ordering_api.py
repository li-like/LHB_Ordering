"""
点餐功能API测试脚本
测试所有的点餐相关接口
"""

import requests
import json

BASE_URL = 'http://localhost:8000'

def test_meal_categories():
    """测试餐品分类接口"""
    print("=== 测试餐品分类接口 ===")
    
    # 获取分类列表
    response = requests.get(f'{BASE_URL}/api/ordering/categories/')
    print(f"获取分类列表: {response.status_code}")
    if response.status_code == 200:
        categories = response.json()
        print(f"分类数量: {len(categories)}")
        for category in categories[:3]:  # 只显示前3个
            print(f"- {category['name']}: {category.get('meal_count', 0)}个餐品")
    
    # 获取简化分类列表
    response = requests.get(f'{BASE_URL}/api/ordering/categories/simple_list/')
    print(f"获取简化分类列表: {response.status_code}")

def test_meal_items():
    """测试餐品接口"""
    print("\n=== 测试餐品接口 ===")
    
    # 获取餐品列表
    response = requests.get(f'{BASE_URL}/api/ordering/items/')
    print(f"获取餐品列表: {response.status_code}")
    if response.status_code == 200:
        items = response.json()
        print(f"餐品数量: {len(items)}")
        for item in items[:3]:  # 只显示前3个
            print(f"- {item['name']}: {item['difficulty']}, {item['prep_time']}分钟")
    
    # 获取热门餐品
    response = requests.get(f'{BASE_URL}/api/ordering/items/popular/')
    print(f"获取热门餐品: {response.status_code}")

def test_meal_requests():
    """测试点餐需求接口"""
    print("\n=== 测试点餐需求接口 ===")
    
    # 获取点餐需求列表
    response = requests.get(f'{BASE_URL}/api/ordering/requests/')
    print(f"获取点餐需求列表: {response.status_code}")
    if response.status_code == 200:
        requests_data = response.json()
        print(f"点餐需求数量: {len(requests_data)}")
        for req in requests_data[:3]:  # 只显示前3个
            print(f"- {req['meal_name']} x{req['quantity']}: {req['status']}")
    
    # 获取待处理的点餐需求
    response = requests.get(f'{BASE_URL}/api/ordering/requests/pending/')
    print(f"获取待处理点餐需求: {response.status_code}")
    
    # 获取点餐需求汇总
    response = requests.get(f'{BASE_URL}/api/ordering/requests/summary/')
    print(f"获取点餐需求汇总: {response.status_code}")
    if response.status_code == 200:
        summary = response.json()
        print(f"汇总数据: {summary}")

def test_meal_confirmations():
    """测试制作确认接口"""
    print("\n=== 测试制作确认接口 ===")
    
    # 获取制作确认列表
    response = requests.get(f'{BASE_URL}/api/ordering/confirmations/')
    print(f"获取制作确认列表: {response.status_code}")

def test_meal_batches():
    """测试批量点餐接口"""
    print("\n=== 测试批量点餐接口 ===")
    
    # 获取批量点餐列表
    response = requests.get(f'{BASE_URL}/api/ordering/batches/')
    print(f"获取批量点餐列表: {response.status_code}")

def test_meal_stats():
    """测试统计接口"""
    print("\n=== 测试统计接口 ===")
    
    # 获取统计数据
    response = requests.get(f'{BASE_URL}/api/ordering/stats/')
    print(f"获取统计数据: {response.status_code}")

def main():
    """运行所有测试"""
    print("开始测试点餐功能API...")
    
    try:
        test_meal_categories()
        test_meal_items()
        test_meal_requests()
        test_meal_confirmations()
        test_meal_batches()
        test_meal_stats()
        
        print("\n=== API测试完成 ===")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Django服务器已启动在localhost:8000")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == '__main__':
    main()
