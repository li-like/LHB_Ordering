from django.contrib import admin
from .models import (
    MealCategory, MealItem, MealRequest, 
    MealConfirmation, MealOrderBatch, FamilyMealStats
)

@admin.register(MealCategory)
class MealCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'sort_order', 'is_active', 'created_by', 'created_at']
    list_filter = ['family', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['family', 'sort_order']

@admin.register(MealItem)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'category', 'meal_type', 'difficulty', 'prep_time', 'popularity', 'is_available']
    list_filter = ['family', 'category', 'meal_type', 'difficulty', 'is_available', 'created_at']
    search_fields = ['name', 'description', 'tags']
    ordering = ['family', '-popularity', 'name']

@admin.register(MealRequest)
class MealRequestAdmin(admin.ModelAdmin):
    list_display = ['meal_item', 'requester', 'family', 'quantity', 'priority', 'status', 'created_at']
    list_filter = ['family', 'status', 'priority', 'created_at']
    search_fields = ['meal_item__name', 'requester__nickname', 'special_requests']
    ordering = ['-created_at']

@admin.register(MealConfirmation)
class MealConfirmationAdmin(admin.ModelAdmin):
    list_display = ['meal_request', 'confirmer', 'status', 'estimated_time', 'actual_completion_time']
    list_filter = ['status', 'created_at']
    search_fields = ['meal_request__meal_item__name', 'confirmer__nickname']
    ordering = ['-created_at']

@admin.register(MealOrderBatch)
class MealOrderBatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'coordinator', 'target_time', 'status', 'created_at']
    list_filter = ['family', 'status', 'target_time']
    search_fields = ['name', 'coordinator__nickname']
    ordering = ['-target_time']

@admin.register(FamilyMealStats)
class FamilyMealStatsAdmin(admin.ModelAdmin):
    list_display = ['family', 'total_meals_ordered', 'total_meals_completed', 'most_popular_meal', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['family__name', 'most_popular_meal']
    readonly_fields = ['last_updated']
