from rest_framework.exceptions import NotFound, PermissionDenied

from .models import Membership, Space


def get_membership(user, space_id):
    try:
        return Membership.objects.select_related("space", "account").get(space_id=space_id, account=user)
    except Membership.DoesNotExist as exc:
        # 返回 404，避免泄露其他空间是否存在。
        raise NotFound("空间不存在") from exc


def get_space(user, space_id):
    membership = get_membership(user, space_id)
    return membership.space, membership


def require_owner(membership):
    if membership.role != "owner":
        raise PermissionDenied("仅空间创建者可执行此操作")
