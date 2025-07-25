from django.db import models
from django.utils import timezone
from datetime import timedelta
from wechat_auth.models import WeChatUser, Family

# ==================== 点餐功能相关模型 ====================

class MealCategory(models.Model):
    """餐品分类"""
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='meal_categories', verbose_name='所属家庭')
    name = models.CharField(max_length=64, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    icon = models.URLField(blank=True, null=True, verbose_name='分类图标')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '餐品分类'
        verbose_name_plural = '餐品分类'
        unique_together = ('family', 'name')  # 同一家庭内分类名称不能重复
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"{self.family.name} - {self.name}"

class MealItem(models.Model):
    """餐品"""
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    
    MEAL_TYPE_CHOICES = [
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '零食'),
        ('dessert', '甜品'),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='meal_items', verbose_name='所属家庭')
    category = models.ForeignKey(MealCategory, on_delete=models.CASCADE, related_name='meals', verbose_name='所属分类')
    name = models.CharField(max_length=128, verbose_name='餐品名称')
    description = models.TextField(blank=True, verbose_name='描述')
    image = models.URLField(blank=True, null=True, verbose_name='餐品图片')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='lunch', verbose_name='餐品类型')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium', verbose_name='制作难度')
    prep_time = models.IntegerField(default=30, verbose_name='预计制作时间(分钟)')
    ingredients = models.JSONField(default=list, verbose_name='所需食材')  # ["食材1", "食材2"]
    cooking_steps = models.JSONField(default=list, verbose_name='制作步骤')  # ["步骤1", "步骤2"]
    tags = models.JSONField(default=list, verbose_name='标签')  # ["健康", "素食", "快手菜"]
    popularity = models.IntegerField(default=0, verbose_name='受欢迎程度')
    is_available = models.BooleanField(default=True, verbose_name='是否可点餐')
    created_by = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '餐品'
        verbose_name_plural = '餐品'
        unique_together = ('family', 'name')  # 同一家庭内餐品名称不能重复
        ordering = ['-popularity', 'name']

    def __str__(self):
        return f"{self.family.name} - {self.name}"

    def increase_popularity(self):
        """增加受欢迎程度"""
        self.popularity += 1
        self.save()

class MealRequest(models.Model):
    """点餐需求"""
    STATUS_CHOICES = [
        ('pending', '等待确认'),
        ('confirmed', '已确认'),
        ('cooking', '制作中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    PRIORITY_CHOICES = [
        ('low', '不急'),
        ('normal', '一般'),
        ('high', '比较急'),
        ('urgent', '很急'),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='meal_requests', verbose_name='所属家庭')
    requester = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, related_name='meal_requests', verbose_name='点餐人')
    meal_item = models.ForeignKey(MealItem, on_delete=models.CASCADE, related_name='requests', verbose_name='餐品')
    quantity = models.IntegerField(default=1, verbose_name='数量')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal', verbose_name='优先级')
    preferred_time = models.DateTimeField(null=True, blank=True, verbose_name='希望用餐时间')
    special_requests = models.TextField(blank=True, verbose_name='特殊要求')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点餐时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '点餐需求'
        verbose_name_plural = '点餐需求'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.requester.nickname} 点餐: {self.meal_item.name} x{self.quantity}"

    def can_be_cancelled(self):
        """判断是否可以取消"""
        return self.status in ['pending', 'confirmed']

    def is_overdue(self):
        """判断是否过期（超过24小时未处理）"""
        if self.status == 'pending':
            return timezone.now() - self.created_at > timedelta(hours=24)
        return False

class MealConfirmation(models.Model):
    """制作确认"""
    STATUS_CHOICES = [
        ('accepted', '接受制作'),
        ('declined', '拒绝制作'),
        ('delegated', '委托他人'),
    ]

    meal_request = models.OneToOneField(MealRequest, on_delete=models.CASCADE, related_name='confirmation', verbose_name='关联点餐')
    confirmer = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, related_name='confirmations', verbose_name='确认人')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='确认状态')
    estimated_time = models.DateTimeField(null=True, blank=True, verbose_name='预计完成时间')
    actual_start_time = models.DateTimeField(null=True, blank=True, verbose_name='实际开始时间')
    actual_completion_time = models.DateTimeField(null=True, blank=True, verbose_name='实际完成时间')
    delegated_to = models.ForeignKey(WeChatUser, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='delegated_confirmations', verbose_name='委托给')
    notes = models.TextField(blank=True, verbose_name='备注')
    difficulty_rating = models.IntegerField(null=True, blank=True, verbose_name='制作难度评分(1-5)')
    satisfaction_rating = models.IntegerField(null=True, blank=True, verbose_name='满意度评分(1-5)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='确认时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '制作确认'
        verbose_name_plural = '制作确认'

    def __str__(self):
        return f"{self.confirmer.nickname} {self.get_status_display()}: {self.meal_request.meal_item.name}"

    def start_cooking(self):
        """开始制作"""
        self.actual_start_time = timezone.now()
        self.meal_request.status = 'cooking'
        self.save()
        self.meal_request.save()

    def complete_cooking(self):
        """完成制作"""
        self.actual_completion_time = timezone.now()
        self.meal_request.status = 'completed'
        self.save()
        self.meal_request.save()
        # 增加餐品受欢迎程度
        self.meal_request.meal_item.increase_popularity()

class MealOrderBatch(models.Model):
    """批量点餐（多个需求的集合）"""
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='meal_batches', verbose_name='所属家庭')
    name = models.CharField(max_length=128, verbose_name='批次名称')  # 如："今晚晚餐"、"明天午餐"
    meal_requests = models.ManyToManyField(MealRequest, related_name='batches', verbose_name='包含的点餐需求')
    target_time = models.DateTimeField(verbose_name='目标用餐时间')
    coordinator = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, related_name='coordinated_batches', verbose_name='协调人')
    status = models.CharField(max_length=20, choices=[
        ('pending', '待处理'),
        ('confirmed', '已确认'),
        ('cooking', '制作中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ], default='pending', verbose_name='批次状态')
    notes = models.TextField(blank=True, verbose_name='批次备注')
    meal_type = models.CharField(max_length=20, choices=[
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '零食'),
        ('dessert', '甜品'),
    ], verbose_name='餐点类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '批量点餐'
        verbose_name_plural = '批量点餐'
        ordering = ['-target_time']

    def __str__(self):
        return f"{self.family.name} - {self.name}"

    def get_total_requests(self):
        """获取总的点餐需求数量"""
        return self.meal_requests.count()

    def get_pending_requests(self):
        """获取待处理的点餐需求"""
        return self.meal_requests.filter(status='pending')

# ==================== 数据统计相关模型 ====================

class FamilyMealStats(models.Model):
    """家庭用餐统计"""
    family = models.OneToOneField(Family, on_delete=models.CASCADE, related_name='meal_stats', verbose_name='家庭')
    total_meals_ordered = models.IntegerField(default=0, verbose_name='总点餐次数')
    total_meals_completed = models.IntegerField(default=0, verbose_name='总完成次数')
    most_popular_meal = models.CharField(max_length=128, blank=True, verbose_name='最受欢迎餐品')
    most_active_requester = models.CharField(max_length=128, blank=True, verbose_name='最活跃点餐人')
    most_active_cook = models.CharField(max_length=128, blank=True, verbose_name='最活跃制作人')
    average_completion_time = models.IntegerField(default=0, verbose_name='平均制作时间(分钟)')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')

    class Meta:
        verbose_name = '家庭用餐统计'
        verbose_name_plural = '家庭用餐统计'

    def __str__(self):
        return f"{self.family.name} 用餐统计"

    def update_stats(self):
        """更新统计数据"""
        # 这里可以添加统计逻辑
        pass
