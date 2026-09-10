from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Account, AuthToken, Dish, Invite, MealChoice, MealPlanItem, MealRecord,
    MealRecordItem, MealSession, MediaAsset, Membership, Menu, MenuSection,
    Preference, Space, SpaceAppearance, ThemePreset,
)


@admin.register(Account)
class AccountAdmin(UserAdmin):
    model = Account
    ordering = ("-created_at",)
    list_display = ("id", "email", "nickname", "is_active", "is_staff", "created_at")
    search_fields = ("email", "nickname", "wechat_openid")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("资料", {"fields": ("nickname", "avatar_url", "wechat_openid")}),
        ("权限", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("时间", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "is_staff", "is_active")}),)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "expires_at", "revoked_at", "last_used_at")
    readonly_fields = ("digest", "created_at", "last_used_at")


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "max_members", "created_at")
    search_fields = ("name", "owner__email")
    inlines = (MembershipInline,)


class DishInline(admin.TabularInline):
    model = Dish
    extra = 0


@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "menu", "sort_order")
    inlines = (DishInline,)


admin.site.register([
    ThemePreset, SpaceAppearance, Membership, Invite, Menu, Dish,
    MealSession, MealChoice, MealPlanItem, MealRecord, MealRecordItem,
    Preference, MediaAsset,
])
