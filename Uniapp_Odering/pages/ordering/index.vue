<template>
	<view class="container">
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">家庭餐厅</text>
			<view class="header-actions">
				<button class="request-btn" @click="goToMyRequests">
					<text class="request-icon">📋</text>
					<text class="request-text">我的点餐</text>
				</button>
			</view>
		</view>
		
		<!-- 快捷统计卡片 -->
		<view class="stats-cards">
			<view class="stat-card" @click="goToPendingRequests">
				<view class="stat-number">{{ pendingCount }}</view>
				<view class="stat-label">待处理</view>
				<view class="stat-icon">⏳</view>
			</view>
			<view class="stat-card" @click="goToTodayRequests">
				<view class="stat-number">{{ todayCount }}</view>
				<view class="stat-label">今日点餐</view>
				<view class="stat-icon">📅</view>
			</view>
			<view class="stat-card" @click="goToStats">
				<view class="stat-number">{{ familyMemberCount }}</view>
				<view class="stat-label">家庭成员</view>
				<view class="stat-icon">👥</view>
			</view>
		</view>
		
		<!-- 餐品分类标签栏 -->
		<scroll-view class="category-tabs" scroll-x="true" show-scrollbar="false">
			<view class="category-tab" 
				v-for="(category, index) in categories" 
				:key="index"
				:class="{ active: currentCategory === category.id }"
				@click="selectCategory(category.id)"
			>
				<text class="category-icon">{{ category.icon || '🍽️' }}</text>
				<text class="category-text">{{ category.name }}</text>
				<text class="category-count">({{ category.meal_count }})</text>
			</view>
		</scroll-view>
		
		<!-- 餐品列表 -->
		<scroll-view 
			class="meal-list" 
			scroll-y="true" 
			@scrolltolower="loadMoreMeals"
			refresher-enabled="true"
			:refresher-triggered="refreshing"
			@refresherrefresh="onRefresh"
		>
			<!-- 搜索栏 -->
			<view class="search-bar">
				<view class="search-input-wrapper">
					<input 
						class="search-input" 
						v-model="searchKeyword" 
						placeholder="搜索餐品..."
						@input="onSearchInput"
						confirm-type="search"
						@confirm="onSearchInput"
					/>
					<text class="search-icon">🔍</text>
				</view>
			</view>
			
			<!-- 空数据提示 -->
			<view v-if="!loading && meals.length === 0" class="empty-state">
				<text class="empty-icon">🍽️</text>
				<text class="empty-text">暂无可点餐品</text>
				<button class="empty-action-btn" @click="goToAddMeal">
					添加餐品
				</button>
			</view>
			
			<!-- 餐品计数 -->
			<view class="meal-count" v-if="!loading && meals.length > 0">
				找到 {{ meals.length }} 个餐品
			</view>
			
			<!-- 餐品列表项 -->
			<view class="meal-item" 
				v-for="meal in meals" 
				:key="meal.id"
				@click="showMealDetail(meal)"
			>
				<image class="meal-cover" :src="meal.image || '/static/food-decoration.png'" mode="aspectFill"></image>
				<view class="meal-info">
					<view class="meal-header">
						<text class="meal-name">{{ meal.name }}</text>
						<view class="meal-badges">
							<view class="difficulty-badge" :class="meal.difficulty">
								{{ getDifficultyText(meal.difficulty) }}
							</view>
							<view v-if="!meal.is_available" class="unavailable-badge">
								暂不可点
							</view>
						</view>
					</view>
					<text class="meal-desc">{{ meal.description || '暂无描述' }}</text>
					<view class="meal-meta">
						<view class="meta-item">
							<text class="meta-icon">⏱️</text>
							<text class="meta-text">{{ meal.prep_time }}分钟</text>
						</view>
						<view class="meta-item">
							<text class="meta-icon">🔥</text>
							<text class="meta-text">{{ meal.popularity }}人喜欢</text>
						</view>
						<view class="meta-item">
							<text class="meta-icon">📊</text>
							<text class="meta-text">{{ meal.request_count }}次点餐</text>
						</view>
					</view>
					<view class="meal-tags">
						<text class="tag" v-for="tag in meal.tags" :key="tag">{{ tag }}</text>
					</view>
				</view>
				<view class="meal-actions">
					<button 
						class="order-btn" 
						:disabled="!meal.is_available"
						@click.stop="orderMeal(meal)"
					>
						{{ meal.is_available ? '点餐' : '不可点' }}
					</button>
				</view>
			</view>
			
			<!-- 加载更多提示 -->
			<view class="load-more" v-if="hasMore">
				<text class="load-text">{{ loading ? '加载中...' : '上拉加载更多' }}</text>
			</view>
		</scroll-view>
		
		<!-- 底部悬浮按钮 -->
		<view class="fab-group">
			<view class="fab secondary" @click="goToCart" v-if="cartCount > 0">
				<text class="fab-icon">🛒</text>
				<view class="fab-badge">{{ cartCount }}</view>
			</view>
			<view class="fab primary" @click="goToAddMeal">
				<text class="fab-icon">➕</text>
			</view>
		</view>
		
		<!-- 点餐弹窗 -->
		<view class="modal-overlay" v-if="showOrderModal" @click="closeOrderModal">
			<view class="order-modal" @click.stop>
				<view class="modal-header">
					<text class="modal-title">点餐 - {{ selectedMeal?.name }}</text>
					<text class="modal-close" @click="closeOrderModal">✕</text>
				</view>
				<view class="modal-content">
					<view class="form-group">
						<text class="form-label">数量</text>
						<view class="quantity-selector">
							<button class="quantity-btn" @click="decreaseQuantity">-</button>
							<text class="quantity-value">{{ orderQuantity }}</text>
							<button class="quantity-btn" @click="increaseQuantity">+</button>
						</view>
					</view>
					<view class="form-group">
						<text class="form-label">优先级</text>
						<view class="priority-selector">
							<view class="priority-option" 
								v-for="priority in priorityOptions" 
								:key="priority.value"
								:class="{ active: orderPriority === priority.value }"
								@click="selectPriority(priority.value)"
							>
								<text class="priority-text">{{ priority.label }}</text>
							</view>
						</view>
					</view>
					<view class="form-group">
						<text class="form-label">特殊要求</text>
						<textarea 
							class="form-textarea" 
							v-model="specialRequests" 
							placeholder="请输入特殊要求（可选）"
							maxlength="200"
						></textarea>
					</view>
				</view>
				<view class="modal-actions">
					<button class="modal-btn cancel" @click="closeOrderModal">取消</button>
					<button class="modal-btn confirm" @click="confirmOrder">确认点餐</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '../../utils/api.js'
import orderingManager from '../../utils/orderingManager.js'

export default {
	data() {
		return {
			// 分类相关
			categories: [],
			currentCategory: 'all',
			
			// 餐品相关
			meals: [],
			loading: false,
			refreshing: false,
			hasMore: true,
			page: 1,
			searchKeyword: '',
			
			// 统计数据
			pendingCount: 0,
			todayCount: 0,
			familyMemberCount: 0,
			
			// 点餐相关
			showOrderModal: false,
			selectedMeal: null,
			orderQuantity: 1,
			orderPriority: 'normal',
			specialRequests: '',
			cartCount: 0,
			
			// 优先级选项
			priorityOptions: [
				{ value: 'low', label: '不急' },
				{ value: 'normal', label: '一般' },
				{ value: 'high', label: '比较急' },
				{ value: 'urgent', label: '很急' }
			]
		}
	},
	
	onLoad() {
		this.loadCategories();
		this.loadMeals();
		this.loadStats();
	},
	
	methods: {
		// 加载餐品分类
		async loadCategories() {
			try {
				const result = await orderingManager.getCategoriesSimple();
				this.categories = [
					{ id: 'all', name: '全部', meal_count: 0 },
					...result
				];
				
				// 计算全部分类的餐品数量
				this.categories[0].meal_count = result.reduce((sum, cat) => sum + cat.meal_count, 0);
			} catch (error) {
				console.error('加载分类失败:', error);
				uni.showToast({
					title: '加载分类失败',
					icon: 'error'
				});
			}
		},
		
		// 加载餐品列表
		async loadMeals(isRefresh = false) {
			if (this.loading) return;
			
			this.loading = true;
			
			try {
				if (isRefresh) {
					this.page = 1;
					this.meals = [];
				}
				
				const params = {
					page: this.page,
					category: this.currentCategory === 'all' ? '' : this.currentCategory,
					search: this.searchKeyword,
					available_only: 'true'
				};
				
				const result = await orderingManager.getMeals(params);
				const meals = result.results || result || [];
				
				if (isRefresh) {
					this.meals = meals;
				} else {
					this.meals = [...this.meals, ...meals];
				}
				
				this.hasMore = meals.length > 0;
				this.page++;
				
			} catch (error) {
				console.error('加载餐品失败:', error);
				uni.showToast({
					title: '加载失败',
					icon: 'error'
				});
			} finally {
				this.loading = false;
			}
		},
		
		// 加载统计数据
		async loadStats() {
			try {
				const summary = await orderingManager.getRequestsSummary();
				this.pendingCount = summary.pending || 0;
				this.todayCount = summary.total || 0; // 简化处理，实际应该过滤今日数据
				this.familyMemberCount = 2; // 临时数据，实际应该从家庭接口获取
			} catch (error) {
				console.error('加载统计失败:', error);
			}
		},
		
		// 搜索输入
		onSearchInput() {
			clearTimeout(this.searchTimer);
			this.searchTimer = setTimeout(() => {
				this.loadMeals(true);
			}, 500);
		},
		
		// 下拉刷新
		async onRefresh() {
			this.refreshing = true;
			try {
				await Promise.all([
					this.loadCategories(),
					this.loadMeals(true),
					this.loadStats()
				]);
			} finally {
				this.refreshing = false;
			}
		},
		
		// 选择分类
		selectCategory(categoryId) {
			if (this.currentCategory === categoryId) return;
			
			this.currentCategory = categoryId;
			this.loadMeals(true);
		},
		
		// 加载更多
		loadMoreMeals() {
			if (this.hasMore && !this.loading) {
				this.loadMeals();
			}
		},
		
		// 显示餐品详情
		showMealDetail(meal) {
			// 可以跳转到详情页面或显示详情弹窗
			uni.navigateTo({
				url: `/pages/ordering/meal-detail?id=${meal.id}`
			});
		},
		
		// 点餐
		orderMeal(meal) {
			this.selectedMeal = meal;
			this.orderQuantity = 1;
			this.orderPriority = 'normal';
			this.specialRequests = '';
			this.showOrderModal = true;
		},
		
		// 关闭点餐弹窗
		closeOrderModal() {
			this.showOrderModal = false;
			this.selectedMeal = null;
		},
		
		// 数量控制
		decreaseQuantity() {
			if (this.orderQuantity > 1) {
				this.orderQuantity--;
			}
		},
		
		increaseQuantity() {
			this.orderQuantity++;
		},
		
		// 选择优先级
		selectPriority(priority) {
			this.orderPriority = priority;
		},
		
		// 确认点餐
		async confirmOrder() {
			try {
				const orderData = {
					meal_item: this.selectedMeal.id,
					quantity: this.orderQuantity,
					priority: this.orderPriority,
					special_requests: this.specialRequests,
					family_id: 1 // 临时硬编码，实际应该从用户状态获取
				};
				
				await orderingManager.createMealRequest(orderData);
				
				uni.showToast({
					title: '点餐成功',
					icon: 'success'
				});
				
				this.closeOrderModal();
				this.loadStats(); // 刷新统计数据
				
			} catch (error) {
				console.error('点餐失败:', error);
				uni.showToast({
					title: '点餐失败',
					icon: 'error'
				});
			}
		},
		
		// 获取难度文本
		getDifficultyText(difficulty) {
			const map = {
				'easy': '简单',
				'medium': '中等',
				'hard': '困难'
			};
			return map[difficulty] || '未知';
		},
		
		// 页面跳转方法
		goToMyRequests() {
			uni.navigateTo({
				url: '/pages/ordering/my-requests'
			});
		},
		
		goToPendingRequests() {
			uni.navigateTo({
				url: '/pages/ordering/pending-requests'
			});
		},
		
		goToTodayRequests() {
			uni.navigateTo({
				url: '/pages/ordering/today-requests'
			});
		},
		
		goToStats() {
			uni.navigateTo({
				url: '/pages/ordering/stats'
			});
		},
		
		goToCart() {
			uni.navigateTo({
				url: '/pages/ordering/cart'
			});
		},
		
		goToAddMeal() {
			uni.navigateTo({
				url: '/pages/ordering/add-meal'
			});
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #FFF5F8;
	padding-bottom: 120rpx;
}

.page-header {
	background: #FFFFFF;
	padding: 30rpx;
	border-bottom: 1rpx solid #F0F0F0;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.page-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333333;
}

.request-btn {
	background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
	color: white;
	border: none;
	border-radius: 25rpx;
	padding: 16rpx 24rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 107, 0.3);
}

.request-icon {
	margin-right: 8rpx;
	font-size: 20rpx;
}

.request-text {
	font-size: 24rpx;
}

/* 统计卡片 */
.stats-cards {
	padding: 20rpx;
	display: flex;
	gap: 20rpx;
}

.stat-card {
	flex: 1;
	background: white;
	border-radius: 16rpx;
	padding: 24rpx;
	position: relative;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.stat-number {
	font-size: 32rpx;
	font-weight: bold;
	color: #FF6B95;
}

.stat-label {
	font-size: 24rpx;
	color: #666666;
	margin-top: 8rpx;
}

.stat-icon {
	position: absolute;
	top: 20rpx;
	right: 20rpx;
	font-size: 24rpx;
	opacity: 0.6;
}

/* 分类标签栏 */
.category-tabs {
	background: #FFFFFF;
	white-space: nowrap;
	padding: 20rpx 30rpx;
	border-bottom: 1rpx solid #F0F0F0;
}

.category-tab {
	display: inline-block;
	padding: 16rpx 24rpx;
	margin-right: 20rpx;
	background: #F8F8F8;
	border-radius: 20rpx;
	transition: all 0.3s;
}

.category-tab.active {
	background: #FF6B95;
	color: #FFFFFF;
}

.category-icon {
	margin-right: 8rpx;
	font-size: 20rpx;
}

.category-text {
	font-size: 26rpx;
}

.category-count {
	font-size: 20rpx;
	margin-left: 8rpx;
	opacity: 0.7;
}

/* 餐品列表 */
.meal-list {
	flex: 1;
	height: calc(100vh - 300rpx);
	padding: 20rpx 30rpx;
}

.search-bar {
	margin-bottom: 20rpx;
}

.search-input-wrapper {
	position: relative;
	background: #FFFFFF;
	border-radius: 25rpx;
	padding: 20rpx 50rpx 20rpx 30rpx;
	border: 1rpx solid #E0E0E0;
}

.search-input {
	width: 100%;
	font-size: 28rpx;
	color: #333333;
	background-color: transparent;
	border: none;
}

.search-icon {
	position: absolute;
	right: 20rpx;
	top: 50%;
	transform: translateY(-50%);
	font-size: 24rpx;
	color: #999999;
}

.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 100rpx 30rpx;
	text-align: center;
}

.empty-icon {
	font-size: 80rpx;
	margin-bottom: 20rpx;
	opacity: 0.3;
}

.empty-text {
	font-size: 28rpx;
	color: #999999;
	margin-bottom: 40rpx;
}

.empty-action-btn {
	background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
	color: white;
	border: none;
	border-radius: 25rpx;
	padding: 20rpx 40rpx;
	font-size: 28rpx;
}

.meal-count {
	font-size: 24rpx;
	color: #666666;
	margin-bottom: 20rpx;
	text-align: center;
}

/* 餐品项 */
.meal-item {
	background: #FFFFFF;
	border-radius: 20rpx;
	margin-bottom: 20rpx;
	padding: 20rpx;
	display: flex;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.meal-cover {
	width: 120rpx;
	height: 120rpx;
	border-radius: 15rpx;
	margin-right: 20rpx;
}

.meal-info {
	flex: 1;
}

.meal-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 8rpx;
}

.meal-name {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	flex: 1;
	margin-right: 16rpx;
}

.meal-badges {
	display: flex;
	gap: 8rpx;
}

.difficulty-badge {
	background: #4CAF50;
	color: white;
	font-size: 20rpx;
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
}

.difficulty-badge.medium {
	background: #FF9800;
}

.difficulty-badge.hard {
	background: #F44336;
}

.unavailable-badge {
	background: #999999;
	color: white;
	font-size: 20rpx;
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
}

.meal-desc {
	font-size: 24rpx;
	color: #666666;
	margin-bottom: 12rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.meal-meta {
	display: flex;
	margin-bottom: 12rpx;
}

.meta-item {
	display: flex;
	align-items: center;
	margin-right: 20rpx;
}

.meta-icon {
	font-size: 20rpx;
	margin-right: 6rpx;
}

.meta-text {
	font-size: 22rpx;
	color: #999999;
}

.meal-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 8rpx;
}

.tag {
	font-size: 20rpx;
	color: #FF6B95;
	background: rgba(255, 107, 149, 0.1);
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
}

.meal-actions {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 100rpx;
}

.order-btn {
	background: #FF6B95;
	color: white;
	border: none;
	border-radius: 25rpx;
	padding: 16rpx 24rpx;
	font-size: 24rpx;
}

.order-btn:disabled {
	background: #CCCCCC;
	color: #999999;
}

/* 悬浮按钮 */
.fab-group {
	position: fixed;
	bottom: 30rpx;
	right: 30rpx;
	display: flex;
	flex-direction: column;
	gap: 20rpx;
	z-index: 999;
}

.fab {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.2);
	position: relative;
}

.fab.primary {
	background: #FF6B95;
}

.fab.secondary {
	background: #4CAF50;
}

.fab-icon {
	font-size: 48rpx;
	color: #FFFFFF;
	font-weight: bold;
}

.fab-badge {
	position: absolute;
	top: -10rpx;
	right: -10rpx;
	background: #F44336;
	color: white;
	font-size: 20rpx;
	padding: 4rpx 8rpx;
	border-radius: 50%;
	min-width: 32rpx;
	text-align: center;
}

/* 点餐弹窗 */
.modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.order-modal {
	background: white;
	border-radius: 20rpx;
	width: 90%;
	max-width: 600rpx;
	max-height: 80vh;
	overflow: hidden;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #F0F0F0;
}

.modal-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.modal-close {
	font-size: 40rpx;
	color: #999999;
	padding: 10rpx;
}

.modal-content {
	padding: 30rpx;
}

.form-group {
	margin-bottom: 30rpx;
}

.form-label {
	display: block;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 16rpx;
}

.quantity-selector {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.quantity-btn {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
	border: 1rpx solid #E0E0E0;
	background: white;
	font-size: 32rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.quantity-value {
	font-size: 32rpx;
	font-weight: bold;
	min-width: 60rpx;
	text-align: center;
}

.priority-selector {
	display: flex;
	gap: 16rpx;
	flex-wrap: wrap;
}

.priority-option {
	padding: 16rpx 24rpx;
	border: 1rpx solid #E0E0E0;
	border-radius: 20rpx;
	background: white;
	transition: all 0.3s;
}

.priority-option.active {
	background: #FF6B95;
	border-color: #FF6B95;
	color: white;
}

.priority-text {
	font-size: 26rpx;
}

.form-textarea {
	width: 100%;
	min-height: 120rpx;
	padding: 20rpx;
	border: 1rpx solid #E0E0E0;
	border-radius: 12rpx;
	font-size: 26rpx;
	box-sizing: border-box;
}

.modal-actions {
	display: flex;
	gap: 20rpx;
	padding: 30rpx;
	border-top: 1rpx solid #F0F0F0;
}

.modal-btn {
	flex: 1;
	padding: 24rpx;
	border-radius: 12rpx;
	font-size: 28rpx;
	text-align: center;
}

.modal-btn.cancel {
	background: #F8F8F8;
	color: #666666;
	border: 1rpx solid #E0E0E0;
}

.modal-btn.confirm {
	background: #FF6B95;
	color: white;
	border: none;
}

.load-more {
	padding: 40rpx;
	text-align: center;
}

.load-text {
	font-size: 26rpx;
	color: #999999;
}
</style>
