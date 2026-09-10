<template>
  <view class="auth-page">
    <view class="auth-decoration deco-one" /><view class="auth-decoration deco-two" />
    <view class="auth-layout">
      <view class="brand-panel">
        <view class="brand-mark"><view class="heart-left" /><view class="heart-right" /></view>
        <text class="eyebrow">TWO AT THE TABLE</text>
        <text class="brand-title">把“吃什么”变成<br/>两个人的小期待</text>
        <text class="brand-copy">一起选菜、一起决定，也一起留下每顿饭的故事。</text>
        <view class="brand-points"><text>共同菜单</text><text>专属主题</text><text>口味记忆</text></view>
      </view>

      <view class="auth-card v2-card">
        <view class="segmented">
          <button :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
          <button :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
        </view>
        <text class="form-title">{{ mode === 'login' ? '欢迎回到餐桌' : '创建你的餐桌身份' }}</text>
        <text class="form-copy">{{ mode === 'login' ? '今晚也一起认真吃饭。' : '注册后可以创建或加入情侣空间。' }}</text>

        <view v-if="mode === 'register'" class="field">
          <text>你的称呼</text><input v-model.trim="form.display_name" maxlength="20" placeholder="例如：小满" />
        </view>
        <view class="field">
          <text>邮箱</text><input v-model.trim="form.email" type="text" placeholder="name@example.com" />
        </view>
        <view class="field">
          <text>密码</text><input v-model="form.password" password placeholder="至少 8 位" @confirm="submit" />
        </view>
        <button class="primary-button" :loading="loading" :disabled="loading" @click="submit">{{ mode === 'login' ? '进入我们的餐桌' : '注册并继续' }}</button>

        <!-- #ifdef MP-WEIXIN -->
        <view class="divider"><view/><text>或</text><view/></view>
        <button class="wechat-button" :loading="wechatLoading" @click="wechat">微信快捷登录</button>
        <!-- #endif -->

        <button v-if="showDev" class="dev-button" @click="fillDev">开发体验：填入本地账号</button>
        <text class="agreement">继续即代表你同意仅将空间内容分享给已加入的伴侣。</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import store from '../../../store'

const mode = ref('login')
const loading = ref(false)
const wechatLoading = ref(false)
const form = reactive({ email: '', password: '', display_name: '' })
const showDev = computed(() => import.meta.env && import.meta.env.VITE_ENABLE_DEV_LOGIN === 'true')

function message(error) { uni.showToast({ title: error.message || '操作失败', icon: 'none', duration: 2600 }) }
async function continueToApp() {
  const result = await store.bootstrap()
  uni.reLaunch({ url: result.route === 'home' ? '/pages/v2/home/index' : '/pages/v2/onboarding/index' })
}
async function submit() {
  if (!/^\S+@\S+\.\S+$/.test(form.email)) return uni.showToast({ title: '请输入有效邮箱', icon: 'none' })
  if (form.password.length < 8) return uni.showToast({ title: '密码至少 8 位', icon: 'none' })
  if (mode.value === 'register' && !form.display_name) return uni.showToast({ title: '请填写你的称呼', icon: 'none' })
  loading.value = true
  try { await store.authenticate(mode.value, { ...form }); await continueToApp() } catch (error) { message(error) } finally { loading.value = false }
}
async function wechat() {
  wechatLoading.value = true
  try { await store.wechatLogin(); await continueToApp() } catch (error) { message(error) } finally { wechatLoading.value = false }
}
function fillDev() {
  form.email = import.meta.env.VITE_DEV_EMAIL || 'demo@example.com'
  form.password = import.meta.env.VITE_DEV_PASSWORD || 'demo-password'
  mode.value = 'login'
  uni.showToast({ title: '已填入开发账号，请点击登录', icon: 'none' })
}
</script>

<style scoped>
.auth-page { min-height: 100vh; box-sizing: border-box; padding: calc(28px + env(safe-area-inset-top)) 22px calc(28px + env(safe-area-inset-bottom)); background: #F8F2E8; color: #2F2925; position: relative; overflow: hidden; }
.auth-decoration { position: absolute; border-radius: 50%; opacity: .55; filter: blur(2px); }.deco-one{width:260px;height:260px;background:#E9C8B9;right:-100px;top:-70px}.deco-two{width:190px;height:190px;background:#D8E0CF;left:-80px;bottom:20px}
.auth-layout { width: 100%; max-width: 980px; margin: 0 auto; position: relative; z-index: 1; }
.brand-panel { padding: 24px 4px 32px; display:flex;flex-direction:column;align-items:flex-start; }
.brand-mark { width: 48px; height: 48px; position:relative; margin-bottom:20px; }.heart-left,.heart-right{position:absolute;width:30px;height:38px;border:3px solid #E86F51;border-radius:22px 22px 14px 14px;transform:rotate(-38deg);left:5px;top:4px}.heart-right{transform:rotate(38deg);left:14px;border-color:#7F9B78}
.eyebrow { color:#9B5D47; font-size:11px; font-weight:700; letter-spacing:3px; }.brand-title{font-family:Georgia,'Songti SC',serif;font-size:34px;line-height:1.3;font-weight:700;margin-top:12px}.brand-copy{font-size:14px;line-height:1.7;color:#736960;margin-top:14px;max-width:420px}.brand-points{display:flex;gap:10px;margin-top:22px;flex-wrap:wrap}.brand-points text{font-size:12px;padding:7px 12px;border:1px solid rgba(47,41,37,.12);border-radius:20px;background:rgba(255,255,255,.45)}
.auth-card { padding: 24px; background:rgba(255,252,247,.94); }
.segmented { display:grid;grid-template-columns:1fr 1fr;background:#EFE7DD;border-radius:12px;padding:4px;margin-bottom:25px}.segmented button{height:38px;line-height:38px;background:transparent;color:#81776E;font-size:14px;padding:0}.segmented button::after{border:0}.segmented button.active{background:#FFFCF7;color:#2F2925;border-radius:9px;box-shadow:0 2px 8px rgba(56,44,43,.08);font-weight:700}
.form-title{display:block;font-size:23px;font-weight:750}.form-copy{display:block;font-size:13px;color:#81776E;margin-top:7px;margin-bottom:22px}.field{margin-top:15px}.field text{display:block;font-size:12px;font-weight:650;margin:0 0 8px 3px}.field input{height:48px;border:1px solid #DDD3C8;border-radius:13px;padding:0 14px;background:#FFFDFC;font-size:14px;box-sizing:border-box}.field input:focus{border-color:#E86F51}
.primary-button,.wechat-button{height:49px;line-height:49px;border-radius:14px;font-size:15px;font-weight:700;margin-top:22px}.primary-button{background:#E86F51;color:#fff;box-shadow:0 10px 24px rgba(232,111,81,.22)}.primary-button::after,.wechat-button::after,.dev-button::after{border:0}.wechat-button{margin-top:0;background:#7F9B78;color:white}.divider{display:flex;align-items:center;gap:12px;margin:18px 0;color:#A79C92;font-size:11px}.divider view{height:1px;background:#E6DED5;flex:1}.dev-button{background:transparent;color:#9B5D47;font-size:12px;margin-top:11px}.agreement{display:block;text-align:center;color:#A0978F;font-size:10px;line-height:1.6;margin-top:16px}
@media (min-width: 820px) { .auth-page{display:flex;align-items:center}.auth-layout{display:grid;grid-template-columns:1.05fr .8fr;align-items:center;gap:70px}.brand-title{font-size:48px}.auth-card{padding:34px}.brand-panel{padding:0} }
</style>
