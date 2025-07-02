<template>
	<view class="container">
		<!-- 头部统计卡片 -->
		<view class="stats-header">
			<view class="stats-card">
				<text class="stats-number">{{ pendingStats.total_count || 0 }}</text>
				<text class="stats-label">待确认</text>
			</view>
			<view class="stats-card">
				<text class="stats-number">{{ pendingStats.member_count || 0 }}</text>
				<text class="stats-label">成员数</text>
			</view>
			<view class="stats-card">
				<text class="stats-number">{{ pendingStats.meal_count || 0 }}</text>
				<text class="stats-label">餐品数</text>
			</view>
		</view>

		<!-- 筛选器 -->
		<view class="filter-section">
			<view class="filter-tabs">
				<view 
					v-for="tab in filterTabs" 
					:key="tab.value"
					class="filter-tab"
					:class="{ active: currentFilter === tab.value }"
					@click="changeFilter(tab.value)"
				>
					{{ tab.label }}
				</view>
			</view>
		</view>

		<!-- 批量操作按钮 -->
		<view class="batch-actions" v-if="selectedRequests.length > 0">
			<view class="batch-info">
				已选择 {{ selectedRequests.length }} 项
			</view>
			<view class="batch-buttons">
				<button class="btn-confirm" @click="batchConfirm">批量确认</button>
				<button class="btn-reject" @click="batchReject">批量拒绝</button>
			</view>
		</view>

		<!-- 点餐列表 -->
		<view class="requests-list">
			<view 
				v-for="request in filteredRequests" 
				:key="request.id"
				class="request-item"
				:class="{ selected: selectedRequests.includes(request.id) }"
			>
				<!-- 选择框 -->
				<view class="checkbox-wrapper" @click.stop="toggleSelect(request.id)">
					<view class="checkbox" :class="{ checked: selectedRequests.includes(request.id) }">
						<text class="checkbox-icon" v-if="selectedRequests.includes(request.id)">✓</text>
					</view>
				</view>

				<!-- 请求信息 -->
				<view class="request-content" @click="viewRequestDetail(request)">
					<view class="request-header">
						<view class="member-info">
							<image 
								:src="request.member_avatar || '/static/default-avatar.png'" 
								class="member-avatar"
							></image>
							<text class="member-name">{{ request.member_name }}</text>
						</view>
						<view class="request-time">
							{{ formatTime(request.created_at) }}
						</view>
					</view>

					<view class="meal-info">
						<image 
							:src="request.meal_image || '/static/dishes/default.jpg'" 
							class="meal-image"
						></image>
						<view class="meal-details">
							<text class="meal-name">{{ request.meal_name }}</text>
							<text class="meal-category">{{ request.meal_category }}</text>
							<text class="meal-quantity">数量: {{ request.quantity }}</text>
						</view>
					</view>

					<view class="request-note" v-if="request.note">
						<text class="note-label">备注:</text>
						<text class="note-content">{{ request.note }}</text>
					</view>
				</view>

				<!-- 操作按钮 -->
				<view class="request-actions">
					<button class="btn-confirm-single" @click.stop="confirmRequest(request)">确认</button>
					<button class="btn-reject-single" @click.stop="rejectRequest(request)">拒绝</button>
				</view>
			</view>
		</view>

		<!-- 加载更多 -->
		<view class="load-more" v-if="hasMore && !loading">
			<button @click="loadMore" class="load-more-btn">加载更多</button>
		</view>

		<!-- 加载中 -->
		<view class="loading" v-if="loading">
			<text>加载中...</text>
		</view>

		<!-- 空状态 -->
		<view class="empty-state" v-if="!loading && filteredRequests.length === 0">
			<image src="/static/empty-state.png" class="empty-image"></image>
			<text class="empty-text">暂无待确认的点餐</text>
		</view>
	</view>
</template>

<script>
import orderingManager from '@/utils/orderingManager.js'

export default {
	data() {
		return {
			pendingRequests: [],
			pendingStats: {},
			currentFilter: 'all',
			selectedRequests: [],
			loading: false,
			hasMore: true,
			page: 1,
			filterTabs: [
				{ label: '全部', value: 'all' },
				{ label: '今日', value: 'today' },
				{ label: '本周', value: 'week' },
				{ label: '按成员', value: 'member' },
				{ label: '按餐品', value: 'meal' }
			]
		}
	},
	
	computed: {
		filteredRequests() {
			if (this.currentFilter === 'all') {
				return this.pendingRequests
			}
			
			const now = new Date()
			const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
			const weekStart = new Date(today)
			weekStart.setDate(today.getDate() - today.getDay())
			
			return this.pendingRequests.filter(request => {
				const requestDate = new Date(request.created_at)
				
				switch (this.currentFilter) {
					case 'today':
						return requestDate >= today
					case 'week':
						return requestDate >= weekStart
					case 'member':
						// 这里可以根据具体需求实现按成员筛选
						return true
					case 'meal':
						// 这里可以根据具体需求实现按餐品筛选
						return true
					default:
						return true
				}
			})
		}
	},
	
	onLoad() {
		this.loadPendingRequests()
		this.loadPendingStats()
	},
	
	onPullDownRefresh() {
		this.refreshData()
	},
	
	onReachBottom() {
		if (this.hasMore && !this.loading) {
			this.loadMore()
		}
	},
	
	methods: {
		async loadPendingRequests() {
			try {
				this.loading = true
				const params = {
					status: 'pending',
					page: this.page,
					page_size: 20
				}
				
				const response = await orderingManager.getMealRequests(params)
				
				if (this.page === 1) {
					this.pendingRequests = response.results || []
				} else {
					this.pendingRequests.push(...(response.results || []))
				}
				
				this.hasMore = !!response.next
			} catch (error) {
				console.error('加载待确认点餐失败:', error)
				uni.showToast({
					title: '加载失败',
					icon: 'none'
				})
			} finally {
				this.loading = false
				uni.stopPullDownRefresh()
			}
		},
		
		async loadPendingStats() {
			try {
				const today = new Date().toISOString().split('T')[0]
				this.pendingStats = await orderingManager.getMealStats({
					date: today,
					status: 'pending'
				})
			} catch (error) {
				console.error('加载统计数据失败:', error)
			}
		},
		
		async refreshData() {
			this.page = 1
			this.selectedRequests = []
			await Promise.all([
				this.loadPendingRequests(),
				this.loadPendingStats()
			])
		},
		
		loadMore() {
			this.page++
			this.loadPendingRequests()
		},
		
		changeFilter(filter) {
			this.currentFilter = filter
			this.selectedRequests = []
		},
		
		toggleSelect(requestId) {
			const index = this.selectedRequests.indexOf(requestId)
			if (index > -1) {
				this.selectedRequests.splice(index, 1)
			} else {
				this.selectedRequests.push(requestId)
			}
		},
		
		async confirmRequest(request) {
			try {
				uni.showLoading({ title: '确认中...' })
				
				await orderingManager.confirmMealRequest(request.id, {
					status: 'confirmed',
					admin_note: '管理员确认'
				})
				
				uni.showToast({
					title: '确认成功',
					icon: 'success'
				})
				
				this.refreshData()
			} catch (error) {
				console.error('确认点餐失败:', error)
				uni.showToast({
					title: '确认失败',
					icon: 'none'
				})
			} finally {
				uni.hideLoading()
			}
		},
		
		async rejectRequest(request) {
			try {
				const res = await uni.showModal({
					title: '拒绝确认',
					content: '确定要拒绝这个点餐请求吗？',
					showCancel: true
				})
				
				if (!res.confirm) return
				
				uni.showLoading({ title: '处理中...' })
				
				await orderingManager.confirmMealRequest(request.id, {
					status: 'rejected',
					admin_note: '管理员拒绝'
				})
				
				uni.showToast({
					title: '已拒绝',
					icon: 'success'
				})
				
				this.refreshData()
			} catch (error) {
				console.error('拒绝点餐失败:', error)
				uni.showToast({
					title: '操作失败',
					icon: 'none'
				})
			} finally {
				uni.hideLoading()
			}
		},
		
		async batchConfirm() {
			try {
				const res = await uni.showModal({
					title: '批量确认',
					content: `确定要确认选中的 ${this.selectedRequests.length} 个点餐请求吗？`,
					showCancel: true
				})
				
				if (!res.confirm) return
				
				uni.showLoading({ title: '批量确认中...' })
				
				const promises = this.selectedRequests.map(id => 
					orderingManager.confirmMealRequest(id, {
						status: 'confirmed',
						admin_note: '批量确认'
					})
				)
				
				await Promise.all(promises)
				
				uni.showToast({
					title: '批量确认成功',
					icon: 'success'
				})
				
				this.refreshData()
			} catch (error) {
				console.error('批量确认失败:', error)
				uni.showToast({
					title: '批量确认失败',
					icon: 'none'
				})
			} finally {
				uni.hideLoading()
			}
		},
		
		async batchReject() {
			try {
				const res = await uni.showModal({
					title: '批量拒绝',
					content: `确定要拒绝选中的 ${this.selectedRequests.length} 个点餐请求吗？`,
					showCancel: true
				})
				
				if (!res.confirm) return
				
				uni.showLoading({ title: '批量拒绝中...' })
				
				const promises = this.selectedRequests.map(id => 
					orderingManager.confirmMealRequest(id, {
						status: 'rejected',
						admin_note: '批量拒绝'
					})
				)
				
				await Promise.all(promises)
				
				uni.showToast({
					title: '批量拒绝成功',
					icon: 'success'
				})
				
				this.refreshData()
			} catch (error) {
				console.error('批量拒绝失败:', error)
				uni.showToast({
					title: '批量拒绝失败',
					icon: 'none'
				})
			} finally {
				uni.hideLoading()
			}
		},
		
		viewRequestDetail(request) {
			// 可以导航到详情页面或显示详情弹窗
			console.log('查看点餐详情:', request)
		},
		
		formatTime(timeStr) {
			const time = new Date(timeStr)
			const now = new Date()
			const diff = now - time
			
			if (diff < 60000) { // 1分钟内
				return '刚刚'
			} else if (diff < 3600000) { // 1小时内
				return Math.floor(diff / 60000) + '分钟前'
			} else if (diff < 86400000) { // 24小时内
				return Math.floor(diff / 3600000) + '小时前'
			} else {
				return time.toLocaleDateString()
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

/* 头部统计 */
.stats-header {
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
	font-size: 28rpx;
	color: #666;
	margin-top: 10rpx;
}

/* 筛选器 */
.filter-section {
	background: white;
	margin-bottom: 20rpx;
}

.filter-tabs {
	display: flex;
	padding: 0 20rpx;
}

.filter-tab {
	flex: 1;
	text-align: center;
	padding: 30rpx 20rpx;
	font-size: 28rpx;
	color: #666;
	border-bottom: 4rpx solid transparent;
}

.filter-tab.active {
	color: #FF6B95;
	border-bottom-color: #FF6B95;
	font-weight: bold;
}

/* 批量操作 */
.batch-actions {
	display: flex;
	align-items: center;
	justify-content: space-between;
	background: #FF6B95;
	color: white;
	padding: 20rpx;
	margin-bottom: 20rpx;
}

.batch-info {
	font-size: 28rpx;
}

.batch-buttons {
	display: flex;
	gap: 20rpx;
}

.btn-confirm, .btn-reject {
	padding: 10rpx 30rpx;
	border-radius: 40rpx;
	border: 2rpx solid white;
	background: transparent;
	color: white;
	font-size: 24rpx;
}

/* 点餐列表 */
.requests-list {
	padding: 0 20rpx;
}

.request-item {
	background: white;
	border-radius: 20rpx;
	margin-bottom: 20rpx;
	padding: 30rpx;
	display: flex;
	align-items: flex-start;
	gap: 20rpx;
	position: relative;
}

.request-item.selected {
	background: #fff5f8;
	border: 2rpx solid #FF6B95;
}

.checkbox-wrapper {
	padding: 10rpx;
}

.checkbox {
	width: 40rpx;
	height: 40rpx;
	border: 2rpx solid #ddd;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.checkbox.checked {
	background: #FF6B95;
	border-color: #FF6B95;
}

.checkbox-icon {
	color: white;
	font-size: 24rpx;
	font-weight: bold;
}

.request-content {
	flex: 1;
}

.request-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.member-info {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.member-avatar {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
}

.member-name {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.request-time {
	font-size: 24rpx;
	color: #999;
}

.meal-info {
	display: flex;
	gap: 20rpx;
	margin-bottom: 20rpx;
}

.meal-image {
	width: 120rpx;
	height: 120rpx;
	border-radius: 15rpx;
}

.meal-details {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 10rpx;
}

.meal-name {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.meal-category {
	font-size: 24rpx;
	color: #666;
}

.meal-quantity {
	font-size: 28rpx;
	color: #FF6B95;
	font-weight: bold;
}

.request-note {
	background: #f8f8f8;
	padding: 20rpx;
	border-radius: 10rpx;
	margin-bottom: 20rpx;
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

.request-actions {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.btn-confirm-single, .btn-reject-single {
	padding: 15rpx 30rpx;
	border-radius: 40rpx;
	border: none;
	font-size: 24rpx;
	min-width: 120rpx;
}

.btn-confirm-single {
	background: #4CAF50;
	color: white;
}

.btn-reject-single {
	background: #f44336;
	color: white;
}

/* 加载更多 */
.load-more {
	padding: 40rpx;
	text-align: center;
}

.load-more-btn {
	background: #FF6B95;
	color: white;
	border-radius: 40rpx;
	padding: 20rpx 60rpx;
	border: none;
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
