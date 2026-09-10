<template>
  <view v-if="open" class="overlay" @click="$emit('close')">
    <view class="dialog v2-card" @click.stop>
      <text class="kicker">DINNER MEMORY</text><text class="title">给这顿饭留点记忆</text><text class="copy">都可以跳过，之后仍能在记录里看到这顿饭。</text>
      <text class="label">今天吃得怎么样</text><view class="stars"><button v-for="value in 5" :key="value" :class="{active:value<=rating}" @click="rating=value">☆</button></view>
      <textarea v-model.trim="note" maxlength="300" placeholder="一句小记：谁做的、哪里特别好吃……" />
      <button class="photo" :loading="uploading" @click="pickPhoto"><image v-if="photoUrl" :src="photoUrl" mode="aspectFill"/><view v-else class="photo-icon"><view/></view><text>{{ photoUrl ? '重新选择照片' : '添加用餐照片' }}</text></button>
      <button class="complete" :loading="submitting" @click="submit">保存并完成本餐</button><button class="skip" :disabled="submitting" @click="$emit('submit', {})">跳过并完成</button>
    </view>
  </view>
</template>
<script setup>
import { ref,watch } from 'vue';import api from '../../services/api'
const props=defineProps({open:Boolean,spaceId:[String,Number],submitting:Boolean});const emit=defineEmits(['close','submit']);const rating=ref(0),note=ref(''),photoUrl=ref(''),uploading=ref(false)
watch(()=>props.open,value=>{if(value){rating.value=0;note.value='';photoUrl.value=''}})
async function pickPhoto(){try{const chosen=await new Promise((resolve,reject)=>uni.chooseImage({count:1,sizeType:['compressed'],sourceType:['album','camera'],success:resolve,fail:reject}));uploading.value=true;const data=await api.uploadAsset(props.spaceId,chosen.tempFilePaths[0],'record');const url=data.url||data.image_url||data.file_url;if(!url)throw new Error('服务端未返回图片 URL');photoUrl.value=url}catch(error){if(!String(error.errMsg||'').includes('cancel'))uni.showToast({title:error.message||'照片上传失败',icon:'none'})}finally{uploading.value=false}}
function submit(){emit('submit',{...(rating.value?{rating:rating.value}:{}),...(note.value?{note:note.value}:{}),...(photoUrl.value?{photo_url:photoUrl.value}:{})})}
</script>
<style scoped>
.overlay{position:fixed;z-index:80;inset:0;background:rgba(30,25,22,.48);display:flex;align-items:flex-end;justify-content:center;padding:16px 14px calc(16px + env(safe-area-inset-bottom))}.dialog{width:100%;max-width:520px;background:var(--color-surface);padding:23px}.kicker{display:block;color:var(--color-primary);font-size:9px;letter-spacing:2px;font-weight:800}.title{display:block;font-family:Georgia,'Songti SC',serif;font-size:23px;font-weight:700;margin-top:6px}.copy{display:block;color:var(--color-muted);font-size:10px;margin-top:6px}.label{display:block;font-size:11px;color:var(--color-muted);margin-top:18px}.stars{display:flex;gap:7px;margin:5px 0 14px}.stars button{margin:0;padding:0;background:transparent;color:#CFC5B9;font-size:30px;width:35px;line-height:35px}.stars button::after{border:0}.stars button.active{color:var(--color-accent)}textarea{width:100%;height:82px;border:1px solid rgba(47,41,37,.14);border-radius:12px;padding:11px;background:rgba(255,255,255,.5);font-size:12px}.photo{height:72px;margin-top:11px;border:1px dashed var(--color-secondary);background:rgba(127,155,120,.06);border-radius:12px;color:var(--color-secondary);font-size:11px;display:flex;align-items:center;justify-content:center;gap:9px}.photo::after,.complete::after,.skip::after{border:0}.photo image{width:54px;height:54px;border-radius:9px}.photo-icon{width:29px;height:29px;border:2px solid var(--color-secondary);border-radius:50%;position:relative}.photo-icon:before,.photo-icon:after{content:'';position:absolute;width:13px;height:2px;background:var(--color-secondary);left:6px;top:12px}.photo-icon:after{transform:rotate(90deg)}.complete{height:46px;line-height:46px;background:var(--color-primary);color:white;border-radius:13px;font-size:13px;font-weight:700;margin-top:14px}.skip{background:transparent;color:var(--color-muted);font-size:11px;margin-top:5px}@media(min-width:700px){.overlay{align-items:center}.dialog{padding:29px}}
</style>
