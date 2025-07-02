from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    MealCategory, MealItem, MealRequest, 
    MealConfirmation, MealOrderBatch, FamilyMealStats
)
from .serializers import (
    MealCategorySerializer, MealItemSerializer, MealRequestSerializer,
    MealConfirmationSerializer, MealOrderBatchSerializer, FamilyMealStatsSerializer,
    MealCategorySimpleSerializer, MealItemSimpleSerializer, MealRequestSimpleSerializer
)
from wechat_auth.models import Family, FamilyMembership

class MealCategoryViewSet(viewsets.ModelViewSet):
    """餐品分类管理"""
    serializer_class = MealCategorySerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问用于测试

    def get_queryset(self):
        """只返回用户所在家庭的分类"""
        user = self.request.user
        
        # 临时处理：如果是匿名用户，返回所有分类
        if user.is_anonymous:
            return MealCategory.objects.filter(is_active=True).order_by('sort_order', 'created_at')
        
        # 获取用户所在的家庭
        family_ids = FamilyMembership.objects.filter(
            user=user, is_active=True
        ).values_list('family_id', flat=True)
        
        return MealCategory.objects.filter(
            family_id__in=family_ids, is_active=True
        ).order_by('sort_order', 'created_at')

    def perform_create(self, serializer):
        """创建分类时设置创建者和家庭"""
        # 获取用户当前选择的家庭（这里需要前端传递family_id）
        family_id = self.request.data.get('family_id')
        if not family_id:
            # 如果没有指定家庭，使用用户第一个家庭
            membership = FamilyMembership.objects.filter(
                user=self.request.user, is_active=True
            ).first()
            if membership:
                family_id = membership.family.id
        
        serializer.save(
            created_by=self.request.user,
            family_id=family_id
        )

    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        """简化的分类列表（用于下拉选择）"""
        queryset = self.get_queryset()
        serializer = MealCategorySimpleSerializer(queryset, many=True)
        return Response(serializer.data)

class MealItemViewSet(viewsets.ModelViewSet):
    """餐品管理"""
    serializer_class = MealItemSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问用于测试

    def get_queryset(self):
        """获取用户所在家庭的餐品"""
        user = self.request.user
        
        # 临时处理：如果是匿名用户，返回所有餐品
        if user.is_anonymous:
            queryset = MealItem.objects.all()
        else:
            family_ids = FamilyMembership.objects.filter(
                user=user, is_active=True
            ).values_list('family_id', flat=True)
            queryset = MealItem.objects.filter(family_id__in=family_ids)
        
        # 筛选条件
        category_id = self.request.query_params.get('category')
        meal_type = self.request.query_params.get('meal_type')
        difficulty = self.request.query_params.get('difficulty')
        search = self.request.query_params.get('search')
        available_only = self.request.query_params.get('available_only', 'true')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if meal_type:
            queryset = queryset.filter(meal_type=meal_type)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        if available_only.lower() == 'true':
            queryset = queryset.filter(is_available=True)
        
        return queryset.order_by('-popularity', 'name')

    def perform_create(self, serializer):
        """创建餐品时设置创建者和家庭"""
        family_id = self.request.data.get('family_id')
        if not family_id:
            membership = FamilyMembership.objects.filter(
                user=self.request.user, is_active=True
            ).first()
            if membership:
                family_id = membership.family.id
        
        serializer.save(
            created_by=self.request.user,
            family_id=family_id
        )

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """获取热门餐品"""
        queryset = self.get_queryset().filter(
            popularity__gt=0
        ).order_by('-popularity')[:10]
        
        serializer = MealItemSimpleSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """切换餐品可用状态"""
        meal_item = self.get_object()
        meal_item.is_available = not meal_item.is_available
        meal_item.save()
        
        serializer = self.get_serializer(meal_item)
        return Response(serializer.data)

class MealRequestViewSet(viewsets.ModelViewSet):
    """点餐需求管理"""
    serializer_class = MealRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取用户相关的点餐需求"""
        user = self.request.user
        family_ids = FamilyMembership.objects.filter(
            user=user, is_active=True
        ).values_list('family_id', flat=True)
        
        queryset = MealRequest.objects.filter(family_id__in=family_ids)
        
        # 筛选条件
        status_filter = self.request.query_params.get('status')
        requester_filter = self.request.query_params.get('requester')
        date_filter = self.request.query_params.get('date')
        my_requests = self.request.query_params.get('my_requests')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if requester_filter:
            queryset = queryset.filter(requester_id=requester_filter)
        if date_filter:
            queryset = queryset.filter(created_at__date=date_filter)
        if my_requests == 'true':
            queryset = queryset.filter(requester=user)
        
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """创建点餐需求时设置请求者和家庭"""
        family_id = self.request.data.get('family_id')
        if not family_id:
            membership = FamilyMembership.objects.filter(
                user=self.request.user, is_active=True
            ).first()
            if membership:
                family_id = membership.family.id
        
        serializer.save(
            requester=self.request.user,
            family_id=family_id
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消点餐需求"""
        meal_request = self.get_object()
        
        if not meal_request.can_be_cancelled():
            return Response(
                {'error': '当前状态无法取消'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        meal_request.status = 'cancelled'
        meal_request.save()
        
        serializer = self.get_serializer(meal_request)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """获取待处理的点餐需求"""
        queryset = self.get_queryset().filter(status='pending')
        serializer = MealRequestSimpleSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取点餐需求汇总"""
        queryset = self.get_queryset()
        
        summary = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'confirmed': queryset.filter(status='confirmed').count(),
            'cooking': queryset.filter(status='cooking').count(),
            'completed': queryset.filter(status='completed').count(),
            'cancelled': queryset.filter(status='cancelled').count(),
        }
        
        return Response(summary)

class MealConfirmationViewSet(viewsets.ModelViewSet):
    """制作确认管理"""
    serializer_class = MealConfirmationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取用户相关的制作确认"""
        user = self.request.user
        family_ids = FamilyMembership.objects.filter(
            user=user, is_active=True
        ).values_list('family_id', flat=True)
        
        return MealConfirmation.objects.filter(
            meal_request__family_id__in=family_ids
        ).order_by('-created_at')

    def perform_create(self, serializer):
        """创建制作确认时设置确认者"""
        serializer.save(confirmer=self.request.user)

    @action(detail=True, methods=['post'])
    def start_cooking(self, request, pk=None):
        """开始制作"""
        confirmation = self.get_object()
        confirmation.start_cooking()
        
        serializer = self.get_serializer(confirmation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete_cooking(self, request, pk=None):
        """完成制作"""
        confirmation = self.get_object()
        confirmation.complete_cooking()
        
        # 可以添加评分
        difficulty_rating = request.data.get('difficulty_rating')
        satisfaction_rating = request.data.get('satisfaction_rating')
        
        if difficulty_rating:
            confirmation.difficulty_rating = difficulty_rating
        if satisfaction_rating:
            confirmation.satisfaction_rating = satisfaction_rating
        
        confirmation.save()
        
        serializer = self.get_serializer(confirmation)
        return Response(serializer.data)

class MealOrderBatchViewSet(viewsets.ModelViewSet):
    """批量点餐管理"""
    serializer_class = MealOrderBatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取用户相关的批量点餐"""
        user = self.request.user
        family_ids = FamilyMembership.objects.filter(
            user=user, is_active=True
        ).values_list('family_id', flat=True)
        
        return MealOrderBatch.objects.filter(
            family_id__in=family_ids
        ).order_by('-target_time')

    def perform_create(self, serializer):
        """创建批量点餐时设置协调人和家庭"""
        family_id = self.request.data.get('family_id')
        if not family_id:
            membership = FamilyMembership.objects.filter(
                user=self.request.user, is_active=True
            ).first()
            if membership:
                family_id = membership.family.id
        
        serializer.save(
            coordinator=self.request.user,
            family_id=family_id
        )

    @action(detail=True, methods=['post'])
    def add_requests(self, request, pk=None):
        """添加点餐需求到批次"""
        batch = self.get_object()
        request_ids = request.data.get('request_ids', [])
        
        meal_requests = MealRequest.objects.filter(
            id__in=request_ids,
            family=batch.family,
            status='pending'
        )
        
        batch.meal_requests.add(*meal_requests)
        
        serializer = self.get_serializer(batch)
        return Response(serializer.data)

class FamilyMealStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """家庭用餐统计（只读）"""
    serializer_class = FamilyMealStatsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取用户家庭的统计数据"""
        user = self.request.user
        family_ids = FamilyMembership.objects.filter(
            user=user, is_active=True
        ).values_list('family_id', flat=True)
        
        return FamilyMealStats.objects.filter(family_id__in=family_ids)

    @action(detail=True, methods=['post'])
    def update_stats(self, request, pk=None):
        """更新统计数据"""
        stats = self.get_object()
        stats.update_stats()
        
        serializer = self.get_serializer(stats)
        return Response(serializer.data)
