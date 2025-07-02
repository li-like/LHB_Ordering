from django.shortcuts import render

# Create your views here.
# 该文件实现了微信登录的视图逻辑，处理小程序端发送的登录请求。
import requests  # 导入 requests 库，用于发送 HTTP 请求
from rest_framework.views import APIView  # 导入 DRF 的 API 视图类
from rest_framework.response import Response  # 导入 DRF 的响应类
from rest_framework import status  # 导入 DRF 的状态码模块
from .models import WeChatUser, Family, FamilyMembership, UserPreferences, CookingRecord, FavoriteMeal  # 导入模型
from .serializers import (
    WeChatUserSerializer, FamilySerializer, FamilyMembershipSerializer,
    UserPreferencesSerializer, FamilyCreateSerializer, JoinFamilySerializer,
    TransferAdminSerializer
)  # 导入序列化器
from django.conf import settings  # 导入 Django 的配置模块
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.db import transaction  # 导入事务模块
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import logging

# 获取logger
logger = logging.getLogger(__name__)


class WeChatLoginView(APIView):
    def post(self, request):
        code = request.data.get('code')
        user_info = request.data.get('userInfo', {})
        if not code:
            return Response({'error': '缺少 code 参数'}, status=status.HTTP_400_BAD_REQUEST)

        appid = settings.WECHAT_APPID
        secret = settings.WECHAT_SECRET
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        params = {
            'appid': appid,
            'secret': secret,
            'js_code': code,
            'grant_type': 'authorization_code'
        }

        response = requests.get(url, params=params)
        data = response.json()

        if 'errcode' in data:
            return Response({'error': data.get('errmsg')}, status=status.HTTP_400_BAD_REQUEST)

        openid = data.get('openid')
        session_key = data.get('session_key')

        user, created = WeChatUser.objects.update_or_create(
            openid=openid,
            defaults={
                'session_key': session_key,
                'nickname': user_info.get('nickName', ''),
                'avatar': user_info.get('avatarUrl', '')
            }
        )

        return Response({
            'openid': openid,
            'user_id': user.id,
            'nickname': user.nickname,
            'avatar': user.avatar
        }, status=status.HTTP_200_OK)


class UserInfoView(APIView):
    # 临时移除认证要求用于开发测试
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # 从请求头或参数中获取 openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.GET.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            return Response({
                'openid': user.openid,
                'nickname': user.nickname,
                'avatar': user.avatar
            }, status=status.HTTP_200_OK)
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @transaction.atomic
    def post(self, request):
        """更新用户信息"""
        # 从请求头或参数中获取 openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.data.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 获取要更新的字段
            nickname = request.data.get('nickName') or request.data.get('nickname')
            avatar = request.data.get('avatarUrl') or request.data.get('avatar')
            
            # 打印调试信息
            print(f"收到更新请求 - OpenID: {openid}")
            print(f"请求数据: {request.data}")
            print(f"昵称: {nickname}, 头像: {avatar}")
            
            # 验证数据
            if nickname is not None:
                if len(nickname.strip()) == 0:
                    return Response({'error': '昵称不能为空'}, status=status.HTTP_400_BAD_REQUEST)
                if len(nickname) > 20:
                    return Response({'error': '昵称不能超过20个字符'}, status=status.HTTP_400_BAD_REQUEST)
                user.nickname = nickname.strip()
                print(f"更新昵称为: {user.nickname}")
            
            if avatar is not None:
                user.avatar = avatar
                print(f"更新头像为: {user.avatar}")
            
            # 保存更改
            user.save()
            
            # 验证数据是否保存成功
            updated_user = WeChatUser.objects.get(openid=openid)
            print(f"保存后验证 - 昵称: {updated_user.nickname}, 头像: {updated_user.avatar}")
            
            return Response({
                'success': True,
                'message': '用户信息更新成功',
                'data': {
                    'openid': user.openid,
                    'nickname': user.nickname,
                    'avatar': user.avatar
                }
            }, status=status.HTTP_200_OK)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'更新失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NicknameCheckView(APIView):
    """昵称重复检查视图"""
    
    def post(self, request):
        """检查昵称是否可用"""
        nickname = request.data.get('nickname')
        exclude_openid = request.data.get('exclude_openid')
        
        if not nickname:
            return Response({'error': '昵称不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查昵称长度
        if len(nickname) > 128:
            return Response({
                'available': False,
                'error': '昵称长度不能超过128个字符'
            }, status=status.HTTP_200_OK)
        
        # 检查昵称是否包含特殊字符（可选）
        import re
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_\-\s]+$', nickname):
            return Response({
                'available': False,
                'error': '昵称只能包含中文、英文、数字、下划线和连字符'
            }, status=status.HTTP_200_OK)
        
        try:
            # 查询是否存在相同昵称的用户
            query = WeChatUser.objects.filter(nickname=nickname)
            
            # 如果指定了排除的openid，则排除该用户
            if exclude_openid:
                query = query.exclude(openid=exclude_openid)
            
            exists = query.exists()
            
            return Response({
                'available': not exists,
                'message': '昵称可用' if not exists else '昵称已被使用'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"检查昵称可用性失败: {str(e)}")
            return Response({'error': f'检查失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserStatsView(APIView):
    # 临时移除认证要求用于开发测试
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # 从请求头或参数中获取 openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.GET.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            today = timezone.now().date()
            
            # 计算加入天数
            days_joined = (today - user.created_at.date()).days
            
            # 计算喜爱菜品数量
            favorite_meals_count = user.favoritemeal_set.count()
            
            # 计算下厨天数
            cooking_days_count = user.cookingrecord_set.count()
            
            # 计算分享菜谱数量
            shared_recipes_count = user.sharedrecipe_set.count()
            
            return Response({
                'daysJoined': days_joined,
                'favoriteMeals': favorite_meals_count,
                'cookingDays': cooking_days_count,
                'sharedRecipes': shared_recipes_count
            }, status=status.HTTP_200_OK)
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

class AvatarUploadView(APIView):
    """头像上传视图"""
    
    @transaction.atomic
    def post(self, request):
        # 从请求头获取 openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.data.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'avatar' not in request.FILES:
            return Response({'error': '请选择头像文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return Response({'error': '仅支持 JPG、PNG、GIF 格式的图片'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证文件大小 (5MB 限制)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response({'error': '头像文件不能超过5MB'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 检查用户是否存在
            user = WeChatUser.objects.get(openid=openid)
            
            # 生成唯一文件名
            file_extension = os.path.splitext(avatar_file.name)[1]
            unique_filename = f"avatars/{openid}_{uuid.uuid4().hex}{file_extension}"
            
            # 确保目录存在
            avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            
            # 保存文件
            file_path = default_storage.save(unique_filename, ContentFile(avatar_file.read()))
            
            # 构建完整的URL
            base_url = "http://192.168.10.4:8000"  # 开发环境URL
            avatar_url = f"{base_url}/media/{file_path}"
            
            # 打印调试信息
            print(f"文件保存路径: {file_path}")
            print(f"头像URL: {avatar_url}")
            
            # 更新用户头像
            user.avatar = avatar_url
            user.save()
            
            # 验证数据是否保存成功
            updated_user = WeChatUser.objects.get(openid=openid)
            print(f"头像保存后验证 - 用户: {updated_user.nickname}, 头像: {updated_user.avatar}")
            
            return Response({
                'success': True,
                'message': '头像上传成功',
                'avatar_url': avatar_url
            }, status=status.HTTP_200_OK)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'上传失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ======== 家庭功能相关API ========

class FamilyListView(APIView):
    """获取用户的家庭列表"""
    
    def get(self, request):
        # 获取openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.GET.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 获取用户加入的所有家庭
            memberships = FamilyMembership.objects.filter(
                user=user, 
                is_active=True
            ).select_related('family')
            
            families_data = []
            for membership in memberships:
                family = membership.family
                family_data = {
                    'id': family.id,
                    'name': family.name,
                    'invite_code': family.invite_code,
                    'code_enabled': family.code_enabled,
                    'max_members': family.max_members,
                    'created_at': family.created_at,
                    'member_count': family.memberships.filter(is_active=True).count(),
                    'current_user_permission': membership.permission_level,
                    'display_name': membership.display_name
                }
                families_data.append(family_data)
                
            return Response({
                'success': True,
                'families': families_data
            }, status=status.HTTP_200_OK)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"获取家庭列表失败: {str(e)}")
            return Response({'error': f'获取失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilyCreateView(APIView):
    """创建家庭"""
    
    @transaction.atomic
    def post(self, request):
        # 获取openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.data.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 检查用户是否已经创建或加入了太多家庭（可选限制）
            current_families_count = FamilyMembership.objects.filter(
                user=user, 
                is_active=True
            ).count()
            
            if current_families_count >= 5:  # 限制最多加入5个家庭
                return Response({'error': '您最多只能加入5个家庭'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证输入数据
            serializer = FamilyCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': '数据验证失败',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建家庭
            family = serializer.save()
            
            # 创建用户与家庭的关系（创建者为管理员）
            display_name = request.data.get('display_name', '家长')
            FamilyMembership.objects.create(
                user=user,
                family=family,
                display_name=display_name,
                permission_level='admin'
            )
            
            # 返回创建的家庭信息
            family_data = {
                'id': family.id,
                'name': family.name,
                'invite_code': family.invite_code,
                'code_enabled': family.code_enabled,
                'max_members': family.max_members,
                'created_at': family.created_at,
                'member_count': 1,
                'current_user_permission': 'admin',
                'display_name': display_name
            }
            
            return Response({
                'success': True,
                'message': '家庭创建成功',
                'family': family_data
            }, status=status.HTTP_201_CREATED)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"创建家庭失败: {str(e)}")
            return Response({'error': f'创建失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilyJoinView(APIView):
    """通过邀请码加入家庭"""
    
    @transaction.atomic
    def post(self, request):
        # 获取openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.data.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 验证输入数据
            serializer = JoinFamilySerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': '数据验证失败',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            invite_code = serializer.validated_data['invite_code']
            display_name = serializer.validated_data['display_name']
            
            # 查找家庭
            try:
                family = Family.objects.get(invite_code=invite_code, code_enabled=True)
            except Family.DoesNotExist:
                return Response({'error': '邀请码无效或已过期'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查用户是否已经是该家庭成员
            existing_membership = FamilyMembership.objects.filter(
                user=user, 
                family=family,
                is_active=True
            ).first()
            
            if existing_membership:
                return Response({'error': '您已经是该家庭的成员'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查家庭是否已满
            current_members_count = family.memberships.filter(is_active=True).count()
            if current_members_count >= family.max_members:
                return Response({'error': '该家庭成员已满'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查用户的家庭数量限制
            user_families_count = FamilyMembership.objects.filter(
                user=user, 
                is_active=True
            ).count()
            
            if user_families_count >= 5:
                return Response({'error': '您最多只能加入5个家庭'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建成员关系
            membership = FamilyMembership.objects.create(
                user=user,
                family=family,
                display_name=display_name,
                permission_level='member'
            )
            
            # 返回加入结果
            family_data = {
                'id': family.id,
                'name': family.name,
                'invite_code': family.invite_code,
                'code_enabled': family.code_enabled,
                'max_members': family.max_members,
                'created_at': family.created_at,
                'member_count': family.memberships.filter(is_active=True).count(),
                'current_user_permission': 'member',
                'display_name': display_name
            }
            
            return Response({
                'success': True,
                'message': '成功加入家庭',
                'family': family_data
            }, status=status.HTTP_201_CREATED)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"加入家庭失败: {str(e)}")
            return Response({'error': f'加入失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilyMembersView(APIView):
    """获取家庭成员列表"""
    
    def get(self, request, family_id):
        # 获取openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.GET.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 检查用户是否是该家庭成员
            user_membership = FamilyMembership.objects.filter(
                user=user,
                family_id=family_id,
                is_active=True
            ).first()
            
            if not user_membership:
                return Response({'error': '您不是该家庭的成员'}, status=status.HTTP_403_FORBIDDEN)
            
            # 获取所有活跃成员
            members = FamilyMembership.objects.filter(
                family_id=family_id,
                is_active=True
            ).select_related('user').order_by('-permission_level', 'joined_at')
            
            members_data = []
            for member in members:
                member_data = {
                    'id': member.id,
                    'user_info': {
                        'openid': member.user.openid,
                        'nickname': member.user.nickname,
                        'avatar': member.user.avatar
                    },
                    'display_name': member.display_name,
                    'permission_level': member.permission_level,
                    'joined_at': member.joined_at,
                    'is_current_user': member.user.openid == openid
                }
                members_data.append(member_data)
            
            return Response({
                'success': True,
                'members': members_data,
                'total_count': len(members_data),
                'current_user_permission': user_membership.permission_level
            }, status=status.HTTP_200_OK)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"获取家庭成员失败: {str(e)}")
            return Response({'error': f'获取失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilyDetailView(APIView):
    """获取家庭详情"""
    
    def get(self, request, family_id):
        # 获取openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.GET.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 检查用户是否是该家庭成员
            user_membership = FamilyMembership.objects.filter(
                user=user,
                family_id=family_id,
                is_active=True
            ).first()
            
            if not user_membership:
                return Response({'error': '您不是该家庭的成员'}, status=status.HTTP_403_FORBIDDEN)
            
            # 获取家庭信息
            try:
                family = Family.objects.get(id=family_id)
            except Family.DoesNotExist:
                return Response({'error': '家庭不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 构建返回数据
            family_data = {
                'id': family.id,
                'name': family.name,
                'invite_code': family.invite_code,
                'code_enabled': family.code_enabled,
                'max_members': family.max_members,
                'created_at': family.created_at,
                'member_count': family.memberships.filter(is_active=True).count(),
                'current_user_permission': user_membership.permission_level,
                'current_user_display_name': user_membership.display_name
            }
            
            return Response({
                'success': True,
                'family': family_data
            }, status=status.HTTP_200_OK)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"获取家庭详情失败: {str(e)}")
            return Response({'error': f'获取失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilyTransferAdminView(APIView):
    """转让管理员权限"""
    
    @transaction.atomic
    def post(self, request, family_id):
        # 获取openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.data.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 检查用户是否是该家庭的管理员
            admin_membership = FamilyMembership.objects.filter(
                user=user,
                family_id=family_id,
                permission_level='admin',
                is_active=True
            ).first()
            
            if not admin_membership:
                return Response({'error': '您不是该家庭的管理员'}, status=status.HTTP_403_FORBIDDEN)
            
            # 验证输入数据
            serializer = TransferAdminSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': '数据验证失败',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            target_openid = serializer.validated_data['target_user_openid']
            
            # 不能转让给自己
            if target_openid == openid:
                return Response({'error': '不能转让给自己'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 查找目标用户的成员关系
            try:
                target_user = WeChatUser.objects.get(openid=target_openid)
                target_membership = FamilyMembership.objects.get(
                    user=target_user,
                    family_id=family_id,
                    is_active=True
                )
            except WeChatUser.DoesNotExist:
                return Response({'error': '目标用户不存在'}, status=status.HTTP_404_NOT_FOUND)
            except FamilyMembership.DoesNotExist:
                return Response({'error': '目标用户不是该家庭成员'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 执行权限转让
            # 将当前管理员降级为普通成员
            admin_membership.permission_level = 'member'
            admin_membership.save()
            
            # 将目标用户升级为管理员
            target_membership.permission_level = 'admin'
            target_membership.save()
            
            return Response({
                'success': True,
                'message': f'管理员权限已成功转让给 {target_user.nickname or "用户"}'
            }, status=status.HTTP_200_OK)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"转让管理员权限失败: {str(e)}")
            return Response({'error': f'转让失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilyLeaveView(APIView):
    """退出家庭"""
    
    @transaction.atomic
    def post(self, request, family_id):
        # 获取openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.data.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 查找用户的成员关系
            try:
                membership = FamilyMembership.objects.get(
                    user=user,
                    family_id=family_id,
                    is_active=True
                )
            except FamilyMembership.DoesNotExist:
                return Response({'error': '您不是该家庭的成员'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 如果是管理员，检查是否还有其他成员
            if membership.permission_level == 'admin':
                other_members_count = FamilyMembership.objects.filter(
                    family_id=family_id,
                    is_active=True
                ).exclude(user=user).count()
                
                if other_members_count > 0:
                    return Response({
                        'error': '作为管理员，您需要先转让管理员权限或解散家庭才能退出'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 设置成员关系为非活跃状态（软删除）
            membership.is_active = False
            membership.save()
            
            # 如果家庭没有活跃成员了，自动解散家庭
            remaining_members = FamilyMembership.objects.filter(
                family_id=family_id,
                is_active=True
            ).count()
            
            if remaining_members == 0:
                family = Family.objects.get(id=family_id)
                family.code_enabled = False  # 禁用邀请码
                family.save()
            
            return Response({
                'success': True,
                'message': '成功退出家庭'
            }, status=status.HTTP_200_OK)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"退出家庭失败: {str(e)}")
            return Response({'error': f'退出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilyDismissView(APIView):
    """解散家庭（仅管理员）"""
    
    @transaction.atomic
    def post(self, request, family_id):
        # 获取openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.data.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 检查用户是否是该家庭的管理员
            admin_membership = FamilyMembership.objects.filter(
                user=user,
                family_id=family_id,
                permission_level='admin',
                is_active=True
            ).first()
            
            if not admin_membership:
                return Response({'error': '只有管理员才能解散家庭'}, status=status.HTTP_403_FORBIDDEN)
            
            # 获取家庭对象
            try:
                family = Family.objects.get(id=family_id)
            except Family.DoesNotExist:
                return Response({'error': '家庭不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 将所有成员关系设为非活跃状态
            FamilyMembership.objects.filter(
                family_id=family_id,
                is_active=True
            ).update(is_active=False)
            
            # 禁用家庭邀请码
            family.code_enabled = False
            family.save()
            
            return Response({
                'success': True,
                'message': '家庭已成功解散'
            }, status=status.HTTP_200_OK)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"解散家庭失败: {str(e)}")
            return Response({'error': f'解散失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilySettingsView(APIView):
    """家庭设置管理（仅管理员）"""
    
    @transaction.atomic
    def put(self, request, family_id):
        # 获取openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.data.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 检查用户是否是该家庭的管理员
            admin_membership = FamilyMembership.objects.filter(
                user=user,
                family_id=family_id,
                permission_level='admin',
                is_active=True
            ).first()
            
            if not admin_membership:
                return Response({'error': '只有管理员才能修改家庭设置'}, status=status.HTTP_403_FORBIDDEN)
            
            # 获取家庭对象
            try:
                family = Family.objects.get(id=family_id)
            except Family.DoesNotExist:
                return Response({'error': '家庭不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 更新家庭设置
            name = request.data.get('name')
            code_enabled = request.data.get('code_enabled')
            max_members = request.data.get('max_members')
            
            if name is not None:
                if not name.strip():
                    return Response({'error': '家庭名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)
                if len(name) > 128:
                    return Response({'error': '家庭名称不能超过128个字符'}, status=status.HTTP_400_BAD_REQUEST)
                family.name = name.strip()
            
            if code_enabled is not None:
                family.code_enabled = bool(code_enabled)
                
            if max_members is not None:
                if not isinstance(max_members, int) or max_members < 2 or max_members > 20:
                    return Response({'error': '最大成员数必须在2-20之间'}, status=status.HTTP_400_BAD_REQUEST)
                
                # 检查当前成员数是否超过新的限制
                current_members = family.memberships.filter(is_active=True).count()
                if current_members > max_members:
                    return Response({
                        'error': f'当前成员数({current_members})超过新的限制({max_members})'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                family.max_members = max_members
            
            family.save()
            
            # 返回更新后的家庭信息
            family_data = {
                'id': family.id,
                'name': family.name,
                'invite_code': family.invite_code,
                'code_enabled': family.code_enabled,
                'max_members': family.max_members,
                'created_at': family.created_at,
                'member_count': family.memberships.filter(is_active=True).count(),
                'current_user_permission': 'admin'
            }
            
            return Response({
                'success': True,
                'message': '家庭设置已更新',
                'family': family_data
            }, status=status.HTTP_200_OK)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"更新家庭设置失败: {str(e)}")
            return Response({'error': f'更新失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilyRemoveMemberView(APIView):
    """移除家庭成员（仅管理员）"""
    
    @transaction.atomic
    def post(self, request, family_id):
        # 获取openid
        openid = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if not openid:
            openid = request.data.get('openid')
        
        if not openid:
            return Response({'error': '缺少用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = WeChatUser.objects.get(openid=openid)
            
            # 检查用户是否是该家庭的管理员
            admin_membership = FamilyMembership.objects.filter(
                user=user,
                family_id=family_id,
                permission_level='admin',
                is_active=True
            ).first()
            
            if not admin_membership:
                return Response({'error': '只有管理员才能移除成员'}, status=status.HTTP_403_FORBIDDEN)
            
            # 获取要移除的用户openid
            target_openid = request.data.get('target_user_openid')
            if not target_openid:
                return Response({'error': '缺少目标用户标识'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 不能移除自己
            if target_openid == openid:
                return Response({'error': '不能移除自己'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 查找目标用户的成员关系
            try:
                target_user = WeChatUser.objects.get(openid=target_openid)
                target_membership = FamilyMembership.objects.get(
                    user=target_user,
                    family_id=family_id,
                    is_active=True
                )
            except WeChatUser.DoesNotExist:
                return Response({'error': '目标用户不存在'}, status=status.HTTP_404_NOT_FOUND)
            except FamilyMembership.DoesNotExist:
                return Response({'error': '目标用户不是该家庭成员'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 不能移除其他管理员
            if target_membership.permission_level == 'admin':
                return Response({'error': '不能移除其他管理员'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 移除成员（设为非活跃状态）
            target_membership.is_active = False
            target_membership.save()
            
            return Response({
                'success': True,
                'message': f'成功移除成员 {target_user.nickname or "用户"}'
            }, status=status.HTTP_200_OK)
            
        except WeChatUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"移除家庭成员失败: {str(e)}")
            return Response({'error': f'移除失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CookingRecordsView(APIView):
    """用餐记录相关API"""
    
    def get(self, request, family_id):
        """获取家庭用餐记录列表"""
        try:
            openid = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not openid:
                return Response({'error': '未授权访问'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 验证用户是否为家庭成员
            user = WeChatUser.objects.get(openid=openid)
            membership = FamilyMembership.objects.get(
                user=user,
                family_id=family_id,
                is_active=True
            )
            
            # 获取查询参数
            page_size = int(request.GET.get('page_size', 20))
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            cook_id = request.GET.get('cook_id')
            
            # 查询用餐记录
            records = CookingRecord.objects.filter(family_id=family_id).order_by('-cook_date')
            
            # 应用筛选条件
            if start_date:
                records = records.filter(cook_date__gte=start_date)
            if end_date:
                records = records.filter(cook_date__lte=end_date)
            if cook_id:
                records = records.filter(user__openid=cook_id)
            
            # 限制返回数量
            records = records[:page_size]
            
            # 构造返回数据
            records_data = []
            for record in records:
                records_data.append({
                    'id': record.id,
                    'cookId': record.user.openid,
                    'cookName': record.user.nickname,
                    'cookAvatar': record.user.avatar,
                    'dishName': record.meal_name,
                    'cookTime': record.cook_date.isoformat(),
                    'participants': record.participants,
                    'rating': record.rating,
                    'notes': record.notes,
                    'images': record.images,
                    'createdAt': record.created_at.isoformat()
                })
            
            return Response({
                'success': True,
                'records': records_data,
                'total': len(records_data)
            }, status=status.HTTP_200_OK)
            
        except (WeChatUser.DoesNotExist, FamilyMembership.DoesNotExist):
            return Response({'error': '无权限访问该家庭'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"获取用餐记录失败: {str(e)}")
            return Response({'error': f'获取失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, family_id):
        """创建用餐记录"""
        try:
            openid = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not openid:
                return Response({'error': '未授权访问'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 验证用户是否为家庭成员
            user = WeChatUser.objects.get(openid=openid)
            membership = FamilyMembership.objects.get(
                user=user,
                family_id=family_id,
                is_active=True
            )
            
            # 获取请求数据
            meal_name = request.data.get('dish_name')
            cook_time = request.data.get('cook_time')
            participants = request.data.get('participants', [])
            rating = request.data.get('rating', 5)
            notes = request.data.get('notes', '')
            images = request.data.get('images', [])
            
            if not meal_name:
                return Response({'error': '菜品名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建用餐记录
            record = CookingRecord.objects.create(
                user=user,
                family_id=family_id,
                meal_name=meal_name,
                cook_date=cook_time or timezone.now(),
                participants=participants,
                rating=rating,
                notes=notes,
                images=images
            )
            
            # 构造返回数据
            record_data = {
                'id': record.id,
                'cookId': record.user.openid,
                'cookName': record.user.nickname,
                'cookAvatar': record.user.avatar,
                'dishName': record.meal_name,
                'cookTime': record.cook_date.isoformat(),
                'participants': record.participants,
                'rating': record.rating,
                'notes': record.notes,
                'images': record.images,
                'createdAt': record.created_at.isoformat()
            }
            
            return Response({
                'success': True,
                'record': record_data,
                'message': '用餐记录创建成功'
            }, status=status.HTTP_201_CREATED)
            
        except (WeChatUser.DoesNotExist, FamilyMembership.DoesNotExist):
            return Response({'error': '无权限访问该家庭'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"创建用餐记录失败: {str(e)}")
            return Response({'error': f'创建失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FavoriteMealsView(APIView):
    """喜爱菜品相关API"""
    
    def get(self, request, family_id):
        """获取家庭喜爱菜品列表"""
        try:
            openid = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not openid:
                return Response({'error': '未授权访问'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 验证用户是否为家庭成员
            user = WeChatUser.objects.get(openid=openid)
            membership = FamilyMembership.objects.get(
                user=user,
                family_id=family_id,
                is_active=True
            )
            
            # 获取查询参数
            page_size = int(request.GET.get('page_size', 50))
            category = request.GET.get('category')
            sort_by = request.GET.get('sort_by', 'count')
            
            # 查询喜爱菜品
            meals = FavoriteMeal.objects.filter(family_id=family_id)
            
            # 应用筛选条件
            if category:
                meals = meals.filter(category=category)
            
            # 应用排序
            if sort_by == 'count':
                meals = meals.order_by('-count')
            elif sort_by == 'recent':
                meals = meals.order_by('-add_time')
            elif sort_by == 'name':
                meals = meals.order_by('meal_name')
            elif sort_by == 'likes':
                meals = meals.order_by('-likes')
            
            # 限制返回数量
            meals = meals[:page_size]
            
            # 构造返回数据
            meals_data = []
            for meal in meals:
                meals_data.append({
                    'id': meal.id,
                    'name': meal.meal_name,
                    'category': meal.category,
                    'count': meal.count,
                    'image': meal.image,
                    'description': meal.description,
                    'tags': meal.tags,
                    'likes': meal.likes,
                    'isLiked': openid in meal.liked_by,
                    'lastCooked': meal.last_cooked.isoformat() if meal.last_cooked else None,
                    'addedBy': meal.user.nickname,
                    'addTime': meal.add_time.isoformat()
                })
            
            return Response({
                'success': True,
                'meals': meals_data,
                'total': len(meals_data)
            }, status=status.HTTP_200_OK)
            
        except (WeChatUser.DoesNotExist, FamilyMembership.DoesNotExist):
            return Response({'error': '无权限访问该家庭'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"获取喜爱菜品失败: {str(e)}")
            return Response({'error': f'获取失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, family_id):
        """添加喜爱菜品"""
        try:
            openid = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not openid:
                return Response({'error': '未授权访问'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 验证用户是否为家庭成员
            user = WeChatUser.objects.get(openid=openid)
            membership = FamilyMembership.objects.get(
                user=user,
                family_id=family_id,
                is_active=True
            )
            
            # 获取请求数据
            meal_name = request.data.get('name')
            category = request.data.get('category', '其他')
            count = request.data.get('count', 1)
            image = request.data.get('image', '')
            description = request.data.get('description', '')
            tags = request.data.get('tags', [])
            
            if not meal_name:
                return Response({'error': '菜品名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查是否已存在
            if FavoriteMeal.objects.filter(family_id=family_id, meal_name=meal_name).exists():
                return Response({'error': '该菜品已存在'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建喜爱菜品
            meal = FavoriteMeal.objects.create(
                user=user,
                family_id=family_id,
                meal_name=meal_name,
                category=category,
                count=count,
                image=image,
                description=description,
                tags=tags
            )
            
            # 构造返回数据
            meal_data = {
                'id': meal.id,
                'name': meal.meal_name,
                'category': meal.category,
                'count': meal.count,
                'image': meal.image,
                'description': meal.description,
                'tags': meal.tags,
                'likes': meal.likes,
                'isLiked': False,
                'lastCooked': None,
                'addedBy': meal.user.nickname,
                'addTime': meal.add_time.isoformat()
            }
            
            return Response({
                'success': True,
                'meal': meal_data,
                'message': '喜爱菜品添加成功'
            }, status=status.HTTP_201_CREATED)
            
        except (WeChatUser.DoesNotExist, FamilyMembership.DoesNotExist):
            return Response({'error': '无权限访问该家庭'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"添加喜爱菜品失败: {str(e)}")
            return Response({'error': f'添加失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FavoriteMealLikeView(APIView):
    """菜品点赞相关API"""
    
    def post(self, request, family_id, meal_id):
        """点赞菜品"""
        try:
            openid = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not openid:
                return Response({'error': '未授权访问'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 验证用户是否为家庭成员
            user = WeChatUser.objects.get(openid=openid)
            membership = FamilyMembership.objects.get(
                user=user,
                family_id=family_id,
                is_active=True
            )
            
            # 获取菜品
            meal = FavoriteMeal.objects.get(id=meal_id, family_id=family_id)
            
            # 切换点赞状态
            liked_by = meal.liked_by or []
            if openid in liked_by:
                # 取消点赞
                liked_by.remove(openid)
                meal.likes = max(0, meal.likes - 1)
                action = 'unliked'
            else:
                # 点赞
                liked_by.append(openid)
                meal.likes += 1
                action = 'liked'
            
            meal.liked_by = liked_by
            meal.save()
            
            return Response({
                'success': True,
                'action': action,
                'likes': meal.likes,
                'isLiked': openid in meal.liked_by
            }, status=status.HTTP_200_OK)
            
        except (WeChatUser.DoesNotExist, FamilyMembership.DoesNotExist):
            return Response({'error': '无权限访问该家庭'}, status=status.HTTP_403_FORBIDDEN)
        except FavoriteMeal.DoesNotExist:
            return Response({'error': '菜品不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"切换点赞状态失败: {str(e)}")
            return Response({'error': f'操作失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)