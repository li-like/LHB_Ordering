<template>
	<view class="container">
		<!-- 头部信息卡片 -->
		<view class="header-card">
			<view class="card-icon">
				<text class="icon">📊</text>
			</view>
			<view class="card-info">
				<text class="title">加入天数统计</text>
				<text class="subtitle">您与我们一起的美好时光</text>
			</view>
		</view>

		<!-- 统计概览 -->
		<view class="stats-overview">
			<view class="big-number">
				<text class="number">{{ joinedDays }}</text>
				<text class="unit">天</text>
			</view>
			<view class="joined-info">
				<text class="date-label">加入时间</text>
				<text class="date-value">{{ formattedJoinDate }}</text>
			</view>
		</view>

		<!-- 里程碑 -->
		<view class="milestone-section">
			<view class="section-title">
				<text class="title-text">成就里程碑</text>
			</view>
			<view class="milestone-list">
				<view class="milestone-item" :class="{ achieved: milestone.achieved }" v-for="milestone in milestones" :key="milestone.id">
					<view class="milestone-icon">
						<text class="icon">{{ milestone.icon }}</text>
					</view>
					<view class="milestone-info">
						<text class="milestone-title">{{ milestone.title }}</text>
						<text class="milestone-desc">{{ milestone.description }}</text>
					</view>
					<view class="milestone-status">
						<text class="status-icon">{{ milestone.achieved ? '✅' : '🔒' }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 时间轴 -->
		<view class="timeline-section">
			<view class="section-title">
				<text class="title-text">时间轴</text>
			</view>
			<view class="timeline-list">
				<view class="timeline-item" v-for="event in timelineEvents" :key="event.id">
					<view class="timeline-dot"></view>
					<view class="timeline-content">
						<text class="event-title">{{ event.title }}</text>
						<text class="event-desc">{{ event.description }}</text>
						<text class="event-date">{{ event.date }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 鼓励信息 -->
		<view class="encouragement-section">
			<view class="encouragement-card">
				<text class="encouragement-text">{{ encouragementMessage }}</text>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			joinedDays: 0,
			joinTime: Date.now(),
			milestones: [
				{
					id: 1,
					icon: '🎉',
					title: '新手上路',
					description: '加入家庭点餐第1天',
					threshold: 1,
					achieved: false
				},
				{
					id: 2,
					icon: '⭐',
					title: '一周老友',
					description: '使用满7天',
					threshold: 7,
					achieved: false
				},
				{
					id: 3,
					icon: '🏆',
					title: '月度活跃',
					description: '使用满30天',
					threshold: 30,
					achieved: false
				},
				{
					id: 4,
					icon: '👑',
					title: '资深用户',
					description: '使用满100天',
					threshold: 100,
					achieved: false
				},
				{
					id: 5,
					icon: '💎',
					title: '忠实伙伴',
					description: '使用满365天',
					threshold: 365,
					achieved: false
				}
			],
			timelineEvents: []
		}
	},
	
	computed: {
		formattedJoinDate() {
			return new Date(this.joinTime).toLocaleDateString('zh-CN', {
				year: 'numeric',
				month: 'long',
				day: 'numeric'
			});
		},
		
		encouragementMessage() {
			if (this.joinedDays < 7) {
				return '🌟 欢迎来到家庭点餐！希望您能享受美好的用餐时光～';
			} else if (this.joinedDays < 30) {
				return '🎯 您已经是我们的老朋友了！继续加油，更多惊喜等着您！';
			} else if (this.joinedDays < 100) {
				return '🏅 感谢您的陪伴！您已经是我们的月度活跃用户了！';
			} else {
				return '🎉 哇！您真是我们的资深用户！感谢您一直以来的支持！';
			}
		}
	},
	
	onLoad(options) {
		if (options.days) {
			this.joinedDays = parseInt(options.days);
		}
		if (options.joinTime) {
			this.joinTime = parseInt(options.joinTime);
		}
		
		this.updateMilestones();
		this.generateTimelineEvents();
	},
	
	methods: {
		updateMilestones() {
			this.milestones.forEach(milestone => {
				milestone.achieved = this.joinedDays >= milestone.threshold;
			});
		},
		
		generateTimelineEvents() {
			const events = [];
			const joinDate = new Date(this.joinTime);
			
			// 加入事件
			events.push({
				id: 1,
				title: '加入家庭点餐',
				description: '欢迎来到我们的大家庭！',
				date: joinDate.toLocaleDateString('zh-CN')
			});
			
			// 模拟一些里程碑事件
			if (this.joinedDays >= 7) {
				const date = new Date(joinDate.getTime() + 7 * 24 * 60 * 60 * 1000);
				events.push({
					id: 2,
					title: '解锁一周成就',
					description: '您已经使用满一周了！',
					date: date.toLocaleDateString('zh-CN')
				});
			}
			
			if (this.joinedDays >= 30) {
				const date = new Date(joinDate.getTime() + 30 * 24 * 60 * 60 * 1000);
				events.push({
					id: 3,
					title: '月度活跃用户',
					description: '恭喜成为月度活跃用户！',
					date: date.toLocaleDateString('zh-CN')
				});
			}
			
			// 按时间倒序排列
			this.timelineEvents = events.reverse();
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #FFF5F8;
	padding: 30rpx;
}

.header-card {
	background: linear-gradient(135deg, #FF6B95, #FFB6C1);
	border-radius: 24rpx;
	padding: 40rpx;
	display: flex;
	align-items: center;
	margin-bottom: 30rpx;
}

.card-icon {
	width: 80rpx;
	height: 80rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
}

.card-icon .icon {
	font-size: 36rpx;
}

.card-info {
	flex: 1;
}

.title {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: white;
	margin-bottom: 8rpx;
}

.subtitle {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.stats-overview {
	background: white;
	border-radius: 24rpx;
	padding: 50rpx 40rpx;
	text-align: center;
	margin-bottom: 30rpx;
}

.big-number {
	margin-bottom: 30rpx;
}

.number {
	font-size: 100rpx;
	font-weight: bold;
	color: #FF6B95;
	line-height: 1;
}

.unit {
	font-size: 32rpx;
	color: #FF6B95;
	margin-left: 8rpx;
}

.joined-info {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.date-label {
	font-size: 24rpx;
	color: #999;
	margin-bottom: 8rpx;
}

.date-value {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
}

.milestone-section, .timeline-section {
	margin-bottom: 40rpx;
}

.section-title {
	margin-bottom: 20rpx;
}

.title-text {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
}

.milestone-list {
	background: white;
	border-radius: 20rpx;
	overflow: hidden;
}

.milestone-item {
	display: flex;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #F5F5F5;
	opacity: 0.5;
}

.milestone-item:last-child {
	border-bottom: none;
}

.milestone-item.achieved {
	opacity: 1;
}

.milestone-icon {
	width: 60rpx;
	height: 60rpx;
	background: #FFF0F5;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 20rpx;
}

.milestone-icon .icon {
	font-size: 28rpx;
}

.milestone-info {
	flex: 1;
}

.milestone-title {
	display: block;
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
	margin-bottom: 8rpx;
}

.milestone-desc {
	font-size: 22rpx;
	color: #999;
}

.milestone-status {
	margin-left: 20rpx;
}

.status-icon {
	font-size: 24rpx;
}

.timeline-list {
	background: white;
	border-radius: 20rpx;
	padding: 30rpx;
}

.timeline-item {
	display: flex;
	align-items: flex-start;
	margin-bottom: 40rpx;
	position: relative;
}

.timeline-item:last-child {
	margin-bottom: 0;
}

.timeline-item:last-child::after {
	display: none;
}

.timeline-item::after {
	content: '';
	position: absolute;
	left: 16rpx;
	top: 40rpx;
	width: 2rpx;
	height: 60rpx;
	background: #E4E7ED;
}

.timeline-dot {
	width: 32rpx;
	height: 32rpx;
	background: #FF6B95;
	border-radius: 50%;
	margin-right: 24rpx;
	margin-top: 4rpx;
	flex-shrink: 0;
}

.timeline-content {
	flex: 1;
}

.event-title {
	display: block;
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
	margin-bottom: 8rpx;
}

.event-desc {
	display: block;
	font-size: 24rpx;
	color: #666;
	margin-bottom: 8rpx;
}

.event-date {
	font-size: 22rpx;
	color: #999;
}

.encouragement-section {
	margin-bottom: 40rpx;
}

.encouragement-card {
	background: linear-gradient(135deg, #FFE4E1, #FFF0F5);
	border-radius: 20rpx;
	padding: 40rpx;
	text-align: center;
}

.encouragement-text {
	font-size: 26rpx;
	color: #FF6B95;
	line-height: 1.6;
	font-weight: 500;
}
</style>
