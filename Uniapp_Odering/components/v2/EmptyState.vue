<template>
  <view class="empty-state">
    <view class="empty-mark"><view class="plate-line" /></view>
    <text class="empty-title">{{ title }}</text>
    <text class="empty-copy">{{ copy }}</text>
    <button v-if="action" class="text-button" @click="$emit('action')">{{ action }}</button>
  </view>
</template>

<script setup>
defineProps({ title: String, copy: String, action: String })
defineEmits(['action'])
</script>

<style scoped>
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 42px 20px; text-align: center; }
.empty-mark { width: 52px; height: 52px; border: 2px solid var(--color-secondary); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 14px; opacity: .8; }
.plate-line { width: 28px; height: 2px; border-radius: 2px; background: var(--color-secondary); }
.empty-title { color: var(--color-text); font-size: 17px; font-weight: 700; }
.empty-copy { color: var(--color-muted); font-size: 13px; line-height: 1.6; margin-top: 6px; }
.text-button { background: transparent; color: var(--color-primary); font-size: 14px; padding: 8px 16px; margin-top: 8px; }
.text-button::after { border: 0; }
</style>
