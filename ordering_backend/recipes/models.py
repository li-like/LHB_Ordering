from django.db import models
from wechat_auth.models import WeChatUser, Family

# Create your models here.

class Recipe(models.Model):
    """菜谱模型"""
    
    DIFFICULTY_CHOICES = [
        (1, '简单'),
        (2, '一般'),
        (3, '中等'),
        (4, '困难'),
        (5, '大师级'),
    ]
    
    CATEGORY_CHOICES = [
        ('meat', '荤菜'),
        ('vegetable', '素菜'),
        ('soup', '汤品'),
        ('staple', '主食'),
        ('snack', '小食'),
        ('dessert', '甜品'),
        ('other', '其他'),
    ]
    
    # 基本信息
    name = models.CharField(max_length=128, verbose_name='菜谱名称')
    description = models.TextField(blank=True, default='', verbose_name='菜谱描述')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name='菜品分类')
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1, verbose_name='难度等级')
    cook_time = models.IntegerField(default=30, verbose_name='制作时间(分钟)')
    servings = models.IntegerField(default=2, verbose_name='份量(人份)')
    cover_image = models.URLField(blank=True, null=True, verbose_name='封面图片')
    tags = models.JSONField(default=list, verbose_name='标签列表')
    
    # 关联信息
    author = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, verbose_name='作者')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, blank=True, null=True, verbose_name='所属家庭')
    
    # 状态信息
    is_public = models.BooleanField(default=False, verbose_name='是否公开分享')
    first_try_date = models.DateField(blank=True, null=True, verbose_name='初学日期')
    success_count = models.IntegerField(default=0, verbose_name='成功制作次数')
    total_attempts = models.IntegerField(default=0, verbose_name='总尝试次数')
    
    # 社交统计
    rating = models.FloatField(default=0.0, verbose_name='平均评分')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        return f"{self.name} - {self.author.nickname or '匿名'}"
    
    @property
    def success_rate(self):
        """成功率"""
        if self.total_attempts == 0:
            return 0
        return round(self.success_count / self.total_attempts * 100, 1)
    
    class Meta:
        verbose_name = '菜谱'
        verbose_name_plural = '菜谱'
        ordering = ['-created_at']


class RecipeIngredient(models.Model):
    """食材清单模型"""
    
    INGREDIENT_CATEGORY_CHOICES = [
        ('main', '主料'),
        ('auxiliary', '辅料'),
        ('seasoning', '调料'),
    ]
    
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients', verbose_name='菜谱')
    name = models.CharField(max_length=64, verbose_name='食材名称')
    amount = models.CharField(max_length=32, default='适量', verbose_name='用量')
    unit = models.CharField(max_length=16, blank=True, default='', verbose_name='单位')
    category = models.CharField(max_length=20, choices=INGREDIENT_CATEGORY_CHOICES, default='main', verbose_name='食材分类')
    notes = models.CharField(max_length=128, blank=True, default='', verbose_name='备注')
    order = models.IntegerField(default=0, verbose_name='排序')
    
    def __str__(self):
        return f"{self.recipe.name} - {self.name}"
    
    class Meta:
        verbose_name = '食材'
        verbose_name_plural = '食材'
        ordering = ['category', 'order']


class RecipeStep(models.Model):
    """制作步骤模型"""
    
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps', verbose_name='菜谱')
    step_number = models.IntegerField(verbose_name='步骤序号')
    title = models.CharField(max_length=64, blank=True, default='', verbose_name='步骤标题')
    description = models.TextField(verbose_name='详细描述')
    images = models.JSONField(default=list, verbose_name='步骤图片列表')
    time_required = models.IntegerField(blank=True, null=True, verbose_name='所需时间(分钟)')
    temperature = models.CharField(max_length=32, blank=True, default='', verbose_name='温度要求')
    tips = models.TextField(blank=True, default='', verbose_name='小贴士')
    
    def __str__(self):
        return f"{self.recipe.name} - 步骤{self.step_number}"
    
    class Meta:
        verbose_name = '制作步骤'
        verbose_name_plural = '制作步骤'
        ordering = ['step_number']
        unique_together = ['recipe', 'step_number']


class RecipeNote(models.Model):
    """制作笔记模型"""
    
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='notes', verbose_name='菜谱')
    author = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, verbose_name='笔记作者')
    content = models.TextField(verbose_name='笔记内容')
    images = models.JSONField(default=list, verbose_name='相关图片')
    rating = models.IntegerField(choices=[(i, f'{i}星') for i in range(1, 6)], blank=True, null=True, verbose_name='本次评分')
    success = models.BooleanField(default=True, verbose_name='是否成功')
    modifications = models.TextField(blank=True, default='', verbose_name='改进建议')
    cooking_date = models.DateTimeField(auto_now_add=True, verbose_name='制作时间')
    
    def __str__(self):
        return f"{self.recipe.name} - {self.author.nickname or '匿名'} - {self.cooking_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        verbose_name = '制作笔记'
        verbose_name_plural = '制作笔记'
        ordering = ['-cooking_date']
