<template>
	<scroll-view 
		class="container"
		scroll-y="true"
		refresher-enabled="true"
		:refresher-triggered="refreshing"
		@refresherrefresh="onRefresh"
	>
		<!-- 菜谱信息 -->
		<view class="recipe-header" v-if="recipe">
			<image class="recipe-cover" :src="recipe.cover_image || '/static/food-decoration.png'" mode="aspectFill"></image>
			<view class="recipe-info">
				<text class="recipe-name">{{ recipe.name }}</text>
				<text class="recipe-desc">{{ recipe.description }}</text>
			</view>
		</view>
		
		<!-- 制作笔记表单 -->
		<view class="note-form">
			<view class="section">
				<view class="section-title">
					<text class="section-icon">📝</text>
					<text class="section-text">制作心得</text>
				</view>
				
				<view class="form-group">
					<text class="label">制作过程记录</text>
					<textarea 
						class="textarea" 
						v-model="form.content" 
						placeholder="记录您的制作过程、心得体会、改进建议等..."
						maxlength="500"
						confirm-type="done"
						adjust-position="true"
						cursor-spacing="10"
						auto-height="true"
					></textarea>
					<text class="char-count">{{ form.content.length }}/500</text>
				</view>
				
				<view class="form-group">
					<text class="label">制作图片</text>
					<view class="image-upload-area">
						<view class="image-item" v-for="(image, index) in form.images" :key="index">
							<image class="preview-image" :src="image" mode="aspectFill"></image>
							<view class="remove-image" @click="removeImage(index)">×</view>
						</view>
						<view class="add-image" @click="addImage" v-if="form.images.length < 6">
							<text class="add-icon">+</text>
							<text class="add-text">添加图片</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 评分和标记 -->
			<view class="section">
				<view class="section-title">
					<text class="section-icon">⭐</text>
					<text class="section-text">制作评价</text>
				</view>
				
				<view class="form-group">
					<text class="label">制作成功度</text>
					<view class="rating-selector">
						<view class="rating-item" 
							v-for="star in 5" 
							:key="star"
							:class="{ active: form.rating >= star }"
							@click="selectRating(star)"
						>
							<text class="star">⭐</text>
						</view>
					</view>
				</view>
				
				<view class="form-group">
					<text class="label">制作结果</text>
					<view class="success-selector">
						<view class="success-option" 
							:class="{ active: form.success === true }"
							@click="form.success = true"
						>
							<text class="success-icon">✅</text>
							<text class="success-text">成功</text>
						</view>
						<view class="success-option" 
							:class="{ active: form.success === false }"
							@click="form.success = false"
						>
							<text class="fail-icon">❌</text>
							<text class="fail-text">失败</text>
						</view>
					</view>
				</view>
				
				<view class="form-group">
					<text class="label">改进建议</text>
					<input 
						class="input" 
						v-model="form.modifications" 
						placeholder="下次制作时可以尝试的改进..." 
						maxlength="100"
						confirm-type="done"
						adjust-position="true"
						cursor-spacing="10"
					/>
				</view>
			</view>
		</view>
		
		<!-- 提交按钮 -->
		<view class="submit-section">
			<button class="submit-btn" @click="submitNote" :disabled="submitting">
				{{ submitting ? '提交中...' : '保存笔记' }}
			</button>
		</view>
	</scroll-view>
</template>

<script>
import recipeManager from '../../utils/recipeManager.js'

export default {
	data() {
		return {
			recipeId: null,
			recipe: null,
			submitting: false,
			refreshing: false,
			form: {
				content: '',
				images: [],
				rating: 5,
				success: true,
				modifications: ''
			}
		}
	},
	
	onLoad(options) {
		console.log('制作笔记页面接收到的参数:', options)
		this.recipeId = options.id
		if (!this.recipeId) {
			uni.showToast({
				title: '缺少菜谱ID',
				icon: 'error'
			})
			setTimeout(() => {
				uni.navigateBack()
			}, 1500)
			return
		}
		this.loadRecipeInfo()
	},
	
	methods: {
		// 加载菜谱信息
		async loadRecipeInfo() {
			try {
				console.log('开始加载菜谱信息, ID:', this.recipeId)
				const result = await recipeManager.getRecipeDetail(this.recipeId)
				console.log('菜谱信息加载结果:', result)
				if (result.success) {
					this.recipe = result.data
				} else {
					throw new Error(result.error || '加载菜谱失败')
				}
			} catch (error) {
				console.error('加载菜谱信息失败:', error)
				uni.showToast({
					title: '加载失败',
					icon: 'error'
				})
			}
		},
		
		// 下拉刷新
		async onRefresh() {
			this.refreshing = true;
			try {
				await this.loadRecipeInfo();
			} finally {
				this.refreshing = false;
			}
		},
		
		// 选择评分
		selectRating(rating) {
			this.form.rating = rating
		},
		
		// 添加图片
		addImage() {
			uni.chooseImage({
				count: 6 - this.form.images.length,
				success: (res) => {
					this.form.images.push(...res.tempFilePaths)
				}
			})
		},
		
		// 移除图片
		removeImage(index) {
			this.form.images.splice(index, 1)
		},
		
		// 提交笔记
		async submitNote() {
			if (!this.form.content.trim()) {
				uni.showToast({
					title: '请填写制作心得',
					icon: 'none'
				})
				return
			}
			
			if (this.submitting) return
			
			this.submitting = true
			
			try {
				const noteData = {
					recipe_id: this.recipeId,
					content: this.form.content,
					images: this.form.images,
					rating: this.form.rating,
					success: this.form.success,
					modifications: this.form.modifications,
					cooking_date: new Date().toISOString()
				}
				
				const result = await recipeManager.createRecipeNote(this.recipeId, noteData)
				
				if (result.success) {
					uni.showToast({
						title: '保存成功',
						icon: 'success'
					})
					
					// 延迟返回，确保toast显示完成
					setTimeout(() => {
						// 通过事件总线通知详情页刷新数据
						uni.$emit('recipeNoteAdded', this.recipeId)
						uni.navigateBack()
					}, 1500)
				} else {
					throw new Error(result.error || '保存失败')
				}
			} catch (error) {
				console.error('保存笔记失败:', error)
				uni.showToast({
					title: error.message || '保存失败',
					icon: 'error'
				})
			} finally {
				this.submitting = false
			}
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #FFF5F8;
	padding-bottom: 40rpx;
	/* 修复滚动和显示问题 */
	position: relative;
	overflow-x: hidden;
}

.recipe-header {
	background: #FFFFFF;
	margin: 20rpx 30rpx;
	border-radius: 20rpx;
	padding: 30rpx;
	display: flex;
	align-items: center;
}

.recipe-cover {
	width: 120rpx;
	height: 120rpx;
	border-radius: 15rpx;
	margin-right: 20rpx;
}

.recipe-info {
	flex: 1;
}

.recipe-name {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 8rpx;
}

.recipe-desc {
	font-size: 24rpx;
	color: #666666;
}

.note-form {
	padding: 0 30rpx;
}

.section {
	background: #FFFFFF;
	border-radius: 20rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
}

.section-title {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.section-icon {
	font-size: 24rpx;
	margin-right: 8rpx;
}

.section-text {
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
}

.form-group {
	margin-bottom: 30rpx;
}

.form-group:last-child {
	margin-bottom: 0;
}

.label {
	display: block;
	font-size: 26rpx;
	color: #333333;
	margin-bottom: 12rpx;
}

.input, .textarea {
	width: 100%;
	padding: 24rpx 20rpx;
	border: 2rpx solid #E0E0E0;
	border-radius: 12rpx;
	font-size: 30rpx;
	background: #FFFFFF;
	box-sizing: border-box;
	color: #333333;
	line-height: 1.5;
	outline: none;
	-webkit-appearance: none;
	appearance: none;
	/* 确保输入框有足够高度 */
	min-height: 88rpx;
	height: 88rpx;
	display: flex;
	align-items: center;
	transition: border-color 0.3s ease;
}

.input:focus, .textarea:focus {
	border-color: #FF6B95;
	background: #FAFAFA;
}

.textarea {
	height: 220rpx;
	min-height: 220rpx;
	resize: none;
	align-items: flex-start;
	padding-top: 24rpx;
	line-height: 1.6;
}

.char-count {
	display: block;
	text-align: right;
	font-size: 22rpx;
	color: #999999;
	margin-top: 8rpx;
}

.image-upload-area {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
}

.image-item {
	position: relative;
	width: 150rpx;
	height: 150rpx;
}

.preview-image {
	width: 100%;
	height: 100%;
	border-radius: 10rpx;
}

.remove-image {
	position: absolute;
	top: -8rpx;
	right: -8rpx;
	width: 40rpx;
	height: 40rpx;
	background: #FF4757;
	color: #FFFFFF;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24rpx;
	font-weight: bold;
}

.add-image {
	width: 150rpx;
	height: 150rpx;
	border: 2rpx dashed #E0E0E0;
	border-radius: 10rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.add-icon {
	font-size: 40rpx;
	color: #999999;
	margin-bottom: 8rpx;
}

.add-text {
	font-size: 22rpx;
	color: #999999;
}

.rating-selector {
	display: flex;
	gap: 10rpx;
}

.rating-item {
	padding: 10rpx;
	border-radius: 8rpx;
	cursor: pointer;
	transition: all 0.3s ease;
}

.rating-item:hover {
	background-color: rgba(255, 107, 149, 0.1);
}

.rating-item.active .star {
	color: #FFD700;
	transform: scale(1.1);
}

.star {
	font-size: 32rpx;
	color: #E0E0E0;
	transition: all 0.3s ease;
}

.success-selector {
	display: flex;
	gap: 20rpx;
}

.success-option {
	flex: 1;
	padding: 20rpx;
	border: 2rpx solid #E0E0E0;
	border-radius: 15rpx;
	text-align: center;
	transition: all 0.3s;
}

.success-option.active {
	border-color: #FF6B95;
	background: rgba(255, 107, 149, 0.1);
}

.success-icon, .fail-icon {
	display: block;
	font-size: 32rpx;
	margin-bottom: 8rpx;
}

.success-text, .fail-text {
	font-size: 26rpx;
	color: #333333;
}

.submit-section {
	padding: 40rpx 30rpx;
}

.submit-btn {
	width: 100%;
	height: 80rpx;
	background: #FF6B95;
	color: #FFFFFF;
	border: none;
	border-radius: 40rpx;
	font-size: 32rpx;
	font-weight: bold;
}

.submit-btn:disabled {
	background: #CCCCCC;
}
</style>