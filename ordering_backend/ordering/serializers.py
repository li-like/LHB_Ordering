from rest_framework import serializers
from .models import (
    MealCategory, MealItem, MealRequest, 
    MealConfirmation, MealOrderBatch, FamilyMealStats
)
from wechat_auth.models import WeChatUser, Family
from django.utils import timezone

class MealCategorySerializer(serializers.ModelSerializer):
    """餐品分类序列化器"""
    created_by_name = serializers.CharField(source='created_by.nickname', read_only=True)
    meal_count = serializers.SerializerMethodField()

    class Meta:
        model = MealCategory
        fields = [
            'id', 'name', 'description', 'icon', 'sort_order', 
            'is_active', 'created_by', 'created_by_name', 'meal_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_meal_count(self, obj):
        """获取分类下的餐品数量"""
        return obj.meals.filter(is_available=True).count()

class MealItemSerializer(serializers.ModelSerializer):
    """餐品序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.nickname', read_only=True)
    request_count = serializers.SerializerMethodField()

    class Meta:
        model = MealItem
        fields = [
            'id', 'name', 'description', 'image', 'meal_type', 
            'difficulty', 'prep_time', 'ingredients', 'cooking_steps',
            'tags', 'popularity', 'is_available', 'category', 'category_name',
            'created_by', 'created_by_name', 'request_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'popularity', 'created_at', 'updated_at']

    def get_request_count(self, obj):
        """获取餐品的点餐次数"""
        return obj.requests.count()

class MealRequestSerializer(serializers.ModelSerializer):
    """点餐需求序列化器"""
    requester_name = serializers.CharField(source='requester.nickname', read_only=True)
    meal_name = serializers.CharField(source='meal_item.name', read_only=True)
    meal_image = serializers.URLField(source='meal_item.image', read_only=True)
    meal_prep_time = serializers.IntegerField(source='meal_item.prep_time', read_only=True)
    can_cancel = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = MealRequest
        fields = [
            'id', 'meal_item', 'meal_name', 'meal_image', 'meal_prep_time',
            'quantity', 'priority', 'preferred_time', 'special_requests',
            'status', 'notes', 'requester', 'requester_name',
            'can_cancel', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['requester', 'created_at', 'updated_at']

    def get_can_cancel(self, obj):
        """是否可以取消"""
        return obj.can_be_cancelled()

    def get_is_overdue(self, obj):
        """是否过期"""
        return obj.is_overdue()

class MealConfirmationSerializer(serializers.ModelSerializer):
    """制作确认序列化器"""
    confirmer_name = serializers.CharField(source='confirmer.nickname', read_only=True)
    delegated_to_name = serializers.CharField(source='delegated_to.nickname', read_only=True)
    meal_request_details = MealRequestSerializer(source='meal_request', read_only=True)

    class Meta:
        model = MealConfirmation
        fields = [
            'id', 'status', 'estimated_time', 'actual_start_time', 
            'actual_completion_time', 'delegated_to', 'delegated_to_name',
            'notes', 'difficulty_rating', 'satisfaction_rating',
            'confirmer', 'confirmer_name', 'meal_request_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['confirmer', 'created_at', 'updated_at']

class MealOrderBatchSerializer(serializers.ModelSerializer):
    """批量点餐序列化器"""
    coordinator_name = serializers.CharField(source='coordinator.nickname', read_only=True)
    meal_requests_details = MealRequestSerializer(source='meal_requests', many=True, read_only=True)
    total_requests = serializers.SerializerMethodField()
    pending_requests = serializers.SerializerMethodField()

    class Meta:
        model = MealOrderBatch
        fields = [
            'id', 'name', 'target_time', 'status', 'notes',
            'coordinator', 'coordinator_name',
            'meal_requests_details', 'total_requests', 'pending_requests',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['coordinator', 'created_at', 'updated_at']

    def get_total_requests(self, obj):
        """总点餐需求数量"""
        return obj.get_total_requests()

    def get_pending_requests(self, obj):
        """待处理点餐需求数量"""
        return obj.get_pending_requests().count()

    def validate_target_time(self, value):
        """验证 target_time 是否为有效时间字符串"""
        # 如果已经是 datetime 对象，直接返回
        if isinstance(value, timezone.datetime):
            return value
            
        if not isinstance(value, str):
            raise serializers.ValidationError('target_time 必须是字符串')
        try:
            # 支持多种 ISO 格式
            if value.endswith('Z'):
                # 处理 UTC 时间格式，如 "2025-07-04T05:20:00.191Z"
                value = value.replace('Z', '+00:00')
            
            # 使用 Django 的 timezone 解析 ISO 格式
            from django.utils.dateparse import parse_datetime
            parsed_time = parse_datetime(value)
            if parsed_time is None:
                raise ValueError("无法解析时间格式")
            return parsed_time
        except ValueError:
            raise serializers.ValidationError('target_time 格式无效，应为 ISO 时间字符串')

    def validate_status(self, value):
        """验证 status 字段"""
        return value

    def validate(self, attrs):
        """整体验证方法 - 处理 meal_requests"""
        # 打印调试信息
        print(f"序列化器验证 - initial_data: {self.initial_data}")
        print(f"序列化器验证 - attrs: {attrs}")
        
        # 从初始数据中获取 meal_requests（绕过字段验证）
        meal_requests_data = self.initial_data.get('meal_requests', [])
        
        # 验证 meal_requests 数据格式
        if not isinstance(meal_requests_data, list):
            raise serializers.ValidationError({'meal_requests': ['必须是数组']})
        
        for i, request_data in enumerate(meal_requests_data):
            if not isinstance(request_data, dict):
                raise serializers.ValidationError({'meal_requests': [f'第{i+1}个元素必须是字典']})
            if 'meal_item' not in request_data:
                raise serializers.ValidationError({'meal_requests': [f'第{i+1}个元素缺少 meal_item 字段']})
            if 'quantity' not in request_data:
                raise serializers.ValidationError({'meal_requests': [f'第{i+1}个元素缺少 quantity 字段']})
            if 'special_requests' not in request_data:
                request_data['special_requests'] = ''
        
        # 将 meal_requests 数据存储到 attrs 中供后续使用
        attrs['_meal_requests_data'] = meal_requests_data
        
        # 将 meal_requests 设为空列表，避免序列化器字段验证失败
        attrs['meal_requests'] = []
        
        # 添加 meal_type 字段验证
        if 'meal_type' not in attrs:
            raise serializers.ValidationError({'meal_type': ['必须指定餐点类型']})
        
        print(f"序列化器验证完成 - 最终 attrs: {attrs}")
        return attrs

class FamilyMealStatsSerializer(serializers.ModelSerializer):
    """家庭用餐统计序列化器"""
    family_name = serializers.CharField(source='family.name', read_only=True)
    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = FamilyMealStats
        fields = [
            'id', 'family', 'family_name', 'total_meals_ordered',
            'total_meals_completed', 'completion_rate', 'most_popular_meal',
            'most_active_requester', 'most_active_cook', 'average_completion_time',
            'last_updated'
        ]
        read_only_fields = ['family', 'last_updated']

    def get_completion_rate(self, obj):
        """计算完成率"""
        if obj.total_meals_ordered > 0:
            return round((obj.total_meals_completed / obj.total_meals_ordered) * 100, 2)
        return 0

# ==================== 简化版序列化器（用于列表展示） ====================

class MealCategorySimpleSerializer(serializers.ModelSerializer):
    """餐品分类简化序列化器"""
    meal_count = serializers.SerializerMethodField()

    class Meta:
        model = MealCategory
        fields = ['id', 'name', 'icon', 'meal_count']

    def get_meal_count(self, obj):
        return obj.meals.filter(is_available=True).count()

class MealItemSimpleSerializer(serializers.ModelSerializer):
    """餐品简化序列化器"""
    class Meta:
        model = MealItem
        fields = [
            'id', 'name', 'image', 'meal_type', 'difficulty', 
            'prep_time', 'popularity', 'is_available'
        ]

class MealRequestSimpleSerializer(serializers.ModelSerializer):
    """点餐需求简化序列化器"""
    requester_name = serializers.CharField(source='requester.nickname', read_only=True)
    meal_name = serializers.CharField(source='meal_item.name', read_only=True)

    class Meta:
        model = MealRequest
        fields = [
            'id', 'meal_name', 'quantity', 'priority', 'status',
            'requester_name', 'created_at'
        ]
