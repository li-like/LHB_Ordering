<template>
  <view class="panel">
    <view class="hero">
      <view class="date-chip">{{ dateLabel }}</view>
      <text class="hero-title">{{ heading }}</text>
      <text class="hero-copy">{{ subheading }}</text>
      <view class="member-line" v-if="members.length">
        <view v-for="member in members.slice(0,2)" :key="member.id" class="member"><Avatar :src="member.avatar_url" :name="member.display_name" :frame="member.avatar_frame" :size="30"/><text>{{ member.display_name }}</text></view>
      </view>
    </view>

    <view v-if="session" class="status-card v2-card">
      <view><text class="section-kicker">本次晚餐</text><text class="section-title">{{ session.title }}</text></view>
      <text class="status-pill">{{ statusText }}</text>
      <view v-if="session.choices.length" class="choice-list">
        <view v-for="dish in session.choices" :key="dish.id" class="choice-row">
          <image v-if="dish.image_url" :src="dish.image_url" mode="aspectFill"/><view v-else class="dish-placeholder"><view/></view>
          <text>{{ dish.name }}</text><view class="choice-dot"/>
        </view>
      </view>
      <text v-else class="quiet">还没有选择，先从下面挑一道想吃的。</text>
      <button v-if="session.status === 'draft' && session.choices.length" class="primary-button" @click="$emit('confirm')">确认今晚菜单</button>
      <button v-else-if="session.status === 'confirmed'" class="primary-button" @click="$emit('start')">开始准备</button>
      <button v-else-if="session.status === 'cooking' || session.status === 'started'" class="primary-button" @click="$emit('complete')">吃好啦，完成本餐</button>
    </view>
    <view v-else class="start-card v2-card">
      <view class="plate"><view/></view><view class="start-copy"><text>还没有发起今晚的选择</text><text>先开一桌，两个人再慢慢决定。</text></view>
      <button class="small-button" @click="$emit('create-session')">开始选菜</button>
    </view>

    <view class="section-head"><view><text class="section-kicker">INSPIRATION</text><text class="section-title">从你们的菜单挑一挑</text></view></view>
    <view v-if="dishes.length" class="dish-grid">
      <button v-for="dish in dishes.slice(0,8)" :key="dish.id" class="dish-card v2-card" @click="$emit('choose', dish)">
        <image v-if="dish.image_url" :src="dish.image_url" mode="aspectFill"/><view v-else class="dish-image-fallback"><view class="plate small"><view/></view></view>
        <view class="dish-info"><text>{{ dish.name }}</text><text>{{ dish.description || '加入今晚候选' }}</text></view><view class="add-mark">+</view>
      </button>
    </view>
    <EmptyState v-else title="菜单还是空的" copy="去菜单页添加第一道属于你们的菜。" />
  </view>
</template>

<script setup>
import { computed } from 'vue'
import Avatar from './Avatar.vue'; import EmptyState from './EmptyState.vue'
const props = defineProps({ session: Object, menus: { type:Array,default:()=>[] }, members:{type:Array,default:()=>[]}, homeTitle:{type:String,default:'今天吃什么'} })
defineEmits(['choose','create-session','confirm','start','complete'])
const dishes = computed(() => props.menus.flatMap(menu => menu.dishes || []))
const statuses={draft:'正在选择',confirmed:'已确认',cooking:'准备中',completed:'已完成'}
const statusText=computed(()=>statuses[props.session?.status]||'进行中')
const heading=computed(()=>props.session?.status==='confirmed'?'菜单定好了':props.homeTitle)
const subheading=computed(()=>props.session?.status==='confirmed'?'接下来就一起准备吧。':'不用猜对方的心思，把想吃的放到同一张桌上。')
const dateLabel=computed(()=>new Intl.DateTimeFormat('zh-CN',{month:'long',day:'numeric',weekday:'short'}).format(new Date()))
</script>

<style scoped>
.hero{padding:10px 3px 24px}.date-chip{display:inline-flex;padding:6px 10px;background:rgba(232,111,81,.11);border-radius:20px;color:var(--color-primary);font-size:11px;font-weight:700}.hero-title{display:block;font-family:Georgia,'Songti SC',serif;font-size:30px;font-weight:700;margin-top:13px}.hero-copy{display:block;color:var(--color-muted);font-size:13px;line-height:1.65;margin-top:8px;max-width:580px}.member-line{display:flex;gap:17px;margin-top:17px}.member{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--color-muted)}
.status-card{padding:19px}.section-kicker{display:block;font-size:9px;letter-spacing:1.8px;color:var(--color-primary);font-weight:800}.section-title{display:block;font-size:19px;font-weight:750;margin-top:5px}.status-pill{position:absolute;right:17px;top:17px;padding:6px 10px;border-radius:20px;background:rgba(127,155,120,.13);color:var(--color-secondary);font-size:11px;font-weight:700}.choice-list{margin-top:14px;border-top:1px solid rgba(47,41,37,.07)}.choice-row{height:52px;display:flex;align-items:center;gap:10px;border-bottom:1px solid rgba(47,41,37,.07);font-size:14px}.choice-row image,.dish-placeholder{width:35px;height:35px;border-radius:9px}.dish-placeholder{background:#F0E6DA;display:flex;align-items:center;justify-content:center}.dish-placeholder view{width:16px;height:2px;background:var(--color-muted)}.choice-row text{flex:1}.choice-dot{width:7px;height:7px;border-radius:50%;background:var(--color-secondary)}.quiet{display:block;color:var(--color-muted);font-size:12px;margin-top:15px}.primary-button{height:44px;line-height:44px;border-radius:13px;background:var(--color-primary);color:white;font-size:14px;font-weight:700;margin-top:17px}.primary-button::after{border:0}
.start-card{display:flex;align-items:center;gap:13px;padding:17px}.plate{width:39px;height:39px;border:2px solid var(--color-secondary);border-radius:50%;display:flex;align-items:center;justify-content:center;box-sizing:border-box}.plate view{width:20px;height:2px;background:var(--color-secondary)}.start-copy{display:flex;flex-direction:column;gap:3px;flex:1}.start-copy text:first-child{font-size:14px;font-weight:700}.start-copy text:last-child{font-size:11px;color:var(--color-muted)}.small-button{background:var(--color-secondary);color:white;border-radius:11px;font-size:12px;height:37px;line-height:37px;padding:0 13px}.small-button::after{border:0}.section-head{margin:27px 3px 13px}.dish-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.dish-card{text-align:left;padding:0;overflow:hidden;background:var(--color-surface);position:relative}.dish-card::after{border:0}.dish-card image,.dish-image-fallback{width:100%;height:112px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,rgba(232,111,81,.12),rgba(127,155,120,.15))}.plate.small{width:42px;height:42px}.dish-info{padding:12px 38px 13px 12px}.dish-info text{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.dish-info text:first-child{font-size:14px;font-weight:700;color:var(--color-text)}.dish-info text:last-child{font-size:10px;color:var(--color-muted);margin-top:4px}.add-mark{position:absolute;right:12px;bottom:15px;width:23px;height:23px;border-radius:50%;background:var(--color-primary);color:white;text-align:center;line-height:21px;font-size:18px;font-weight:400}
@media(min-width:720px){.dish-grid{grid-template-columns:repeat(4,1fr)}.dish-card image,.dish-image-fallback{height:128px}.status-card{padding:24px}.hero-title{font-size:38px}}
</style>
