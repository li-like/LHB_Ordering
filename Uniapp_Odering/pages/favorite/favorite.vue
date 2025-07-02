<template>
	<view class="page-container">
		<view class="container">
			<!-- 页面标题 -->
			<view class="page-header">
				<text class="page-title">家庭喜爱菜品</text>
				<view class="add-meal-btn" @click="showAddMeal">
					<text class="add-icon">+</text>
					<text class="add-text">添加菜品</text>
				</view>
			</view>
			
			<!-- 统计信息 -->
			<view class="stats-card">
				<view class="stat-item">
					<text class="stat-number">{{ statistics.favoriteMealsCount }}</text>
					<text class="stat-label">总菜品数</text>
				</view>
				<view class="stat-item">
					<text class="stat-number">{{ getTopCategory().name }}</text>
					<text class="stat-label">最爱类型</text>
				</view>
				<view class="stat-item">
					<text class="stat-number">{{ getRecentlyAdded() }}</text>
					<text class="stat-label">最近添加</text>
				</view>
			</view>
			
			<!-- 分类筛选 -->
			<view class="category-section">
				<scroll-view scroll-x class="category-scroll">
					<view class="category-list">
						<view 
							class="category-item" 
							:class="{ active: selectedCategory === 'all' }"
							@click="setCategory('all')"
						>
							<text>全部</text>
						</view>
						<view 
							class="category-item" 
							:class="{ active: selectedCategory === category }"
							v-for="category in categories" 
							:key="category"
							@click="setCategory(category)"
						>
							<text>{{ category }}</text>
						</view>
					</view>
				</scroll-view>
			</view>
			
			<!-- 排序选项 -->
			<view class="sort-section">
				<view class="sort-options">
					<view 
						class="sort-item" 
						:class="{ active: sortBy === 'count' }"
						@click="setSortBy('count')"
					>
						<text>按次数</text>
					</view>
					<view 
						class="sort-item" 
						:class="{ active: sortBy === 'recent' }"
						@click="setSortBy('recent')"
					>
						<text>按时间</text>
					</view>
					<view 
						class="sort-item" 
						:class="{ active: sortBy === 'name' }"
						@click="setSortBy('name')"
					>
						<text>按名称</text>
					</view>
				</view>
			</view>
			
			<!-- 菜品列表 -->
			<view class="meals-section">
				<view v-if="loading" class="loading-section">
					<text>加载中...</text>
				</view>
				
				<view v-else-if="filteredMeals.length === 0" class="empty-section">
					<text class="empty-icon">🍽️</text>
					<text class="empty-text">还没有喜爱菜品</text>
					<text class="empty-desc">点击右上角添加第一道菜品吧</text>
				</view>
				
				<view v-else class="meals-grid">
					<view 
						class="meal-card" 
						v-for="meal in filteredMeals" 
						:key="meal.id"
						@click="showMealDetail(meal)"
					>
						<!-- 菜品图片 -->
						<view class="meal-image-container">
							<image 
								class="meal-image" 
								:src="meal.image || '/static/dishes/default.jpg'" 
								mode="aspectFill"
								@error="handleImageError"
							></image>
							<view class="meal-count-badge">
								<text class="count-text">{{ meal.count }}次</text>
							</view>
						</view>
						
						<!-- 菜品信息 -->
						<view class="meal-info">
							<text class="meal-name">{{ meal.name }}</text>
							<view class="meal-meta">
								<text class="meal-category">{{ meal.category }}</text>
								<text class="meal-time">{{ formatTime(meal.addTime) }}</text>
							</view>
							<text class="meal-last-cooked">最后制作：{{ meal.lastCooked }}</text>
							<text class="meal-added-by">添加者：{{ meal.addedBy }}</text>
						</view>
						
						<!-- 操作按钮 -->
						<view class="meal-actions">
							<view class="action-btn like-btn" @click.stop="toggleLike(meal)">
								<text class="action-icon">❤️</text>
							</view>
							<view class="action-btn cook-btn" @click.stop="recordCooking(meal)">
								<text class="action-icon">🍳</text>
							</view>
							<view class="action-btn share-btn" @click.stop="shareMeal(meal)">
								<text class="action-icon">📤</text>
							</view>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 添加菜品弹窗 -->
		<uni-popup ref="addMealPopup" type="center" :mask-click="false">
			<view class="add-meal-popup">
				<view class="popup-header">
					<text class="popup-title">添加喜爱菜品</text>
					<view class="close-btn" @click="hideAddMeal">
						<text class="close-icon">×</text>
					</view>
				</view>
				
				<view class="popup-content">
					<view class="form-group">
						<text class="form-label">菜品名称</text>
						<input 
							class="form-input" 
							v-model="newMeal.name" 
							placeholder="请输入菜品名称"
							maxlength="20"
						/>
					</view>
					
					<view class="form-group">
						<text class="form-label">菜品分类</text>
						<picker 
							mode="selector" 
							:range="categoryOptions" 
							:value="newMeal.categoryIndex"
							@change="onCategoryChange"
						>
							<view class="picker-input">
								<text>{{ categoryOptions[newMeal.categoryIndex] || '请选择分类' }}</text>
								<text class="picker-arrow">></text>
							</view>
						</picker>
					</view>
					
					<view class="form-group">
						<text class="form-label">菜品图片（可选）</text>
						<view class="image-upload" @click="selectImage">
							<image 
								v-if="newMeal.image" 
								class="upload-preview" 
								:src="newMeal.image" 
								mode="aspectFill"
							></image>
							<view v-else class="upload-placeholder">
								<text class="upload-icon">📷</text>
								<text class="upload-text">点击添加图片</text>
							</view>
						</view>
					</view>
					
					<view class="form-group">
						<text class="form-label">制作次数</text>
						<view class="count-input">
							<view class="count-btn" @click="decreaseCount">
								<text>-</text>
							</view>
							<input 
								class="count-value" 
								v-model.number="newMeal.count" 
								type="number"
								min="1"
							/>
							<view class="count-btn" @click="increaseCount">
								<text>+</text>
							</view>
						</view>
					</view>
				</view>
				
				<view class="popup-footer">
					<view class="popup-btn cancel-btn" @click="hideAddMeal">
						<text>取消</text>
					</view>
					<view class="popup-btn confirm-btn" @click="confirmAddMeal">
						<text>添加</text>
					</view>
				</view>
			</view>
		</uni-popup>
		
		<!-- 菜品详情弹窗 -->
		<uni-popup ref="mealDetailPopup" type="center">
			<view class="meal-detail-popup" v-if="selectedMeal">
				<view class="detail-header">
					<text class="detail-title">{{ selectedMeal.name }}</text>
					<view class="close-btn" @click="hideMealDetail">
						<text class="close-icon">×</text>
					</view>
				</view>
				
				<view class="detail-content">
					<image 
						class="detail-image" 
						:src="selectedMeal.image || '/static/dishes/default.jpg'" 
						mode="aspectFill"
					></image>
					
					<view class="detail-info">
						<view class="info-row">
							<text class="info-label">分类：</text>
							<text class="info-value">{{ selectedMeal.category }}</text>
						</view>
						<view class="info-row">
							<text class="info-label">制作次数：</text>
							<text class="info-value">{{ selectedMeal.count }}次</text>
						</view>
						<view class="info-row">
							<text class="info-label">最后制作：</text>
							<text class="info-value">{{ selectedMeal.lastCooked }}</text>
						</view>
						<view class="info-row">
							<text class="info-label">添加者：</text>
							<text class="info-value">{{ selectedMeal.addedBy }}</text>
						</view>
						<view class="info-row">
							<text class="info-label">添加时间：</text>
							<text class="info-value">{{ formatDate(selectedMeal.addTime) }}</text>
						</view>
					</view>
				</view>
				
				<view class="detail-footer">
					<view class="detail-btn edit-btn" @click="editMeal">
						<text>编辑</text>
					</view>
					<view class="detail-btn cook-btn" @click="recordCookingFromDetail">
						<text>记录制作</text>
					</view>
				</view>
			</view>
		</uni-popup>
	</view>
</template>

<script>
import familyManager from '@/utils/familyManager.js'

export default {
	name: 'FavoritePage',
	components: {
		// 如果需要使用 uni-popup 组件，需要先导入
		// 'uni-popup': () => import('@dcloudio/uni-ui/lib/uni-popup/uni-popup.vue')
	},
	data() {
		return {
			loading: false,
			statistics: {
				favoriteMealsCount: 0,
				memberCount: 0
			},
			favoriteMeals: [],
			selectedCategory: 'all',
			sortBy: 'count', // count, recent, name
			categories: ['荤菜', '素菜', '汤品', '蛋类', '川菜', '粤菜', '湘菜', '家常菜', '甜品', '其他'],
			categoryOptions: ['荤菜', '素菜', '汤品', '蛋类', '川菜', '粤菜', '湘菜', '家常菜', '甜品', '其他'],
			newMeal: {
				name: '',
				category: '',
				categoryIndex: 0,
				count: 1,
				image: ''
			},
			selectedMeal: null
		}
	},
	
	computed: {
		filteredMeals() {
			let meals = [...this.favoriteMeals]
			
			// 按分类筛选
			if (this.selectedCategory !== 'all') {
				meals = meals.filter(meal => meal.category === this.selectedCategory)
			}
			
			// 排序
			switch (this.sortBy) {
				case 'count':
					meals.sort((a, b) => b.count - a.count)
					break
				case 'recent':
					meals.sort((a, b) => new Date(b.addTime) - new Date(a.addTime))
					break
				case 'name':
					meals.sort((a, b) => a.name.localeCompare(b.name))
					break
			}
			
			return meals
		}
	},
	
	onLoad() {
		this.initializePage()
	},
	
	onShow() {
		this.refreshData()
	},
	
	onUnload() {
		// 清理事件监听
		familyManager.off('favoriteMealsUpdated', this.onFavoriteMealsUpdated)
	},
	
	methods: {
		/**
		 * 初始化页面
		 */
		async initializePage() {
			// 注册事件监听
			familyManager.on('favoriteMealsUpdated', this.onFavoriteMealsUpdated)
			
			await this.loadData()
		},
		
		/**
		 * 加载数据
		 */
		async loadData() {
			this.loading = true
			
			try {
				// 确保家庭管理器已初始化
				if (!familyManager.getCurrentFamily()) {
					await familyManager.initialize()
				}
				
				// 获取统计数据
				this.statistics = familyManager.getStatistics()
				
				// 获取喜爱菜品
				this.favoriteMeals = familyManager.getFavoriteMeals()
				
			} catch (error) {
				console.error('加载数据失败:', error)
				uni.showToast({
					title: '加载失败',
					icon: 'error'
				})
			} finally {
				this.loading = false
			}
		},
		
		/**
		 * 刷新数据
		 */
		async refreshData() {
			await this.loadData()
		},
		
		/**
		 * 监听喜爱菜品更新
		 */
		onFavoriteMealsUpdated(event) {
			this.favoriteMeals = event.data
			this.statistics = familyManager.getStatistics()
		},
		
		/**
		 * 设置分类筛选
		 */
		setCategory(category) {
			this.selectedCategory = category
		},
		
		/**
		 * 设置排序方式
		 */
		setSortBy(sortBy) {
			this.sortBy = sortBy
		},
		
		/**
		 * 获取最受欢迎的菜品分类
		 */
		getTopCategory() {
			if (this.favoriteMeals.length === 0) {
				return { name: '-', count: 0 }
			}
			
			const categoryCount = {}
			this.favoriteMeals.forEach(meal => {
				categoryCount[meal.category] = (categoryCount[meal.category] || 0) + meal.count
			})
			
			const topCategory = Object.keys(categoryCount).reduce((a, b) => 
				categoryCount[a] > categoryCount[b] ? a : b
			)
			
			return {
				name: topCategory,
				count: categoryCount[topCategory]
			}
		},
		
		/**
		 * 获取最近添加的菜品数量
		 */
		getRecentlyAdded() {
			const sevenDaysAgo = new Date()
			sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
			
			return this.favoriteMeals.filter(meal => 
				new Date(meal.addTime) >= sevenDaysAgo
			).length
		},
		
		/**
		 * 显示添加菜品弹窗
		 */
		showAddMeal() {
			this.resetNewMeal()
			this.$refs.addMealPopup.open()
		},
		
		/**
		 * 隐藏添加菜品弹窗
		 */
		hideAddMeal() {
			this.$refs.addMealPopup.close()
		},
		
		/**
		 * 重置新菜品表单
		 */
		resetNewMeal() {
			this.newMeal = {
				name: '',
				category: '',
				categoryIndex: 0,
				count: 1,
				image: ''
			}
		},
		
		/**
		 * 分类选择变化
		 */
		onCategoryChange(e) {
			this.newMeal.categoryIndex = e.detail.value
			this.newMeal.category = this.categoryOptions[e.detail.value]
		},
		
		/**
		 * 选择图片
		 */
		selectImage() {
			uni.chooseImage({
				count: 1,
				sourceType: ['album', 'camera'],
				success: (res) => {
					this.newMeal.image = res.tempFilePaths[0]
				},
				fail: (error) => {
					console.error('选择图片失败:', error)
				}
			})
		},
		
		/**
		 * 减少次数
		 */
		decreaseCount() {
			if (this.newMeal.count > 1) {
				this.newMeal.count--
			}
		},
		
		/**
		 * 增加次数
		 */
		increaseCount() {
			this.newMeal.count++
		},
		
		/**
		 * 确认添加菜品
		 */
		async confirmAddMeal() {
			if (!this.newMeal.name.trim()) {
				uni.showToast({
					title: '请输入菜品名称',
					icon: 'error'
				})
				return
			}
			
			if (!this.newMeal.category) {
				uni.showToast({
					title: '请选择菜品分类',
					icon: 'error'
				})
				return
			}
			
			try {
				// 构造菜品数据
				const mealData = {
					name: this.newMeal.name,
					category: this.newMeal.category,
					count: this.newMeal.count,
					image: this.newMeal.image,
					description: '',
					tags: []
				}
				
				// 使用 familyManager 添加菜品
				const newMeal = await familyManager.addFavoriteMeal(mealData)
				
				// 更新本地数据
				this.favoriteMeals = familyManager.getFavoriteMeals()
				this.statistics = familyManager.getStatistics()
				
				uni.showToast({
					title: '添加成功',
					icon: 'success'
				})
				
				this.hideAddMeal()
				
			} catch (error) {
				console.error('添加菜品失败:', error)
				uni.showToast({
					title: '添加失败，请重试',
					icon: 'error'
				})
			}
		},
		
		/**
		 * 显示菜品详情
		 */
		showMealDetail(meal) {
			this.selectedMeal = meal
			this.$refs.mealDetailPopup.open()
		},
		
		/**
		 * 隐藏菜品详情
		 */
		hideMealDetail() {
			this.$refs.mealDetailPopup.close()
			this.selectedMeal = null
		},
		
		/**
		 * 切换喜欢状态
		 */
		async toggleLike(meal) {
			try {
				await familyManager.toggleFavoriteMealLike(meal.id)
				
				// 更新本地数据
				this.favoriteMeals = familyManager.getFavoriteMeals()
				
			} catch (error) {
				console.error('切换点赞状态失败:', error)
				uni.showToast({
					title: '操作失败，请重试',
					icon: 'error'
				})
			}
		},
		
		/**
		 * 记录制作
		 */
		recordCooking(meal) {
			// 跳转到用餐记录页面，并传递菜品信息
			uni.navigateTo({
				url: `/pages/cooking/cooking?dish=${encodeURIComponent(meal.name)}`
			})
		},
		
		/**
		 * 分享菜品
		 */
		shareMeal(meal) {
			// TODO: 实现分享功能
			uni.showToast({
				title: '功能开发中',
				icon: 'none'
			})
		},
		
		/**
		 * 编辑菜品
		 */
		editMeal() {
			// TODO: 实现编辑功能
			uni.showToast({
				title: '功能开发中',
				icon: 'none'
			})
			this.hideMealDetail()
		},
		
		/**
		 * 从详情页面记录制作
		 */
		recordCookingFromDetail() {
			this.hideMealDetail()
			this.recordCooking(this.selectedMeal)
		},
		
		/**
		 * 处理图片加载错误
		 */
		handleImageError() {
			// 使用默认图片
		},
		
		/**
		 * 格式化时间
		 */
		formatTime(time) {
			if (!time) return ''
			
			const now = new Date()
			const date = new Date(time)
			const diff = now - date
			
			if (diff < 60000) { // 1分钟内
				return '刚刚'
			} else if (diff < 3600000) { // 1小时内
				return `${Math.floor(diff / 60000)}分钟前`
			} else if (diff < 86400000) { // 1天内
				return `${Math.floor(diff / 3600000)}小时前`
			} else if (diff < 604800000) { // 1周内
				return `${Math.floor(diff / 86400000)}天前`
			} else {
				return this.formatDate(date)
			}
		},
		
		/**
		 * 格式化日期
		 */
		formatDate(date) {
			if (!date) return ''
			
			const d = new Date(date)
			const year = d.getFullYear()
			const month = (d.getMonth() + 1).toString().padStart(2, '0')
			const day = d.getDate().toString().padStart(2, '0')
			
			return `${year}-${month}-${day}`
		}
	}
}
</script>

<style lang="scss" scoped>
.page-container {
	background-color: #f8f9fa;
	min-height: 100vh;
}

.container {
	padding: 20rpx;
}

/* 页面标题 */
.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
	
	.page-title {
		font-size: 36rpx;
		font-weight: bold;
		color: #333;
	}
	
	.add-meal-btn {
		display: flex;
		align-items: center;
		background: linear-gradient(135deg, #FF6B95, #FF8E8E);
		padding: 12rpx 20rpx;
		border-radius: 30rpx;
		color: white;
		
		.add-icon {
			font-size: 24rpx;
			margin-right: 8rpx;
		}
		
		.add-text {
			font-size: 24rpx;
		}
	}
}

/* 统计卡片 */
.stats-card {
	display: flex;
	background: white;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
	
	.stat-item {
		flex: 1;
		text-align: center;
		
		.stat-number {
			display: block;
			font-size: 36rpx;
			font-weight: bold;
			color: #FF6B95;
			margin-bottom: 8rpx;
		}
		
		.stat-label {
			font-size: 24rpx;
			color: #999;
		}
	}
}

/* 分类筛选 */
.category-section {
	margin-bottom: 20rpx;
	
	.category-scroll {
		white-space: nowrap;
	}
	
	.category-list {
		display: flex;
		padding: 0 10rpx;
		
		.category-item {
			flex-shrink: 0;
			padding: 16rpx 28rpx;
			margin-right: 20rpx;
			background: white;
			border-radius: 30rpx;
			font-size: 28rpx;
			color: #666;
			border: 2rpx solid transparent;
			
			&.active {
				background: #FF6B95;
				color: white;
			}
		}
	}
}

/* 排序选项 */
.sort-section {
	margin-bottom: 20rpx;
	
	.sort-options {
		display: flex;
		background: white;
		border-radius: 12rpx;
		padding: 8rpx;
		
		.sort-item {
			flex: 1;
			text-align: center;
			padding: 16rpx;
			font-size: 28rpx;
			color: #666;
			border-radius: 8rpx;
			
			&.active {
				background: #FF6B95;
				color: white;
			}
		}
	}
}

/* 菜品列表 */
.meals-section {
	.loading-section, .empty-section {
		text-align: center;
		padding: 100rpx 0;
		color: #999;
	}
	
	.empty-section {
		.empty-icon {
			font-size: 80rpx;
			display: block;
			margin-bottom: 20rpx;
		}
		
		.empty-text {
			font-size: 32rpx;
			display: block;
			margin-bottom: 10rpx;
		}
		
		.empty-desc {
			font-size: 28rpx;
			color: #ccc;
		}
	}
}

.meals-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
}

.meal-card {
	background: white;
	border-radius: 16rpx;
	overflow: hidden;
	box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
	
	.meal-image-container {
		position: relative;
		height: 200rpx;
		
		.meal-image {
			width: 100%;
			height: 100%;
		}
		
		.meal-count-badge {
			position: absolute;
			top: 10rpx;
			right: 10rpx;
			background: rgba(0, 0, 0, 0.7);
			color: white;
			padding: 6rpx 12rpx;
			border-radius: 16rpx;
			
			.count-text {
				font-size: 20rpx;
			}
		}
	}
	
	.meal-info {
		padding: 20rpx;
		
		.meal-name {
			font-size: 30rpx;
			font-weight: bold;
			color: #333;
			display: block;
			margin-bottom: 12rpx;
		}
		
		.meal-meta {
			display: flex;
			justify-content: space-between;
			margin-bottom: 8rpx;
			
			.meal-category {
				font-size: 24rpx;
				color: #FF6B95;
				background: rgba(255, 107, 149, 0.1);
				padding: 4rpx 12rpx;
				border-radius: 12rpx;
			}
			
			.meal-time {
				font-size: 20rpx;
				color: #999;
			}
		}
		
		.meal-last-cooked {
			font-size: 22rpx;
			color: #666;
			display: block;
			margin-bottom: 6rpx;
		}
		
		.meal-added-by {
			font-size: 22rpx;
			color: #999;
		}
	}
	
	.meal-actions {
		display: flex;
		padding: 20rpx;
		border-top: 1rpx solid #f0f0f0;
		
		.action-btn {
			flex: 1;
			text-align: center;
			padding: 12rpx;
			margin: 0 6rpx;
			border-radius: 8rpx;
			font-size: 20rpx;
			
			&.like-btn {
				background: rgba(255, 107, 149, 0.1);
				color: #FF6B95;
			}
			
			&.cook-btn {
				background: rgba(255, 165, 0, 0.1);
				color: #FFA500;
			}
			
			&.share-btn {
				background: rgba(0, 122, 255, 0.1);
				color: #007AFF;
			}
		}
	}
}

/* 弹窗样式 */
.add-meal-popup, .meal-detail-popup {
	width: 600rpx;
	background: white;
	border-radius: 16rpx;
	overflow: hidden;
}

.popup-header, .detail-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #f0f0f0;
	
	.popup-title, .detail-title {
		font-size: 32rpx;
		font-weight: bold;
		color: #333;
	}
	
	.close-btn {
		width: 60rpx;
		height: 60rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		
		.close-icon {
			font-size: 40rpx;
			color: #999;
		}
	}
}

.popup-content {
	padding: 30rpx;
	
	.form-group {
		margin-bottom: 30rpx;
		
		.form-label {
			display: block;
			font-size: 28rpx;
			color: #333;
			margin-bottom: 12rpx;
		}
		
		.form-input {
			width: 100%;
			padding: 20rpx;
			border: 2rpx solid #e0e0e0;
			border-radius: 8rpx;
			font-size: 28rpx;
		}
		
		.picker-input {
			display: flex;
			justify-content: space-between;
			align-items: center;
			padding: 20rpx;
			border: 2rpx solid #e0e0e0;
			border-radius: 8rpx;
			font-size: 28rpx;
			
			.picker-arrow {
				color: #999;
			}
		}
		
		.image-upload {
			border: 2rpx dashed #e0e0e0;
			border-radius: 8rpx;
			overflow: hidden;
			
			.upload-preview {
				width: 100%;
				height: 200rpx;
			}
			
			.upload-placeholder {
				height: 200rpx;
				display: flex;
				flex-direction: column;
				align-items: center;
				justify-content: center;
				color: #999;
				
				.upload-icon {
					font-size: 48rpx;
					margin-bottom: 12rpx;
				}
				
				.upload-text {
					font-size: 28rpx;
				}
			}
		}
		
		.count-input {
			display: flex;
			align-items: center;
			
			.count-btn {
				width: 60rpx;
				height: 60rpx;
				border: 2rpx solid #e0e0e0;
				display: flex;
				align-items: center;
				justify-content: center;
				font-size: 32rpx;
				color: #666;
			}
			
			.count-value {
				flex: 1;
				text-align: center;
				padding: 20rpx;
				border-top: 2rpx solid #e0e0e0;
				border-bottom: 2rpx solid #e0e0e0;
				font-size: 28rpx;
			}
		}
	}
}

.popup-footer {
	display: flex;
	border-top: 1rpx solid #f0f0f0;
	
	.popup-btn {
		flex: 1;
		padding: 30rpx;
		text-align: center;
		font-size: 32rpx;
		
		&.cancel-btn {
			color: #999;
		}
		
		&.confirm-btn {
			color: #FF6B95;
			border-left: 1rpx solid #f0f0f0;
		}
	}
}

.detail-content {
	.detail-image {
		width: 100%;
		height: 300rpx;
	}
	
	.detail-info {
		padding: 30rpx;
		
		.info-row {
			display: flex;
			margin-bottom: 20rpx;
			
			.info-label {
				font-size: 28rpx;
				color: #666;
				min-width: 160rpx;
			}
			
			.info-value {
				font-size: 28rpx;
				color: #333;
				flex: 1;
			}
		}
	}
}

.detail-footer {
	display: flex;
	padding: 30rpx;
	border-top: 1rpx solid #f0f0f0;
	
	.detail-btn {
		flex: 1;
		padding: 20rpx;
		margin: 0 10rpx;
		text-align: center;
		font-size: 28rpx;
		border-radius: 8rpx;
		
		&.edit-btn {
			border: 2rpx solid #FF6B95;
			color: #FF6B95;
		}
		
		&.cook-btn {
			background: #FF6B95;
			color: white;
		}
	}
}
</style>
