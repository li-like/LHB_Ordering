from django.urls import path  # 导入 Django 的 URL 路径模块
from .views import (
    WeChatLoginView, UserStatsView, UserInfoView, AvatarUploadView, NicknameCheckView,
    # 家庭相关视图
    FamilyListView, FamilyCreateView, FamilyJoinView, FamilyMembersView, 
    FamilyDetailView, FamilyTransferAdminView, FamilyLeaveView, 
    FamilyDismissView, FamilySettingsView, FamilyRemoveMemberView,
    # 用餐记录和喜爱菜品相关视图
    CookingRecordsView, FavoriteMealsView, FavoriteMealLikeView
)  # 导入视图类

# 定义了微信登录接口和家庭功能的 URL 路由。
urlpatterns = [  # 定义 URL 路由列表
    # 用户相关接口
    path('login/', WeChatLoginView.as_view(), name='wechat-login'),
    path('user-stats/', UserStatsView.as_view(), name='user-stats'),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
    path('upload-avatar/', AvatarUploadView.as_view(), name='upload-avatar'),
    path('check-nickname/', NicknameCheckView.as_view(), name='check-nickname'),
    
    # 家庭相关接口
    path('families/', FamilyListView.as_view(), name='family-list'),  # 获取用户的家庭列表
    path('families/create/', FamilyCreateView.as_view(), name='family-create'),  # 创建家庭
    path('families/join/', FamilyJoinView.as_view(), name='family-join'),  # 加入家庭
    path('families/<int:family_id>/', FamilyDetailView.as_view(), name='family-detail'),  # 家庭详情
    path('families/<int:family_id>/members/', FamilyMembersView.as_view(), name='family-members'),  # 获取家庭成员
    path('families/<int:family_id>/remove-member/', FamilyRemoveMemberView.as_view(), name='family-remove-member'),  # 移除成员
    path('families/<int:family_id>/transfer-admin/', FamilyTransferAdminView.as_view(), name='family-transfer-admin'),  # 转让管理员
    path('families/<int:family_id>/leave/', FamilyLeaveView.as_view(), name='family-leave'),  # 退出家庭
    path('families/<int:family_id>/dismiss/', FamilyDismissView.as_view(), name='family-dismiss'),  # 解散家庭
    path('families/<int:family_id>/settings/', FamilySettingsView.as_view(), name='family-settings'),  # 家庭设置
    
    # 用餐记录相关接口
    path('families/<int:family_id>/cooking-records/', CookingRecordsView.as_view(), name='cooking-records'),
    path('families/<int:family_id>/cooking-records/create/', CookingRecordsView.as_view(), name='cooking-records-create'),
    
    # 喜爱菜品相关接口
    path('families/<int:family_id>/favorite-meals/', FavoriteMealsView.as_view(), name='favorite-meals'),
    path('families/<int:family_id>/favorite-meals/create/', FavoriteMealsView.as_view(), name='favorite-meals-create'),
    path('families/<int:family_id>/favorite-meals/<int:meal_id>/like/', FavoriteMealLikeView.as_view(), name='favorite-meal-like'),
    path('families/<int:family_id>/favorite-meals/<int:meal_id>/unlike/', FavoriteMealLikeView.as_view(), name='favorite-meal-unlike'),
]