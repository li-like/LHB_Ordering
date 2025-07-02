from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'categories', views.MealCategoryViewSet, basename='mealcategory')
router.register(r'items', views.MealItemViewSet, basename='mealitem')
router.register(r'requests', views.MealRequestViewSet, basename='mealrequest')
router.register(r'confirmations', views.MealConfirmationViewSet, basename='mealconfirmation')
router.register(r'batches', views.MealOrderBatchViewSet, basename='mealorderbatch')
router.register(r'stats', views.FamilyMealStatsViewSet, basename='familymealstats')

# URL模式
urlpatterns = [
    path('api/ordering/', include(router.urls)),
]

# API路由说明：
# /api/ordering/categories/ - 餐品分类管理
# /api/ordering/items/ - 餐品管理  
# /api/ordering/requests/ - 点餐需求管理
# /api/ordering/confirmations/ - 制作确认管理
# /api/ordering/batches/ - 批量点餐管理
# /api/ordering/stats/ - 统计数据（只读）

# 额外的自定义接口：
# /api/ordering/categories/simple_list/ - 简化的分类列表
# /api/ordering/items/popular/ - 热门餐品
# /api/ordering/items/{id}/toggle_availability/ - 切换餐品可用状态
# /api/ordering/requests/pending/ - 待处理的点餐需求
# /api/ordering/requests/summary/ - 点餐需求汇总
# /api/ordering/requests/{id}/cancel/ - 取消点餐需求
# /api/ordering/confirmations/{id}/start_cooking/ - 开始制作
# /api/ordering/confirmations/{id}/complete_cooking/ - 完成制作
# /api/ordering/batches/{id}/add_requests/ - 添加点餐需求到批次
# /api/ordering/stats/{id}/update_stats/ - 更新统计数据
