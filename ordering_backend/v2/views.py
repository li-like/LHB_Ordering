import requests

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Account, AuthToken, Dish, Invite, MealChoice, MealPlanItem, MealRecord, MediaAsset,
    MealRecordItem, MealSession, Membership, Menu, MenuSection, Preference,
    Space, ThemePreset,
)
from .permissions import get_membership, get_space
from .serializers import (
    AccountSerializer, AppearanceSerializer, DishSerializer, LoginSerializer,
    MealChoiceSerializer, MealRecordSerializer, MealSessionSerializer, MediaAssetSerializer,
    MembershipSerializer, MenuSectionSerializer, MenuSerializer,
    PreferenceSerializer, RegisterSerializer, SpaceSerializer,
    ThemePresetSerializer,
)
from .services import initialize_space


def auth_payload(account):
    return {"token": AuthToken.issue(account), "account": AccountSerializer(account).data}


def menu_for_user(user, menu_id):
    menu = get_object_or_404(Menu.objects.prefetch_related("sections__dishes"), pk=menu_id)
    get_membership(user, menu.space_id)
    return menu


def section_for_user(user, section_id):
    section = get_object_or_404(MenuSection.objects.select_related("menu"), pk=section_id)
    get_membership(user, section.menu.space_id)
    return section


def dish_for_user(user, dish_id):
    dish = get_object_or_404(Dish.objects.select_related("section__menu"), pk=dish_id)
    get_membership(user, dish.section.menu.space_id)
    return dish


def session_for_user(user, session_id):
    session = get_object_or_404(
        MealSession.objects.select_related("space", "created_by").prefetch_related("choices__member__account", "choices__dish", "plan_items"),
        pk=session_id,
    )
    membership = get_membership(user, session.space_id)
    return session, membership


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = Account.objects.create_user(**serializer.validated_data)
        return Response(auth_payload(account), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        account = authenticate(request, email=email, password=serializer.validated_data["password"])
        if account is None:
            return Response({"detail": "邮箱或密码错误"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(auth_payload(account))


class WechatLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code", "").strip()
        if not code:
            raise ValidationError({"code": "微信登录 code 必填"})
        if not settings.WECHAT_APP_ID or not settings.WECHAT_APP_SECRET:
            return Response({"detail": "服务端尚未配置微信登录"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            result = requests.get(
                "https://api.weixin.qq.com/sns/jscode2session",
                params={"appid": settings.WECHAT_APP_ID, "secret": settings.WECHAT_APP_SECRET, "js_code": code, "grant_type": "authorization_code"},
                timeout=8,
            ).json()
        except (requests.RequestException, ValueError):
            return Response({"detail": "微信服务暂时不可用"}, status=status.HTTP_502_BAD_GATEWAY)
        openid = result.get("openid")
        if not openid:
            return Response({"detail": result.get("errmsg", "微信登录失败")}, status=status.HTTP_400_BAD_REQUEST)
        account, _ = Account.objects.get_or_create(wechat_openid=openid)
        changed = False
        nickname = request.data.get("nickname")
        avatar_url = request.data.get("avatar_url")
        if nickname is not None:
            account.nickname = str(nickname)[:50]
            changed = True
        if avatar_url is not None:
            account.avatar_url = str(avatar_url)[:500]
            changed = True
        if changed:
            account.full_clean()
            account.save()
        return Response(auth_payload(account))


class LogoutView(APIView):
    def post(self, request):
        token = request.auth
        token.revoked_at = timezone.now()
        token.save(update_fields=["revoked_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response(AccountSerializer(request.user).data)

    def patch(self, request):
        serializer = AccountSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SpaceListCreateView(APIView):
    def get(self, request):
        spaces = Space.objects.filter(memberships__account=request.user).select_related("appearance__preset").prefetch_related("memberships__account").distinct()
        return Response(SpaceSerializer(spaces, many=True, context={"request": request}).data)

    @transaction.atomic
    def post(self, request):
        serializer = SpaceSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        space = serializer.save(owner=request.user)
        initialize_space(space, request.user)
        space = Space.objects.select_related("appearance__preset").prefetch_related("memberships__account").get(pk=space.pk)
        return Response(SpaceSerializer(space, context={"request": request}).data, status=status.HTTP_201_CREATED)


class JoinSpaceView(APIView):
    @transaction.atomic
    def post(self, request):
        code = str(request.data.get("code", "")).strip().upper()
        if not code:
            raise ValidationError({"code": "邀请码必填"})
        try:
            invite = Invite.objects.select_for_update().select_related("space").get(code_hash=Invite.hash_code(code))
        except Invite.DoesNotExist as exc:
            raise ValidationError({"code": "邀请码无效"}) from exc
        if not invite.usable:
            raise ValidationError({"code": "邀请码已过期或不可用"})
        space = Space.objects.select_for_update().get(pk=invite.space_id)
        existing = Membership.objects.filter(space=space, account=request.user).first()
        if existing:
            return Response(SpaceSerializer(space, context={"request": request}).data)
        if Membership.objects.filter(space=space).count() >= space.max_members:
            raise ValidationError({"code": "空间成员已满"})
        membership = Membership.objects.create(space=space, account=request.user, display_name=request.user.nickname or "伴侣")
        Preference.objects.create(membership=membership)
        invite.use_count += 1
        invite.save(update_fields=["use_count"])
        space = Space.objects.select_related("appearance__preset").prefetch_related("memberships__account").get(pk=space.pk)
        return Response(SpaceSerializer(space, context={"request": request}).data, status=status.HTTP_201_CREATED)


class SpaceDetailView(APIView):
    def get(self, request, space_id):
        space, _ = get_space(request.user, space_id)
        space = Space.objects.select_related("appearance__preset").prefetch_related("memberships__account").get(pk=space.pk)
        return Response(SpaceSerializer(space, context={"request": request}).data)

    def patch(self, request, space_id):
        space, _ = get_space(request.user, space_id)
        serializer = SpaceSerializer(space, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MembersView(APIView):
    def get(self, request, space_id):
        space, _ = get_space(request.user, space_id)
        members = space.memberships.select_related("account").order_by("joined_at")
        return Response(MembershipSerializer(members, many=True).data)


class MyMembershipView(APIView):
    def patch(self, request, space_id):
        membership = get_membership(request.user, space_id)
        serializer = MembershipSerializer(membership, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InviteCreateView(APIView):
    def post(self, request, space_id):
        membership = get_membership(request.user, space_id)
        hours = request.data.get("expires_in_hours", 72)
        max_uses = request.data.get("max_uses", 1)
        try:
            hours, max_uses = int(hours), int(max_uses)
        except (TypeError, ValueError) as exc:
            raise ValidationError("expires_in_hours 和 max_uses 必须是整数") from exc
        if not 1 <= hours <= 720 or not 1 <= max_uses <= membership.space.max_members:
            raise ValidationError("邀请码有效期或使用次数超出允许范围")
        invite, code = Invite.create_for(membership, hours=hours, max_uses=max_uses)
        return Response({"id": invite.id, "code": code, "expires_at": invite.expires_at, "max_uses": invite.max_uses}, status=status.HTTP_201_CREATED)


class ThemeListView(APIView):
    def get(self, request):
        themes = ThemePreset.objects.filter(is_active=True).order_by("sort_order", "id")
        return Response(ThemePresetSerializer(themes, many=True).data)


class AppearanceView(APIView):
    def get(self, request, space_id):
        space, _ = get_space(request.user, space_id)
        return Response(AppearanceSerializer(space.appearance).data)

    def patch(self, request, space_id):
        space, _ = get_space(request.user, space_id)
        serializer = AppearanceSerializer(space.appearance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MenuListCreateView(APIView):
    def get(self, request, space_id):
        space, _ = get_space(request.user, space_id)
        menus = space.menus.prefetch_related("sections__dishes").order_by("-is_default", "id")
        return Response(MenuSerializer(menus, many=True).data)

    def post(self, request, space_id):
        space, _ = get_space(request.user, space_id)
        serializer = MenuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        menu = serializer.save(space=space)
        return Response(MenuSerializer(menu).data, status=status.HTTP_201_CREATED)


class MenuDetailView(APIView):
    def get(self, request, menu_id):
        return Response(MenuSerializer(menu_for_user(request.user, menu_id)).data)

    def patch(self, request, menu_id):
        menu = menu_for_user(request.user, menu_id)
        serializer = MenuSerializer(menu, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get("is_default"):
            Menu.objects.filter(space=menu.space, is_default=True).exclude(pk=menu.pk).update(is_default=False)
        serializer.save()
        return Response(serializer.data)


class MenuSectionCreateView(APIView):
    def post(self, request, menu_id):
        menu = menu_for_user(request.user, menu_id)
        serializer = MenuSectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(menu=menu)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MenuSectionDetailView(APIView):
    def patch(self, request, section_id):
        section = section_for_user(request.user, section_id)
        serializer = MenuSectionSerializer(section, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, section_id):
        section_for_user(request.user, section_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DishCreateView(APIView):
    def post(self, request, section_id):
        section = section_for_user(request.user, section_id)
        serializer = DishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(section=section)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DishDetailView(APIView):
    def patch(self, request, dish_id):
        dish = dish_for_user(request.user, dish_id)
        serializer = DishSerializer(dish, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, dish_id):
        dish = dish_for_user(request.user, dish_id)
        dish.is_active = False
        dish.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class MealSessionListCreateView(APIView):
    def get(self, request, space_id):
        space, _ = get_space(request.user, space_id)
        sessions = space.meal_sessions.prefetch_related("choices__member__account", "choices__dish", "plan_items")
        if str(request.query_params.get("active", "")).lower() in {"1", "true", "yes"}:
            sessions = sessions.filter(status__in=["draft", "confirmed", "cooking"])
        return Response(MealSessionSerializer(sessions, many=True).data)

    def post(self, request, space_id):
        space, membership = get_space(request.user, space_id)
        serializer = MealSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if space.meal_sessions.filter(status__in=["draft", "confirmed", "cooking"]).exists():
            raise ValidationError({"detail": "当前已有正在进行的餐次，请先完成后再开新桌"})
        try:
            session = serializer.save(space=space, created_by=membership)
        except IntegrityError as exc:
            raise ValidationError({"detail": "当前已有正在进行的餐次，请先完成后再开新桌"}) from exc
        return Response(MealSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class MealSessionDetailView(APIView):
    def get(self, request, session_id):
        session, _ = session_for_user(request.user, session_id)
        return Response(MealSessionSerializer(session).data)

    def patch(self, request, session_id):
        session, _ = session_for_user(request.user, session_id)
        if session.status not in {"draft", "confirmed"}:
            raise ValidationError("当前状态不可修改")
        serializer = MealSessionSerializer(session, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChoiceCreateView(APIView):
    def post(self, request, session_id):
        session, membership = session_for_user(request.user, session_id)
        if session.status != "draft":
            raise ValidationError("只能在选择阶段添加意愿")
        serializer = MealChoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dish = serializer.validated_data.get("dish")
        if dish and dish.section.menu.space_id != session.space_id:
            raise ValidationError({"dish": "菜品不属于当前空间"})
        choice = MealChoice(session=session, member=membership, **serializer.validated_data)
        try:
            choice.full_clean()
            choice.save()
        except IntegrityError as exc:
            raise ValidationError("该意愿已添加") from exc
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages) from exc
        return Response(MealChoiceSerializer(choice).data, status=status.HTTP_201_CREATED)


class ConfirmSessionView(APIView):
    @transaction.atomic
    def post(self, request, session_id):
        session, _ = session_for_user(request.user, session_id)
        session = MealSession.objects.select_for_update().get(pk=session.pk)
        if session.status != "draft":
            raise ValidationError("只有选择中的餐次可以确认")
        supplied = request.data.get("items")
        items = []
        if supplied is None:
            seen = set()
            for choice in session.choices.select_related("dish"):
                key = (choice.dish_id, choice.custom_name)
                if key in seen:
                    continue
                seen.add(key)
                items.append({"dish": choice.dish, "name": choice.dish.name if choice.dish else choice.custom_name, "image_url": choice.dish.image_url if choice.dish else "", "quantity": 1})
        else:
            if not isinstance(supplied, list):
                raise ValidationError({"items": "必须是数组"})
            for raw in supplied:
                if not isinstance(raw, dict):
                    raise ValidationError({"items": "每项必须是对象"})
                dish = None
                if raw.get("dish"):
                    dish = dish_for_user(request.user, raw["dish"])
                    if dish.section.menu.space_id != session.space_id:
                        raise ValidationError({"items": "菜品不属于当前空间"})
                name = str(raw.get("name") or (dish.name if dish else "")).strip()
                if not name or len(name) > 50:
                    raise ValidationError({"items": "每项需要有效名称"})
                quantity = raw.get("quantity", 1)
                if not isinstance(quantity, int) or not 1 <= quantity <= 20:
                    raise ValidationError({"items": "数量必须为 1 到 20 的整数"})
                items.append({"dish": dish, "name": name, "image_url": raw.get("image_url") or (dish.image_url if dish else ""), "quantity": quantity})
        if not items:
            raise ValidationError({"items": "确认菜单不能为空"})
        session.plan_items.all().delete()
        MealPlanItem.objects.bulk_create([MealPlanItem(session=session, sort_order=index, **item) for index, item in enumerate(items)])
        session.status = "confirmed"
        session.confirmed_at = timezone.now()
        session.save(update_fields=["status", "confirmed_at", "updated_at"])
        session, _ = session_for_user(request.user, session.id)
        return Response(MealSessionSerializer(session).data)


class StartSessionView(APIView):
    def post(self, request, session_id):
        session, _ = session_for_user(request.user, session_id)
        if session.status != "confirmed":
            raise ValidationError("只有已确认的餐次可以开始制作")
        session.status = "cooking"
        session.started_at = timezone.now()
        session.save(update_fields=["status", "started_at", "updated_at"])
        return Response(MealSessionSerializer(session).data)


class CompleteSessionView(APIView):
    @transaction.atomic
    def post(self, request, session_id):
        session, membership = session_for_user(request.user, session_id)
        session = MealSession.objects.select_for_update().get(pk=session.pk)
        if session.status not in {"confirmed", "cooking"}:
            raise ValidationError("只有已确认或制作中的餐次可以完成")
        if not session.plan_items.exists():
            raise ValidationError("确认菜单为空")
        rating = request.data.get("rating")
        if rating is not None and (not isinstance(rating, int) or not 1 <= rating <= 5):
            raise ValidationError({"rating": "评分必须为 1 到 5 的整数"})
        completed_at = timezone.now()
        record = MealRecord(
            session=session, space=session.space, completed_by=membership,
            photo_url=request.data.get("photo_url", ""), note=request.data.get("note", ""),
            rating=rating, completed_at=completed_at,
        )
        try:
            record.full_clean()
            record.save()
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages) from exc
        MealRecordItem.objects.bulk_create([
            MealRecordItem(record=record, dish=item.dish, name=item.name, image_url=item.image_url, quantity=item.quantity)
            for item in session.plan_items.all()
        ])
        session.status = "completed"
        session.completed_at = completed_at
        session.save(update_fields=["status", "completed_at", "updated_at"])
        record = MealRecord.objects.prefetch_related("items").select_related("session", "completed_by__account").get(pk=record.pk)
        return Response(MealRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class RecordListView(APIView):
    def get(self, request, space_id):
        space, _ = get_space(request.user, space_id)
        records = space.meal_records.select_related("session", "completed_by__account").prefetch_related("items")
        return Response(MealRecordSerializer(records, many=True).data)


class PreferenceView(APIView):
    def get_object(self, request, space_id):
        membership = get_membership(request.user, space_id)
        preference, _ = Preference.objects.get_or_create(membership=membership)
        return preference

    def get(self, request, space_id):
        return Response(PreferenceSerializer(self.get_object(request, space_id)).data)

    def patch(self, request, space_id):
        preference = self.get_object(request, space_id)
        serializer = PreferenceSerializer(preference, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MediaAssetCreateView(APIView):
    def post(self, request):
        space = None
        space_id = request.data.get("space_id")
        if space_id:
            space, _ = get_space(request.user, space_id)
        serializer = MediaAssetSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        asset = serializer.save(owner=request.user, space=space)
        return Response(MediaAssetSerializer(asset, context={"request": request}).data, status=status.HTTP_201_CREATED)
