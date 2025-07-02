<template>
	<view class="page-container">
		<view class="container">
			<!-- 页面标题 -->
			<view class="page-header">
				<text class="page-title">用餐记录</text>
				<view class="add-record-btn" @click="showAddRecord">
					<text class="add-icon">+</text>
					<text class="add-text">记录用餐</text>
				</view>
			</view>
			
			<!-- 统计信息 -->
			<view class="stats-card">
				<view class="stat-item">
					<text class="stat-number">{{ statistics.totalMeals }}</text>
					<text class="stat-label">总用餐次数</text>
				</view>
				<view class="stat-item">
					<text class="stat-number">{{ statistics.recentMeals }}</text>
					<text class="stat-label">近7天</text>
				</view>
				<view class="stat-item">
					<text class="stat-number">{{ statistics.memberCount }}</text>
					<text class="stat-label">家庭成员</text>
				</view>
			</view>
			
			<!-- 筛选选项 -->
			<view class="filter-section">
				<scroll-view scroll-x class="filter-scroll">
					<view class="filter-list">
						<view 
							class="filter-item" 
							:class="{ active: selectedFilter === 'all' }"
							@click="setFilter('all')"
						>
							<text>全部</text>
						</view>
						<view 
							class="filter-item" 
							:class="{ active: selectedFilter === 'today' }"
							@click="setFilter('today')"
						>
							<text>今天</text>
						</view>
						<view 
							class="filter-item" 
							:class="{ active: selectedFilter === 'week' }"
							@click="setFilter('week')"
						>
							<text>本周</text>
						</view>
						<view 
							class="filter-item" 
							:class="{ active: selectedFilter === 'month' }"
							@click="setFilter('month')"
						>
							<text>本月</text>
						</view>
					</view>
				</scroll-view>
			</view>
			
			<!-- 用餐记录列表 -->
			<view class="records-section">
				<view v-if="loading" class="loading-section">
					<text>加载中...</text>
				</view>
				
				<view v-else-if="filteredRecords.length === 0" class="empty-section">
					<text class="empty-icon">🍽️</text>
					<text class="empty-text">还没有用餐记录</text>
					<text class="empty-desc">点击右上角记录第一次用餐吧</text>
				</view>
				
				<view v-else class="records-list">
					<view 
						class="record-item" 
						v-for="record in filteredRecords" 
						:key="record.id"
						@click="showRecordDetail(record)"
					>
						<!-- 记录头部 -->
						<view class="record-header">
							<view class="cook-info">
								<image class="cook-avatar" :src="record.cookAvatar || '/static/default-avatar.png'" mode="aspectFill"></image>
								<view class="cook-details">
									<text class="cook-name">{{ record.cookName }}</text>
									<text class="cook-time">{{ formatTime(record.cookTime) }}</text>
								</view>
							</view>
							<view class="dish-rating" v-if="record.rating">
								<view class="stars">
									<text 
										class="star" 
										v-for="n in 5" 
										:key="n"
										:class="{ filled: n <= record.rating }"
									>★</text>
								</view>
							</view>
						</view>
						
						<!-- 菜品信息 -->
						<view class="dish-info">
							<text class="dish-name">{{ record.dishName }}</text>
						</view>
						
						<!-- 参与用餐人员 -->
						<view class="participants-section" v-if="record.participants && record.participants.length > 0">
							<text class="participants-label">参与用餐：</text>
							<view class="participants-list">
								<view class="participant-item" v-for="participant in record.participants.slice(0, 4)" :key="participant.id">
									<image class="participant-avatar" :src="participant.avatar || '/static/default-avatar.png'" mode="aspectFill"></image>
								</view>
								<view v-if="record.participants.length > 4" class="more-participants">
									<text>+{{ record.participants.length - 4 }}</text>
								</view>
							</view>
						</view>
						
						<!-- 菜品图片 -->
						<view class="dish-images" v-if="record.images && record.images.length > 0">
							<image 
								class="dish-image" 
								v-for="(image, index) in record.images.slice(0, 3)" 
								:key="index"
								:src="image" 
								mode="aspectFill"
								@click.stop="previewImage(record.images, index)"
							></image>
							<view v-if="record.images.length > 3" class="more-images">
								<text>+{{ record.images.length - 3 }}</text>
							</view>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 添加记录弹窗 -->
		<view class="modal-mask" v-if="showAddRecordModal" @tap="closeAddRecordModal">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">记录用餐</text>
					<text class="modal-close" @click="closeAddRecordModal">×</text>
				</view>
				
				<view class="modal-body">
					<view class="form-item">
						<text class="form-label">菜品名称</text>
						<input class="form-input" v-model="newRecord.dishName" placeholder="请输入菜品名称" />
					</view>
					
					<view class="form-item">
						<text class="form-label">下厨人员</text>
						<picker mode="selector" :range="familyMembers" range-key="name" @change="onCookChange">
							<view class="picker-input">
								<text>{{ newRecord.cookName || '请选择下厨人员' }}</text>
								<text class="picker-arrow">></text>
							</view>
						</picker>
					</view>
					
					<view class="form-item">
						<text class="form-label">参与用餐</text>
						<view class="members-select">
							<view 
								class="member-checkbox" 
								v-for="member in familyMembers" 
								:key="member.id"
								@click="toggleParticipant(member)"
							>
								<view class="checkbox" :class="{ checked: isParticipantSelected(member) }">
									<text v-if="isParticipantSelected(member)">✓</text>
								</view>
								<image class="member-avatar-small" :src="member.avatar" mode="aspectFill"></image>
								<text class="member-name-small">{{ member.name }}</text>
							</view>
						</view>
					</view>
					
					<view class="form-item">
						<text class="form-label">评分</text>
						<view class="rating-select">
							<text 
								class="rating-star" 
								v-for="n in 5" 
								:key="n"
								:class="{ active: n <= newRecord.rating }"
								@click="setRating(n)"
							>★</text>
						</view>
					</view>
				</view>
				
				<view class="modal-footer">
					<button class="cancel-btn" @click="closeAddRecordModal">取消</button>
					<button class="confirm-btn" @click="confirmAddRecord">确定</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import familyManager from '../../utils/familyManager.js'

export default {
	data() {
		return {
			statistics: {
				totalMeals: 0,
				recentMeals: 0,
				memberCount: 0
			},
			records: [],
			filteredRecords: [],
			selectedFilter: 'all',
			loading: false,
			showAddRecordModal: false,
			newRecord: {
				dishName: '',
				cookId: '',
				cookName: '',
				participants: [],
				rating: 5,
				notes: ''
			},
			familyMembers: []
		}
	},
	
	onLoad(options) {
		// 处理从其他页面传来的参数
		if (options.dish) {
			try {
				this.newRecord.dishName = decodeURIComponent(options.dish)
			} catch (error) {
				console.error('解析菜品参数失败:', error)
			}
		}
		
		this.initializeData();
	},
	
	onShow() {
		this.refreshData();
	},
	
	methods: {
		// 初始化数据
		async initializeData() {
			this.loading = true;
			
			try {
				// 等待家庭管理器初始化
				if (!familyManager.getCurrentFamily()) {
					await familyManager.initialize();
				}
				
				// 获取家庭成员
				this.familyMembers = familyManager.getFamilyMembers().map(member => ({
					id: member.user_info.openid,
					name: member.user_info.nickname,
					avatar: member.user_info.avatar,
					displayName: member.display_name
				}));
				
				// 获取用餐记录
				await this.loadCookingRecords();
				
				// 更新统计数据
				this.updateStatistics();
				
				// 应用筛选
				this.applyFilter();
				
			} catch (error) {
				console.error('初始化数据失败:', error);
				uni.showToast({
					title: '加载失败',
					icon: 'none'
				});
			} finally {
				this.loading = false;
			}
		},
		
		// 刷新数据
		async refreshData() {
			await this.loadCookingRecords();
			this.updateStatistics();
			this.applyFilter();
		},
		
		// 加载用餐记录
		async loadCookingRecords() {
			this.records = await familyManager.loadCookingRecords();
		},
		
		// 更新统计数据
		updateStatistics() {
			this.statistics = familyManager.getStatistics();
		},
		
		// 设置筛选条件
		setFilter(filter) {
			this.selectedFilter = filter;
			this.applyFilter();
		},
		
		// 应用筛选
		applyFilter() {
			const now = new Date();
			let filtered = [...this.records];
			
			switch (this.selectedFilter) {
				case 'today':
					const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
					filtered = this.records.filter(record => 
						new Date(record.cookTime) >= today
					);
					break;
				case 'week':
					const weekStart = new Date(now);
					weekStart.setDate(now.getDate() - 7);
					filtered = this.records.filter(record => 
						new Date(record.cookTime) >= weekStart
					);
					break;
				case 'month':
					const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
					filtered = this.records.filter(record => 
						new Date(record.cookTime) >= monthStart
					);
					break;
				default:
					// 'all' - 显示全部
					break;
			}
			
			this.filteredRecords = filtered;
		},
		
		// 格式化时间
		formatTime(timestamp) {
			const date = new Date(timestamp);
			const now = new Date();
			const diff = now - date;
			
			// 小于1小时显示分钟
			if (diff < 60 * 60 * 1000) {
				const minutes = Math.floor(diff / (60 * 1000));
				return minutes <= 0 ? '刚刚' : `${minutes}分钟前`;
			}
			
			// 小于24小时显示小时
			if (diff < 24 * 60 * 60 * 1000) {
				const hours = Math.floor(diff / (60 * 60 * 1000));
				return `${hours}小时前`;
			}
			
			// 小于7天显示天数
			if (diff < 7 * 24 * 60 * 60 * 1000) {
				const days = Math.floor(diff / (24 * 60 * 60 * 1000));
				return `${days}天前`;
			}
			
			// 其他显示具体日期
			return `${date.getMonth() + 1}/${date.getDate()}`;
		},
		
		// 显示记录详情
		showRecordDetail(record) {
			// TODO: 跳转到记录详情页面
			console.log('显示记录详情:', record);
		},
		
		// 预览图片
		previewImage(images, current) {
			uni.previewImage({
				urls: images,
				current: current
			});
		},
		
		// 显示添加记录弹窗
		showAddRecord() {
			if (this.familyMembers.length === 0) {
				uni.showToast({
					title: '请先加入家庭',
					icon: 'none'
				});
				return;
			}
			
			this.resetNewRecord();
			this.showAddRecordModal = true;
		},
		
		// 关闭添加记录弹窗
		closeAddRecordModal() {
			this.showAddRecordModal = false;
		},
		
		// 重置新记录数据
		resetNewRecord() {
			this.newRecord = {
				dishName: '',
				cookId: '',
				cookName: '',
				participants: [],
				rating: 5
			};
		},
		
		// 下厨人员选择
		onCookChange(e) {
			const selected = this.familyMembers[e.detail.value];
			this.newRecord.cookId = selected.id;
			this.newRecord.cookName = selected.name;
		},
		
		// 切换参与人员
		toggleParticipant(member) {
			const index = this.newRecord.participants.findIndex(p => p.id === member.id);
			if (index > -1) {
				this.newRecord.participants.splice(index, 1);
			} else {
				this.newRecord.participants.push({
					id: member.id,
					name: member.name,
					avatar: member.avatar
				});
			}
		},
		
		// 检查是否选中参与人员
		isParticipantSelected(member) {
			return this.newRecord.participants.some(p => p.id === member.id);
		},
		
		// 设置评分
		setRating(rating) {
			this.newRecord.rating = rating;
		},
		
		// 确认添加记录
		async confirmAddRecord() {
			// 验证必填项
			if (!this.newRecord.dishName.trim()) {
				uni.showToast({
					title: '请输入菜品名称',
					icon: 'none'
				});
				return;
			}
			
			if (!this.newRecord.cookId) {
				uni.showToast({
					title: '请选择下厨人员',
					icon: 'none'
				});
				return;
			}
			
			try {
				const selectedMember = this.familyMembers.find(m => m.id === this.newRecord.cookId)
				
				// 构造记录数据
				const recordData = {
					cook_id: this.newRecord.cookId,
					cook_name: this.newRecord.cookName,
					cook_avatar: selectedMember?.avatar || '/static/default-avatar.png',
					dish_name: this.newRecord.dishName,
					cook_time: new Date().toISOString(),
					participants: this.newRecord.participants,
					rating: this.newRecord.rating,
					notes: this.newRecord.notes || '',
					images: []
				}
				
				// 使用 familyManager 添加记录
				const newRecord = await familyManager.addCookingRecord(recordData)
				
				// 更新本地数据
				this.records = familyManager.getCookingRecords()
				this.applyFilter()
				this.updateStatistics()
				
				this.closeAddRecordModal()
				
				uni.showToast({
					title: '记录成功',
					icon: 'success'
				})
				
			} catch (error) {
				console.error('添加记录失败:', error)
				uni.showToast({
					title: '记录失败，请重试',
					icon: 'none'
				})
			}
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #F8F9FA;
	padding-bottom: 40rpx;
}

.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx;
	background: white;
}

.page-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333333;
}

.add-record-btn {
	display: flex;
	align-items: center;
	background: #FF6B95;
	color: white;
	padding: 12rpx 20rpx;
	border-radius: 20rpx;
}

.add-icon {
	margin-right: 8rpx;
	font-size: 20rpx;
}

.add-text {
	font-size: 24rpx;
}

.stats-card {
	display: flex;
	background: linear-gradient(135deg, #FF6B95, #FFB6C1);
	margin: 20rpx;
	border-radius: 20rpx;
	padding: 30rpx;
	color: white;
}

.stat-item {
	flex: 1;
	text-align: center;
}

.stat-number {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	margin-bottom: 8rpx;
}

.stat-label {
	font-size: 24rpx;
	opacity: 0.9;
}

.filter-section {
	background: white;
	margin: 20rpx 20rpx 0;
	border-radius: 20rpx;
	padding: 20rpx 0;
}

.filter-scroll {
	white-space: nowrap;
}

.filter-list {
	display: flex;
	padding: 0 20rpx;
}

.filter-item {
	padding: 12rpx 24rpx;
	margin-right: 20rpx;
	border-radius: 20rpx;
	background: #F5F5F5;
	color: #666666;
	font-size: 24rpx;
	white-space: nowrap;
}

.filter-item.active {
	background: #FF6B95;
	color: white;
}

.records-section {
	margin: 20rpx;
}

.loading-section, .empty-section {
	text-align: center;
	padding: 80rpx 40rpx;
	background: white;
	border-radius: 20rpx;
}

.empty-icon {
	display: block;
	font-size: 64rpx;
	margin-bottom: 20rpx;
}

.empty-text {
	display: block;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 12rpx;
}

.empty-desc {
	font-size: 24rpx;
	color: #999999;
}

.records-list {
	background: white;
	border-radius: 20rpx;
	overflow: hidden;
}

.record-item {
	padding: 30rpx;
	border-bottom: 1rpx solid #F5F5F5;
}

.record-item:last-child {
	border-bottom: none;
}

.record-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.cook-info {
	display: flex;
	align-items: center;
}

.cook-avatar {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
	margin-right: 16rpx;
}

.cook-details {
	display: flex;
	flex-direction: column;
}

.cook-name {
	font-size: 28rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 4rpx;
}

.cook-time {
	font-size: 22rpx;
	color: #999999;
}

.dish-rating .stars {
	display: flex;
	align-items: center;
}

.star {
	color: #E0E0E0;
	font-size: 24rpx;
	margin-left: 2rpx;
}

.star.filled {
	color: #FFD700;
}

.dish-info {
	margin-bottom: 20rpx;
}

.dish-name {
	font-size: 32rpx;
	font-weight: 500;
	color: #333333;
}

.participants-section {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.participants-label {
	font-size: 24rpx;
	color: #666666;
	margin-right: 16rpx;
}

.participants-list {
	display: flex;
	align-items: center;
}

.participant-item {
	position: relative;
	margin-right: 8rpx;
}

.participant-avatar {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	border: 2rpx solid white;
}

.more-participants {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: #E0E0E0;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 20rpx;
	color: #666666;
}

.dish-images {
	display: flex;
	gap: 12rpx;
}

.dish-image {
	width: 120rpx;
	height: 120rpx;
	border-radius: 12rpx;
}

.more-images {
	width: 120rpx;
	height: 120rpx;
	border-radius: 12rpx;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	color: white;
	font-size: 24rpx;
}

/* 弹窗样式 */
.modal-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.modal-content {
	width: 650rpx;
	max-height: 80vh;
	background: white;
	border-radius: 20rpx;
	overflow: hidden;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #F5F5F5;
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

.modal-body {
	padding: 30rpx;
	max-height: 60vh;
	overflow-y: auto;
}

.form-item {
	margin-bottom: 30rpx;
}

.form-label {
	display: block;
	font-size: 26rpx;
	color: #333333;
	margin-bottom: 12rpx;
}

.form-input {
	width: 100%;
	height: 80rpx;
	border: 1rpx solid #E5E5E5;
	border-radius: 12rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	box-sizing: border-box;
}

.picker-input {
	width: 100%;
	height: 80rpx;
	border: 1rpx solid #E5E5E5;
	border-radius: 12rpx;
	padding: 0 20rpx;
	display: flex;
	align-items: center;
	justify-content: space-between;
	font-size: 28rpx;
	color: #333333;
	box-sizing: border-box;
}

.picker-arrow {
	color: #C0C4CC;
}

.members-select {
	display: flex;
	flex-wrap: wrap;
	gap: 20rpx;
}

.member-checkbox {
	display: flex;
	align-items: center;
	padding: 12rpx;
	border: 1rpx solid #E5E5E5;
	border-radius: 12rpx;
	min-width: 140rpx;
}

.checkbox {
	width: 24rpx;
	height: 24rpx;
	border: 2rpx solid #E5E5E5;
	border-radius: 4rpx;
	margin-right: 12rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 16rpx;
	color: white;
}

.checkbox.checked {
	background: #FF6B95;
	border-color: #FF6B95;
}

.member-avatar-small {
	width: 32rpx;
	height: 32rpx;
	border-radius: 50%;
	margin-right: 8rpx;
}

.member-name-small {
	font-size: 24rpx;
	color: #333333;
}

.rating-select {
	display: flex;
	align-items: center;
}

.rating-star {
	font-size: 36rpx;
	color: #E0E0E0;
	margin-right: 8rpx;
}

.rating-star.active {
	color: #FFD700;
}

.modal-footer {
	display: flex;
	border-top: 1rpx solid #F5F5F5;
}

.cancel-btn, .confirm-btn {
	flex: 1;
	height: 88rpx;
	border: none;
	font-size: 28rpx;
	line-height: 88rpx;
}

.cancel-btn {
	background: #F5F5F5;
	color: #666666;
}

.confirm-btn {
	background: #FF6B95;
	color: white;
}
</style>
