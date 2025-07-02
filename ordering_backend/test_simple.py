import requests

def test_api():
    base_url = 'http://192.168.10.4:8000'
    test_user = 'ocYjt6oIJsFk2RgC7duPZVScsBV8'  # 冷汉堡
    
    print("1. 测试菜谱大全模式(未登录):")
    try:
        response = requests.get(f'{base_url}/api/recipes/?mode=all', timeout=5)
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'返回数量: {len(data.get("data", []))}')
            for recipe in data.get('data', []):
                print(f'  - {recipe["name"]} by {recipe["author"]["nickname"]} (公开: {recipe["is_public"]})')
        else:
            print(f'错误: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')
    
    print("\n2. 测试菜谱大全模式(已登录):")
    try:
        response = requests.get(f'{base_url}/api/recipes/?mode=all&current_user={test_user}', timeout=5)
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'返回数量: {len(data.get("data", []))}')
            for recipe in data.get('data', []):
                print(f'  - {recipe["name"]} by {recipe["author"]["nickname"]} (公开: {recipe["is_public"]}, 可编辑: {recipe.get("can_edit", False)})')
        else:
            print(f'错误: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')
    
    print("\n3. 测试我的菜谱模式:")
    try:
        response = requests.get(f'{base_url}/api/recipes/?mode=user&author={test_user}&current_user={test_user}', timeout=5)
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'返回数量: {len(data.get("data", []))}')
            for recipe in data.get('data', []):
                print(f'  - {recipe["name"]} by {recipe["author"]["nickname"]} (公开: {recipe["is_public"]}, 可编辑: {recipe.get("can_edit", False)})')
        else:
            print(f'错误: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')

if __name__ == '__main__':
    test_api()
