<template>
  <view>
    <view class="page-heading"><view><text class="kicker">OUR COLLECTION</text><text class="title">你们的菜单</text><text class="copy">默认内容只是开始，每个名字、封面和菜品都可以换成你们自己的。</text></view><button class="refresh" @click="$emit('refresh')">刷新</button></view>
    <view v-if="menus.length" class="menu-list">
      <view v-for="menu in menus" :key="menu.id" class="menu-section">
        <view class="menu-cover v2-card" :style="menu.cover_image_url ? {backgroundImage:`linear-gradient(90deg,rgba(35,29,25,.68),rgba(35,29,25,.12)),url(${menu.cover_image_url})`} : {}">
          <view><text class="cover-label">MENU</text><text class="cover-title">{{ menu.name }}</text><text class="cover-meta">{{ menu.dishes.length }} 道菜 · {{ styleName(menu.display_style) }}</text></view>
          <button @click="$emit('add', menu)">添加菜品</button>
        </view>
        <view :class="['menu-dishes', `style-${effectiveStyle(menu)}`]">
          <button v-for="dish in menu.dishes" :key="dish.id" class="menu-dish v2-card" @click="$emit('edit-dish', dish)">
            <image v-if="dish.image_url" :src="dish.image_url" mode="aspectFill"/><view v-else class="fallback" :style="fallbackStyle(dish)"><view class="fallback-plate"><text>{{ dish.name.slice(0,1) }}</text></view><text>{{ dish.section_name || '私房菜' }}</text></view>
            <view><text class="dish-name">{{ dish.name }}</text><text class="dish-desc">{{ dish.description || '你们的私房味道' }}</text></view>
          </button>
        </view>
      </view>
    </view>
    <EmptyState v-else title="还没有菜单" copy="创建空间时默认菜单可能仍在准备，刷新试试；也可以开始添加第一道菜。" action="刷新菜单" @action="$emit('refresh')" />
  </view>
</template>
<script setup>
import EmptyState from './EmptyState.vue'
const props=defineProps({ menus:{type:Array,default:()=>[]},defaultImageStyle:{type:String,default:'rounded'} });defineEmits(['add','refresh','edit-dish'])
const names={inherit:'跟随主题',cover:'满幅',rounded:'圆角',polaroid:'拍立得',circle:'圆形'};const styleName=key=>names[key]||'跟随主题'
const effectiveStyle=menu=>menu.display_style==='inherit'?(props.defaultImageStyle||'rounded'):(menu.display_style||props.defaultImageStyle||'rounded')
const fallbackStyle=dish=>({background:`linear-gradient(145deg, ${dish.section_accent||'#D9B27C'}, var(--color-surface))`})
</script>
<style scoped>
.page-heading{display:flex;justify-content:space-between;align-items:flex-start;margin:7px 3px 22px}.kicker{display:block;color:var(--color-primary);font-size:9px;letter-spacing:2px;font-weight:800}.title{display:block;font-family:Georgia,'Songti SC',serif;font-size:29px;font-weight:700;margin-top:7px}.copy{display:block;color:var(--color-muted);font-size:12px;line-height:1.6;margin-top:7px;max-width:540px}.refresh{margin:0;background:transparent;color:var(--color-primary);font-size:12px;padding:7px}.refresh::after{border:0}.menu-section{margin-bottom:27px}.menu-cover{height:150px;padding:20px;background:linear-gradient(120deg,#9B5D47,#7F9B78);background-size:cover;background-position:center;color:white;display:flex;align-items:flex-end;justify-content:space-between;box-sizing:border-box;overflow:hidden}.cover-label,.cover-title,.cover-meta{display:block;text-shadow:0 1px 5px rgba(0,0,0,.18)}.cover-label{font-size:9px;letter-spacing:2px}.cover-title{font-size:23px;font-family:Georgia,'Songti SC',serif;font-weight:700;margin-top:4px}.cover-meta{font-size:10px;margin-top:5px;opacity:.86}.menu-cover button{margin:0;background:rgba(255,255,255,.9);color:#3A322D;border-radius:11px;height:36px;line-height:36px;font-size:11px;padding:0 13px}.menu-cover button::after,.menu-dish::after{border:0}.menu-dishes{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:11px}.menu-dish{overflow:hidden;background:var(--color-surface);padding:0;margin:0;text-align:left;color:var(--color-text);width:100%}.menu-dish image,.fallback{width:100%;height:108px;display:flex;flex-direction:column;gap:5px;align-items:center;justify-content:center;background:rgba(127,155,120,.12)}.fallback-plate{width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.72);border:2px solid rgba(255,255,255,.9);display:flex;align-items:center;justify-content:center;box-shadow:0 5px 13px rgba(47,41,37,.12)}.fallback-plate text{font-family:Georgia,'Songti SC',serif;font-size:20px;font-weight:700;color:var(--color-text)}.fallback>text{font-size:9px;color:var(--color-text);font-weight:700}.menu-dish>view:last-child{padding:10px 11px 12px}.dish-name,.dish-desc{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.dish-name{font-size:13px;font-weight:700}.dish-desc{font-size:10px;color:var(--color-muted);margin-top:3px}
.style-rounded .menu-dish image,.style-rounded .fallback{width:calc(100% - 14px);margin:7px 7px 0;border-radius:12px;height:96px}.style-polaroid .menu-dish{padding:7px 7px 0;border-radius:5px}.style-polaroid .menu-dish image,.style-polaroid .fallback{height:96px}.style-polaroid .menu-dish:nth-child(odd){transform:rotate(-1deg)}.style-polaroid .menu-dish:nth-child(even){transform:rotate(1deg)}.style-circle .menu-dish{text-align:center;background:transparent;box-shadow:none}.style-circle .menu-dish image,.style-circle .fallback{width:86px;height:86px;border-radius:50%;margin:10px auto 0}.style-circle .menu-dish>view:last-child{padding-top:8px}.style-cover .menu-dish image,.style-cover .fallback{height:122px}
@media(min-width:720px){.menu-cover{height:190px;padding:25px}.menu-dishes{grid-template-columns:repeat(4,1fr)}.menu-dish image,.fallback{height:125px}.style-rounded .menu-dish image,.style-rounded .fallback,.style-polaroid .menu-dish image,.style-polaroid .fallback{height:112px}.style-cover .menu-dish image,.style-cover .fallback{height:140px}}
</style>
