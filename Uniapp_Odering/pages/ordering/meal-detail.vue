<template>
	<view class="container">
		<!-- 餐品图片轮播 -->
		<swiper class="meal-swiper" :indicator-dots="mealImages.length > 1" indicator-color="rgba(255,255,255,0.5)" indicator-active-color="#FF6B95">
			<swiper-item v-for="(image, index) in mealImages" :key="index">
				<image :src="image" mode="aspectFill" class="meal-image" @click="previewImage(image)"></image>
			</swiper-item>
		</swiper>

		<!-- 餐品基本信息 -->
		<view class="meal-info">
			<view class="meal-header">
				<text class="meal-name">{{ mealDetail.name }}</text>
				<view class="meal-actions">
					<button class="action-btn" @click="toggleFavorite">
						<text class="action-icon">{{ isFavorite ? '❤️' : '🤍' }}</text>
					</button>
					<button class="action-btn" v-if="canEdit" @click="editMeal">
						<text class="action-icon">✏️</text>
					</button>
				</view>
			</view>
			
			<view class="meal-meta">
				<text class="meal-category">{{ mealDetail.category_name }}</text>
				<text class="meal-price" v-if="mealDetail.price">¥{{ mealDetail.price }}</text>
			</view>
			
			<text class="meal-description" v-if="mealDetail.description">{{ mealDetail.description }}</text>
			
			<!-- 营养信息 -->
			<view class="nutrition-info" v-if="mealDetail.nutritional_info">
				<text class="info-title">营养信息</text>
				<view class="nutrition-grid">
					<view class="nutrition-item" v-for="(value, key) in nutritionalData" :key="key">
						<text class="nutrition-label">{{ getNutritionLabel(key) }}</text>
						<text class="nutrition-value">{{ value }}</text>
					</view>
				</view>
			</view>
			
			<!-- 标签 -->
			<view class="meal-tags" v-if="mealDetail.tags && mealDetail.tags.length > 0">
				<text class="tag" v-for="tag in mealDetail.tags" :key="tag"># {{ tag }}</text>
			</view>
		</view>

		<!-- 点餐统计 -->
		<view class="order-stats">
			<text class="stats-title">点餐统计</text>
			<view class="stats-grid">
				<view class="stats-item">
					<text class="stats-number">{{ orderStats.total_orders || 0 }}</text>
					<text class="stats-label">总点餐数</text>
				</view>
				<view class="stats-item">
					<text class="stats-number">{{ orderStats.recent_orders || 0 }}</text>
					<text class="stats-label">近7天</text>
				</view>
				<view class="stats-item">
					<text class="stats-number">{{ orderStats.today_orders || 0 }}</text>
					<text class="stats-label">今日</text>
				</view>
				<view class="stats-item">
					<text class="stats-number">{{ Math.round(orderStats.avg_rating * 10) / 10 || 0 }}</text>
					<text class="stats-label">平均评分</text>
				</view>
			</view>
		</view>

		<!-- 最近点餐记录 -->
		<view class="recent-orders">
			<view class="section-header">
				<text class="section-title">最近点餐</text>
				<text class="view-all" @click="viewAllOrders">查看全部</text>
			</view>
			<view class="orders-list">
				<view v-for="order in recentOrders" :key="order.id" class="order-item">
					<image :src="order.member_avatar || '/static/default-avatar.png'" class="member-avatar"></image>
					<view class="order-info">
						<text class="member-name">{{ order.member_name }}</text>
						<text class="order-time">{{ formatTime(order.created_at) }}</text>
					</view>
					<view class="order-details">
						<text class="order-quantity">{{ order.quantity }}份</text>
						<view class="order-status" :class="'status-' + order.status">
							{{ getStatusText(order.status) }}
						</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 评价列表 -->
		<view class="reviews-section" v-if="reviews.length > 0">
			<view class="section-header">
				<text class="section-title">用户评价</text>
				<text class="review-count">({{ reviews.length }}条)</text>
			</view>
			<view class="reviews-list">
				<view v-for="review in reviews" :key="review.id" class="review-item">
					<view class="review-header">
						<image :src="review.member_avatar || '/static/default-avatar.png'" class="member-avatar"></image>
						<view class="review-info">
							<text class="member-name">{{ review.member_name }}</text>
							<view class="review-rating">
								<text v-for="star in 5" :key="star" class="star" :class="{ active: star <= review.rating }">⭐</text>
							</view>
						</view>
						<text class="review-time">{{ formatTime(review.created_at) }}</text>
					</view>
					<text class="review-content" v-if="review.comment">{{ review.comment }}</text>
				</view>
			</view>
		</view>

		<!-- 底部操作栏 -->
		<view class="bottom-actions">
			<view class="quantity-selector">
				<button class="quantity-btn" :disabled="quantity <= 1" @click="decreaseQuantity">-</button>
				<text class="quantity-text">{{ quantity }}</text>
				<button class="quantity-btn" @click="increaseQuantity">+</button>
			</view>
			<button class="order-btn" @click="showOrderModal">立即点餐</button>
		</view>

		<!-- 点餐弹窗 -->
		<uni-popup ref="orderPopup" type="bottom" :mask-click="false">
			<view class="order-modal">
				<view class="modal-header">
					<text class="modal-title">确认点餐</text>
					<text class="modal-close" @click="closeOrderModal">×</text>
				</view>
				
				<view class="order-summary">
					<image :src="mealDetail.image || '/static/dishes/default.jpg'" class="summary-image"></image>
					<view class="summary-info">
						<text class="summary-name">{{ mealDetail.name }}</text>
						<text class="summary-quantity">数量: {{ quantity }}份</text>
					</view>
				</view>
				
				<view class="order-form">
					<view class="form-item">
						<text class="form-label">备注</text>
						<textarea 
							v-model="orderNote" 
							placeholder="请输入特殊要求或备注..."
							class="form-textarea"
							maxlength="200"
						></textarea>
					</view>
				</view>
				
				<view class="modal-actions">
					<button class="cancel-btn" @click="closeOrderModal">取消</button>
					<button class="confirm-btn" @click="confirmOrder" :loading="ordering">确认点餐</button>
				</view>
			</view>
		</uni-popup>
	</view>
</template>

<script>
import orderingManager from '@/utils/orderingManager.js'
import userManager from '@/utils/userManager.js'

export default {
	data() {
		return {
			mealId: null,
			mealDetail: {},
			orderStats: {},
			recentOrders: [],
			reviews: [],
			quantity: 1,
			orderNote: '',
			ordering: false,
			isFavorite: false,
			canEdit: false
		}
	},
	
	computed: {
		mealImages() {
			if (this.mealDetail.images && this.mealDetail.images.length > 0) {
				return this.mealDetail.images
			}
			return [this.mealDetail.image || '/static/dishes/default.jpg']
		},
		
		nutritionalData() {
			if (!this.mealDetail.nutritional_info) return {}
			try {
				return JSON.parse(this.mealDetail.nutritional_info)
			} catch {
				return {}
			}
		}
	},
	
	onLoad(options) {
		if (options.id) {
			this.mealId = options.id
			this.loadMealDetail()
		}
	},
	
	onShow() {
		// 检查用户权限
		this.checkPermissions()
	},
	
	methods: {
		async loadMealDetail() {
			try {
				uni.showLoading({ title: '加载中...' })
				
				await Promise.all([
					this.loadMealInfo(),
					this.loadOrderStats(),
					this.loadRecentOrders(),
					this.loadReviews()
				])
			} catch (error) {
				console.error('加载餐品详情失败:', error)
				uni.showToast({
					title: '加载失败',
					icon: 'none'
				})
			} finally {
				uni.hideLoading()
			}
		},
		
		async loadMealInfo() {
			this.mealDetail = await orderingManager.getMealItem(this.mealId)
		},
		
		async loadOrderStats() {
			this.orderStats = await orderingManager.getMealStats({
				meal_id: this.mealId
			}) || {}
		},
		
		async loadRecentOrders() {
			const response = await orderingManager.getMealRequests({
				meal_id: this.mealId,
				page_size: 5,
				ordering: '-created_at'
			})
			this.recentOrders = response.results || []
		},
		
		async loadReviews() {
			// 如果有评价系统，可以在这里加载
			// this.reviews = await orderingManager.getMealReviews(this.mealId)
			this.reviews = []
		},
		
		async checkPermissions() {
			const currentUser = userManager.getCurrentUser()
			if (currentUser) {
				// 检查是否为管理员
				this.canEdit = currentUser.is_admin || currentUser.role === 'admin'
				
				// 检查是否已收藏
				try {
					// 如果有收藏功能，可以在这里检查
					// this.isFavorite = await orderingManager.checkFavorite(this.mealId)
				} catch (error) {
					console.error('检查收藏状态失败:', error)
				}
			}
		},
		
		previewImage(imageUrl) {
			uni.previewImage({
				urls: this.mealImages,
				current: imageUrl
			})
		},
		
		async toggleFavorite() {
			try {
				if (this.isFavorite) {
					// await orderingManager.removeFavorite(this.mealId)
					this.isFavorite = false
					uni.showToast({
						title: '已取消收藏',
						icon: 'success'
					})
				} else {
					// await orderingManager.addFavorite(this.mealId)
					this.isFavorite = true
					uni.showToast({
						title: '已添加收藏',
						icon: 'success'
					})
				}
			} catch (error) {
				console.error('收藏操作失败:', error)
				uni.showToast({
					title: '操作失败',
					icon: 'none'
				})
			}
		},
		
		editMeal() {
			uni.navigateTo({
				url: `/pages/ordering/add-meal?id=${this.mealId}`
			})
		},
		
		decreaseQuantity() {
			if (this.quantity > 1) {
				this.quantity--
			}
		},
		
		increaseQuantity() {
			this.quantity++
		},
		
		showOrderModal() {
			this.$refs.orderPopup.open()
		},
		
		closeOrderModal() {
			this.$refs.orderPopup.close()
			this.orderNote = ''
		},
		
		async confirmOrder() {
			try {
				this.ordering = true
				
				const orderData = {
					meal_id: this.mealId,
					quantity: this.quantity,
					note: this.orderNote
				}
				
				await orderingManager.createMealRequest(orderData)
				
				uni.showToast({
					title: '点餐成功',
					icon: 'success'
				})
				
				this.closeOrderModal()
				this.quantity = 1
				
				// 刷新数据
				this.loadOrderStats()
				this.loadRecentOrders()
			} catch (error) {
				console.error('点餐失败:', error)
				uni.showToast({
					title: '点餐失败',
					icon: 'none'
				})
			} finally {
				this.ordering = false
			}
		},
		
		viewAllOrders() {
			uni.navigateTo({
				url: `/pages/ordering/meal-orders?meal_id=${this.mealId}`
			})
		},
		
		getNutritionLabel(key) {
			const labels = {
				calories: '热量',
				protein: '蛋白质',
				carbs: '碳水化合物',
				fat: '脂肪',
				fiber: '纤维',
				sodium: '钠'
			}
			return labels[key] || key
		},
		
		getStatusText(status) {
			const statusMap = {
				'pending': '待确认',
				'confirmed': '已确认',
				'rejected': '已拒绝'
			}
			return statusMap[status] || status
		},
		
		formatTime(timeStr) {
			const time = new Date(timeStr)
			const now = new Date()
			const diff = now - time
			
			if (diff < 86400000) { // 24小时内
				return time.toLocaleTimeString('zh-CN', { 
					hour: '2-digit', 
					minute: '2-digit' 
				})
			} else {
				return time.toLocaleDateString('zh-CN')
			}
		}
	}
}
</script>

<style scoped>
.container {
	background-color: #f5f5f5;
	min-height: 100vh;
	padding-bottom: 120rpx;
}

/* 餐品图片轮播 */
.meal-swiper {
	height: 500rpx;
}

.meal-image {
	width: 100%;
	height: 100%;
}

/* 餐品信息 */
.meal-info {
	background: white;
	padding: 30rpx;
	margin-bottom: 20rpx;
}

.meal-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 20rpx;
}

.meal-name {
	font-size: 40rpx;
	font-weight: bold;
	color: #333;
	flex: 1;
	margin-right: 20rpx;
}

.meal-actions {
	display: flex;
	gap: 20rpx;
}

.action-btn {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
	border: 2rpx solid #eee;
	background: white;
	display: flex;
	align-items: center;
	justify-content: center;
}

.action-icon {
	font-size: 32rpx;
}

.meal-meta {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.meal-category {
	font-size: 28rpx;
	color: #666;
	padding: 10rpx 20rpx;
	background: #f0f0f0;
	border-radius: 20rpx;
}

.meal-price {
	font-size: 36rpx;
	font-weight: bold;
	color: #FF6B95;
}

.meal-description {
	font-size: 28rpx;
	color: #666;
	line-height: 1.6;
	margin-bottom: 20rpx;
}

/* 营养信息 */
.nutrition-info {
	margin-bottom: 30rpx;
}

.info-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
}

.nutrition-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20rpx;
}

.nutrition-item {
	text-align: center;
	padding: 20rpx;
	background: #f8f8f8;
	border-radius: 10rpx;
}

.nutrition-label {
	display: block;
	font-size: 24rpx;
	color: #666;
	margin-bottom: 5rpx;
}

.nutrition-value {
	display: block;
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
}

/* 标签 */
.meal-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
}

.tag {
	font-size: 24rpx;
	color: #FF6B95;
	background: #fff5f8;
	padding: 10rpx 20rpx;
	border-radius: 20rpx;
}

/* 点餐统计 */
.order-stats {
	background: white;
	padding: 30rpx;
	margin-bottom: 20rpx;
}

.stats-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
}

.stats-grid {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 20rpx;
}

.stats-item {
	text-align: center;
}

.stats-number {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	color: #FF6B95;
	margin-bottom: 10rpx;
}

.stats-label {
	font-size: 24rpx;
	color: #666;
}

/* 最近点餐 */
.recent-orders {
	background: white;
	padding: 30rpx;
	margin-bottom: 20rpx;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.view-all {
	font-size: 28rpx;
	color: #FF6B95;
}

.orders-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.order-item {
	display: flex;
	align-items: center;
	gap: 20rpx;
	padding: 20rpx;
	background: #f8f8f8;
	border-radius: 15rpx;
}

.member-avatar {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
}

.order-info {
	flex: 1;
}

.member-name {
	display: block;
	font-size: 28rpx;
	color: #333;
	font-weight: bold;
	margin-bottom: 5rpx;
}

.order-time {
	font-size: 24rpx;
	color: #999;
}

.order-details {
	text-align: right;
}

.order-quantity {
	display: block;
	font-size: 28rpx;
	color: #333;
	margin-bottom: 10rpx;
}

.order-status {
	font-size: 20rpx;
	padding: 5rpx 15rpx;
	border-radius: 15rpx;
	color: white;
}

.order-status.status-pending {
	background: #FF9800;
}

.order-status.status-confirmed {
	background: #4CAF50;
}

.order-status.status-rejected {
	background: #f44336;
}

/* 评价列表 */
.reviews-section {
	background: white;
	padding: 30rpx;
	margin-bottom: 20rpx;
}

.review-count {
	font-size: 24rpx;
	color: #999;
	margin-left: 10rpx;
}

.reviews-list {
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}

.review-item {
	border-bottom: 1rpx solid #f0f0f0;
	padding-bottom: 20rpx;
}

.review-header {
	display: flex;
	align-items: center;
	gap: 20rpx;
	margin-bottom: 15rpx;
}

.review-info {
	flex: 1;
}

.review-rating {
	margin-top: 5rpx;
}

.star {
	font-size: 24rpx;
	color: #ddd;
}

.star.active {
	color: #FFD700;
}

.review-time {
	font-size: 24rpx;
	color: #999;
}

.review-content {
	font-size: 28rpx;
	color: #666;
	line-height: 1.5;
}

/* 底部操作栏 */
.bottom-actions {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background: white;
	padding: 20rpx 30rpx;
	border-top: 1rpx solid #eee;
	display: flex;
	align-items: center;
	gap: 30rpx;
	box-shadow: 0 -2rpx 20rpx rgba(0,0,0,0.1);
}

.quantity-selector {
	display: flex;
	align-items: center;
	gap: 20rpx;
	border: 2rpx solid #eee;
	border-radius: 40rpx;
	padding: 10rpx;
}

.quantity-btn {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
	border: none;
	background: #f5f5f5;
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.quantity-btn:disabled {
	background: #f0f0f0;
	color: #ccc;
}

.quantity-text {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	min-width: 60rpx;
	text-align: center;
}

.order-btn {
	flex: 1;
	background: linear-gradient(45deg, #FF6B95, #FF8C94);
	color: white;
	border-radius: 40rpx;
	padding: 25rpx;
	border: none;
	font-size: 32rpx;
	font-weight: bold;
}

/* 点餐弹窗 */
.order-modal {
	background: white;
	border-radius: 30rpx 30rpx 0 0;
	padding: 40rpx;
	max-height: 80vh;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
}

.modal-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
}

.modal-close {
	font-size: 40rpx;
	color: #999;
	width: 60rpx;
	height: 60rpx;
	text-align: center;
	line-height: 60rpx;
}

.order-summary {
	display: flex;
	align-items: center;
	gap: 30rpx;
	padding: 30rpx;
	background: #f8f8f8;
	border-radius: 20rpx;
	margin-bottom: 30rpx;
}

.summary-image {
	width: 100rpx;
	height: 100rpx;
	border-radius: 15rpx;
}

.summary-info {
	flex: 1;
}

.summary-name {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 10rpx;
}

.summary-quantity {
	font-size: 28rpx;
	color: #FF6B95;
}

.order-form {
	margin-bottom: 40rpx;
}

.form-item {
	margin-bottom: 30rpx;
}

.form-label {
	display: block;
	font-size: 28rpx;
	color: #333;
	margin-bottom: 15rpx;
}

.form-textarea {
	width: 100%;
	min-height: 150rpx;
	padding: 20rpx;
	border: 2rpx solid #eee;
	border-radius: 15rpx;
	font-size: 28rpx;
	background: #f8f8f8;
}

.modal-actions {
	display: flex;
	gap: 30rpx;
}

.cancel-btn, .confirm-btn {
	flex: 1;
	padding: 25rpx;
	border-radius: 40rpx;
	border: none;
	font-size: 32rpx;
	font-weight: bold;
}

.cancel-btn {
	background: #f5f5f5;
	color: #666;
}

.confirm-btn {
	background: linear-gradient(45deg, #FF6B95, #FF8C94);
	color: white;
}
</style>
