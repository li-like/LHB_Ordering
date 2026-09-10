<template>
  <view class="app-page" :class="[`cards-${appearance.card_style}`]" :style="tokenStyle">
    <view class="background-layer" />
    <view v-if="loading" class="loading-screen"><view class="loader"/><text>正在摆好餐桌…</text></view>
    <template v-else>
      <view class="topbar safe-top">
        <view class="topbar-inner">
          <view><text class="eyebrow">OUR TABLE</text><text class="space-name">{{ space.name }}</text></view>
          <view class="top-actions">
            <view class="couple-stack">
              <Avatar v-for="member in members.slice(0,2)" :key="member.id" :src="member.avatar_url" :name="member.display_name" :frame="member.avatar_frame" :size="34" />
            </view>
            <button class="round-button" aria-label="个性化设置" @click="customize"><view class="settings-icon"><view/></view></button>
          </view>
        </view>
      </view>

      <scroll-view scroll-y class="content-scroll">
        <view class="content-shell">
          <TodayPanel v-if="activeTab === 'today'" :session="activeSession" :menus="menus" :members="members" :home-title="appearance.home_title" @choose="chooseDish" @create-session="createSession" @confirm="confirmSession" @start="startSession" @complete="completeSession" />
          <MenuPanel v-else-if="activeTab === 'menu'" :menus="menus" :default-image-style="appearance.menu_image_style" @add="editDish" @edit-dish="editExistingDish" @refresh="refreshMenus" />
          <RecordsPanel v-else-if="activeTab === 'records'" :records="records" @refresh="refreshRecords" />
          <UsPanel v-else :space="space" :members="members" :user="appState.user" @invite="invite" @customize="customize" @logout="logout" />
        </view>
      </scroll-view>
      <BottomNav :active="activeTab" :labels="appearance.navigation_labels" @change="switchTab" />
      <MealMemoryDialog :open="memoryOpen" :space-id="space.id" :submitting="completing" @close="memoryOpen=false" @submit="finishSession" />
    </template>
  </view>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Avatar from '../../../components/v2/Avatar.vue'
import BottomNav from '../../../components/v2/BottomNav.vue'
import TodayPanel from '../../../components/v2/TodayPanel.vue'
import MenuPanel from '../../../components/v2/MenuPanel.vue'
import RecordsPanel from '../../../components/v2/RecordsPanel.vue'
import UsPanel from '../../../components/v2/UsPanel.vue'
import MealMemoryDialog from '../../../components/v2/MealMemoryDialog.vue'
import api from '../../../services/api'
import store, { state as appState } from '../../../store'

const loading = ref(true)
const memoryOpen = ref(false), completing = ref(false)
const activeTab = computed(() => appState.active_tab)
const appearance = computed(() => appState.appearance)
const tokenStyle = computed(() => store.tokenStyle)
const space = computed(() => appState.current_space || { name: '我们的餐桌' })
const members = computed(() => appState.members || [])
const menus = computed(() => appState.menus || [])
const records = computed(() => appState.records || [])
const activeSession = computed(() => appState.meal_sessions[0] || null)

function toast(error) { uni.showToast({ title: error.message || '操作没有完成，请重试', icon: 'none', duration: 2600 }) }
function tonightSession() {
  return { meal_type: 'dinner', title: '今晚一起吃', scheduled_for: new Date().toISOString() }
}
async function init() {
  try {
    const result = await store.bootstrap()
    if (result.route !== 'home') return uni.reLaunch({ url: result.route === 'auth' ? '/pages/v2/auth/index' : '/pages/v2/onboarding/index' })
  } catch (error) { toast(error) } finally { loading.value = false }
}
async function switchTab(tab) {
  store.setTab(tab)
  if (tab === 'records' && !appState.records.length) await refreshRecords()
}
async function createSession() {
  try { await api.createMealSession(space.value.id, tonightSession()); await store.refreshToday() } catch (error) { toast(error) }
}
async function chooseDish(dish) {
  try {
    let session = activeSession.value
    if (!session) session = await api.createMealSession(space.value.id, tonightSession())
    await api.choose(session.id, { dish: dish.id })
    await store.refreshToday()
  } catch (error) { toast(error) }
}
async function confirmSession() {
  if (!activeSession.value) return
  try { await api.confirm(activeSession.value.id); await store.refreshToday() } catch (error) { toast(error) }
}
async function startSession() { try { await api.start(activeSession.value.id); await store.refreshToday() } catch (error) { toast(error) } }
function completeSession() { memoryOpen.value = true }
async function finishSession(memory) { completing.value=true;try { await api.complete(activeSession.value.id, memory);memoryOpen.value=false;await store.refreshToday();await store.refreshRecords();uni.showToast({title:'这顿饭已收藏',icon:'success'}) } catch (error) { toast(error) } finally { completing.value=false } }
async function refreshMenus() { try { await store.refreshMenus() } catch (error) { toast(error) } }
async function refreshRecords() { try { await store.refreshRecords() } catch (error) { toast(error) } }
function editDish(menu) {
  if (!menu.primary_section_id) return uni.showToast({ title: '请先为菜单创建栏目', icon: 'none' })
  uni.navigateTo({ url: `/pages/v2/dish/edit?section_id=${menu.primary_section_id}` })
}
function editExistingDish(dish) { uni.navigateTo({ url: `/pages/v2/dish/edit?section_id=${dish.section_id}&dish_id=${dish.id}` }) }
function customize() { uni.navigateTo({ url: '/pages/v2/customize/index' }) }
async function invite() {
  try {
    const result = await api.createInvite(space.value.id)
    const code = result.invite_code || result.code
    if (!code) throw new Error('服务端未返回邀请码')
    uni.setClipboardData({ data: code, success: () => uni.showToast({ title: '邀请码已复制', icon: 'success' }) })
  } catch (error) { toast(error) }
}
async function logout() { try { await store.logout(); uni.reLaunch({ url: '/pages/v2/auth/index' }) } catch (error) { toast(error) } }
onMounted(init)
</script>

<style scoped>
.app-page{height:100vh;background:var(--color-bg);color:var(--color-text);position:relative;overflow:hidden}.background-layer{position:absolute;inset:0;background-image:var(--page-background-image);background-size:cover;background-position:center;opacity:.72}.topbar{position:relative;z-index:5;background:rgba(255,252,247,.83);border-bottom:1px solid rgba(47,41,37,.07);backdrop-filter:blur(14px)}.topbar-inner{height:67px;max-width:920px;margin:0 auto;padding:0 18px;display:flex;align-items:center;justify-content:space-between;box-sizing:border-box}.eyebrow{display:block;font-size:9px;letter-spacing:2px;color:var(--color-primary);font-weight:800}.space-name{display:block;font-family:Georgia,'Songti SC',serif;font-size:20px;font-weight:700;margin-top:3px}.top-actions{display:flex;align-items:center;gap:10px}.couple-stack{display:flex}.couple-stack :deep(.avatar-wrap)+:deep(.avatar-wrap){margin-left:-8px}.round-button{width:36px;height:36px;padding:0;border-radius:50%;background:var(--color-surface);display:flex;align-items:center;justify-content:center}.round-button::after{border:1px solid rgba(47,41,37,.1)}.settings-icon{width:17px;height:17px;border:2px solid var(--color-muted);border-radius:50%;box-sizing:border-box;position:relative}.settings-icon view{position:absolute;width:5px;height:5px;border:2px solid var(--color-muted);border-radius:50%;left:4px;top:4px;box-sizing:border-box}.settings-icon:before,.settings-icon:after{content:'';position:absolute;background:var(--color-muted);width:3px;height:21px;left:5px;top:-4px;transform:rotate(45deg)}.settings-icon:after{transform:rotate(-45deg)}
.content-scroll{position:relative;z-index:2;height:calc(100vh - 67px - env(safe-area-inset-top));box-sizing:border-box}.content-shell{max-width:920px;margin:0 auto;padding:22px 16px calc(92px + env(safe-area-inset-bottom));box-sizing:border-box}.loading-screen{height:100%;position:relative;z-index:3;display:flex;flex-direction:column;gap:13px;align-items:center;justify-content:center;color:var(--color-muted);font-size:13px}.loader{width:30px;height:30px;border:3px solid rgba(127,155,120,.22);border-top-color:#7F9B78;border-radius:50%;animation:spin .8s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
.topbar{background:var(--color-surface);color:var(--color-text);border-bottom-color:var(--color-muted)}.round-button::after{border-color:var(--color-muted)}
@media(min-width:760px){.content-shell{padding:30px 22px 105px}.topbar-inner{padding:0 22px}}
</style>
