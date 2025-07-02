#!/usr/bin/env python
"""
创建菜谱测试数据
"""
import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_backend.settings')
django.setup()

from recipes.models import Recipe, RecipeIngredient, RecipeStep, RecipeNote
from wechat_auth.models import WeChatUser, Family, FamilyMember

def create_test_recipes():
    """创建测试菜谱数据"""
    
    # 获取或创建测试用户
    user, created = WeChatUser.objects.get_or_create(
        openid='test_user_recipe',
        defaults={
            'nickname': '美食达人',
            'avatar': '/static/default-avatar.png',
            'session_key': 'test_session_key'
        }
    )
    
    # 获取或创建测试家庭
    try:
        family = Family.objects.get(name='美食之家')
        print(f"找到已存在的家庭: {family}")
    except Family.DoesNotExist:
        family = Family(name='美食之家')
        family.generate_invite_code()  # 使用模型方法生成唯一邀请码
        family.save()
        print(f"创建新家庭: {family}")
        
        # 创建家庭成员关系
        FamilyMember.objects.get_or_create(
            user=user,
            family=family,
            defaults={
                'relation': '管理员',
                'is_admin': True
            }
        )
    
    # 创建菜谱1：红烧肉
    recipe1, created = Recipe.objects.get_or_create(
        name='红烧肉',
        author=user,
        defaults={
            'description': '软糯香甜的经典家常菜，肥而不腻，入口即化',
            'category': 'meat',
            'difficulty': 3,
            'cook_time': 60,
            'servings': 4,
            'cover_image': '/static/dishes/hongshaorou.jpg',
            'tags': ['荤菜', '热菜', '下饭', '经典'],
            'family': family,
            'is_public': True,
            'success_count': 8,
            'total_attempts': 10,
            'rating': 4.5,
            'likes': 15
        }
    )
    
    if created:
        # 添加食材
        ingredients_data = [
            {'name': '五花肉', 'amount': '500', 'unit': '克', 'category': 'main', 'notes': '选择肥瘦相间的', 'order': 1},
            {'name': '生抽', 'amount': '2', 'unit': '勺', 'category': 'seasoning', 'order': 2},
            {'name': '老抽', 'amount': '1', 'unit': '勺', 'category': 'seasoning', 'notes': '上色用', 'order': 3},
            {'name': '冰糖', 'amount': '适量', 'unit': '', 'category': 'seasoning', 'order': 4},
            {'name': '料酒', 'amount': '1', 'unit': '勺', 'category': 'seasoning', 'order': 5},
            {'name': '八角', 'amount': '2', 'unit': '个', 'category': 'seasoning', 'order': 6},
        ]
        
        for ing_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe1, **ing_data)
        
        # 添加制作步骤
        steps_data = [
            {
                'step_number': 1,
                'title': '准备食材',
                'description': '将五花肉切成3厘米见方的块状，用开水焯水去腥，捞出备用。',
                'time_required': 10,
                'tips': '焯水时可以加入料酒去腥'
            },
            {
                'step_number': 2,
                'title': '炒糖色',
                'description': '锅中放入少量油，小火加热，放入冰糖炒至焦糖色，注意不要炒糊。',
                'time_required': 5,
                'temperature': '小火',
                'tips': '一定要小火，糖色不能炒过头'
            },
            {
                'step_number': 3,
                'title': '炒制上色',
                'description': '倒入肉块翻炒，让每块肉都裹上糖色，炒至微微出油。',
                'time_required': 8,
                'temperature': '中火',
                'tips': '炒制时间不要太长'
            },
            {
                'step_number': 4,
                'title': '调味炖煮',
                'description': '加入生抽、老抽、料酒和八角，倒入热水没过肉块，大火烧开后转小火炖40分钟。',
                'time_required': 45,
                'temperature': '先大火后小火',
                'tips': '水要一次加够，中途尽量不要加水'
            },
            {
                'step_number': 5,
                'title': '收汁盛盘',
                'description': '大火收汁，汤汁浓稠即可关火，撒上葱花装盘。',
                'time_required': 5,
                'temperature': '大火',
                'tips': '收汁时要不断翻炒，避免糊锅'
            }
        ]
        
        for step_data in steps_data:
            RecipeStep.objects.create(recipe=recipe1, **step_data)
    
    # 创建菜谱2：清炒时蔬
    recipe2, created = Recipe.objects.get_or_create(
        name='清炒时蔬',
        author=user,
        defaults={
            'description': '清淡健康的素食料理，保持蔬菜的原汁原味',
            'category': 'vegetable',
            'difficulty': 1,
            'cook_time': 15,
            'servings': 2,
            'cover_image': '/static/dishes/qingchaoshishu.jpg',
            'tags': ['素菜', '清淡', '健康', '快手'],
            'family': family,
            'is_public': True,
            'success_count': 12,
            'total_attempts': 12,
            'rating': 4.2,
            'likes': 8
        }
    )
    
    if created:
        # 添加食材
        ingredients_data = [
            {'name': '西兰花', 'amount': '200', 'unit': '克', 'category': 'main', 'order': 1},
            {'name': '胡萝卜', 'amount': '1', 'unit': '根', 'category': 'main', 'order': 2},
            {'name': '蒜', 'amount': '3', 'unit': '瓣', 'category': 'seasoning', 'order': 3},
            {'name': '盐', 'amount': '适量', 'unit': '', 'category': 'seasoning', 'order': 4},
            {'name': '生抽', 'amount': '1', 'unit': '勺', 'category': 'seasoning', 'order': 5},
        ]
        
        for ing_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe2, **ing_data)
        
        # 添加制作步骤
        steps_data = [
            {
                'step_number': 1,
                'title': '准备蔬菜',
                'description': '西兰花掰成小朵，胡萝卜切片，蒜切末。',
                'time_required': 5,
                'tips': '蔬菜要洗净沥干'
            },
            {
                'step_number': 2,
                'title': '焯水处理',
                'description': '西兰花和胡萝卜分别用开水焯水1分钟，捞出备用。',
                'time_required': 3,
                'tips': '焯水时间不要太长，保持脆嫩'
            },
            {
                'step_number': 3,
                'title': '爆炒调味',
                'description': '热锅下油，爆香蒜末，倒入蔬菜翻炒，加盐和生抽调味即可。',
                'time_required': 5,
                'temperature': '大火',
                'tips': '动作要快，保持蔬菜的脆嫩口感'
            }
        ]
        
        for step_data in steps_data:
            RecipeStep.objects.create(recipe=recipe2, **step_data)
    
    # 创建菜谱3：蒸蛋羹
    recipe3, created = Recipe.objects.get_or_create(
        name='蒸蛋羹',
        author=user,
        defaults={
            'description': '嫩滑如豆腐的营养蒸蛋，老少皆宜',
            'category': 'other',
            'difficulty': 2,
            'cook_time': 20,
            'servings': 2,
            'cover_image': '/static/dishes/zhengdangeng.jpg',
            'tags': ['蛋类', '嫩滑', '营养', '蒸制'],
            'family': family,
            'is_public': False,
            'success_count': 5,
            'total_attempts': 6,
            'rating': 4.0,
            'likes': 6
        }
    )
    
    if created:
        # 添加食材
        ingredients_data = [
            {'name': '鸡蛋', 'amount': '3', 'unit': '个', 'category': 'main', 'order': 1},
            {'name': '温水', 'amount': '150', 'unit': '毫升', 'category': 'main', 'notes': '蛋液的1.5倍', 'order': 2},
            {'name': '盐', 'amount': '少许', 'unit': '', 'category': 'seasoning', 'order': 3},
            {'name': '香油', 'amount': '几滴', 'unit': '', 'category': 'seasoning', 'order': 4},
        ]
        
        for ing_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe3, **ing_data)
        
        # 添加制作步骤
        steps_data = [
            {
                'step_number': 1,
                'title': '调制蛋液',
                'description': '鸡蛋打散，加入温水和少许盐，搅拌均匀，过筛去泡沫。',
                'time_required': 5,
                'tips': '水温约40度，蛋水比例1:1.5'
            },
            {
                'step_number': 2,
                'title': '准备蒸制',
                'description': '蛋液倒入蒸碗，用保鲜膜封好，用牙签扎几个小孔。',
                'time_required': 2,
                'tips': '保鲜膜防止水汽滴入'
            },
            {
                'step_number': 3,
                'title': '蒸制成型',
                'description': '水开后放入蒸锅，中小火蒸12-15分钟至凝固。',
                'time_required': 15,
                'temperature': '中小火',
                'tips': '火不要太大，否则表面会起泡'
            },
            {
                'step_number': 4,
                'title': '调味享用',
                'description': '出锅后滴几滴香油，可根据喜好加生抽调色。',
                'time_required': 1,
                'tips': '趁热享用口感最佳'
            }
        ]
        
        for step_data in steps_data:
            RecipeStep.objects.create(recipe=recipe3, **step_data)
    
    print("✅ 菜谱测试数据创建完成！")
    print(f"创建的菜谱：")
    print(f"1. {recipe1.name} - {recipe1.category}")
    print(f"2. {recipe2.name} - {recipe2.category}")
    print(f"3. {recipe3.name} - {recipe3.category}")

if __name__ == '__main__':
    create_test_recipes()
