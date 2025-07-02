"""
点餐功能测试数据创建脚本
运行方式：python manage.py shell < create_meal_test_data.py
"""

from django.utils import timezone
from wechat_auth.models import WeChatUser, Family, FamilyMembership
from ordering.models import MealCategory, MealItem, MealRequest

# 创建测试用户
user1, created = WeChatUser.objects.get_or_create(
    openid='test_user_001',
    defaults={
        'session_key': 'test_session_001',
        'nickname': '小明',
        'avatar': 'https://example.com/avatar1.jpg'
    }
)

user2, created = WeChatUser.objects.get_or_create(
    openid='test_user_002',
    defaults={
        'session_key': 'test_session_002',
        'nickname': '小红',
        'avatar': 'https://example.com/avatar2.jpg'
    }
)

# 创建测试家庭
family, created = Family.objects.get_or_create(
    name='温馨家庭',
    defaults={
        'invite_code': '123456',
        'max_members': 10
    }
)

# 创建家庭成员关系
membership1, created = FamilyMembership.objects.get_or_create(
    user=user1,
    family=family,
    defaults={
        'display_name': '爸爸',
        'permission_level': 'admin'
    }
)

membership2, created = FamilyMembership.objects.get_or_create(
    user=user2,
    family=family,
    defaults={
        'display_name': '妈妈',
        'permission_level': 'member'
    }
)

# 创建餐品分类
category1, created = MealCategory.objects.get_or_create(
    family=family,
    name='家常菜',
    defaults={
        'description': '日常家庭料理',
        'sort_order': 1,
        'created_by': user1
    }
)

category2, created = MealCategory.objects.get_or_create(
    family=family,
    name='汤品',
    defaults={
        'description': '营养汤类',
        'sort_order': 2,
        'created_by': user1
    }
)

category3, created = MealCategory.objects.get_or_create(
    family=family,
    name='主食',
    defaults={
        'description': '米饭面条等主食',
        'sort_order': 3,
        'created_by': user1
    }
)

# 创建餐品
meals_data = [
    {
        'name': '红烧肉',
        'category': category1,
        'description': '香甜软糯的红烧肉',
        'meal_type': 'lunch',
        'difficulty': 'medium',
        'prep_time': 60,
        'ingredients': ['五花肉', '生抽', '老抽', '冰糖', '料酒', '葱', '姜'],
        'cooking_steps': ['切肉块', '焯水去腥', '炒糖色', '炖煮1小时'],
        'tags': ['下饭', '荤菜', '传统']
    },
    {
        'name': '番茄鸡蛋',
        'category': category1,
        'description': '简单快手的番茄炒蛋',
        'meal_type': 'lunch',
        'difficulty': 'easy',
        'prep_time': 15,
        'ingredients': ['鸡蛋', '番茄', '盐', '糖', '葱花'],
        'cooking_steps': ['打散鸡蛋', '炒蛋盛起', '炒番茄', '混合炒制'],
        'tags': ['快手菜', '下饭', '经典']
    },
    {
        'name': '紫菜蛋花汤',
        'category': category2,
        'description': '清淡营养的汤品',
        'meal_type': 'dinner',
        'difficulty': 'easy',
        'prep_time': 10,
        'ingredients': ['紫菜', '鸡蛋', '香油', '盐', '葱花'],
        'cooking_steps': ['水开放紫菜', '打入蛋花', '调味出锅'],
        'tags': ['清汤', '营养', '简单']
    },
    {
        'name': '白米饭',
        'category': category3,
        'description': '香喷喷的大米饭',
        'meal_type': 'lunch',
        'difficulty': 'easy',
        'prep_time': 30,
        'ingredients': ['大米', '水'],
        'cooking_steps': ['淘米', '加水', '电饭煲蒸煮'],
        'tags': ['主食', '必备']
    },
    {
        'name': '青椒肉丝',
        'category': category1,
        'description': '经典的青椒肉丝',
        'meal_type': 'lunch',
        'difficulty': 'medium',
        'prep_time': 25,
        'ingredients': ['青椒', '肉丝', '生抽', '料酒', '淀粉'],
        'cooking_steps': ['肉丝腌制', '青椒切丝', '爆炒出锅'],
        'tags': ['下饭', '荤菜', '家常']
    }
]

for meal_data in meals_data:
    meal, created = MealItem.objects.get_or_create(
        family=family,
        name=meal_data['name'],
        defaults={
            'category': meal_data['category'],
            'description': meal_data['description'],
            'meal_type': meal_data['meal_type'],
            'difficulty': meal_data['difficulty'],
            'prep_time': meal_data['prep_time'],
            'ingredients': meal_data['ingredients'],
            'cooking_steps': meal_data['cooking_steps'],
            'tags': meal_data['tags'],
            'created_by': user1
        }
    )
    if created:
        print(f"创建餐品: {meal.name}")

# 创建一些点餐需求
request1, created = MealRequest.objects.get_or_create(
    family=family,
    requester=user2,
    meal_item=MealItem.objects.get(family=family, name='红烧肉'),
    defaults={
        'quantity': 1,
        'priority': 'normal',
        'special_requests': '请少放糖',
        'preferred_time': timezone.now() + timezone.timedelta(hours=2)
    }
)

request2, created = MealRequest.objects.get_or_create(
    family=family,
    requester=user2,
    meal_item=MealItem.objects.get(family=family, name='白米饭'),
    defaults={
        'quantity': 2,
        'priority': 'normal',
        'special_requests': '要软糯一点'
    }
)

print("测试数据创建完成！")
print(f"家庭: {family.name}")
print(f"成员: {user1.nickname}, {user2.nickname}")
print(f"餐品分类: {MealCategory.objects.filter(family=family).count()} 个")
print(f"餐品: {MealItem.objects.filter(family=family).count()} 个")
print(f"点餐需求: {MealRequest.objects.filter(family=family).count()} 个")
