import { reactive } from 'vue'
import api, { tokenStore } from '../services/api'
import { DEFAULT_APPEARANCE, buildTokens, normalizeAppearance } from '../design/themes'

const SPACE_KEY = 'ordering_v2_space_id'

export const state = reactive({
  ready: false, busy: false, user: null, spaces: [], current_space: null, members: [],
  appearance: normalizeAppearance(DEFAULT_APPEARANCE), menus: [], meal_sessions: [], records: [], preferences: {},
  active_tab: 'today'
})

function tokenFrom(response = {}) {
  return response.access_token || response.token || response.access || ''
}

function saveSession(response) {
  const token = tokenFrom(response)
  if (!token) throw new Error('服务端未返回登录令牌')
  tokenStore.set(token)
}

export const store = {
  state,
  get tokenStyle() { return buildTokens(state.appearance) },
  get hasToken() { return Boolean(tokenStore.get()) },
  setTab(tab) { state.active_tab = tab },
  async authenticate(kind, form) {
    const response = kind === 'register' ? await api.register(form) : await api.login(form)
    saveSession(response)
    state.user = response.user || await api.me()
    return response
  },
  async wechatLogin(profile = {}) {
    const login = await new Promise((resolve, reject) => uni.login({ provider: 'weixin', success: resolve, fail: reject }))
    const response = await api.wechatLogin({ code: login.code, ...profile })
    saveSession(response)
    state.user = response.user || await api.me()
    return response
  },
  async bootstrap() {
    state.busy = true
    try {
      if (!tokenStore.get()) return { route: 'auth' }
      state.user = await api.me()
      state.spaces = await api.spaces()
      if (!state.spaces.length) return { route: 'onboarding' }
      const savedId = uni.getStorageSync(SPACE_KEY)
      state.current_space = state.spaces.find((item) => String(item.id) === String(savedId)) || state.spaces[0]
      await this.loadSpace()
      return { route: 'home' }
    } finally {
      state.busy = false
      state.ready = true
    }
  },
  async loadSpace() {
    if (!state.current_space) return
    const id = state.current_space.id
    uni.setStorageSync(SPACE_KEY, id)
    const results = await Promise.allSettled([
      api.members(id), api.appearance(id), api.menus(id), api.mealSessions(id, { active: true })
    ])
    if (results[0].status === 'fulfilled') state.members = results[0].value
    if (results[1].status === 'fulfilled') state.appearance = normalizeAppearance(results[1].value)
    if (results[2].status === 'fulfilled') state.menus = results[2].value
    if (results[3].status === 'fulfilled') state.meal_sessions = results[3].value.filter(item => item.status !== 'completed')
  },
  async createSpace(data) {
    const space = await api.createSpace(data)
    state.spaces.push(space)
    state.current_space = space
    await this.loadSpace()
    return space
  },
  async joinSpace(code) {
    const space = await api.joinSpace(code)
    state.spaces.push(space)
    state.current_space = space
    await this.loadSpace()
    return space
  },
  async refreshToday() {
    state.meal_sessions = (await api.mealSessions(state.current_space.id)).filter(item => item.status !== 'completed')
  },
  async refreshMenus() { state.menus = await api.menus(state.current_space.id) },
  async refreshRecords() { state.records = await api.records(state.current_space.id, { page_size: 30 }) },
  async saveAppearance(data) {
    state.appearance = await api.updateAppearance(state.current_space.id, data)
    return state.appearance
  },
  async logout() {
    try { await api.logout() } finally {
      tokenStore.set('')
      uni.removeStorageSync(SPACE_KEY)
      Object.assign(state, { ready: false, user: null, spaces: [], current_space: null, members: [], menus: [], meal_sessions: [], records: [] })
    }
  }
}

uni.$on('auth:expired', () => {
  uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
  setTimeout(() => uni.reLaunch({ url: '/pages/v2/auth/index' }), 300)
})

export default store
