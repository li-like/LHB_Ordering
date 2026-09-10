<template>
  <view class="nav-wrap safe-bottom">
    <view class="nav-inner">
      <button v-for="item in items" :key="item.key" class="nav-item" :class="{ active: active === item.key }" @click="$emit('change', item.key)">
        <view class="nav-icon" :class="`icon-${item.key}`"><view class="icon-detail" /></view>
        <text>{{ labels[item.key] || item.fallback }}</text>
      </button>
    </view>
  </view>
</template>

<script setup>
defineProps({ active: String, labels: { type: Object, default: () => ({}) } })
defineEmits(['change'])
const items = [
  { key: 'today', fallback: '今天' }, { key: 'menu', fallback: '菜单' },
  { key: 'records', fallback: '记录' }, { key: 'us', fallback: '我们' }
]
</script>

<style scoped>
.nav-wrap { position: fixed; z-index: 30; left: 0; right: 0; bottom: 0; background: color-mix(in srgb, var(--color-surface) 94%, transparent); border-top: 1px solid color-mix(in srgb, var(--color-muted) 15%, transparent); backdrop-filter: blur(16px); }
.nav-inner { max-width: 920px; margin: 0 auto; height: 62px; display: grid; grid-template-columns: repeat(4, 1fr); }
.nav-item { min-width: 0; padding: 7px 4px 5px; margin: 0; background: transparent; border-radius: 0; line-height: 1; display: flex; flex-direction: column; gap: 5px; align-items: center; justify-content: center; color: var(--color-muted); font-size: 11px; }
.nav-item::after { border: none; }.nav-item.active { color: var(--color-primary); font-weight: 700; }
.nav-icon { width: 19px; height: 19px; box-sizing: border-box; position: relative; color: currentColor; }
.icon-today { border: 2px solid currentColor; border-radius: 50%; }.icon-today .icon-detail { width: 7px; height: 2px; background: currentColor; position:absolute; left:4px; top:7px; }
.icon-menu { border: 2px solid currentColor; border-radius: 3px; }.icon-menu::before,.icon-menu::after,.icon-menu .icon-detail { content:''; position:absolute; left:3px; right:3px; height:2px; background:currentColor; }.icon-menu::before{top:3px}.icon-menu .icon-detail{top:7px}.icon-menu::after{top:11px}
.icon-records { border-left: 2px solid currentColor; border-bottom: 2px solid currentColor; }.icon-records::before,.icon-records::after{content:'';position:absolute;width:8px;height:2px;background:currentColor;left:5px}.icon-records::before{top:5px}.icon-records::after{top:10px}
.icon-us::before,.icon-us::after { content:''; position:absolute; width:9px; height:9px; border:2px solid currentColor; border-radius:50%; box-sizing:border-box; top:1px; }.icon-us::before{left:1px}.icon-us::after{right:1px}.icon-us .icon-detail{position:absolute;left:1px;right:1px;bottom:0;height:7px;border:2px solid currentColor;border-bottom:0;border-radius:10px 10px 0 0}
</style>
