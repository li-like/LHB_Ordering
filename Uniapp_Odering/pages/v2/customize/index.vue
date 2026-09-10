<template>
  <view class="custom-page" :class="[`cards-${form.appearance.card_style}`]" :style="previewTokens">
    <view class="preview-bg" />
    <view class="custom-top safe-top"><view class="top-inner"><button @click="back">‹</button><view><text>空间个性化</text><text>所有改变只属于你们</text></view><button class="save-top" :loading="saving" @click="save">保存</button></view></view>
    <scroll-view scroll-y class="custom-scroll"><view class="custom-shell">
      <view class="preview v2-card"><view class="preview-content"><text class="preview-kicker">OUR TABLE</text><text class="preview-name">{{ form.space_name || '我们的餐桌' }}</text><text class="preview-nav">{{ Object.values(form.appearance.navigation_labels).join(' · ') }}</text></view><Avatar :src="form.member.avatar_url" :name="form.member.display_name" :frame="form.member.avatar_frame" :size="54"/></view>

      <view class="section v2-card"><view class="section-head"><text>空间与个人</text><text>你可以使用昵称，不必是真实姓名</text></view>
        <label class="field"><text>空间名称</text><input v-model.trim="form.space_name" maxlength="24" /></label>
        <label class="field"><text>我的显示名</text><input v-model.trim="form.member.display_name" maxlength="20" /></label>
        <view class="image-setting"><Avatar :src="form.member.avatar_url" :name="form.member.display_name" :frame="form.member.avatar_frame" :size="58"/><view><text>我的头像</text><text>支持从相册选择并安全上传</text></view><button :loading="uploading==='avatar'" @click="pick('avatar')">更换</button></view>
        <text class="label">头像框</text><view class="option-row"><button v-for="frame in frames" :key="frame.key" :class="{active:form.member.avatar_frame===frame.key}" @click="form.member.avatar_frame=frame.key">{{ frame.name }}</button></view>
      </view>

      <view class="section v2-card"><view class="section-head"><text>主题预设</text><text>从默认设计出发，再调成你们的颜色</text></view>
        <view class="theme-list"><button v-for="theme in themes" :key="theme.key" :class="{active:form.appearance.theme_key===theme.key}" @click="selectTheme(theme)"><view class="swatches"><view v-for="color in Object.values(theme.colors).slice(0,3)" :key="color" :style="{background:color}"/></view><view><text>{{ theme.name }}</text><text>{{ theme.description }}</text></view></button></view>
        <label class="field"><text>首页标题</text><input v-model.trim="form.appearance.home_title" maxlength="30" placeholder="今天吃什么" /></label>
        <text class="label">默认菜单图片样式</text><view class="option-row"><button v-for="style in globalImageStyles" :key="style.key" :class="{active:form.appearance.menu_image_style===style.key}" @click="form.appearance.menu_image_style=style.key">{{ style.name }}</button></view>
        <view class="image-setting"><view class="background-thumb" :style="backgroundThumbStyle"><view v-if="form.appearance.background_type==='preset'"/></view><view><text>页面背景</text><text>{{ form.appearance.background_type === 'image' ? '正在使用你们的照片' : '跟随当前主题的受控背景' }}</text></view><button v-if="form.appearance.background_type==='image'" @click="usePresetBackground">跟随主题</button><button :loading="uploading==='background'" @click="pick('background')">选择照片</button></view>
        <view class="color-grid"><label v-for="field in colorFields" :key="field.key" class="field"><text>{{ field.name }}</text><view class="color-input"><view :style="{background:form.appearance.custom_colors[field.key] || selectedTheme.colors[field.key]}"/><input v-model.trim="form.appearance.custom_colors[field.key]" maxlength="7" placeholder="#E86F51" /></view></label></view>
      </view>

      <view class="section v2-card"><view class="section-head"><text>卡片与导航</text><text>保持自由，也保持可读性</text></view>
        <text class="label">卡片样式</text><view class="option-row"><button v-for="style in cardStyles" :key="style.key" :class="{active:form.appearance.card_style===style.key}" @click="form.appearance.card_style=style.key">{{ style.name }}</button></view>
        <label class="field"><text>圆角大小（8–32）</text><slider :value="form.appearance.card_radius" min="8" max="32" activeColor="var(--color-primary)" @change="form.appearance.card_radius=$event.detail.value"/></label>
        <text class="label">四个导航名称</text><view class="nav-inputs"><label v-for="(name,key) in form.appearance.navigation_labels" :key="key"><text>{{ navNames[key] }}</text><input v-model.trim="form.appearance.navigation_labels[key]" maxlength="4" /></label></view>
      </view>

      <view class="section v2-card"><view class="section-head"><text>菜单展示</text><text>菜单名称、封面和呈现方式都能独立设置</text></view>
        <view v-for="(menu,index) in form.menus" :key="menu.id" class="menu-editor">
          <view class="menu-image" :style="menu.cover_image_url?{backgroundImage:`url(${menu.cover_image_url})`}:{}"><button :loading="uploading===`menu-${index}`" @click="pick('menu',index)">更换封面</button></view>
          <label class="field"><text>菜单名称</text><input v-model.trim="menu.name" maxlength="40" /></label>
          <label class="field"><text>菜单描述</text><input v-model.trim="menu.description" maxlength="200" placeholder="写一句属于你们的介绍" /></label>
          <text class="label">展示样式</text><view class="option-row compact"><button v-for="style in menuStyles" :key="style.key" :class="{active:menu.display_style===style.key}" @click="menu.display_style=style.key">{{ style.name }}</button></view>
          <view class="section-editors"><view v-for="section in menu.sections" :key="section.id" class="section-editor"><label class="field"><text>栏目名称</text><input v-model.trim="section.name" maxlength="30" /></label><label class="field"><text>栏目强调色</text><view class="color-input"><view :style="{background:section.accent_color || '#D9B27C'}"/><input v-model.trim="section.accent_color" maxlength="7" placeholder="#D9B27C" /></view></label></view></view>
        </view>
      </view>
      <view class="section v2-card"><view class="section-head"><text>我的口味</text><text>仅属于你的成员偏好，用于以后推荐和避雷</text></view>
        <label class="field"><text>喜欢的标签</text><input v-model.trim="preferenceInputs.favorite_tags" placeholder="清淡、番茄、面食" /></label>
        <label class="field"><text>不喜欢的标签</text><input v-model.trim="preferenceInputs.disliked_tags" placeholder="香菜、太甜" /></label>
        <label class="field"><text>过敏与忌口</text><input v-model.trim="preferenceInputs.allergens" placeholder="花生、乳制品" /></label>
        <label class="field"><text>饮食限制</text><input v-model.trim="preferenceInputs.dietary_restrictions" placeholder="素食、低盐" /></label>
        <label class="field"><text>补充备注</text><textarea v-model.trim="preferenceInputs.note" maxlength="500" placeholder="例如：工作日晚餐想吃得简单一些" /></label>
      </view>
      <button class="save-button" :loading="saving" :disabled="saving" @click="save">保存全部个性化设置</button>
      <text class="save-note">为保证小程序清晰易用，配色、圆角和布局在安全范围内开放。</text>
    </view></scroll-view>
  </view>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import Avatar from '../../../components/v2/Avatar.vue'
import { CARD_STYLES, DEFAULT_APPEARANCE, THEME_PRESETS, buildTokens, getTheme, normalizeAppearance } from '../../../design/themes'
import api from '../../../services/api'
import store, { state } from '../../../store'

const saving=ref(false),uploading=ref('')
const themes=THEME_PRESETS,cardStyles=CARD_STYLES
const frames=[{key:'none',name:'无边框'},{key:'heart',name:'爱心'},{key:'ring',name:'圆环'},{key:'floral',name:'花朵'},{key:'pixel',name:'像素'}]
const menuStyles=[{key:'inherit',name:'跟随主题'},{key:'cover',name:'满幅'},{key:'polaroid',name:'拍立得'},{key:'circle',name:'圆形'}]
const globalImageStyles=[{key:'cover',name:'满幅'},{key:'rounded',name:'圆角'},{key:'polaroid',name:'拍立得'},{key:'circle',name:'圆形'}]
const colorFields=[{key:'primary',name:'主色'},{key:'secondary',name:'伴侣色'},{key:'accent',name:'强调色'}]
const navNames={today:'第一个',menu:'第二个',records:'第三个',us:'第四个'}
const form=reactive({space_name:'',member:{display_name:'',avatar_url:'',avatar_frame:'none'},appearance:normalizeAppearance(DEFAULT_APPEARANCE),menus:[]})
const selectedTheme=computed(()=>getTheme(form.appearance.theme_key));const previewTokens=computed(()=>buildTokens(form.appearance))
const backgroundThumbStyle=computed(()=>({backgroundImage:buildTokens(form.appearance)['--page-background-image']}))
const preferenceInputs=reactive({favorite_tags:'',disliked_tags:'',allergens:'',dietary_restrictions:'',note:''})
const arrayFields=['favorite_tags','disliked_tags','allergens','dietary_restrictions']
function hydrate(){form.space_name=state.current_space?.name||'我们的餐桌';const uid=state.user?.id;const mine=state.members.find(m=>String(m.user?.id||m.user_id)===String(uid))||state.members[0]||state.user||{};Object.assign(form.member,{display_name:mine.display_name||state.user?.display_name||'我',avatar_url:mine.avatar_url||'',avatar_frame:mine.avatar_frame||'none'});form.appearance=normalizeAppearance(JSON.parse(JSON.stringify(state.appearance||DEFAULT_APPEARANCE)));form.menus=JSON.parse(JSON.stringify(state.menus||[]))}
async function init(){if(!state.current_space){const result=await store.bootstrap();if(result.route!=='home')return uni.reLaunch({url:'/pages/v2/auth/index'})}hydrate();try{const prefs=await api.preferences(state.current_space.id);arrayFields.forEach(key=>preferenceInputs[key]=(prefs[key]||[]).join('、'));preferenceInputs.note=prefs.note||''}catch(error){uni.showToast({title:error.message||'口味偏好加载失败',icon:'none'})}}
function selectTheme(theme){form.appearance.theme_key=theme.key;form.appearance.custom_colors={};form.appearance.background_type='preset';form.appearance.background_value='';form.appearance.background_image_url=''}
function usePresetBackground(){form.appearance.background_type='preset';form.appearance.background_value='';form.appearance.background_image_url=''}
function urlOf(data){return data.url||data.image_url||data.file_url||data.asset_url||''}
async function pick(kind,index=-1){
  const key=kind==='menu'?`menu-${index}`:kind
  try{
    const result=await new Promise((resolve,reject)=>uni.chooseImage({count:1,sizeType:['compressed'],sourceType:['album','camera'],success:resolve,fail:reject}))
    uploading.value=key
    const asset=await api.uploadAsset(state.current_space.id,result.tempFilePaths[0],kind==='menu'?'menu':kind)
    const url=urlOf(asset);if(!url)throw new Error('图片已上传，但服务端未返回 URL')
    if(kind==='avatar')form.member.avatar_url=url
    else if(kind==='background'){form.appearance.background_type='image';form.appearance.background_value=url;form.appearance.background_image_url=url}
    else form.menus[index].cover_image_url=url
  }catch(error){if(!String(error.errMsg||'').includes('cancel'))uni.showToast({title:error.message||'图片上传失败',icon:'none'})}finally{uploading.value=''}
}
function valid(){if(!form.space_name||!form.member.display_name)return '空间名称和显示名不能为空';if(!form.appearance.home_title)return '首页标题不能为空';for(const key of Object.keys(form.appearance.navigation_labels)){if(!form.appearance.navigation_labels[key])return '导航名称不能为空'}for(const value of Object.values(form.appearance.custom_colors)){if(value&&!/^#[0-9A-Fa-f]{6}$/.test(value))return '自定义颜色需使用 #RRGGBB 格式'}for(const menu of form.menus){if(!menu.name)return '菜单名称不能为空';for(const section of menu.sections||[]){if(!section.name)return '栏目名称不能为空';if(section.accent_color&&!/^#[0-9A-Fa-f]{6}$/.test(section.accent_color))return '栏目强调色需使用 #RRGGBB 格式'}}return ''}
async function save(){const issue=valid();if(issue)return uni.showToast({title:issue,icon:'none'});saving.value=true
  try{state.current_space=await api.updateSpace(state.current_space.id,{name:form.space_name});const member=await api.updateMe(state.current_space.id,{display_name:form.member.display_name,avatar_url:form.member.avatar_url,avatar_frame:form.member.avatar_frame});const mineIndex=state.members.findIndex(m=>String(m.user?.id||m.user_id)===String(state.user?.id));if(mineIndex>=0)state.members[mineIndex]=member;await store.saveAppearance(form.appearance);await Promise.all(form.menus.filter(m=>m.id).map(m=>api.updateMenu(state.current_space.id,m.id,{name:m.name,description:m.description,cover_image_url:m.cover_image_url,display_style:m.display_style})));await Promise.all(form.menus.flatMap(menu=>(menu.sections||[]).filter(section=>section.id).map(section=>api.updateSection(section.id,{name:section.name,accent_color:section.accent_color}))));const preferencePayload={note:preferenceInputs.note};arrayFields.forEach(key=>preferencePayload[key]=preferenceInputs[key].split(/[，,、]/).map(item=>item.trim()).filter(Boolean));state.preferences=await api.updatePreferences(state.current_space.id,preferencePayload);await store.refreshMenus();uni.showToast({title:'已经换成你们的样子',icon:'success'});setTimeout(()=>uni.navigateBack(),650)
  }catch(error){uni.showToast({title:error.message||'保存失败，未伪造成功状态',icon:'none',duration:3000})}finally{saving.value=false}}
function back(){uni.navigateBack()}
onMounted(()=>init().catch(error=>uni.showToast({title:error.message||'加载失败',icon:'none'})))
</script>

<style scoped>
.custom-page{height:100vh;background:var(--color-bg);color:var(--color-text);position:relative;overflow:hidden}.preview-bg{position:absolute;inset:0;background-image:var(--page-background-image);background-size:cover;background-position:center;opacity:.72}.custom-top{position:relative;z-index:5;background:rgba(255,252,247,.9);border-bottom:1px solid rgba(47,41,37,.08)}.top-inner{max-width:820px;height:64px;margin:0 auto;padding:0 15px;display:grid;grid-template-columns:55px 1fr 65px;align-items:center;box-sizing:border-box}.top-inner button{background:transparent;padding:0;margin:0;font-size:29px;text-align:left;color:var(--color-text)}.top-inner button::after{border:0}.top-inner>view{text-align:center}.top-inner>view text{display:block}.top-inner>view text:first-child{font-size:16px;font-weight:750}.top-inner>view text:last-child{font-size:9px;color:var(--color-muted);margin-top:2px}.top-inner .save-top{text-align:right;color:var(--color-primary);font-size:13px;font-weight:700}.custom-scroll{position:relative;z-index:2;height:calc(100vh - 64px - env(safe-area-inset-top))}.custom-shell{max-width:820px;margin:0 auto;padding:17px 14px calc(35px + env(safe-area-inset-bottom));box-sizing:border-box}.preview{min-height:98px;padding:18px;display:flex;align-items:center;justify-content:space-between;background:var(--color-surface)}.preview-kicker{display:block;font-size:8px;letter-spacing:2px;color:var(--color-primary);font-weight:800}.preview-name{display:block;font-family:Georgia,'Songti SC',serif;font-size:22px;font-weight:700;margin-top:4px}.preview-nav{display:block;font-size:10px;color:var(--color-muted);margin-top:7px}.section{padding:20px;margin-top:14px;background:var(--color-surface)}.section-head{margin-bottom:17px}.section-head text{display:block}.section-head text:first-child{font-size:17px;font-weight:750}.section-head text:last-child{font-size:10px;color:var(--color-muted);margin-top:4px}.field{display:block;margin-top:14px}.field>text,.label{display:block;font-size:11px;color:var(--color-muted);font-weight:650;margin:0 0 7px 2px}.field input,.nav-inputs input,.field textarea{width:100%;height:43px;border:1px solid rgba(47,41,37,.15);border-radius:11px;padding:0 12px;box-sizing:border-box;background:rgba(255,255,255,.65);font-size:13px}.field textarea{height:82px;padding-top:10px}.image-setting{display:flex;align-items:center;gap:8px;margin-top:17px;padding:12px;background:rgba(127,155,120,.08);border-radius:13px}.image-setting>view:nth-child(2){flex:1}.image-setting>view:nth-child(2) text{display:block}.image-setting>view:nth-child(2) text:first-child{font-size:13px;font-weight:700}.image-setting>view:nth-child(2) text:last-child{font-size:9px;color:var(--color-muted);margin-top:3px}.image-setting button,.menu-image button{margin:0;background:var(--color-secondary);color:#fff;font-size:10px;height:34px;line-height:34px;border-radius:10px;padding:0 9px}.image-setting button::after,.menu-image button::after{border:0}.option-row{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:11px}.option-row button{margin:0;background:rgba(127,155,120,.08);border:1px solid transparent;color:var(--color-muted);height:35px;line-height:33px;font-size:10px;border-radius:10px;padding:0 11px}.option-row button::after{border:0}.option-row button.active{border-color:var(--color-primary);color:var(--color-primary);background:rgba(232,111,81,.08);font-weight:700}.theme-list{display:grid;gap:8px}.theme-list>button{margin:0;background:rgba(127,155,120,.06);padding:12px;border-radius:13px;display:flex;align-items:center;gap:11px;text-align:left}.theme-list>button::after{border:1px solid transparent;border-radius:13px}.theme-list>button.active::after{border-color:var(--color-primary)}.theme-list button>view:last-child{flex:1}.theme-list text{display:block;color:var(--color-text)}.theme-list text:first-child{font-size:13px;font-weight:700}.theme-list text:last-child{font-size:9px;color:var(--color-muted);margin-top:3px}.swatches{display:flex}.swatches view{width:18px;height:35px}.swatches view:first-child{border-radius:8px 0 0 8px}.swatches view:last-child{border-radius:0 8px 8px 0}.background-thumb{width:54px;height:45px;flex:0 0 auto;background-size:cover;background-position:center;background-color:var(--color-bg);border-radius:9px;display:flex;align-items:center;justify-content:center}.background-thumb>view{width:25px;height:2px;background:var(--color-secondary)}.color-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.color-input{display:flex;align-items:center;border:1px solid rgba(47,41,37,.15);border-radius:11px;background:rgba(255,255,255,.65);padding-left:8px}.color-input>view{width:17px;height:17px;border-radius:50%;flex:0 0 auto}.color-input input{border:0;padding:0 5px;min-width:0}.nav-inputs{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.nav-inputs label text{display:block;font-size:9px;color:var(--color-muted);margin:0 0 4px 2px}.menu-editor{border-top:1px solid rgba(47,41,37,.08);padding-top:15px;margin-top:15px}.menu-editor:first-of-type{border-top:0}.menu-image{height:105px;background:linear-gradient(120deg,var(--color-primary),var(--color-secondary));background-size:cover;background-position:center;border-radius:13px;padding:10px;display:flex;align-items:flex-end;justify-content:flex-end}.menu-image button{background:rgba(255,255,255,.9);color:var(--color-text)}.section-editors{margin-top:12px;padding:10px;background:rgba(127,155,120,.06);border-radius:12px}.section-editor{display:grid;grid-template-columns:1fr 1fr;gap:8px;border-top:1px solid rgba(47,41,37,.07);padding-bottom:10px}.section-editor:first-child{border-top:0}.save-button{height:49px;line-height:49px;background:var(--color-primary);color:white;border-radius:14px;font-size:14px;font-weight:700;margin-top:18px}.save-button::after{border:0}.save-note{display:block;text-align:center;color:var(--color-muted);font-size:9px;margin-top:9px}.cards-glass .section,.cards-glass .preview{background:rgba(255,255,255,.66);backdrop-filter:blur(12px)}
.custom-top{background:var(--color-surface);color:var(--color-text);border-bottom-color:var(--color-muted)}
@media(min-width:720px){.custom-shell{padding:25px 20px 50px}.section{padding:27px}.theme-list{grid-template-columns:repeat(4,1fr)}.theme-list>button{display:block}.swatches{margin-bottom:10px}.nav-inputs{grid-template-columns:repeat(4,1fr)}.menu-editor{display:grid;grid-template-columns:180px 1fr;gap:15px;align-items:center}.menu-image{height:120px;grid-row:span 4}.section-editors{grid-column:1 / -1}}
</style>
