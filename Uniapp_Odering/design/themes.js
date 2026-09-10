export const THEME_PRESETS = [
  {
    key: 'warm-table', name: '暖心餐桌', description: '米白、珊瑚橙与鼠尾草绿。',
    colors: { primary: '#E98D74', secondary: '#88A47C', accent: '#E8B65A', background: '#FFF8EF', surface: '#FFFFFF', text: '#3E332D', muted: '#8A7D75' }, background_type: 'color', background_value: '#FFF8EF'
  },
  {
    key: 'berry-date', name: '莓果约会', description: '克制的莓红与奶油粉。',
    colors: { primary: '#B8576B', secondary: '#D9909E', accent: '#F0B86E', background: '#FFF5F6', surface: '#FFFFFF', text: '#432E33', muted: '#92777D' }, background_type: 'gradient', background_value: 'berry'
  },
  {
    key: 'sage-kitchen', name: '鼠尾草厨房', description: '自然、平静的清新绿色。',
    colors: { primary: '#6E8B74', secondary: '#A9B8A5', accent: '#D8A85D', background: '#F4F7F1', surface: '#FFFFFF', text: '#2F3B31', muted: '#758078' }, background_type: 'gradient', background_value: 'sage'
  },
  {
    key: 'night-bistro', name: '夜色小馆', description: '适合晚餐记录的深色主题。',
    colors: { primary: '#E39A6D', secondary: '#78909C', accent: '#E4C06A', background: '#202326', surface: '#303438', text: '#F7F2EA', muted: '#B8B0A6' }, background_type: 'color', background_value: '#202326'
  }
]

export const DEFAULT_APPEARANCE = {
  theme_key: 'warm-table', background_type: 'preset', background_value: '', background_image_url: '', custom_colors: {}, card_radius: 20, card_style: 'soft', menu_image_style: 'rounded', home_title: '今天吃什么',
  navigation_labels: { today: '今天', menu: '菜单', records: '记录', us: '我们' }
}

export const CARD_STYLES = [
  { key: 'preset', name: '跟随主题' }, { key: 'soft', name: '柔和阴影' }, { key: 'solid', name: '清爽实色' }, { key: 'glass', name: '半透明' }
]

export function normalizeAppearance(value = {}) {
  return { ...DEFAULT_APPEARANCE, ...value,
    custom_colors: { ...(value.custom_colors || value.colors || {}) },
    navigation_labels: { ...DEFAULT_APPEARANCE.navigation_labels, ...(value.navigation_labels || value.nav_labels || {}) }
  }
}

export function getTheme(key) {
  return THEME_PRESETS.find((theme) => theme.key === key) || THEME_PRESETS[0]
}

export function buildTokens(appearance = DEFAULT_APPEARANCE) {
  const normalized = normalizeAppearance(appearance)
  const preset = getTheme(normalized.theme_key)
  const colors = { ...preset.colors, ...normalized.custom_colors }
  const type = normalized.background_type === 'preset' ? preset.background_type : normalized.background_type
  const value = normalized.background_type === 'preset' ? preset.background_value : normalized.background_value
  const gradients = {
    berry: 'linear-gradient(145deg, #FFF5F6 0%, #F7DDE3 48%, #F5E8DA 100%)',
    sage: 'linear-gradient(145deg, #F4F7F1 0%, #DDE8D9 52%, #F6EEE1 100%)',
    sunset: 'linear-gradient(145deg, #FFF4E8, #F4C5B8)', ocean: 'linear-gradient(145deg, #EAF5F5, #C9DDE4)', cream: 'linear-gradient(145deg, #FFF9EF, #F1E6D4)'
  }
  let backgroundImage = 'none'
  if (type === 'image' && value) backgroundImage = `url(${value})`
  else if (type === 'gradient' && gradients[value]) backgroundImage = gradients[value]
  return {
    '--color-primary': colors.primary, '--color-secondary': colors.secondary, '--color-accent': colors.accent,
    '--color-bg': colors.background, '--color-surface': colors.surface, '--color-text': colors.text, '--color-muted': colors.muted,
    '--card-radius': `${Math.min(32, Math.max(8, Number(normalized.card_radius) || 20))}px`,
    '--page-background-image': backgroundImage
  }
}
