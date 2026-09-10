"""
URL configuration for ordering_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin  # 导入 Django 管理后台模块
from django.urls import path, include  # 导入 URL 路径和包含模块
from django.conf import settings  # 导入设置模块
from django.conf.urls.static import static  # 导入静态文件处理模块

urlpatterns = [  # 定义项目的 URL 路由列表
    path('admin/', admin.site.urls),  # 将 /admin/ 路径映射到管理后台
    path('api/v2/', include('v2.urls')),
]

# 在开发环境中处理媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
