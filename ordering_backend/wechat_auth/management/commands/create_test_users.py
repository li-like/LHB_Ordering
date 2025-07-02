from django.core.management.base import BaseCommand
from wechat_auth.models import WeChatUser

class Command(BaseCommand):
    help = '创建测试用户数据'

    def handle(self, *args, **options):
        # 创建测试用户
        test_users = [
            {
                'openid': 'test_openid_001',
                'nickname': '测试用户小明',
                'avatar': 'https://example.com/avatar1.jpg',
                'session_key': 'test_session_key_001'
            },
            {
                'openid': 'test_openid_002', 
                'nickname': '测试用户小红',
                'avatar': 'https://example.com/avatar2.jpg',
                'session_key': 'test_session_key_002'
            },
            {
                'openid': 'test_openid_003',
                'nickname': '测试用户小李',
                'avatar': 'https://example.com/avatar3.jpg', 
                'session_key': 'test_session_key_003'
            }
        ]
        
        for user_data in test_users:
            user, created = WeChatUser.objects.get_or_create(
                openid=user_data['openid'],
                defaults={
                    'nickname': user_data['nickname'],
                    'avatar': user_data['avatar'],
                    'session_key': user_data['session_key']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'创建用户: {user.nickname} (OpenID: {user.openid})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'用户已存在: {user.nickname} (OpenID: {user.openid})')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'操作完成！数据库中共有 {WeChatUser.objects.count()} 个用户')
        )
