# 情侣点餐 V2 后端

V2 是独立的 Django/DRF 模块化单体。旧 `wechat_auth`、`ordering`、`recipes` 源码被保留，但不再加入 `INSTALLED_APPS` 或 URL，因而不会加载旧迁移链和匿名接口。

## 本地启动

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

配置项见 `.env.example`。生产环境必须提供随机 `DJANGO_SECRET_KEY`，关闭 `DJANGO_DEBUG`，配置明确域名和 CORS 来源，并在微信后台轮换旧仓库中曾暴露的 AppSecret。图片默认写入 `media/v2/<account-id>/`；生产环境可将 Django storage 替换成 S3/COS 兼容对象存储。

## 认证

所有受保护接口使用：

```http
Authorization: Bearer <opaque-token>
```

服务端只保存 token 的 SHA-256 摘要，原 token 仅在注册/登录时返回，可通过 logout 撤销。微信端只接受临时 `code` 并由服务端调用 `jscode2session`；openid 永远不能充当 token。

| 方法 | 路径 | 用途 |
|---|---|---|
| POST | `/api/v2/auth/register` | H5 邮箱注册，字段 `email/password/nickname?` |
| POST | `/api/v2/auth/login` | H5 邮箱密码登录 |
| POST | `/api/v2/auth/wechat` | 小程序 `code` 登录，允许 `nickname/avatar_url` |
| POST | `/api/v2/auth/logout` | 撤销当前 token |
| GET/PATCH | `/api/v2/auth/me` | 当前账号资料 |

## 空间、主题和个性化

| 方法 | 路径 |
|---|---|
| GET/POST | `/api/v2/spaces` |
| POST | `/api/v2/spaces/join` (`code`) |
| GET/PATCH | `/api/v2/spaces/{id}` |
| GET | `/api/v2/spaces/{id}/members` |
| PATCH | `/api/v2/spaces/{id}/members/me` |
| POST | `/api/v2/spaces/{id}/invites` |
| GET | `/api/v2/themes` |
| GET/PATCH | `/api/v2/spaces/{id}/appearance` |
| GET/PATCH | `/api/v2/spaces/{id}/preferences/me` |
| POST | `/api/v2/media-assets` (multipart) |

空间默认上限两人，但模型允许扩展到 20 人。成员个性化字段为 `display_name/avatar_url/avatar_frame/accent_color`。外观字段为：

- `preset_slug`：预置主题标识；默认包含暖心餐桌、莓果约会、鼠尾草厨房、夜色小馆。
- `palette_overrides`：只允许 `primary/secondary/accent/background/surface/text/muted`，值只能是十六进制颜色。
- `background_type/background_value`：只允许 preset、颜色、受控渐变 token 或图片 URL。
- `card_style/corner_radius/menu_image_style/home_title`：卡片形态、0–32 圆角、菜单图片形态和首页名。
- `navigation_labels`：只允许覆盖 `today/menu/records/us`，名称 1–8 字。

不接受 CSS 字符串。上传图片需要有效 token；只接受真实 JPEG/PNG/WEBP、最大 5MB、宽高 16–4096。关联 `space_id` 时会检查成员身份，响应 `url` 是可直接保存到背景、头像、菜单、菜品或记录字段的绝对 URL。

## 菜单和点餐闭环

| 方法 | 路径 |
|---|---|
| GET/POST | `/api/v2/spaces/{id}/menus` |
| GET/PATCH | `/api/v2/menus/{id}` |
| POST | `/api/v2/menus/{id}/sections` |
| PATCH/DELETE | `/api/v2/sections/{id}` |
| POST | `/api/v2/sections/{id}/dishes` |
| PATCH/DELETE | `/api/v2/dishes/{id}` |
| GET/POST | `/api/v2/spaces/{id}/meal-sessions` |
| GET/PATCH | `/api/v2/meal-sessions/{id}` |
| POST | `/api/v2/meal-sessions/{id}/choices` |
| POST | `/api/v2/meal-sessions/{id}/confirm` |
| POST | `/api/v2/meal-sessions/{id}/start` |
| POST | `/api/v2/meal-sessions/{id}/complete` |
| GET | `/api/v2/spaces/{id}/records` |

创建空间会初始化一份可改名、换图、重排的默认菜单，包含三类八道菜和栏目配色。`choices` 接受 `dish` 或 `custom_name`；`confirm` 可显式传 `items`，不传则把双方选择去重后生成最终计划。状态严格按 `draft → confirmed → cooking → completed` 流转，完成时把计划快照到不可受后续菜单改名影响的 `MealRecordItem`。

`GET /api/v2/spaces/{id}/meal-sessions?active=true` 只返回未完成的餐次。数据库约束保证每个空间最多只有一个 `draft/confirmed/cooking` 餐次，并阻止同一成员重复加入同一菜品或自定义菜名。

完成餐次时可提交 `rating` (1–5)、`note` 和鉴权上传后的 `photo_url`。记录响应会包含原餐次 `title`、评分、小记、照片和菜品快照，无效 URL 或超长文本不会落库。

所有按空间组织的资源都会通过当前 `Membership` 做对象级隔离，未加入空间时统一返回 404，避免泄露资源是否存在。

## 校验

```powershell
python manage.py test v2 -v 2
python manage.py makemigrations --check --dry-run
python manage.py check
python manage.py check --deploy
```

`check --deploy` 在默认开发配置下会提示 DEBUG、开发密钥、HTTPS/HSTS 等警告；这些是部署配置警告，不是模型或路由错误。生产环境应通过环境变量消除它们。
