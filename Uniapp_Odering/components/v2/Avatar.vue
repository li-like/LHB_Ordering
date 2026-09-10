<template>
  <view class="avatar-wrap" :class="`frame-${frame}`" :style="sizeStyle">
    <view class="frame-decoration" />
    <view class="avatar">
      <image v-if="src" class="avatar-image" :src="src" mode="aspectFill" />
      <text v-else class="avatar-letter">{{ letter }}</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ src: { type: String, default: '' }, name: { type: String, default: '' }, frame: { type: String, default: 'none' }, size: { type: Number, default: 48 } })
const letter = computed(() => (props.name || '你').trim().slice(0, 1))
const sizeStyle = computed(() => ({ width: `${props.size}px`, height: `${props.size}px` }))
</script>

<style scoped>
.avatar-wrap { flex: 0 0 auto; position: relative; box-sizing: border-box; }
.avatar { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; border-radius: 50%; overflow: hidden; background: #F4E5DD; color: var(--color-primary); font-weight: 700; position: relative; z-index: 2; box-sizing: border-box; }
.avatar-image { width: 100%; height: 100%; border-radius: 50%; }
.avatar-letter { font-size: 18px; }
.frame-ring .avatar { border: 3px solid var(--color-surface); box-shadow: 0 0 0 2px var(--color-secondary); }
.frame-heart .avatar { border: 3px solid var(--color-primary); }
.frame-heart::before,.frame-heart::after { content: ''; position: absolute; z-index: 3; width: 8px; height: 12px; top: -4px; background: var(--color-primary); border-radius: 8px 8px 3px 3px; transform: rotate(-45deg); left: 50%; margin-left: -7px; }
.frame-heart::after { transform: rotate(45deg); margin-left: -2px; }
.frame-floral .avatar { border: 2px solid var(--color-accent); }
.frame-floral .frame-decoration,.frame-floral .frame-decoration::before,.frame-floral .frame-decoration::after { position:absolute;z-index:3;width:8px;height:8px;border-radius:50%;background:var(--color-accent);content:''; }
.frame-floral .frame-decoration { left:-2px;top:5px;box-shadow:4px -5px 0 var(--color-primary),7px 2px 0 var(--color-secondary),2px 6px 0 var(--color-accent); }
.frame-floral .frame-decoration::before { right:-44px;bottom:-34px;box-shadow:-4px 5px 0 var(--color-primary),-7px -2px 0 var(--color-secondary),-2px -6px 0 var(--color-accent); }
.frame-pixel .avatar { border-radius: 7px; border: 3px solid var(--color-text); box-shadow: 4px 4px 0 var(--color-accent); }
.frame-pixel .avatar-image { border-radius: 3px; }
</style>
