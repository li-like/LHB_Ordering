import { normalizeAppearance } from '../../design/themes'

const list = (value) => Array.isArray(value) ? value : (value && (value.results || value.items)) || []
const image = (value) => value && (value.image_url || value.dish_image_url || value.cover_image_url || value.image || '')

export function mapUser(value = {}) {
  return { id: value.id, username: value.username || '', email: value.email || '', display_name: value.display_name || value.nickname || value.username || '我', avatar_url: value.avatar_url || value.avatar || '', avatar_frame: value.avatar_frame || 'none' }
}

export function mapMember(value = {}) {
  return { ...value, user: mapUser(value.account || value.user || value), display_name: value.display_name || value.nickname || (value.account && value.account.nickname) || '成员', avatar_url: value.avatar_url || (value.account && value.account.avatar_url) || '', avatar_frame: value.avatar_frame || 'none' }
}

export function mapSpace(value = {}) {
  return { ...value, id: value.id, name: value.name || value.title || '我们的餐桌', role: value.role || value.current_user_role || 'member' }
}

export function mapDish(value = {}, sectionId) {
  const section = typeof sectionId === 'object' ? sectionId : { id: sectionId }
  return { ...value, id: value.dish || value.id, section_id: value.section_id || section.id, section_name: value.section_name || section.name || '', section_accent: value.section_accent || section.accent_color || '', name: value.name || value.dish_name || value.title || value.custom_name || '未命名菜品', description: value.description || value.note || '', image_url: image(value), selected: Boolean(value.selected || value.is_selected) }
}

export function mapMenu(value = {}) {
  const sections = list(value.sections).map(section => ({ ...section, dishes: list(section.dishes).map(dish => mapDish(dish, section)) }))
  return { ...value, id: value.id, name: value.name || value.title || '私房菜单', cover_image_url: value.cover_url || image(value), display_style: value.image_style || value.display_style || 'grid', sections, dishes: sections.length ? sections.flatMap(section => section.dishes) : list(value.dishes || value.items).map(mapDish), primary_section_id: sections[0] && sections[0].id }
}

export function mapMealSession(value = {}) {
  return { ...value, id: value.id, title: value.title || value.name || '今天吃什么', status: value.status || 'draft', meal_type: value.meal_type || 'dinner', choices: list(value.choices).map(mapDish), plan_items: list(value.plan_items || value.items).map(mapDish) }
}

export function mapRecord(value = {}) {
  return { ...value, id: value.id, title: value.title || value.name || '一次好好吃饭', completed_at: value.completed_at || value.date || '', images: value.photo_url ? [value.photo_url] : list(value.images), items: list(value.items || value.plan_items).map(mapDish) }
}

export const unwrapList = list
export function mapAppearance(value = {}) {
  const backgroundType = value.background_type || (value.background_image_url ? 'image' : 'preset')
  const backgroundValue = value.background_value || value.background_image_url || ''
  return normalizeAppearance({ theme_key: value.preset_slug || value.theme_key, custom_colors: value.palette_overrides || value.custom_colors, background_type: backgroundType, background_value: backgroundValue, background_image_url: backgroundType === 'image' ? backgroundValue : '', card_radius: value.corner_radius ?? value.card_radius, card_style: value.card_style, menu_image_style: value.menu_image_style, home_title: value.home_title, navigation_labels: value.navigation_labels })
}

export function serializeAppearance(value = {}) {
  const backgroundType = value.background_type || (value.background_image_url ? 'image' : 'preset')
  const backgroundValue = backgroundType === 'image' ? (value.background_value || value.background_image_url || '') : (value.background_value || '')
  return { preset_slug: value.theme_key, palette_overrides: value.custom_colors || {}, background_type: backgroundType, background_value: backgroundValue, card_style: value.card_style, corner_radius: value.card_radius, menu_image_style: value.menu_image_style, home_title: value.home_title, navigation_labels: value.navigation_labels }
}
