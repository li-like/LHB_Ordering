# V2 代码审阅与迁移说明

## 旧版主要问题

| 领域 | 审阅结论 | V2 处理 |
|---|---|---|
| 身份认证 | 旧前端多处把 openid 直接当 Bearer token，身份边界不可信 | 改为服务端签发的高熕 opaque token，仅存 SHA-256 摘要，支持过期和退出撤销 |
| 微信登录 | 旧流程存在前端模拟 openid/sessionKey 的分支 | 小程序只上传临时 code，AppSecret 只由 Django 后端使用 |
| 数据隔离 | 旧 API 与本地缓存并存，数据归属和权限不一致 | 所有菜单、餐次、记录、外观和图片都通过 Membership 做对象级空间隔离 |
| 数据模型 | 以“家庭/订单”为中心，难以表达双方选择、共同确认和用餐回忆 | 改为 Space → Membership → Menu/Section/Dish 与 MealSession/Choice/Plan/Record 两条聚合链 |
| 并发一致性 | 只靠页面状态防止重复操作 | 数据库约束保证每个空间只有一个活动餐次，并防止成员重复添加同一菜品/自定义菜名 |
| 个性化 | 旧 UI 的颜色和文案大量写死，网页与小程序难以共享 | 用空间外观、成员资料、菜单/栏目/菜品三层个性化和受控设计 token 实现 |
| 图片 | 旧实现中本地路径、远程 URL 和上传结果混用 | 统一走鉴权媒体接口，校验真实图片类型、大小、尺寸和空间成员身份 |
| 端一致性 | 页面之间使用不同数据源，且旧文档与实际目录不一致 | H5/小程序共用一套 Vue 页面、store 和 API mapper，启动文档已统一到 V2 |

## 迁移策略

旧代码暂不删除，以便核对原始交互和业务语义；但它们已从 `INSTALLED_APPS`、Django URL 和 `pages.json` 脱离，不会进入 V2 运行时。新功能只应增加在 `ordering_backend/v2`、`Uniapp_Odering/pages/v2`、`components/v2`、`services/api` 和 `store`。

正式上线前建议再完成三项运维工作：

1. 轮换旧仓库历史中可能出现过的微信密钥，并用部署平台密钥管理。
2. 将 SQLite 替换为生产数据库，将 Django 本地 media storage 替换为对象存储/CDN。
3. 配置 HTTPS、明确的 CORS/Allowed Hosts、数据库备份、图片内容审核与隐私政策。
