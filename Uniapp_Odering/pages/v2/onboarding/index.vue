<template>
  <view class="onboarding-page safe-page">
    <view class="onboarding-shell">
      <view class="intro">
        <text class="step">第一步 · 建立二人空间</text>
        <text class="title">把餐桌留给重要的人</text>
        <text class="copy">创建后会自动准备一套默认主题和家常菜单，所有内容之后都能改成你们喜欢的样子。</text>
      </view>
      <view class="choice-grid">
        <button class="choice-card" :class="{ selected: mode === 'create' }" @click="mode='create'">
          <view class="choice-icon create-icon"><view/></view><text class="choice-title">创建新空间</text><text class="choice-copy">由你命名，再邀请另一半加入</text>
        </button>
        <button class="choice-card" :class="{ selected: mode === 'join' }" @click="mode='join'">
          <view class="choice-icon join-icon"><view/></view><text class="choice-title">加入已有空间</text><text class="choice-copy">输入另一半分享的邀请码</text>
        </button>
      </view>

      <view class="setup-card v2-card">
        <template v-if="mode === 'create'">
          <text class="setup-title">先给你们的空间起个名字</text>
          <view class="field"><text>空间名称</text><input v-model.trim="spaceName" maxlength="24" placeholder="例如：小满和阿青的餐桌" /></view>
          <view class="preview-row"><view class="preview-swatch coral"/><view><text class="preview-title">暖暖餐桌</text><text class="preview-copy">默认主题 · 创建后可随时切换</text></view></view>
          <button class="primary-button" :loading="loading" @click="create">创建我们的餐桌</button>
        </template>
        <template v-else>
          <text class="setup-title">输入 6–12 位邀请码</text>
          <view class="field"><text>邀请码</text><input v-model.trim="inviteCode" maxlength="12" placeholder="例如：TABLE26" class="code-input" /></view>
          <button class="primary-button" :loading="loading" @click="join">加入空间</button>
        </template>
        <button class="logout-button" @click="logout">换一个账号</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import store from '../../../store'

const mode = ref('create'), loading = ref(false), spaceName = ref('我们的餐桌'), inviteCode = ref('')
function fail(error) { uni.showToast({ title: error.message || '操作失败', icon: 'none', duration: 2600 }) }
async function create() {
  if (!spaceName.value) return uni.showToast({ title: '请为空間起个名字', icon: 'none' })
  loading.value = true
  try {
    await store.createSpace({ name: spaceName.value, default_theme_key: 'warm-table', seed_default_menus: true })
    uni.reLaunch({ url: '/pages/v2/home/index' })
  } catch (error) { fail(error) } finally { loading.value = false }
}
async function join() {
  if (inviteCode.value.length < 6) return uni.showToast({ title: '请检查邀请码', icon: 'none' })
  loading.value = true
  try { await store.joinSpace(inviteCode.value.toUpperCase()); uni.reLaunch({ url: '/pages/v2/home/index' }) } catch (error) { fail(error) } finally { loading.value = false }
}
async function logout() { await store.logout(); uni.reLaunch({ url: '/pages/v2/auth/index' }) }
</script>

<style scoped>
.onboarding-page{min-height:100vh;background:#F8F2E8;color:#2F2925;padding:calc(30px + env(safe-area-inset-top)) 20px calc(30px + env(safe-area-inset-bottom));box-sizing:border-box}.onboarding-shell{max-width:850px;margin:0 auto}.intro{text-align:center;max-width:580px;margin:0 auto 27px}.step{display:block;color:#E86F51;font-size:12px;font-weight:700;letter-spacing:1px}.title{display:block;font-family:Georgia,'Songti SC',serif;font-size:31px;font-weight:700;margin-top:11px}.copy{display:block;color:#81776E;font-size:14px;line-height:1.7;margin-top:12px}
.choice-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}.choice-card{background:rgba(255,252,247,.72);border:1px solid #E2D8CD;border-radius:18px;padding:20px 12px;color:#2F2925;display:flex;flex-direction:column;align-items:center}.choice-card::after{border:0}.choice-card.selected{border:2px solid #E86F51;background:#FFFCF7;box-shadow:0 8px 25px rgba(83,61,46,.08)}.choice-icon{width:38px;height:38px;border:2px solid #7F9B78;border-radius:50%;margin-bottom:11px;position:relative}.create-icon:before,.create-icon:after{content:'';position:absolute;background:#7F9B78;left:10px;right:10px;height:2px;top:16px}.create-icon:after{transform:rotate(90deg)}.join-icon view{position:absolute;width:15px;height:2px;background:#7F9B78;left:8px;top:16px}.join-icon view:after{content:'';position:absolute;width:7px;height:7px;border-top:2px solid #7F9B78;border-right:2px solid #7F9B78;transform:rotate(45deg);right:-1px;top:-4px}.choice-title{font-size:15px;font-weight:700}.choice-copy{font-size:11px;color:#81776E;margin-top:5px;line-height:1.5}.setup-card{background:#FFFCF7;padding:25px}.setup-title{display:block;font-size:19px;font-weight:700}.field{margin-top:18px}.field text{display:block;font-size:12px;font-weight:650;margin:0 0 8px 3px}.field input{height:49px;border:1px solid #DDD3C8;border-radius:13px;padding:0 14px;background:#FFF;font-size:14px;box-sizing:border-box}.code-input{letter-spacing:4px;text-transform:uppercase}.preview-row{display:flex;align-items:center;gap:12px;margin-top:16px;padding:13px;background:#F8F2E8;border-radius:12px}.preview-swatch{width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#E86F51 50%,#7F9B78 50%)}.preview-title,.preview-copy{display:block}.preview-title{font-size:13px;font-weight:700}.preview-copy{font-size:11px;color:#81776E;margin-top:3px}.primary-button{height:49px;line-height:49px;border-radius:14px;background:#E86F51;color:#fff;font-size:15px;font-weight:700;margin-top:21px}.primary-button::after,.logout-button::after{border:0}.logout-button{background:transparent;color:#81776E;font-size:12px;margin-top:7px}
@media(min-width:760px){.choice-grid{gap:18px}.setup-card{max-width:560px;margin:0 auto;padding:32px}.choice-card{padding:25px}}
</style>
