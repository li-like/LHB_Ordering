from django.db import models
import random
import string

# Create your models here.
class WeChatUser(models.Model):  # 定义一个名为 WeChatUser 的数据库模型类
    # 存储微信用户的 openid，长度 64 字符，唯一且不可重复
    openid = models.CharField(max_length=64, unique=True, verbose_name='微信 openid')
    # 存储微信用户的 session_key，长度 64 字符
    session_key = models.CharField(max_length=64, verbose_name='微信 session_key')
    # 存储用户昵称，长度 128 字符，可为空，但不可重复
    nickname = models.CharField(max_length=128, blank=True, null=True, unique=True, verbose_name='昵称')
    # 存储用户头像的 URL 地址，可为空
    avatar = models.URLField(blank=True, null=True, verbose_name='头像')
    # 记录用户创建时间，自动在创建时添加当前时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 记录用户信息更新时间，自动在每次更新时添加当前时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"{self.nickname or 'Unknown'} ({self.openid[:10]}...)"

    class Meta:  # 定义模型的元数据
        verbose_name = '微信用户'  # 模型的单数名称
        verbose_name_plural = '微信用户'  # 模型的复数名称

class Family(models.Model):
    name = models.CharField(max_length=128, verbose_name='家庭名称')
    invite_code = models.CharField(max_length=6, unique=True, verbose_name='邀请码')
    code_enabled = models.BooleanField(default=True, verbose_name='邀请码是否启用')
    code_expires_at = models.DateTimeField(null=True, blank=True, verbose_name='邀请码过期时间')
    max_members = models.IntegerField(default=10, verbose_name='最大成员数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def generate_invite_code(self):
        """生成6位数字邀请码"""
        while True:
            code = ''.join(random.choices(string.digits, k=6))
            if not Family.objects.filter(invite_code=code).exists():
                self.invite_code = code
                break
        return code

    def __str__(self):
        return f"{self.name} ({self.invite_code})"

    class Meta:
        verbose_name = '家庭'
        verbose_name_plural = '家庭'

class FamilyMembership(models.Model):
    """用户-家庭关系表（多对多中间表）"""
    PERMISSION_CHOICES = [
        ('admin', '管理员'),
        ('member', '普通成员'),
    ]
    
    user = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, verbose_name='用户')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='memberships', verbose_name='家庭')
    display_name = models.CharField(max_length=64, verbose_name='显示角色')  # 如：爸爸、妈妈、儿子等
    permission_level = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='member', verbose_name='权限级别')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    
    class Meta:
        verbose_name = '家庭成员关系'
        verbose_name_plural = '家庭成员关系'
        unique_together = ('user', 'family')  # 确保用户在同一家庭中只能有一个成员关系

    def __str__(self):
        return f"{self.user.nickname} - {self.family.name} ({self.permission_level})"

class UserPreferences(models.Model):
    """用户在特定家庭中的偏好设置"""
    user = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, verbose_name='用户')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, verbose_name='家庭')
    taste_preferences = models.JSONField(default=list, verbose_name='口味偏好')  # ["清淡", "甜食", "辣味"]
    allergies = models.JSONField(default=list, verbose_name='过敏信息')  # ["海鲜", "坚果", "乳制品"]
    dislikes = models.JSONField(default=list, verbose_name='不喜欢的食物')  # ["苦瓜", "香菜", "青椒"]
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户偏好'
        verbose_name_plural = '用户偏好'
        unique_together = ('user', 'family')  # 确保用户在同一家庭中只能有一个偏好设置

    def __str__(self):
        return f"{self.user.nickname} - {self.family.name} 偏好"

# 保留原有的模型以兼容性
class FamilyMember(models.Model):
    """保留原有模型以向后兼容"""
    user = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, verbose_name='用户')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='members', verbose_name='家庭')
    relation = models.CharField(max_length=32, verbose_name='与家庭关系')
    is_admin = models.BooleanField(default=False, verbose_name='是否为管理员')
    join_time = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')

    class Meta:
        verbose_name = '家庭成员(旧)'
        verbose_name_plural = '家庭成员(旧)'

class FavoriteMeal(models.Model):
    user = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, verbose_name='用户')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True, verbose_name='关联家庭')
    meal_name = models.CharField(max_length=128, verbose_name='喜爱菜品')
    category = models.CharField(max_length=64, default='其他', verbose_name='菜品分类')
    count = models.IntegerField(default=1, verbose_name='制作次数')
    image = models.URLField(blank=True, null=True, verbose_name='菜品图片')
    description = models.TextField(blank=True, verbose_name='描述')
    tags = models.JSONField(default=list, verbose_name='标签')  # ["辣", "甜", "家常菜"]
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    liked_by = models.JSONField(default=list, verbose_name='点赞的用户')  # 存储用户openid列表
    last_cooked = models.DateTimeField(null=True, blank=True, verbose_name='最后制作时间')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '喜爱菜品'
        verbose_name_plural = '喜爱菜品'
        unique_together = ('family', 'meal_name')  # 同一家庭内菜品名称不能重复

class CookingRecord(models.Model):
    """下厨记录"""
    user = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, verbose_name='用户')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, verbose_name='家庭')
    meal_name = models.CharField(max_length=128, verbose_name='菜品名称')
    cook_date = models.DateTimeField(auto_now_add=True, verbose_name='下厨时间')  # 添加默认值
    participants = models.JSONField(default=list, verbose_name='参与用餐人员')  # 存储用户openid列表
    rating = models.IntegerField(default=5, verbose_name='评分')  # 1-5分
    notes = models.TextField(blank=True, verbose_name='备注')
    images = models.JSONField(default=list, verbose_name='照片列表')  # 存储图片URL列表
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '下厨记录'
        verbose_name_plural = '下厨记录'

class SharedRecipe(models.Model):
    user = models.ForeignKey(WeChatUser, on_delete=models.CASCADE, verbose_name='用户')
    recipe_name = models.CharField(max_length=128, verbose_name='菜谱名称')
    share_time = models.DateTimeField(auto_now_add=True, verbose_name='分享时间')

    class Meta:
        verbose_name = '分享菜谱'
        verbose_name_plural = '分享菜谱'