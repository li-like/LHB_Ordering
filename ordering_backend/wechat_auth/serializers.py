from rest_framework import serializers  # 导入 DRF 的序列化器模块
from .models import WeChatUser, Family, FamilyMembership, UserPreferences, FavoriteMeal, CookingRecord  # 导入模型

class WeChatUserSerializer(serializers.ModelSerializer):  # 定义一个模型序列化器类
    class Meta:  # 定义序列化器的元数据
        model = WeChatUser  # 指定关联的模型为 WeChatUser
        fields = ['openid', 'nickname', 'avatar', 'created_at']
        read_only_fields = ['openid', 'created_at']

class FamilySerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    current_user_permission = serializers.SerializerMethodField()
    
    class Meta:
        model = Family
        fields = ['id', 'name', 'invite_code', 'code_enabled', 'max_members', 
                 'created_at', 'member_count', 'current_user_permission']
        read_only_fields = ['invite_code', 'created_at', 'member_count', 'current_user_permission']
    
    def get_member_count(self, obj):
        return obj.memberships.filter(is_active=True).count()
    
    def get_current_user_permission(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'openid'):
            openid = request.openid
            try:
                user = WeChatUser.objects.get(openid=openid)
                membership = obj.memberships.filter(user=user, is_active=True).first()
                return membership.permission_level if membership else None
            except WeChatUser.DoesNotExist:
                pass
        return None

class FamilyMembershipSerializer(serializers.ModelSerializer):
    user_info = WeChatUserSerializer(source='user', read_only=True)
    
    class Meta:
        model = FamilyMembership
        fields = ['id', 'user_info', 'display_name', 'permission_level', 
                 'joined_at', 'is_active']
        read_only_fields = ['joined_at']

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ['taste_preferences', 'allergies', 'dislikes', 'updated_at']
        read_only_fields = ['updated_at']

class FavoriteMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteMeal
        fields = ['id', 'meal_name', 'add_time']
        read_only_fields = ['add_time']

class CookingRecordSerializer(serializers.ModelSerializer):
    cook_user = WeChatUserSerializer(source='user', read_only=True)
    
    class Meta:
        model = CookingRecord
        fields = ['id', 'cook_user', 'meal_name', 'cook_date', 
                 'participants', 'created_at']
        read_only_fields = ['created_at']

# 专门用于创建家庭的序列化器
class FamilyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ['name']
    
    def create(self, validated_data):
        family = Family(**validated_data)
        family.generate_invite_code()  # 生成邀请码
        family.save()
        return family

# 用于加入家庭的序列化器
class JoinFamilySerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6, min_length=6)
    display_name = serializers.CharField(max_length=64)
    
    def validate_invite_code(self, value):
        try:
            family = Family.objects.get(invite_code=value, code_enabled=True)
            return value
        except Family.DoesNotExist:
            raise serializers.ValidationError('邀请码无效或已过期')

# 用于管理员转让的序列化器
class TransferAdminSerializer(serializers.Serializer):
    target_user_openid = serializers.CharField(max_length=64)
    
    def validate_target_user_openid(self, value):
        try:
            WeChatUser.objects.get(openid=value)
            return value
        except WeChatUser.DoesNotExist:
            raise serializers.ValidationError('目标用户不存在')