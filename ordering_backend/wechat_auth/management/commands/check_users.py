from django.core.management.base import BaseCommand
from wechat_auth.models import WeChatUser

class Command(BaseCommand):
    help = '检查数据库中的用户数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--openid',
            type=str,
            help='指定用户的openid',
        )

    def handle(self, *args, **options):
        openid = options.get('openid')
        
        if openid:
            try:
                user = WeChatUser.objects.get(openid=openid)
                self.stdout.write(
                    self.style.SUCCESS(f'找到用户: {user.nickname}')
                )
                self.stdout.write(f'OpenID: {user.openid}')
                self.stdout.write(f'昵称: {user.nickname}')
                self.stdout.write(f'头像: {user.avatar}')
                self.stdout.write(f'创建时间: {user.created_at}')
                self.stdout.write(f'更新时间: {user.updated_at}')
            except WeChatUser.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'未找到openid为 {openid} 的用户')
                )
        else:
            # 显示所有用户
            users = WeChatUser.objects.all()
            self.stdout.write(f'数据库中共有 {users.count()} 个用户:')
            for user in users:
                self.stdout.write(f'- {user.nickname} ({user.openid[:10]}...)')
                self.stdout.write(f'  头像: {user.avatar}')
                self.stdout.write(f'  更新时间: {user.updated_at}')
                self.stdout.write('---')
