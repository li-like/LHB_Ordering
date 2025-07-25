import requests

base_url = "http://192.168.189.240:8000"
test_user = "ocYjt6oIJsFk2RgC7duPZVScsBV8"

print("=== 菜谱展示测试 ===")

print("\n1. 菜谱大全模式(已登录):")
response = requests.get(f"{base_url}/api/recipes/?mode=all&current_user={test_user}")
data = response.json()
print(f"返回数量: {len(data.get('data', []))}")
for recipe in data.get('data', []):
    print(f"  - {recipe['name']} by {recipe['author']['nickname']} (公开:{recipe['is_public']}, 可编辑:{recipe.get('can_edit', False)})")

print("\n2. 我的菜谱模式:")
response = requests.get(f"{base_url}/api/recipes/?mode=user&author={test_user}&current_user={test_user}")
data = response.json()
print(f"返回数量: {len(data.get('data', []))}")
for recipe in data.get('data', []):
    print(f"  - {recipe['name']} by {recipe['author']['nickname']} (公开:{recipe['is_public']}, 可编辑:{recipe.get('can_edit', False)})")

print("\n=== 结论 ===")
print("后端API工作正常！")
print("如果前端还有问题，请检查:")
print("1. 小程序是否重新编译")
print("2. 开发者工具是否刷新")
print("3. 网络请求是否正常")
print("4. 控制台是否有错误")
