import hashlib
import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


def validate_string_list(value):
    if not isinstance(value, list) or len(value) > 100:
        raise ValidationError("必须是最多 100 项的数组")
    if any(not isinstance(item, str) or len(item) > 80 for item in value):
        raise ValidationError("数组项必须是长度不超过 80 的字符串")


def validate_palette(value):
    allowed = {"primary", "secondary", "accent", "background", "surface", "text", "muted"}
    if not isinstance(value, dict) or not set(value).issubset(allowed):
        raise ValidationError("包含不支持的配色 token")
    for color in value.values():
        if not isinstance(color, str) or len(color) not in (4, 7) or not color.startswith("#"):
            raise ValidationError("颜色必须是 #RGB 或 #RRGGBB")
        try:
            int(color[1:], 16)
        except ValueError as exc:
            raise ValidationError("颜色必须是十六进制") from exc


def validate_navigation_labels(value):
    allowed = {"today", "menu", "records", "us"}
    if not isinstance(value, dict) or not set(value).issubset(allowed):
        raise ValidationError("导航只允许 today/menu/records/us")
    if any(not isinstance(label, str) or not label.strip() or len(label) > 8 for label in value.values()):
        raise ValidationError("导航名称必须是 1 到 8 个字符")


def media_upload_path(instance, filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    return f"v2/{instance.owner_id}/{uuid.uuid4().hex}.{extension}"


class AccountManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email=None, password=None, **extra_fields):
        if not email and not extra_fields.get("wechat_openid"):
            raise ValueError("邮箱或微信身份至少需要一个")
        email = self.normalize_email(email) if email else None
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    wechat_openid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    nickname = models.CharField(max_length=50, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AccountManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or self.nickname or f"微信用户 {self.pk}"


class AuthToken(models.Model):
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="auth_tokens")
    digest = models.CharField(max_length=64, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def digest_value(raw):
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def issue(cls, account):
        raw = secrets.token_urlsafe(40)
        ttl = getattr(settings, "TOKEN_TTL_DAYS", 30)
        cls.objects.create(account=account, digest=cls.digest_value(raw), expires_at=timezone.now() + timedelta(days=ttl))
        return raw

    @property
    def usable(self):
        return self.revoked_at is None and self.expires_at > timezone.now() and self.account.is_active


class ThemePreset(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=160, blank=True)
    palette = models.JSONField(default=dict, validators=[validate_palette])
    background_type = models.CharField(max_length=16, choices=[("color", "纯色"), ("gradient", "渐变"), ("image", "图片")], default="color")
    background_value = models.CharField(max_length=500, blank=True)
    card_style = models.CharField(max_length=16, choices=[("solid", "实色"), ("soft", "柔和"), ("glass", "毛玻璃")], default="soft")
    corner_radius = models.PositiveSmallIntegerField(default=16, validators=[MaxValueValidator(32)])
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Space(models.Model):
    name = models.CharField(max_length=40)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_spaces")
    max_members = models.PositiveSmallIntegerField(default=2, validators=[MinValueValidator(2), MaxValueValidator(20)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = [("owner", "创建者"), ("member", "成员")]
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="memberships")
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default="member")
    display_name = models.CharField(max_length=30, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    avatar_frame = models.CharField(max_length=20, choices=[("none", "无"), ("heart", "爱心"), ("ring", "圆环"), ("floral", "花朵"), ("pixel", "像素")], default="none")
    accent_color = models.CharField(max_length=7, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["space", "account"], name="v2_unique_space_member")]

    def clean(self):
        if self.accent_color:
            validate_palette({"accent": self.accent_color})

    def __str__(self):
        return f"{self.space} / {self.display_name or self.account}"


class Invite(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="invites")
    created_by = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="created_invites")
    code_hash = models.CharField(max_length=64, unique=True, db_index=True)
    code_hint = models.CharField(max_length=4)
    expires_at = models.DateTimeField()
    max_uses = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)])
    use_count = models.PositiveSmallIntegerField(default=0)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def hash_code(code):
        return hashlib.sha256(code.upper().encode("utf-8")).hexdigest()

    @classmethod
    def create_for(cls, membership, hours=72, max_uses=1):
        code = secrets.token_hex(4).upper()
        invite = cls.objects.create(
            space=membership.space, created_by=membership, code_hash=cls.hash_code(code),
            code_hint=code[-4:], expires_at=timezone.now() + timedelta(hours=hours), max_uses=max_uses,
        )
        return invite, code

    @property
    def usable(self):
        return self.revoked_at is None and self.expires_at > timezone.now() and self.use_count < self.max_uses


class SpaceAppearance(models.Model):
    space = models.OneToOneField(Space, on_delete=models.CASCADE, related_name="appearance")
    preset = models.ForeignKey(ThemePreset, on_delete=models.PROTECT, related_name="spaces", null=True, blank=True)
    palette_overrides = models.JSONField(default=dict, blank=True, validators=[validate_palette])
    background_type = models.CharField(max_length=16, choices=[("preset", "跟随主题"), ("color", "纯色"), ("gradient", "渐变"), ("image", "图片")], default="preset")
    background_value = models.CharField(max_length=500, blank=True)
    card_style = models.CharField(max_length=16, choices=[("preset", "跟随主题"), ("solid", "实色"), ("soft", "柔和"), ("glass", "毛玻璃")], default="preset")
    corner_radius = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(32)])
    menu_image_style = models.CharField(max_length=16, choices=[("cover", "满幅"), ("rounded", "圆角"), ("polaroid", "拍立得"), ("circle", "圆形")], default="rounded")
    home_title = models.CharField(max_length=30, default="今天吃什么")
    navigation_labels = models.JSONField(
        default=dict,
        blank=True,
        validators=[validate_navigation_labels],
        help_text="可覆盖 today/menu/records/us 四个导航名称",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.background_type == "image" and self.background_value and not self.background_value.startswith(("https://", "http://", "/media/")):
            raise ValidationError({"background_value": "背景图片必须是 http(s) URL 或 /media/ 路径"})
        if self.background_type == "color" and self.background_value:
            validate_palette({"background": self.background_value})
        if self.background_type == "gradient" and self.background_value not in {"sunset", "sage", "berry", "ocean", "cream"}:
            raise ValidationError({"background_value": "不支持的渐变 token"})


class Menu(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="menus")
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=200, blank=True)
    cover_url = models.URLField(max_length=500, blank=True)
    image_style = models.CharField(max_length=16, choices=[("inherit", "继承"), ("cover", "满幅"), ("rounded", "圆角"), ("polaroid", "拍立得"), ("circle", "圆形")], default="inherit")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MenuSection(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=30)
    icon = models.CharField(max_length=24, blank=True)
    accent_color = models.CharField(max_length=7, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def clean(self):
        if self.accent_color:
            validate_palette({"accent": self.accent_color})


class Dish(models.Model):
    section = models.ForeignKey(MenuSection, on_delete=models.CASCADE, related_name="dishes")
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=240, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    image_style = models.CharField(max_length=16, choices=[("inherit", "继承"), ("cover", "满幅"), ("rounded", "圆角"), ("polaroid", "拍立得"), ("circle", "圆形")], default="inherit")
    tags = models.JSONField(default=list, blank=True, validators=[validate_string_list])
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]


class MealSession(models.Model):
    STATUS = [("draft", "选择中"), ("confirmed", "已确认"), ("cooking", "制作中"), ("completed", "已完成"), ("cancelled", "已取消")]
    MEAL_TYPES = [("breakfast", "早餐"), ("lunch", "午餐"), ("dinner", "晚餐"), ("snack", "加餐")]
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="meal_sessions")
    created_by = models.ForeignKey(Membership, on_delete=models.PROTECT, related_name="created_sessions")
    title = models.CharField(max_length=60, blank=True)
    meal_type = models.CharField(max_length=16, choices=MEAL_TYPES, default="dinner")
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=16, choices=STATUS, default="draft")
    note = models.CharField(max_length=240, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_for", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["space"],
                condition=models.Q(status__in=["draft", "confirmed", "cooking"]),
                name="v2_one_active_meal_session_per_space",
            )
        ]


class MealChoice(models.Model):
    session = models.ForeignKey(MealSession, on_delete=models.CASCADE, related_name="choices")
    member = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="meal_choices")
    dish = models.ForeignKey(Dish, on_delete=models.SET_NULL, null=True, blank=True, related_name="meal_choices")
    custom_name = models.CharField(max_length=50, blank=True)
    note = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "member", "dish"],
                condition=models.Q(dish__isnull=False),
                name="v2_unique_member_dish_choice",
            ),
            models.UniqueConstraint(
                fields=["session", "member", "custom_name"],
                condition=models.Q(dish__isnull=True) & ~models.Q(custom_name=""),
                name="v2_unique_member_custom_choice",
            ),
        ]

    def clean(self):
        if bool(self.dish_id) == bool(self.custom_name.strip()):
            raise ValidationError("dish 与 custom_name 必须且只能提供一个")
        if self.dish_id and self.dish.section.menu.space_id != self.session.space_id:
            raise ValidationError("菜品不属于当前空间")
        if self.member.space_id != self.session.space_id:
            raise ValidationError("成员不属于当前空间")


class MealPlanItem(models.Model):
    session = models.ForeignKey(MealSession, on_delete=models.CASCADE, related_name="plan_items")
    dish = models.ForeignKey(Dish, on_delete=models.SET_NULL, null=True, blank=True, related_name="plan_items")
    name = models.CharField(max_length=50)
    image_url = models.URLField(max_length=500, blank=True)
    quantity = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)])
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]


class MealRecord(models.Model):
    session = models.OneToOneField(MealSession, on_delete=models.PROTECT, related_name="record")
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="meal_records")
    completed_by = models.ForeignKey(Membership, on_delete=models.PROTECT, related_name="completed_records")
    photo_url = models.URLField(max_length=500, blank=True)
    note = models.CharField(max_length=500, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-completed_at", "-id"]


class MealRecordItem(models.Model):
    record = models.ForeignKey(MealRecord, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey(Dish, on_delete=models.SET_NULL, null=True, blank=True, related_name="record_items")
    name = models.CharField(max_length=50)
    image_url = models.URLField(max_length=500, blank=True)
    quantity = models.PositiveSmallIntegerField(default=1)


class Preference(models.Model):
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE, related_name="preference")
    favorite_tags = models.JSONField(default=list, blank=True, validators=[validate_string_list])
    disliked_tags = models.JSONField(default=list, blank=True, validators=[validate_string_list])
    allergens = models.JSONField(default=list, blank=True, validators=[validate_string_list])
    dietary_restrictions = models.JSONField(default=list, blank=True, validators=[validate_string_list])
    note = models.CharField(max_length=500, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class MediaAsset(models.Model):
    PURPOSES = [
        ("background", "页面背景"), ("avatar", "成员头像"),
        ("menu", "菜单封面"), ("dish", "菜品图片"), ("record", "用餐记录"),
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="media_assets")
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="media_assets", null=True, blank=True)
    purpose = models.CharField(max_length=16, choices=PURPOSES)
    file = models.ImageField(upload_to=media_upload_path, width_field="width", height_field="height")
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
