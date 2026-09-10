from django.core.management.base import BaseCommand
from django.utils import timezone
from wechat_auth.models import WeChatUser, Family, FamilyMembership
from ordering.models import MealCategory, MealItem, MealRequest

class Command(BaseCommand):
    help = 'Create test data for ordering functionality'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data for ordering...')

        # Create test users
        user1, created = WeChatUser.objects.get_or_create(
            openid='test_user_001',
            defaults={
                'session_key': 'test_session_001',
                'nickname': 'xiaoming',
                'avatar': 'https://example.com/avatar1.jpg'
            }
        )

        user2, created = WeChatUser.objects.get_or_create(
            openid='test_user_002',
            defaults={
                'session_key': 'test_session_002',
                'nickname': 'xiaohong',
                'avatar': 'https://example.com/avatar2.jpg'
            }
        )

        # Create test family
        try:
            family = Family.objects.get(name='Test Family')
            self.stdout.write('Using existing test family')
        except Family.DoesNotExist:
            # Generate a unique invite code
            import random
            import string
            while True:
                invite_code = ''.join(random.choices(string.digits, k=6))
                if not Family.objects.filter(invite_code=invite_code).exists():
                    break
            
            family = Family.objects.create(
                name='Test Family',
                invite_code=invite_code,
                max_members=10
            )
            self.stdout.write(f'Created new test family with invite code: {invite_code}')

        # Create family memberships
        membership1, created = FamilyMembership.objects.get_or_create(
            user=user1,
            family=family,
            defaults={
                'display_name': 'Dad',
                'permission_level': 'admin'
            }
        )

        membership2, created = FamilyMembership.objects.get_or_create(
            user=user2,
            family=family,
            defaults={
                'display_name': 'Mom',
                'permission_level': 'member'
            }
        )

        # Create meal categories
        category1, created = MealCategory.objects.get_or_create(
            family=family,
            name='Home Dishes',
            defaults={
                'description': 'Daily home cooking',
                'sort_order': 1,
                'created_by': user1
            }
        )

        category2, created = MealCategory.objects.get_or_create(
            family=family,
            name='Soup',
            defaults={
                'description': 'Nutritious soups',
                'sort_order': 2,
                'created_by': user1
            }
        )

        # Create meal items
        meals_data = [
            {
                'name': 'Braised Pork',
                'category': category1,
                'description': 'Sweet and tender braised pork',
                'meal_type': 'lunch',
                'difficulty': 'medium',
                'prep_time': 60,
                'ingredients': ['pork belly', 'soy sauce', 'sugar', 'wine'],
                'cooking_steps': ['Cut meat', 'Blanch', 'Braise for 1 hour'],
                'tags': ['meat', 'traditional']
            },
            {
                'name': 'Tomato Egg',
                'category': category1,
                'description': 'Simple tomato scrambled eggs',
                'meal_type': 'lunch',
                'difficulty': 'easy',
                'prep_time': 15,
                'ingredients': ['eggs', 'tomatoes', 'salt', 'sugar'],
                'cooking_steps': ['Beat eggs', 'Fry eggs', 'Cook tomatoes', 'Mix'],
                'tags': ['quick', 'classic']
            },
            {
                'name': 'Seaweed Soup',
                'category': category2,
                'description': 'Light and nutritious soup',
                'meal_type': 'dinner',
                'difficulty': 'easy',
                'prep_time': 10,
                'ingredients': ['seaweed', 'eggs', 'sesame oil', 'salt'],
                'cooking_steps': ['Boil water', 'Add seaweed', 'Add egg drops'],
                'tags': ['light', 'nutritious']
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
                self.stdout.write(f"Created meal: {meal.name}")

        # Create meal requests
        braised_pork = MealItem.objects.get(family=family, name='Braised Pork')
        request1, created = MealRequest.objects.get_or_create(
            family=family,
            requester=user2,
            meal_item=braised_pork,
            defaults={
                'quantity': 1,
                'priority': 'normal',
                'special_requests': 'Less sugar please'
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully created test data!'))
        self.stdout.write(f"Family: {family.name}")
        self.stdout.write(f"Members: {user1.nickname}, {user2.nickname}")
        self.stdout.write(f"Categories: {MealCategory.objects.filter(family=family).count()}")
        self.stdout.write(f"Meals: {MealItem.objects.filter(family=family).count()}")
        self.stdout.write(f"Requests: {MealRequest.objects.filter(family=family).count()}")
