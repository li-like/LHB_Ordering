import { request, tokenStore, uploadImage } from './client'
import { mapAppearance, mapMealSession, mapMember, mapMenu, mapRecord, mapSpace, mapUser, serializeAppearance, unwrapList } from './mappers'

const enc = encodeURIComponent
const api = {
  register: ({ display_name, ...data }) => request('auth/register', { method: 'POST', data: { ...data, nickname: display_name } }),
  login: (data) => request('auth/login', { method: 'POST', data }), wechatLogin: (data) => request('auth/wechat', { method: 'POST', data }), logout: () => request('auth/logout', { method: 'POST' }), me: async () => mapUser(await request('auth/me')),
  spaces: async () => unwrapList(await request('spaces')).map(mapSpace), createSpace: async (data) => mapSpace(await request('spaces', { method: 'POST', data: { name: data.name } })), joinSpace: async (code) => mapSpace(await request('spaces/join', { method: 'POST', data: { code } })),
  updateSpace: async (id, data) => mapSpace(await request(`spaces/${enc(id)}`, { method: 'PATCH', data })), members: async (id) => unwrapList(await request(`spaces/${enc(id)}/members`)).map(mapMember), updateMe: async (id, data) => mapMember(await request(`spaces/${enc(id)}/members/me`, { method: 'PATCH', data })), createInvite: (id) => request(`spaces/${enc(id)}/invites`, { method: 'POST' }),
  appearance: async (id) => mapAppearance(await request(`spaces/${enc(id)}/appearance`)), updateAppearance: async (id, data) => mapAppearance(await request(`spaces/${enc(id)}/appearance`, { method: 'PATCH', data: serializeAppearance(data) })), themes: () => request('themes'),
  menus: async (id) => unwrapList(await request(`spaces/${enc(id)}/menus`)).map(mapMenu),
  createMenu: async (id, data) => mapMenu(await request(`spaces/${enc(id)}/menus`, { method: 'POST', data })),
  updateMenu: async (_spaceId, menuId, data) => mapMenu(await request(`menus/${enc(menuId)}`, { method: 'PATCH', data: { name: data.name, description: data.description || '', cover_url: data.cover_image_url, image_style: data.display_style } })),
  updateSection: (sectionId, data) => request(`sections/${enc(sectionId)}`, { method: 'PATCH', data: { name: data.name, accent_color: data.accent_color || '' } }),
  createDish: (_spaceId, sectionId, data) => request(`sections/${enc(sectionId)}/dishes`, { method: 'POST', data }),
  updateDish: (dishId, data) => request(`dishes/${enc(dishId)}`, { method: 'PATCH', data }),
  mealSessions: async (id, query) => unwrapList(await request(`spaces/${enc(id)}/meal-sessions`, { query })).map(mapMealSession), createMealSession: async (id, data) => mapMealSession(await request(`spaces/${enc(id)}/meal-sessions`, { method: 'POST', data })), choose: (id, data) => request(`meal-sessions/${enc(id)}/choices`, { method: 'POST', data }), confirm: (id, data = {}) => request(`meal-sessions/${enc(id)}/confirm`, { method: 'POST', data }), start: (id) => request(`meal-sessions/${enc(id)}/start`, { method: 'POST' }), complete: (id, data = {}) => request(`meal-sessions/${enc(id)}/complete`, { method: 'POST', data }), records: async (id, query) => unwrapList(await request(`spaces/${enc(id)}/records`, { query })).map(mapRecord),
  preferences: (id) => request(`spaces/${enc(id)}/preferences/me`), updatePreferences: (id, data) => request(`spaces/${enc(id)}/preferences/me`, { method: 'PATCH', data }), uploadAsset: (spaceId, filePath, purpose = 'dish') => uploadImage('media-assets', filePath, { space_id: spaceId, purpose })
}

export { tokenStore }
export default api
