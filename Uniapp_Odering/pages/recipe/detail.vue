<template>
	<view class="page-container">
		<scroll-view 
			class="container"
			scroll-y="true"
			refresher-enabled="true"
			:refresher-triggered="refreshing"
			@refresherrefresh="onRefresh"
		>
			<!-- 加载状态 -->
			<view class="loading" v-if="loading">
				<text class="loading-text">加载中...</text>
			</view>
			
			<!-- 菜谱详情 -->
			<view class="recipe-detail" v-else-if="recipe">
				<!-- 头部封面 -->
				<view class="recipe-header">
					<image class="cover-image" :src="recipe.cover_image || '/static/food-decoration.png'" mode="aspectFill"></image>
					<view class="header-overlay">
						<view class="recipe-basic">
							<text class="recipe-name">{{ recipe.name }}</text>
							<text class="recipe-desc">{{ recipe.description }}</text>
							<view class="recipe-meta">
								<view class="meta-item">
									<text class="meta-icon">⏱️</text>
									<text class="meta-text">{{ recipe.cook_time }}分钟</text>
								</view>
								<view class="meta-item">
									<text class="meta-icon">👥</text>
									<text class="meta-text">{{ recipe.servings }}人份</text>
								</view>
								<view class="meta-item">
									<text class="meta-icon">⭐</text>
									<text class="meta-text">{{ formatDifficulty(recipe.difficulty) }}</text>
								</view>
							</view>
						</view>
					</view>
				</view>
				
				<!-- 统计信息 -->
				<view class="stats-section">
					<view class="stat-item">
						<text class="stat-number">{{ recipe.likes || 0 }}</text>
						<text class="stat-label">点赞</text>
					</view>
					<view class="stat-item">
						<text class="stat-number">{{ recipe.success_rate || 0 }}%</text>
						<text class="stat-label">成功率</text>
					</view>
					<view class="stat-item">
						<text class="stat-number">{{ recipe.total_attempts || 0 }}</text>
						<text class="stat-label">制作次数</text>
					</view>
				</view>
				
				<!-- 标签 -->
				<view class="tags-section" v-if="recipe.tags && recipe.tags.length">
					<view class="section-title">
						<text class="title-text">菜品标签</text>
					</view>
					<view class="tags-list">
						<text class="tag" v-for="tag in recipe.tags" :key="tag">{{ tag }}</text>
					</view>
				</view>
				
				<!-- 食材清单 -->
				<view class="ingredients-section" v-if="recipe.ingredients && recipe.ingredients.length">
					<view class="section-title">
						<text class="title-icon">🥕</text>
						<text class="title-text">食材清单</text>
					</view>
					<view class="ingredients-list">
						<view class="ingredient-item" v-for="ingredient in recipe.ingredients" :key="ingredient.id">
							<text class="ingredient-name">{{ ingredient.name }}</text>
							<text class="ingredient-amount">{{ ingredient.amount }}{{ ingredient.unit }}</text>
						</view>
					</view>
				</view>
				
				<!-- 制作步骤 -->
				<view class="steps-section" v-if="recipe.steps && recipe.steps.length">
					<view class="section-title">
						<text class="title-icon">📝</text>
						<text class="title-text">制作步骤 ({{ recipe.steps.length }}步)</text>
					</view>
					<view class="steps-list">
						<view class="step-item" v-for="(step, index) in recipe.steps" :key="step.id || index">
							<view class="step-number">{{ step.step_number || (index + 1) }}</view>
							<view class="step-content">
								<text class="step-title" v-if="step.title">{{ step.title }}</text>
								<text class="step-description">{{ step.description }}</text>
								<view class="step-meta" v-if="step.time_required || step.temperature">
									<text class="step-time" v-if="step.time_required">⏱️ {{ step.time_required }}分钟</text>
									<text class="step-temp" v-if="step.temperature">🔥 {{ step.temperature }}</text>
								</view>
								<text class="step-tips" v-if="step.tips">💡 {{ step.tips }}</text>
								<!-- 步骤图片 -->
								<view class="step-images" v-if="step.images && step.images.length">
									<image class="step-image" v-for="(image, imgIndex) in step.images" :key="imgIndex" 
										:src="image" mode="aspectFill"></image>
								</view>
							</view>
						</view>
					</view>
				</view>
				
				<!-- 调试信息：当没有步骤时显示 -->
				<view class="debug-section" v-else-if="recipe">
					<view class="section-title">
						<text class="title-text">调试信息</text>
					</view>
					<text class="debug-text">步骤数据: {{ JSON.stringify(recipe.steps) }}</text>
					<text class="debug-text">菜谱ID: {{ recipe.id }}</text>
					<text class="debug-text">菜谱名称: {{ recipe.name }}</text>
				</view>
				
				<!-- 制作笔记 -->
				<view class="notes-section" v-if="recipe.notes && recipe.notes.length">
					<view class="section-title">
						<text class="title-icon">📝</text>
						<text class="title-text">制作笔记</text>
					</view>
					<view class="notes-list">
						<view class="note-item" v-for="note in recipe.notes" :key="note.id">
							<view class="note-header">
								<image class="note-avatar" :src="note.author.avatar || '/static/default-avatar.png'" mode="aspectFill"></image>
								<view class="note-author">
									<text class="author-name">{{ note.author.nickname }}</text>
									<text class="note-date">{{ formatDate(note.cooking_date) }}</text>
								</view>
								<view class="note-rating">
									<text class="rating-star" v-for="star in 5" :key="star" :class="{ active: star <= note.rating }">⭐</text>
								</view>
							</view>
							<text class="note-content">{{ note.content }}</text>
							<text class="note-success" :class="{ success: note.success, fail: !note.success }">
								{{ note.success ? '✅ 制作成功' : '❌ 制作失败' }}
							</text>
							<text class="note-modifications" v-if="note.modifications">💡 {{ note.modifications }}</text>
						</view>
					</view>
				</view>
				
				<!-- 占位符，防止内容被底部操作栏遮挡 -->
				<view class="bottom-placeholder"></view>
			</view>
			
			<!-- 错误状态 -->
			<view class="error-state" v-else>
				<text class="error-icon">😞</text>
				<text class="error-text">菜谱加载失败</text>
				<button class="retry-btn" @click="loadRecipe">重新加载</button>
			</view>
		</scroll-view>
		
		<!-- 底部操作栏 - 固定在页面底部 -->
		<view class="bottom-actions" v-if="recipe">
			<button class="action-btn favorite-btn" @click="toggleFavorite">
				<text class="btn-icon">❤️</text>
				<text class="btn-text">收藏</text>
			</button>
			<button class="action-btn edit-btn" @click="goToEdit">
				<text class="btn-icon">✏️</text>
				<text class="btn-text">编辑</text>
			</button>
			<button class="action-btn note-btn" @click="goToNote">
				<text class="btn-icon">📝</text>
				<text class="btn-text">笔记</text>
			</button>
		</view>
	</view>
</template>

<script>
import recipeManager from '../../utils/recipeManager.js'

export default {
	data() {
		return {
			recipeId: null,
			recipe: null,
			loading: true,
			refreshing: false
		}
	},
	
	onLoad(options) {
		this.recipeId = options.id
		this.loadRecipe()
		
		// 监听菜谱更新事件
		uni.$on('recipeUpdated', (updatedRecipeId) => {
			if (updatedRecipeId == this.recipeId) {
				this.loadRecipe()
			}
		})
		
		// 监听笔记添加事件
		uni.$on('recipeNoteAdded', (recipeId) => {
			if (recipeId == this.recipeId) {
				this.loadRecipe()
			}
		})
	},
	
	// 页面卸载时移除事件监听
	onUnload() {
		uni.$off('recipeUpdated')
		uni.$off('recipeNoteAdded')
	},
	
	// 页面显示时刷新数据（从编辑页返回时会触发）
	onShow() {
		// 只有在已经加载过数据的情况下才刷新
		if (this.recipeId && this.recipe) {
			this.loadRecipe()
		}
	},
	
	methods: {
		// 加载菜谱详情
		async loadRecipe() {
			if (!this.recipeId) {
				uni.showToast({
					title: '菜谱ID无效',
					icon: 'error'
				})
				return
			}
			
			this.loading = true
			
			try {
				const result = await recipeManager.getRecipeDetail(this.recipeId)
				if (result.success) {
					this.recipe = result.data
					console.log('菜谱数据:', this.recipe)
					console.log('制作步骤:', this.recipe.steps)
					console.log('食材清单:', this.recipe.ingredients)
				} else {
					throw new Error(result.error || '加载失败')
				}
			} catch (error) {
				console.error('加载菜谱详情失败:', error)
				uni.showToast({
					title: '加载失败',
					icon: 'error'
				})
			} finally {
				this.loading = false
			}
		},
		
		// 格式化难度
		formatDifficulty(difficulty) {
			const levels = ['', '简单', '一般', '中等', '困难', '大师级']
			return levels[difficulty] || '未知'
		},
		
		// 格式化日期
		formatDate(dateStr) {
			const date = new Date(dateStr)
			return `${date.getMonth() + 1}月${date.getDate()}日`
		},
		
		// 下拉刷新
		async onRefresh() {
			this.refreshing = true;
			try {
				await this.loadRecipe();
			} finally {
				this.refreshing = false;
			}
		},
		
		// 收藏切换
		async toggleFavorite() {
			try {
				const result = await recipeManager.toggleFavorite(this.recipeId)
				if (result.success) {
					this.recipe.likes = result.data.likes
					uni.showToast({
						title: result.data.favorited ? '收藏成功' : '取消收藏',
						icon: 'success'
					})
				}
			} catch (error) {
				console.error('收藏操作失败:', error)
				uni.showToast({
					title: '操作失败',
					icon: 'error'
				})
			}
		},
		
		// 跳转到编辑页面
		goToEdit() {
			uni.navigateTo({
				url: `/pages/recipe/edit?id=${this.recipeId}`
			})
		},
		
		// 跳转到制作笔记
		goToNote() {
			uni.navigateTo({
				url: `/pages/recipe/note?id=${this.recipeId}`
			})
		}
	}
}
</script>

<style scoped>
.page-container {
	position: relative;
	min-height: 100vh;
	background: #FFF5F8;
}

.container {
	height: calc(100vh - 120rpx); /* 减去底部操作栏高度 */
	background: #FFF5F8;
	/* 修复在某些情况下的显示问题 */
	position: relative;
	overflow-x: hidden;
}

.bottom-placeholder {
	height: 40rpx; /* 额外的底部间距 */
}

.loading {
	display: flex;
	justify-content: center;
	align-items: center;
	height: 400rpx;
}

.loading-text {
	font-size: 28rpx;
	color: #999999;
}

.recipe-header {
	position: relative;
	height: 400rpx;
	overflow: hidden;
}

.cover-image {
	width: 100%;
	height: 100%;
}

.header-overlay {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
	padding: 60rpx 30rpx 30rpx;
}

.recipe-basic {
	color: #FFFFFF;
}

.recipe-name {
	display: block;
	font-size: 40rpx;
	font-weight: bold;
	margin-bottom: 12rpx;
}

.recipe-desc {
	display: block;
	font-size: 26rpx;
	margin-bottom: 20rpx;
	opacity: 0.9;
}

.recipe-meta {
	display: flex;
	gap: 30rpx;
}

.meta-item {
	display: flex;
	align-items: center;
}

.meta-icon {
	font-size: 20rpx;
	margin-right: 8rpx;
}

.meta-text {
	font-size: 24rpx;
}

.stats-section {
	background: #FFFFFF;
	display: flex;
	justify-content: space-around;
	padding: 30rpx;
	margin: 20rpx 30rpx;
	border-radius: 20rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.stat-item {
	text-align: center;
}

.stat-number {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #FF6B95;
	margin-bottom: 8rpx;
}

.stat-label {
	font-size: 24rpx;
	color: #666666;
}

.tags-section,
.ingredients-section,
.steps-section,
.notes-section {
	background: #FFFFFF;
	margin: 20rpx 30rpx;
	border-radius: 20rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.section-title {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.title-icon {
	font-size: 24rpx;
	margin-right: 8rpx;
}

.title-text {
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
}

.tags-list {
	display: flex;
	flex-wrap: wrap;
	gap: 10rpx;
}

.tag {
	background: rgba(255, 107, 149, 0.1);
	color: #FF6B95;
	padding: 8rpx 16rpx;
	border-radius: 15rpx;
	font-size: 24rpx;
}

.ingredients-list {
	display: flex;
	flex-direction: column;
	gap: 15rpx;
}

.ingredient-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 15rpx;
	background: #F8F8F8;
	border-radius: 10rpx;
}

.ingredient-name {
	font-size: 26rpx;
	color: #333333;
}

.ingredient-amount {
	font-size: 24rpx;
	color: #FF6B95;
	font-weight: bold;
}

.steps-list {
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}

.step-item {
	display: flex;
	gap: 20rpx;
}

.step-number {
	width: 60rpx;
	height: 60rpx;
	background: #FF6B95;
	color: #FFFFFF;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24rpx;
	font-weight: bold;
	flex-shrink: 0;
}

.step-content {
	flex: 1;
}

.step-title {
	display: block;
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 8rpx;
}

.step-description {
	display: block;
	font-size: 26rpx;
	color: #666666;
	line-height: 1.6;
	margin-bottom: 12rpx;
}

.step-meta {
	display: flex;
	gap: 20rpx;
	margin-bottom: 8rpx;
}

.step-time,
.step-temp {
	font-size: 22rpx;
	color: #999999;
}

.step-tips {
	display: block;
	font-size: 22rpx;
	color: #FF6B95;
	background: rgba(255, 107, 149, 0.1);
	padding: 8rpx 12rpx;
	border-radius: 8rpx;
	margin-top: 8rpx;
}

.step-images {
	display: flex;
	flex-wrap: wrap;
	gap: 10rpx;
	margin-top: 12rpx;
}

.step-image {
	width: 120rpx;
	height: 120rpx;
	border-radius: 8rpx;
}

.debug-section {
	background: #FFFFFF;
	margin: 20rpx 30rpx;
	border-radius: 20rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.debug-text {
	display: block;
	font-size: 24rpx;
	color: #666666;
	margin-bottom: 10rpx;
	word-break: break-all;
}

.notes-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.note-item {
	background: #F8F8F8;
	padding: 20rpx;
	border-radius: 15rpx;
}

.note-header {
	display: flex;
	align-items: center;
	margin-bottom: 15rpx;
}

.note-avatar {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
	margin-right: 15rpx;
}

.note-author {
	flex: 1;
}

.author-name {
	display: block;
	font-size: 26rpx;
	color: #333333;
	font-weight: bold;
}

.note-date {
	font-size: 22rpx;
	color: #999999;
}

.note-rating {
	display: flex;
}

.rating-star {
	font-size: 20rpx;
	color: #E0E0E0;
}

.rating-star.active {
	color: #FFD700;
}

.note-content {
	display: block;
	font-size: 26rpx;
	color: #666666;
	line-height: 1.6;
	margin-bottom: 12rpx;
}

.note-success {
	display: block;
	font-size: 22rpx;
	margin-bottom: 8rpx;
}

.note-success.success {
	color: #4CAF50;
}

.note-success.fail {
	color: #FF4757;
}

.note-modifications {
	display: block;
	font-size: 22rpx;
	color: #FF6B95;
	background: rgba(255, 107, 149, 0.1);
	padding: 8rpx 12rpx;
	border-radius: 8rpx;
}

.error-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	height: 400rpx;
	padding: 40rpx;
}

.error-icon {
	font-size: 80rpx;
	margin-bottom: 20rpx;
}

.error-text {
	font-size: 28rpx;
	color: #999999;
	margin-bottom: 30rpx;
}

.retry-btn {
	background: #FF6B95;
	color: #FFFFFF;
	border: none;
	border-radius: 25rpx;
	padding: 20rpx 40rpx;
	font-size: 26rpx;
}

.bottom-actions {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	border-top: 1rpx solid #F0F0F0;
	display: flex;
	gap: 20rpx;
	box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.1);
	z-index: 100;
}

.action-btn {
	flex: 1;
	height: 80rpx;
	border: none;
	border-radius: 40rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8rpx;
	font-size: 26rpx;
	transition: all 0.3s ease;
}

.action-btn:active {
	transform: scale(0.95);
}

.favorite-btn {
	background: rgba(255, 107, 149, 0.1);
	color: #FF6B95;
	border: 2rpx solid #FF6B95;
}

.edit-btn {
	background: rgba(76, 175, 80, 0.1);
	color: #4CAF50;
	border: 2rpx solid #4CAF50;
}

.note-btn {
	background: #FF6B95;
	color: #FFFFFF;
	border: 2rpx solid #FF6B95;
}

.btn-icon {
	font-size: 24rpx;
}

.btn-text {
	font-size: 24rpx;
	font-weight: 500;
}
</style>
