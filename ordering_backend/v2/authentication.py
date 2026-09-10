from django.utils import timezone
from rest_framework import authentication, exceptions

from .models import AuthToken


class OpaqueTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        value = authentication.get_authorization_header(request).decode("utf-8")
        if not value:
            return None
        parts = value.split()
        if len(parts) != 2 or parts[0].lower() != self.keyword.lower():
            raise exceptions.AuthenticationFailed("Authorization 格式应为 Bearer <token>")
        digest = AuthToken.digest_value(parts[1])
        try:
            token = AuthToken.objects.select_related("account").get(digest=digest)
        except AuthToken.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("无效的访问令牌") from exc
        if not token.usable:
            raise exceptions.AuthenticationFailed("访问令牌已过期或被撤销")
        AuthToken.objects.filter(pk=token.pk).update(last_used_at=timezone.now())
        request.auth_token = token
        return token.account, token

    def authenticate_header(self, request):
        return self.keyword
