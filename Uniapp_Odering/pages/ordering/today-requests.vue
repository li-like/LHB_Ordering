<template>
	<view class="container">
		<!-- 日期选择器 -->
		<view class="date-picker">
			<picker mode="date" :value="selectedDate" @change="onDateChange">
				<view class="date-display">
					<text class="date-text">{{ formatDate(selectedDate) }}</text>
					<text class="date-icon">📅</text>
				</view>
			</picker>
		</view>

		<!-- 今日统计概览 -->
		<view class="stats-overview">
			<view class="stats-card">
				<text class="stats-number">{{ todayStats.total_requests || 0 }}</text>
				<text class="stats-label">总点餐数</text>
			</view>
			<view class="stats-card">
				<text class="stats-number">{{ todayStats.confirmed_requests || 0 }}</text>
				<text class="stats-label">已确认</text>
			</view>
			<view class="stats-card">
				<text class="stats-number">{{ todayStats.pending_requests || 0 }}</text>
				<text class="stats-label">待确认</text>
			</view>
			<view class="stats-card">
				<text class="stats-number">{{ todayStats.unique_members || 0 }}</text>
				<text class="stats-label">参与人数</text>
			</view>
		</view>

		<!-- 状态筛选标签 -->
		<view class="status-tabs">
			<view 
				v-for="tab in statusTabs" 
				:key="tab.value"
				class="status-tab"
				:class="{ active: currentStatus === tab.value }"
				@click="changeStatus(tab.value)"
			>
				{{ tab.label }}
				<text class="tab-count" v-if="tab.count > 0">({{ tab.count }})</text>
			</view>
		</view>

		<!-- 按餐品分组的汇总 -->
		<view class="meal-summary" v-if="currentStatus === 'all'">
			<view class="section-title">餐品汇总</view>
			<view class="meal-group" v-for="group in mealGroups" :key="group.meal_id">
				<view class="meal-header" @click="toggleMealGroup(group.meal_id)">
					<view class="meal-info">
						<image :src="group.meal_image || '/static/dishes/default.jpg'" class="meal-image"></image>
						<view class="meal-details">
							<text class="meal-name">{{ group.meal_name }}</text>
							<text class="meal-category">{{ group.meal_category }}</text>
						</view>
					</view>
					<view class="meal-stats">
						<text class="total-quantity">共{{ group.total_quantity }}份</text>
						<text class="request-count">{{ group.requests.length }}人点餐</text>
						<text class="expand-icon" :class="{ expanded: expandedGroups.includes(group.meal_id) }">▼</text>
					</view>
				</view>
				
				<!-- 展开的成员列表 -->
				<view class="member-list" v-if="expandedGroups.includes(group.meal_id)">
					<view 
						v-for="request in group.requests" 
						:key="request.id"
						class="member-item"
						:class="'status-' + request.status"
					>
						<image :src="request.member_avatar || '/static/default-avatar.png'" class="member-avatar"></image>
						<view class="member-info">
							<text class="member-name">{{ request.member_name }}</text>
							<text class="member-quantity">{{ request.quantity }}份</text>
						</view>
						<view class="status-badge" :class="'status-' + request.status">
							{{ getStatusText(request.status) }}
						</view>
						<text class="request-time">{{ formatTime(request.created_at) }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 按时间排序的详细列表 -->
		<view class="requests-timeline" v-else>
			<view class="section-title">详细列表</view>
			<view 
				v-for="request in filteredRequests" 
				:key="request.id"
				class="timeline-item"
				:class="'status-' + request.status"
			>
				<view class="timeline-time">{{ formatTime(request.created_at) }}</view>
				<view class="timeline-content">
					<view class="member-info">
						<image :src="request.member_avatar || '/static/default-avatar.png'" class="member-avatar"></image>
						<text class="member-name">{{ request.member_name }}</text>
					</view>
					<view class="meal-info">
						<text class="meal-name">{{ request.meal_name }}</text>
						<text class="meal-quantity">× {{ request.quantity }}</text>
					</view>
					<view class="status-info">
						<view class="status-badge" :class="'status-' + request.status">
							{{ getStatusText(request.status) }}
						</view>
						<text class="admin-note" v-if="request.admin_note">{{ request.admin_note }}</text>
					</view>
					<view class="request-note" v-if="request.note">
						<text class="note-label">备注:</text>
						<text class="note-content">{{ request.note }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 导出功能 -->
		<view class="export-section">
			<button class="export-btn" @click="exportData">
				导出今日数据
			</button>
		</view>

		<!-- 加载中 -->
		<view class="loading" v-if="loading">
			<text>加载中...</text>
		</view>

		<!-- 空状态 -->
		<view class="empty-state" v-if="!loading && filteredRequests.length === 0">
			<image src="/static/empty-state.png" class="empty-image"></image>
			<text class="empty-text">{{ selectedDate }}暂无点餐记录</text>
		</view>
	</view>
</template>

<script>
import orderingManager from '@/utils/orderingManager.js'

export default {
	data() {
		return {
			selectedDate: this.getTodayDate(),
			todayRequests: [],
			todayStats: {},
			mealGroups: [],
			expandedGroups: [],
			currentStatus: 'all',
			loading: false,
			statusTabs: [
				{ label: '全部', value: 'all', count: 0 },
				{ label: '已确认', value: 'confirmed', count: 0 },
				{ label: '待确认', value: 'pending', count: 0 },
				{ label: '已拒绝', value: 'rejected', count: 0 }
			]
		}
	},
	
	computed: {
		filteredRequests() {
			if (this.currentStatus === 'all') {
				return this.todayRequests
			}
			return this.todayRequests.filter(request => request.status === this.currentStatus)
		}
	},
	
	onLoad() {
		this.loadTodayData()
	},
	
	onPullDownRefresh() {
		this.loadTodayData().then(() => {
			uni.stopPullDownRefresh()
		})
	},
	
	methods: {
		getTodayDate() {
			return new Date().toISOString().split('T')[0]
		},
		
		async loadTodayData() {
			try {
				this.loading = true
				await Promise.all([
					this.loadTodayRequests(),
					this.loadTodayStats()
				])
				this.processMealGroups()
				this.updateStatusCounts()
			} catch (error) {
				console.error('加载今日数据失败:', error)
				uni.showToast({
					title: '加载失败',
					icon: 'none'
				})
			} finally {
				this.loading = false
			}
		},
		
		async loadTodayRequests() {
			const params = {
				date: this.selectedDate,
				page_size: 100  // 获取当日所有数据
			}
			const response = await orderingManager.getMealRequests(params)
			this.todayRequests = response.results || []
		},
		
		async loadTodayStats() {
			this.todayStats = await orderingManager.getMealStats({
				date: this.selectedDate
			})
		},
		
		processMealGroups() {
			const groups = {}
			
			this.todayRequests.forEach(request => {
				const mealId = request.meal_id
				if (!groups[mealId]) {
					groups[mealId] = {
						meal_id: mealId,
						meal_name: request.meal_name,
						meal_category: request.meal_category,
						meal_image: request.meal_image,
						total_quantity: 0,
						requests: []
					}
				}
				
				groups[mealId].total_quantity += request.quantity
				groups[mealId].requests.push(request)
			})
			
			this.mealGroups = Object.values(groups).sort((a, b) => b.total_quantity - a.total_quantity)
		},
		
		updateStatusCounts() {
			const counts = {
				all: this.todayRequests.length,
				confirmed: 0,
				pending: 0,
				rejected: 0
			}
			
			this.todayRequests.forEach(request => {
				counts[request.status] = (counts[request.status] || 0) + 1
			})
			
			this.statusTabs.forEach(tab => {
				tab.count = counts[tab.value] || 0
			})
		},
		
		onDateChange(e) {
			this.selectedDate = e.detail.value
			this.expandedGroups = []
			this.loadTodayData()
		},
		
		changeStatus(status) {
			this.currentStatus = status
		},
		
		toggleMealGroup(mealId) {
			const index = this.expandedGroups.indexOf(mealId)
			if (index > -1) {
				this.expandedGroups.splice(index, 1)
			} else {
				this.expandedGroups.push(mealId)
			}
		},
		
		getStatusText(status) {
			const statusMap = {
				'pending': '待确认',
				'confirmed': '已确认',
				'rejected': '已拒绝'
			}
			return statusMap[status] || status
		},
		
		formatDate(dateStr) {
			const date = new Date(dateStr)
			const today = new Date()
			const yesterday = new Date(today)
			yesterday.setDate(today.getDate() - 1)
			
			if (dateStr === this.getTodayDate()) {
				return '今天 ' + date.toLocaleDateString()
			} else if (dateStr === yesterday.toISOString().split('T')[0]) {
				return '昨天 ' + date.toLocaleDateString()
			} else {
				return date.toLocaleDateString()
			}
		},
		
		formatTime(timeStr) {
			const time = new Date(timeStr)
			return time.toLocaleTimeString('zh-CN', { 
				hour: '2-digit', 
				minute: '2-digit' 
			})
		},
		
		async exportData() {
			try {
				uni.showLoading({ title: '导出中...' })
				
				// 构建导出数据
				const exportData = {
					date: this.selectedDate,
					stats: this.todayStats,
					meal_groups: this.mealGroups,
					requests: this.todayRequests
				}
				
				// 这里可以调用后端API导出Excel或PDF
				// 或者生成本地文件
				console.log('导出数据:', exportData)
				
				uni.showToast({
					title: '导出成功',
					icon: 'success'
				})
			} catch (error) {
				console.error('导出失败:', error)
				uni.showToast({
					title: '导出失败',
					icon: 'none'
				})
			} finally {
				uni.hideLoading()
			}
		}
	}
}
</script>

<style scoped>
.container {
	background-color: #f5f5f5;
	min-height: 100vh;
}

/* 日期选择器 */
.date-picker {
	background: white;
	padding: 30rpx;
	margin-bottom: 20rpx;
}

.date-display {
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 20rpx;
	padding: 20rpx;
	border: 2rpx solid #FF6B95;
	border-radius: 15rpx;
	background: #fff5f8;
}

.date-text {
	font-size: 32rpx;
	color: #FF6B95;
	font-weight: bold;
}

.date-icon {
	font-size: 32rpx;
}

/* 统计概览 */
.stats-overview {
	display: flex;
	padding: 20rpx;
	background: white;
	margin-bottom: 20rpx;
}

.stats-card {
	flex: 1;
	text-align: center;
	padding: 20rpx;
}

.stats-number {
	display: block;
	font-size: 48rpx;
	font-weight: bold;
	color: #FF6B95;
}

.stats-label {
	display: block;
	font-size: 24rpx;
	color: #666;
	margin-top: 10rpx;
}

/* 状态标签 */
.status-tabs {
	display: flex;
	padding: 0 20rpx;
	background: white;
	margin-bottom: 20rpx;
}

.status-tab {
	flex: 1;
	text-align: center;
	padding: 30rpx 20rpx;
	font-size: 28rpx;
	color: #666;
	border-bottom: 4rpx solid transparent;
	position: relative;
}

.status-tab.active {
	color: #FF6B95;
	border-bottom-color: #FF6B95;
	font-weight: bold;
}

.tab-count {
	font-size: 20rpx;
	color: #999;
}

/* 餐品汇总 */
.meal-summary {
	margin-bottom: 40rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	padding: 30rpx;
	background: white;
	margin-bottom: 20rpx;
}

.meal-group {
	background: white;
	margin-bottom: 20rpx;
}

.meal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.meal-info {
	display: flex;
	align-items: center;
	gap: 20rpx;
	flex: 1;
}

.meal-image {
	width: 80rpx;
	height: 80rpx;
	border-radius: 10rpx;
}

.meal-details {
	flex: 1;
}

.meal-name {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 10rpx;
}

.meal-category {
	font-size: 24rpx;
	color: #666;
}

.meal-stats {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	gap: 5rpx;
}

.total-quantity {
	font-size: 32rpx;
	font-weight: bold;
	color: #FF6B95;
}

.request-count {
	font-size: 24rpx;
	color: #666;
}

.expand-icon {
	font-size: 20rpx;
	color: #999;
	transition: transform 0.3s;
}

.expand-icon.expanded {
	transform: rotate(180deg);
}

/* 成员列表 */
.member-list {
	padding: 0 30rpx 30rpx;
}

.member-item {
	display: flex;
	align-items: center;
	gap: 20rpx;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #f5f5f5;
}

.member-avatar {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
}

.member-info {
	flex: 1;
}

.member-name {
	display: block;
	font-size: 28rpx;
	color: #333;
	margin-bottom: 5rpx;
}

.member-quantity {
	font-size: 24rpx;
	color: #666;
}

.status-badge {
	padding: 10rpx 20rpx;
	border-radius: 20rpx;
	font-size: 20rpx;
	color: white;
}

.status-badge.status-pending {
	background: #FF9800;
}

.status-badge.status-confirmed {
	background: #4CAF50;
}

.status-badge.status-rejected {
	background: #f44336;
}

.request-time {
	font-size: 20rpx;
	color: #999;
}

/* 时间线列表 */
.requests-timeline {
	padding: 0 20rpx;
}

.timeline-item {
	background: white;
	border-radius: 20rpx;
	margin-bottom: 20rpx;
	padding: 30rpx;
	border-left: 8rpx solid #ddd;
}

.timeline-item.status-pending {
	border-left-color: #FF9800;
}

.timeline-item.status-confirmed {
	border-left-color: #4CAF50;
}

.timeline-item.status-rejected {
	border-left-color: #f44336;
}

.timeline-time {
	font-size: 24rpx;
	color: #999;
	margin-bottom: 20rpx;
}

.timeline-content .member-info {
	display: flex;
	align-items: center;
	gap: 20rpx;
	margin-bottom: 20rpx;
}

.timeline-content .member-name {
	font-size: 28rpx;
	color: #333;
	font-weight: bold;
}

.meal-info {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.meal-name {
	font-size: 32rpx;
	color: #333;
}

.meal-quantity {
	font-size: 28rpx;
	color: #FF6B95;
	font-weight: bold;
}

.status-info {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.admin-note {
	font-size: 24rpx;
	color: #666;
}

.request-note {
	background: #f8f8f8;
	padding: 20rpx;
	border-radius: 10rpx;
}

.note-label {
	font-size: 24rpx;
	color: #666;
	margin-right: 10rpx;
}

.note-content {
	font-size: 28rpx;
	color: #333;
}

/* 导出按钮 */
.export-section {
	padding: 40rpx;
	text-align: center;
}

.export-btn {
	background: linear-gradient(45deg, #FF6B95, #FF8C94);
	color: white;
	border-radius: 50rpx;
	padding: 25rpx 60rpx;
	border: none;
	font-size: 32rpx;
	font-weight: bold;
	box-shadow: 0 10rpx 30rpx rgba(255, 107, 149, 0.3);
}

/* 加载中 */
.loading {
	text-align: center;
	padding: 40rpx;
	color: #666;
}

/* 空状态 */
.empty-state {
	text-align: center;
	padding: 100rpx 40rpx;
}

.empty-image {
	width: 200rpx;
	height: 200rpx;
	margin-bottom: 40rpx;
}

.empty-text {
	font-size: 28rpx;
	color: #999;
}
</style>
