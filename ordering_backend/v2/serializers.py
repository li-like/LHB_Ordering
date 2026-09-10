from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import (
    Account, Dish, MealChoice, MealPlanItem, MealRecord, MealRecordItem, MediaAsset,
    MealSession, Membership, Menu, MenuSection, Preference, Space,
    SpaceAppearance, ThemePreset,
)


class CleanModelSerializer(serializers.ModelSerializer):
    def _clean(self, instance):
        try:
            instance.full_clean(exclude=None)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages) from exc

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        self._clean(instance)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        self._clean(instance)
        instance.save()
        return instance


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "email", "nickname", "avatar_url", "created_at"]
        read_only_fields = ["id", "email", "created_at"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    nickname = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_email(self, value):
        value = value.lower()
        if Account.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("该邮箱已注册")
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class ThemePresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemePreset
        fields = ["id", "slug", "name", "description", "palette", "background_type", "background_value", "card_style", "corner_radius"]


class AppearanceSerializer(CleanModelSerializer):
    preset_slug = serializers.SlugRelatedField(source="preset", slug_field="slug", queryset=ThemePreset.objects.filter(is_active=True), allow_null=True, required=False)

    class Meta:
        model = SpaceAppearance
        fields = ["preset_slug", "palette_overrides", "background_type", "background_value", "card_style", "corner_radius", "menu_image_style", "home_title", "navigation_labels", "updated_at"]
        read_only_fields = ["updated_at"]

    def validate(self, attrs):
        data = {
            "background_type": attrs.get("background_type", getattr(self.instance, "background_type", "preset")),
            "background_value": attrs.get("background_value", getattr(self.instance, "background_value", "")),
        }
        if data["background_type"] == "preset":
            data["background_value"] = ""
            attrs["background_value"] = ""
        if data["background_type"] in {"color", "gradient", "image"} and not data["background_value"]:
            raise serializers.ValidationError({"background_value": "自定义背景需要提供值"})
        return attrs


class MembershipSerializer(CleanModelSerializer):
    account = AccountSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "account", "role", "display_name", "avatar_url", "avatar_frame", "accent_color", "joined_at"]
        read_only_fields = ["id", "account", "role", "joined_at"]


class SpaceSerializer(CleanModelSerializer):
    my_membership = serializers.SerializerMethodField()
    appearance = AppearanceSerializer(read_only=True)

    class Meta:
        model = Space
        fields = ["id", "name", "max_members", "owner_id", "my_membership", "appearance", "created_at", "updated_at"]
        read_only_fields = ["id", "owner_id", "my_membership", "appearance", "created_at", "updated_at"]

    def get_my_membership(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        membership = next((item for item in obj.memberships.all() if item.account_id == request.user.id), None)
        return MembershipSerializer(membership).data if membership else None


class DishSerializer(CleanModelSerializer):
    class Meta:
        model = Dish
        fields = ["id", "name", "description", "image_url", "image_style", "tags", "sort_order", "is_active"]
        read_only_fields = ["id"]


class MenuSectionSerializer(CleanModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)

    class Meta:
        model = MenuSection
        fields = ["id", "name", "icon", "accent_color", "image_url", "sort_order", "dishes"]
        read_only_fields = ["id", "dishes"]


class MenuSerializer(CleanModelSerializer):
    sections = MenuSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ["id", "space_id", "name", "description", "cover_url", "image_style", "is_default", "sections", "created_at", "updated_at"]
        read_only_fields = ["id", "space_id", "sections", "created_at", "updated_at"]


class MealChoiceSerializer(serializers.ModelSerializer):
    member = MembershipSerializer(read_only=True)
    dish_name = serializers.CharField(source="dish.name", read_only=True)
    dish_image_url = serializers.CharField(source="dish.image_url", read_only=True)

    class Meta:
        model = MealChoice
        fields = ["id", "member", "dish", "dish_name", "dish_image_url", "custom_name", "note", "created_at"]
        read_only_fields = ["id", "member", "dish_name", "dish_image_url", "created_at"]


class MealPlanItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlanItem
        fields = ["id", "dish", "name", "image_url", "quantity", "sort_order"]
        read_only_fields = ["id"]


class MealSessionSerializer(CleanModelSerializer):
    choices = MealChoiceSerializer(many=True, read_only=True)
    plan_items = MealPlanItemSerializer(many=True, read_only=True)

    class Meta:
        model = MealSession
        fields = ["id", "space_id", "title", "meal_type", "scheduled_for", "status", "note", "choices", "plan_items", "confirmed_at", "started_at", "completed_at", "created_at", "updated_at"]
        read_only_fields = ["id", "space_id", "status", "choices", "plan_items", "confirmed_at", "started_at", "completed_at", "created_at", "updated_at"]


class MealRecordItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealRecordItem
        fields = ["id", "dish", "name", "image_url", "quantity"]


class MealRecordSerializer(serializers.ModelSerializer):
    items = MealRecordItemSerializer(many=True, read_only=True)
    completed_by = MembershipSerializer(read_only=True)
    title = serializers.CharField(source="session.title", read_only=True)

    class Meta:
        model = MealRecord
        fields = ["id", "session_id", "title", "completed_by", "photo_url", "note", "rating", "completed_at", "items"]


class PreferenceSerializer(CleanModelSerializer):
    class Meta:
        model = Preference
        fields = ["favorite_tags", "disliked_tags", "allergens", "dietary_restrictions", "note", "updated_at"]
        read_only_fields = ["updated_at"]


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = ["id", "purpose", "file", "url", "width", "height", "size", "content_type", "created_at"]
        read_only_fields = ["id", "url", "width", "height", "size", "content_type", "created_at"]
        extra_kwargs = {"file": {"write_only": True}}

    def validate_file(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("图片不能超过 5MB")
        from PIL import Image, UnidentifiedImageError
        try:
            image = Image.open(value)
            image.verify()
            image = Image.open(value)
            width, height = image.size
            image_format = image.format
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise serializers.ValidationError("文件不是有效图片") from exc
        finally:
            value.seek(0)
        if image_format not in {"JPEG", "PNG", "WEBP"}:
            raise serializers.ValidationError("仅支持 JPEG、PNG、WEBP")
        if width < 16 or height < 16 or width > 4096 or height > 4096:
            raise serializers.ValidationError("图片宽高必须在 16 到 4096 像素之间")
        value._verified_width = width
        value._verified_height = height
        value._verified_format = image_format
        extension = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}[image_format]
        value.name = f"upload.{extension}"
        return value

    def create(self, validated_data):
        upload = validated_data["file"]
        return MediaAsset.objects.create(
            **validated_data,
            width=upload._verified_width,
            height=upload._verified_height,
            size=upload.size,
            content_type={"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}[upload._verified_format],
        )

    def get_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url
