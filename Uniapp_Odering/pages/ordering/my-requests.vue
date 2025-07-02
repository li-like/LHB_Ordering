<template>
	<view class="container">
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">我的点餐</text>
			<view class="header-actions">
				<button class="filter-btn" @click="showFilterOptions">
					<text class="filter-icon">🔍</text>
					<text class="filter-text">筛选</text>
				</button>
			</view>
		</view>
		
		<!-- 快捷筛选标签 -->
		<scroll-view class="filter-tabs" scroll-x="true" show-scrollbar="false">
			<view class="filter-tab" 
				v-for="(filter, index) in filterOptions" 
				:key="index"
				:class="{ active: currentFilter === filter.value }"
				@click="selectFilter(filter.value)"
			>
				<text class="filter-icon">{{ filter.icon }}</text>
				<text class="filter-text">{{ filter.label }}</text>
				<text class="filter-count" v-if="filter.count > 0">({{ filter.count }})</text>
			</view>
		</scroll-view>
		
		<!-- 统计卡片 -->
		<view class="stats-summary">
			<view class="summary-item">
				<text class="summary-number">{{ totalRequests }}</text>
				<text class="summary-label">总点餐数</text>
			</view>
			<view class="summary-item">
				<text class="summary-number">{{ confirmedRequests }}</text>
				<text class="summary-label">已确认</text>
			</view>
			<view class="summary-item">
				<text class="summary-number">{{ rejectedRequests }}</text>
				<text class="summary-label">已拒绝</text>
			</view>
		</view>
		
		<!-- 点餐请求列表 -->
		<scroll-view 
			class="request-list" 
			scroll-y="true" 
			@scrolltolower="loadMoreRequests"
			refresher-enabled="true"
			:refresher-triggered="refreshing"
			@refresherrefresh="onRefresh"
		>
			<!-- 空数据提示 -->
			<view v-if="!loading && requests.length === 0" class="empty-state">
				<text class="empty-icon">📋</text>
				<text class="empty-text">暂无点餐记录</text>
				<button class="empty-action-btn" @click="goToOrdering">
					去点餐
				</button>
			</view>
			
			<!-- 请求列表项 -->
			<view class="request-item" 
				v-for="request in requests" 
				:key="request.id"
				@click="showRequestDetail(request)"
			>
				<view class="request-header">
					<view class="meal-info">
						<image class="meal-cover" :src="request.meal_item?.image || '/static/food-decoration.png'" mode="aspectFill"></image>
						<view class="meal-details">
							<text class="meal-name">{{ request.meal_item?.name || '未知餐品' }}</text>
							<text class="meal-category">{{ request.meal_item?.category?.name || '未分类' }}</text>
							<text class="request-time">{{ formatTime(request.created_at) }}</text>
						</view>
					</view>
					<view class="request-status">
						<view class="status-badge" :class="request.status">
							{{ getStatusText(request.status) }}
						</view>
						<text class="status-time" v-if="request.processed_at">
							{{ formatTime(request.processed_at) }}
						</text>
					</view>
				</view>
				
				<view class="request-content">
					<text class="request-note" v-if="request.notes">
						备注：{{ request.notes }}
					</text>
					<view class="request-meta">
						<view class="meta-item">
							<text class="meta-icon">⏱️</text>
							<text class="meta-text">预计{{ request.meal_item?.prep_time || 0 }}分钟</text>
						</view>
						<view class="meta-item" v-if="request.preferred_meal_time">
							<text class="meta-icon">🕐</text>
							<text class="meta-text">期望{{ request.preferred_meal_time }}</text>
						</view>
						<view class="meta-item" v-if="request.urgency > 1">
							<text class="meta-icon">🔥</text>
							<text class="meta-text">{{ getUrgencyText(request.urgency) }}</text>
						</view>
					</view>
				</view>
				
				<!-- 处理结果 -->
				<view class="request-result" v-if="request.status !== 'pending'">
					<view class="result-info" v-if="request.admin_notes">
						<text class="result-icon">💬</text>
						<text class="result-text">{{ request.admin_notes }}</text>
					</view>
					<view class="result-info" v-if="request.estimated_ready_time">
						<text class="result-icon">🕐</text>
						<text class="result-text">预计{{ request.estimated_ready_time }}完成</text>
					</view>
				</view>
				
				<!-- 操作按钮 -->
				<view class="request-actions" v-if="request.status === 'pending'">
					<button class="action-btn secondary" @click.stop="editRequest(request)">
						修改
					</button>
					<button class="action-btn danger" @click.stop="cancelRequest(request)">
						取消
					</button>
				</view>
				
				<!-- 评价按钮 -->
				<view class="request-actions" v-if="request.status === 'confirmed' && !request.is_rated">
					<button class="action-btn primary" @click.stop="rateRequest(request)">
						评价
					</button>
				</view>
			</view>
			
			<!-- 加载更多提示 -->
			<view class="load-more" v-if="hasMore">
				<text class="load-text">{{ loading ? '加载中...' : '上拉加载更多' }}</text>
			</view>
		</scroll-view>
		
		<!-- 筛选弹窗 -->
		<view class="filter-popup" v-if="showFilter" @click="hideFilterOptions">
			<view class="filter-content" @click.stop>
				<view class="filter-header">
					<text class="filter-title">筛选条件</text>
					<button class="close-btn" @click="hideFilterOptions">✕</button>
				</view>
				<view class="filter-body">
					<view class="filter-group">
						<text class="group-title">请求状态</text>
						<view class="option-list">
							<view class="option-item" 
								v-for="status in statusOptions" 
								:key="status.value"
								:class="{ selected: selectedStatus === status.value }"
								@click="selectStatus(status.value)"
							>
								<text class="option-text">{{ status.label }}</text>
								<text class="option-icon" v-if="selectedStatus === status.value">✓</text>
							</view>
						</view>
					</view>
					<view class="filter-group">
						<text class="group-title">时间范围</text>
						<view class="option-list">
							<view class="option-item" 
								v-for="period in timeOptions" 
								:key="period.value"
								:class="{ selected: selectedPeriod === period.value }"
								@click="selectPeriod(period.value)"
							>
								<text class="option-text">{{ period.label }}</text>
								<text class="option-icon" v-if="selectedPeriod === period.value">✓</text>
							</view>
						</view>
					</view>
				</view>
				<view class="filter-footer">
					<button class="filter-action-btn secondary" @click="resetFilter">
						重置
					</button>
					<button class="filter-action-btn primary" @click="applyFilter">
						应用
					</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import orderingManager from '@/utils/orderingManager.js'

export default {
	name: 'MyRequests',
	data() {
		return {
			// 筛选相关
			currentFilter: 'all',
			filterOptions: [
				{ value: 'all', label: '全部', icon: '📋', count: 0 },
				{ value: 'pending', label: '待处理', icon: '⏳', count: 0 },
				{ value: 'confirmed', label: '已确认', icon: '✅', count: 0 },
				{ value: 'rejected', label: '已拒绝', icon: '❌', count: 0 },
				{ value: 'today', label: '今日', icon: '📅', count: 0 }
			],
			
			// 弹窗筛选
			showFilter: false,
			selectedStatus: '',
			selectedPeriod: '',
			statusOptions: [
				{ value: '', label: '全部状态' },
				{ value: 'pending', label: '待处理' },
				{ value: 'confirmed', label: '已确认' },
				{ value: 'rejected', label: '已拒绝' }
			],
			timeOptions: [
				{ value: '', label: '全部时间' },
				{ value: 'today', label: '今天' },
				{ value: 'week', label: '本周' },
				{ value: 'month', label: '本月' }
			],
			
			// 数据相关
			requests: [],
			totalRequests: 0,
			confirmedRequests: 0,
			rejectedRequests: 0,
			
			// 分页相关
			page: 1,
			hasMore: true,
			loading: false,
			refreshing: false,
		}
	},
	
	onLoad() {
		this.loadRequests()
		this.loadStats()
	},
	
	methods: {
		// 加载我的点餐请求
		async loadRequests(reset = false) {
			if (this.loading) return
			
			this.loading = true
			
			try {
				if (reset) {
					this.page = 1
					this.hasMore = true
					this.requests = []
				}
				
				const params = {
					page: this.page,
					status: this.currentFilter === 'all' ? '' : this.currentFilter,
					...(this.selectedStatus && { status: this.selectedStatus }),
					...(this.selectedPeriod && { period: this.selectedPeriod })
				}
				
				const response = await orderingManager.getMyMealRequests(params)
				
				if (response.success) {
					const newRequests = response.data.results || []
					
					if (reset) {
						this.requests = newRequests
					} else {
						this.requests = [...this.requests, ...newRequests]
					}
					
					this.hasMore = response.data.has_next || false
					this.page++
					
					// 更新筛选标签计数
					this.updateFilterCounts()
				} else {
					uni.showToast({
						title: response.message || '加载失败',
						icon: 'error'
					})
				}
			} catch (error) {
				console.error('加载点餐请求失败:', error)
				uni.showToast({
					title: '网络错误',
					icon: 'error'
				})
			} finally {
				this.loading = false
				this.refreshing = false
			}
		},
		
		// 加载统计信息
		async loadStats() {
			try {
				const response = await orderingManager.getMyRequestStats()
				if (response.success) {
					const stats = response.data
					this.totalRequests = stats.total || 0
					this.confirmedRequests = stats.confirmed || 0
					this.rejectedRequests = stats.rejected || 0
				}
			} catch (error) {
				console.error('加载统计信息失败:', error)
			}
		},
		
		// 更新筛选标签计数
		updateFilterCounts() {
			const counts = {
				all: this.requests.length,
				pending: 0,
				confirmed: 0,
				rejected: 0,
				today: 0
			}
			
			const today = new Date().toDateString()
			
			this.requests.forEach(request => {
				counts[request.status]++
				if (new Date(request.created_at).toDateString() === today) {
					counts.today++
				}
			})
			
			this.filterOptions.forEach(option => {
				option.count = counts[option.value] || 0
			})
		},
		
		// 筛选操作
		selectFilter(filterValue) {
			this.currentFilter = filterValue
			this.loadRequests(true)
		},
		
		showFilterOptions() {
			this.showFilter = true
		},
		
		hideFilterOptions() {
			this.showFilter = false
		},
		
		selectStatus(status) {
			this.selectedStatus = status
		},
		
		selectPeriod(period) {
			this.selectedPeriod = period
		},
		
		resetFilter() {
			this.selectedStatus = ''
			this.selectedPeriod = ''
		},
		
		applyFilter() {
			this.hideFilterOptions()
			this.loadRequests(true)
		},
		
		// 刷新
		onRefresh() {
			this.refreshing = true
			this.loadRequests(true)
			this.loadStats()
		},
		
		// 加载更多
		loadMoreRequests() {
			if (this.hasMore && !this.loading) {
				this.loadRequests()
			}
		},
		
		// 点餐请求操作
		showRequestDetail(request) {
			uni.navigateTo({
				url: `/pages/ordering/request-detail?id=${request.id}`
			})
		},
		
		async editRequest(request) {
			uni.navigateTo({
				url: `/pages/ordering/edit-request?id=${request.id}`
			})
		},
		
		async cancelRequest(request) {
			uni.showModal({
				title: '确认取消',
				content: `确定要取消"${request.meal_item?.name}"的点餐请求吗？`,
				success: async (res) => {
					if (res.confirm) {
						try {
							const response = await orderingManager.cancelMealRequest(request.id)
							if (response.success) {
								uni.showToast({
									title: '取消成功',
									icon: 'success'
								})
								this.loadRequests(true)
								this.loadStats()
							} else {
								uni.showToast({
									title: response.message || '取消失败',
									icon: 'error'
								})
							}
						} catch (error) {
							console.error('取消点餐请求失败:', error)
							uni.showToast({
								title: '网络错误',
								icon: 'error'
							})
						}
					}
				}
			})
		},
		
		async rateRequest(request) {
			uni.navigateTo({
				url: `/pages/ordering/rate-request?id=${request.id}`
			})
		},
		
		// 页面跳转
		goToOrdering() {
			uni.switchTab({
				url: '/pages/ordering/index'
			})
		},
		
		// 辅助方法
		formatTime(timeString) {
			if (!timeString) return ''
			const date = new Date(timeString)
			const now = new Date()
			const diffMs = now - date
			const diffMinutes = Math.floor(diffMs / 60000)
			const diffHours = Math.floor(diffMinutes / 60)
			const diffDays = Math.floor(diffHours / 24)
			
			if (diffMinutes < 1) return '刚刚'
			if (diffMinutes < 60) return `${diffMinutes}分钟前`
			if (diffHours < 24) return `${diffHours}小时前`
			if (diffDays < 7) return `${diffDays}天前`
			
			return date.toLocaleDateString()
		},
		
		getStatusText(status) {
			const statusMap = {
				'pending': '待处理',
				'confirmed': '已确认',
				'rejected': '已拒绝',
				'cancelled': '已取消'
			}
			return statusMap[status] || status
		},
		
		getUrgencyText(urgency) {
			const urgencyMap = {
				1: '普通',
				2: '较急',
				3: '紧急',
				4: '非常紧急'
			}
			return urgencyMap[urgency] || '普通'
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background-color: #f5f5f5;
}

/* 页面标题 */
.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 30rpx;
	background-color: #fff;
	border-bottom: 1rpx solid #eee;
}

.page-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
}

.header-actions {
	display: flex;
	align-items: center;
}

.filter-btn {
	display: flex;
	align-items: center;
	padding: 12rpx 20rpx;
	background-color: #f8f9fa;
	border-radius: 25rpx;
	border: none;
	font-size: 24rpx;
}

.filter-icon {
	margin-right: 8rpx;
}

/* 筛选标签 */
.filter-tabs {
	background-color: #fff;
	padding: 20rpx 30rpx;
	white-space: nowrap;
	border-bottom: 1rpx solid #eee;
}

.filter-tab {
	display: inline-flex;
	align-items: center;
	padding: 12rpx 20rpx;
	margin-right: 20rpx;
	background-color: #f8f9fa;
	border-radius: 25rpx;
	border: 1rpx solid #e9ecef;
	transition: all 0.3s;
}

.filter-tab.active {
	background-color: #007bff;
	color: #fff;
	border-color: #007bff;
}

.filter-icon {
	margin-right: 8rpx;
	font-size: 24rpx;
}

.filter-text {
	font-size: 24rpx;
}

.filter-count {
	margin-left: 8rpx;
	font-size: 20rpx;
	opacity: 0.7;
}

/* 统计卡片 */
.stats-summary {
	display: flex;
	padding: 30rpx;
	background-color: #fff;
	margin-bottom: 20rpx;
}

.summary-item {
	flex: 1;
	text-align: center;
}

.summary-number {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #007bff;
	margin-bottom: 8rpx;
}

.summary-label {
	font-size: 24rpx;
	color: #666;
}

/* 请求列表 */
.request-list {
	height: calc(100vh - 400rpx);
	padding: 0 30rpx;
}

.empty-state {
	text-align: center;
	padding: 100rpx 0;
}

.empty-icon {
	font-size: 80rpx;
	display: block;
	margin-bottom: 20rpx;
}

.empty-text {
	font-size: 28rpx;
	color: #999;
	margin-bottom: 30rpx;
	display: block;
}

.empty-action-btn {
	padding: 20rpx 40rpx;
	background-color: #007bff;
	color: #fff;
	border-radius: 25rpx;
	border: none;
}

/* 请求项 */
.request-item {
	background-color: #fff;
	border-radius: 15rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
}

.request-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 20rpx;
}

.meal-info {
	display: flex;
	flex: 1;
	align-items: center;
}

.meal-cover {
	width: 80rpx;
	height: 80rpx;
	border-radius: 12rpx;
	margin-right: 20rpx;
}

.meal-details {
	flex: 1;
}

.meal-name {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	display: block;
	margin-bottom: 8rpx;
}

.meal-category {
	font-size: 22rpx;
	color: #666;
	display: block;
	margin-bottom: 8rpx;
}

.request-time {
	font-size: 22rpx;
	color: #999;
	display: block;
}

.request-status {
	text-align: right;
}

.status-badge {
	padding: 8rpx 16rpx;
	border-radius: 20rpx;
	font-size: 22rpx;
	color: #fff;
	margin-bottom: 8rpx;
	display: inline-block;
}

.status-badge.pending {
	background-color: #ffc107;
}

.status-badge.confirmed {
	background-color: #28a745;
}

.status-badge.rejected {
	background-color: #dc3545;
}

.status-badge.cancelled {
	background-color: #6c757d;
}

.status-time {
	font-size: 20rpx;
	color: #999;
	display: block;
}

/* 请求内容 */
.request-content {
	margin-bottom: 20rpx;
}

.request-note {
	font-size: 24rpx;
	color: #666;
	line-height: 1.6;
	margin-bottom: 15rpx;
	display: block;
}

.request-meta {
	display: flex;
	gap: 20rpx;
}

.meta-item {
	display: flex;
	align-items: center;
}

.meta-icon {
	margin-right: 8rpx;
	font-size: 24rpx;
}

.meta-text {
	font-size: 22rpx;
	color: #666;
}

/* 处理结果 */
.request-result {
	background-color: #f8f9fa;
	padding: 20rpx;
	border-radius: 12rpx;
	margin-bottom: 20rpx;
}

.result-info {
	display: flex;
	align-items: center;
	margin-bottom: 10rpx;
}

.result-info:last-child {
	margin-bottom: 0;
}

.result-icon {
	margin-right: 10rpx;
	font-size: 24rpx;
}

.result-text {
	font-size: 24rpx;
	color: #555;
}

/* 操作按钮 */
.request-actions {
	display: flex;
	gap: 20rpx;
}

.action-btn {
	flex: 1;
	padding: 16rpx 0;
	border-radius: 8rpx;
	border: none;
	font-size: 24rpx;
	text-align: center;
}

.action-btn.secondary {
	background-color: #6c757d;
	color: #fff;
}

.action-btn.danger {
	background-color: #dc3545;
	color: #fff;
}

.action-btn.primary {
	background-color: #007bff;
	color: #fff;
}

/* 筛选弹窗 */
.filter-popup {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0,0,0,0.5);
	z-index: 1000;
	display: flex;
	align-items: center;
	justify-content: center;
}

.filter-content {
	background-color: #fff;
	border-radius: 15rpx;
	width: 80%;
	max-height: 70%;
	overflow: hidden;
}

.filter-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #eee;
}

.filter-title {
	font-size: 32rpx;
	font-weight: bold;
}

.close-btn {
	background: none;
	border: none;
	font-size: 28rpx;
	color: #999;
}

.filter-body {
	padding: 30rpx;
	max-height: 400rpx;
	overflow-y: auto;
}

.filter-group {
	margin-bottom: 40rpx;
}

.group-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
}

.option-list {
	border-top: 1rpx solid #f0f0f0;
}

.option-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #f0f0f0;
}

.option-item.selected {
	color: #007bff;
}

.option-text {
	font-size: 26rpx;
}

.option-icon {
	font-size: 24rpx;
	color: #007bff;
}

.filter-footer {
	display: flex;
	padding: 30rpx;
	border-top: 1rpx solid #eee;
	gap: 20rpx;
}

.filter-action-btn {
	flex: 1;
	padding: 20rpx 0;
	border-radius: 8rpx;
	border: none;
	font-size: 26rpx;
}

.filter-action-btn.secondary {
	background-color: #f8f9fa;
	color: #6c757d;
}

.filter-action-btn.primary {
	background-color: #007bff;
	color: #fff;
}

/* 加载更多 */
.load-more {
	text-align: center;
	padding: 30rpx 0;
}

.load-text {
	color: #999;
	font-size: 24rpx;
}
</style>
