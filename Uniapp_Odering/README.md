# 情侣点餐 V2 前端

基于 UniApp + Vue 3，同一套业务代码支持 H5 和微信小程序。当前运行页面均在 `pages/v2`，不再依赖旧版本地模拟数据。

## 开发与构建

```powershell
npm install
npm run dev:h5
npm run dev:mp-weixin
npm run build:h5
npm run build:mp-weixin
```

后端地址由 `VITE_API_BASE_URL` 控制，参考 `.env.example`。未设置时默认为 `http://127.0.0.1:8000/api/v2`。

## 页面

- `auth`：H5 邮箱注册/登录和小程序微信登录。
- `onboarding`：创建两人空间或使用邀请码加入。
- `home`：今晚、菜单、记录、我们四个动态导航面板。
- `customize`：空间、成员、背景、主题、颜色、卡片、导航和菜单展示设置。
- `dish/edit`：新建或修改菜品名称、描述、标签和图片。

底部导航使用自定义组件，因为原生 tabBar 无法按每个情侣空间动态改名。外观由 `design/themes.js` 的受控 token 生成，确保自定义在 H5 与小程序上保持一致。
