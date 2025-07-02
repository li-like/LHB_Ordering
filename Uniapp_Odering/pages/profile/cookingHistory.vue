<template>
	<view class="container">
		<!-- 头部统计卡片 -->
		<view class="header-card">
			<view class="card-icon">
				<text class="icon">👨‍🍳</text>
			</view>
			<view class="card-info">
				<text class="title">我的下厨记录</text>
				<text class="subtitle">累计下厨 {{ cookingDays }} 天</text>
			</view>
		</view>

		<!-- 本月统计 -->
		<view class="month-stats">
			<view class="stat-card">
				<text class="stat-number">{{ thisMonthDays }}</text>
				<text class="stat-label">本月下厨</text>
			</view>
			<view class="stat-card">
				<text class="stat-number">{{ thisMonthMeals }}</text>
				<text class="stat-label">制作菜品</text>
			</view>
			<view class="stat-card">
				<text class="stat-number">{{ averageRating }}</text>
				<text class="stat-label">平均评分</text>
			</view>
		</view>

		<!-- 日历视图切换 -->
		<view class="view-toggle">
			<view class="toggle-item" :class="{ active: viewMode === 'calendar' }" @click="switchView('calendar')">
				<text class="toggle-text">日历视图</text>
			</view>
			<view class="toggle-item" :class="{ active: viewMode === 'list' }" @click="switchView('list')">
				<text class="toggle-text">列表视图</text>
			</view>
		</view>

		<!-- 日历视图 -->
		<view class="calendar-view" v-if="viewMode === 'calendar'">
			<view class="calendar-header">
				<text class="month-year">{{ currentMonth }}</text>
				<view class="nav-buttons">
					<text class="nav-btn" @click="prevMonth">‹</text>
					<text class="nav-btn" @click="nextMonth">›</text>
				</view>
			</view>
			<view class="calendar-grid">
				<view class="weekday" v-for="day in weekdays" :key="day">{{ day }}</view>
				<view class="calendar-day" 
					  v-for="day in calendarDays" 
					  :key="day.date"
					  :class="{ 
						  'has-cooking': day.hasCooking, 
						  'other-month': day.isOtherMonth,
						  'today': day.isToday 
					  }"
					  @click="viewDayDetail(day)">
					<text class="day-number">{{ day.day }}</text>
					<view class="cooking-indicator" v-if="day.hasCooking">
						<text class="indicator-dot"></text>
					</view>
				</view>
			</view>
		</view>

		<!-- 列表视图 -->
		<view class="list-view" v-if="viewMode === 'list'">
			<view class="cooking-record" v-for="record in cookingRecords" :key="record.id" @click="viewRecordDetail(record)">
				<view class="record-date">
					<text class="date-text">{{ formatDate(record.date) }}</text>
					<text class="weekday-text">{{ getWeekday(record.date) }}</text>
				</view>
				<view class="record-content">
					<view class="meals-list">
						<view class="meal-item" v-for="meal in record.meals" :key="meal.id">
							<image class="meal-thumb" :src="meal.image" mode="aspectFill"></image>
							<view class="meal-info">
								<text class="meal-name">{{ meal.name }}</text>
								<view class="meal-rating">
									<text class="rating-stars">{{ getStars(meal.rating) }}</text>
									<text class="rating-number">{{ meal.rating }}</text>
								</view>
							</view>
						</view>
					</view>
					<view class="record-summary">
						<text class="summary-text">共制作 {{ record.meals.length }} 道菜</text>
						<text class="time-spent">用时 {{ record.timeSpent }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 空状态 -->
		<view class="empty-state" v-if="cookingRecords.length === 0">
			<text class="empty-icon">🍳</text>
			<text class="empty-title">还没有下厨记录</text>
			<text class="empty-desc">开始您的第一次烹饪之旅吧～</text>
		</view>

		<!-- 成就展示 -->
		<view class="achievements-section">
			<view class="section-title">
				<text class="title-text">烹饪成就</text>
			</view>
			<view class="achievements-grid">
				<view class="achievement-item" v-for="achievement in achievements" :key="achievement.id" :class="{ unlocked: achievement.unlocked }">
					<text class="achievement-icon">{{ achievement.icon }}</text>
					<text class="achievement-name">{{ achievement.name }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			cookingDays: 0,
			viewMode: 'list', // 'calendar' 或 'list'
			currentDate: new Date(),
			weekdays: ['日', '一', '二', '三', '四', '五', '六'],
			cookingRecords: [
				{
					id: 1,
					date: new Date('2024-01-25'),
					meals: [
						{
							id: 1,
							name: '红烧肉',
							image: '/static/dishes/hongshaorou.jpg',
							rating: 4.8
						},
						{
							id: 2,
							name: '蒸蛋羹',
							image: '/static/dishes/zhengdangeng.jpg',
							rating: 4.5
						}
					],
					timeSpent: '2小时30分钟'
				},
				{
					id: 2,
					date: new Date('2024-01-23'),
					meals: [
						{
							id: 3,
							name: '清炒时蔬',
							image: '/static/dishes/qingchaoshishu.jpg',
							rating: 4.2
						}
					],
					timeSpent: '45分钟'
				},
				{
					id: 3,
					date: new Date('2024-01-20'),
					meals: [
						{
							id: 4,
							name: '宫保鸡丁',
							image: '/static/dishes/hongshaorou.jpg',
							rating: 4.6
						},
						{
							id: 5,
							name: '番茄鸡蛋',
							image: '/static/dishes/zhengdangeng.jpg',
							rating: 4.3
						}
					],
					timeSpent: '1小时45分钟'
				}
			],
			achievements: [
				{ id: 1, name: '新手厨师', icon: '🥄', unlocked: true },
				{ id: 2, name: '一周坚持', icon: '🏅', unlocked: true },
				{ id: 3, name: '月度厨神', icon: '👑', unlocked: false },
				{ id: 4, name: '完美评分', icon: '⭐', unlocked: true },
				{ id: 5, name: '多样料理', icon: '🍽️', unlocked: false },
				{ id: 6, name: '效率大师', icon: '⚡', unlocked: false }
			]
		}
	},
	
	computed: {
		currentMonth() {
			return this.currentDate.toLocaleDateString('zh-CN', {
				year: 'numeric',
				month: 'long'
			});
		},
		
		calendarDays() {
			const year = this.currentDate.getFullYear();
			const month = this.currentDate.getMonth();
			const firstDay = new Date(year, month, 1);
			const lastDay = new Date(year, month + 1, 0);
			const firstWeekday = firstDay.getDay();
			
			const days = [];
			const today = new Date();
			
			// 上个月的尾部日期
			for (let i = firstWeekday - 1; i >= 0; i--) {
				const date = new Date(year, month, -i);
				days.push({
					date: date.toDateString(),
					day: date.getDate(),
					isOtherMonth: true,
					hasCooking: this.hasCookingOnDate(date),
					isToday: false
				});
			}
			
			// 当月日期
			for (let day = 1; day <= lastDay.getDate(); day++) {
				const date = new Date(year, month, day);
				days.push({
					date: date.toDateString(),
					day: day,
					isOtherMonth: false,
					hasCooking: this.hasCookingOnDate(date),
					isToday: date.toDateString() === today.toDateString()
				});
			}
			
			// 下个月的开头日期
			const remainingCells = 42 - days.length;
			for (let day = 1; day <= remainingCells; day++) {
				const date = new Date(year, month + 1, day);
				days.push({
					date: date.toDateString(),
					day: day,
					isOtherMonth: true,
					hasCooking: this.hasCookingOnDate(date),
					isToday: false
				});
			}
			
			return days;
		},
		
		thisMonthDays() {
			const now = new Date();
			const thisMonth = now.getMonth();
			const thisYear = now.getFullYear();
			
			return this.cookingRecords.filter(record => {
				const recordDate = new Date(record.date);
				return recordDate.getMonth() === thisMonth && recordDate.getFullYear() === thisYear;
			}).length;
		},
		
		thisMonthMeals() {
			const now = new Date();
			const thisMonth = now.getMonth();
			const thisYear = now.getFullYear();
			
			return this.cookingRecords
				.filter(record => {
					const recordDate = new Date(record.date);
					return recordDate.getMonth() === thisMonth && recordDate.getFullYear() === thisYear;
				})
				.reduce((total, record) => total + record.meals.length, 0);
		},
		
		averageRating() {
			const allMeals = this.cookingRecords.flatMap(record => record.meals);
			if (allMeals.length === 0) return '0.0';
			
			const totalRating = allMeals.reduce((sum, meal) => sum + meal.rating, 0);
			return (totalRating / allMeals.length).toFixed(1);
		}
	},
	
	onLoad(options) {
		if (options.days) {
			this.cookingDays = parseInt(options.days);
		} else {
			this.cookingDays = this.cookingRecords.length;
		}
	},
	
	methods: {
		switchView(mode) {
			this.viewMode = mode;
		},
		
		prevMonth() {
			this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1);
		},
		
		nextMonth() {
			this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1);
		},
		
		hasCookingOnDate(date) {
			return this.cookingRecords.some(record => {
				const recordDate = new Date(record.date);
				return recordDate.toDateString() === date.toDateString();
			});
		},
		
		viewDayDetail(day) {
			if (!day.hasCooking) return;
			
			const record = this.cookingRecords.find(record => {
				const recordDate = new Date(record.date);
				return recordDate.toDateString() === day.date;
			});
			
			if (record) {
				this.viewRecordDetail(record);
			}
		},
		
		viewRecordDetail(record) {
			const mealNames = record.meals.map(meal => meal.name).join('、');
			const dateStr = this.formatDate(record.date);
			
			uni.showModal({
				title: `${dateStr} 的下厨记录`,
				content: `制作菜品：${mealNames}\n用时：${record.timeSpent}\n平均评分：${this.getRecordAverageRating(record)}⭐`,
				showCancel: false
			});
		},
		
		formatDate(date) {
			return new Date(date).toLocaleDateString('zh-CN', {
				month: 'long',
				day: 'numeric'
			});
		},
		
		getWeekday(date) {
			const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
			return weekdays[new Date(date).getDay()];
		},
		
		getStars(rating) {
			const fullStars = Math.floor(rating);
			return '⭐'.repeat(fullStars);
		},
		
		getRecordAverageRating(record) {
			const total = record.meals.reduce((sum, meal) => sum + meal.rating, 0);
			return (total / record.meals.length).toFixed(1);
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #FFF5F8;
}

.header-card {
	background: linear-gradient(135deg, #FF6B95, #FFB6C1);
	padding: 40rpx 30rpx;
	display: flex;
	align-items: center;
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

.month-stats {
	display: flex;
	padding: 30rpx;
	gap: 20rpx;
}

.stat-card {
	flex: 1;
	background: white;
	padding: 30rpx 20rpx;
	border-radius: 20rpx;
	text-align: center;
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 149, 0.1);
}

.stat-number {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	color: #FF6B95;
	margin-bottom: 8rpx;
}

.stat-label {
	font-size: 22rpx;
	color: #666;
}

.view-toggle {
	display: flex;
	margin: 0 30rpx 30rpx;
	background: white;
	border-radius: 50rpx;
	padding: 8rpx;
}

.toggle-item {
	flex: 1;
	text-align: center;
	padding: 16rpx;
	border-radius: 44rpx;
	transition: all 0.3s ease;
}

.toggle-item.active {
	background: #FF6B95;
}

.toggle-text {
	font-size: 24rpx;
	color: #666;
}

.toggle-item.active .toggle-text {
	color: white;
	font-weight: 500;
}

.calendar-view {
	margin: 0 30rpx 30rpx;
	background: white;
	border-radius: 20rpx;
	padding: 30rpx;
}

.calendar-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 30rpx;
}

.month-year {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
}

.nav-buttons {
	display: flex;
	gap: 20rpx;
}

.nav-btn {
	width: 60rpx;
	height: 60rpx;
	background: #FFF0F5;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 28rpx;
	color: #FF6B95;
	text-align: center;
	line-height: 60rpx;
}

.calendar-grid {
	display: grid;
	grid-template-columns: repeat(7, 1fr);
	gap: 10rpx;
}

.weekday {
	text-align: center;
	font-size: 22rpx;
	color: #999;
	padding: 20rpx 0;
	font-weight: 500;
}

.calendar-day {
	position: relative;
	text-align: center;
	padding: 20rpx 0;
	border-radius: 12rpx;
	transition: all 0.3s ease;
}

.calendar-day.has-cooking {
	background: #FFF0F5;
}

.calendar-day.other-month {
	opacity: 0.3;
}

.calendar-day.today {
	background: #FF6B95;
	color: white;
}

.day-number {
	font-size: 24rpx;
	font-weight: 500;
}

.cooking-indicator {
	position: absolute;
	bottom: 8rpx;
	left: 50%;
	transform: translateX(-50%);
}

.indicator-dot {
	width: 8rpx;
	height: 8rpx;
	background: #FF6B95;
	border-radius: 50%;
	display: block;
}

.list-view {
	padding: 0 30rpx 30rpx;
}

.cooking-record {
	background: white;
	border-radius: 20rpx;
	margin-bottom: 20rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 149, 0.1);
}

.record-date {
	background: #FFF0F5;
	padding: 20rpx 30rpx;
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.date-text {
	font-size: 28rpx;
	font-weight: bold;
	color: #FF6B95;
}

.weekday-text {
	font-size: 22rpx;
	color: #999;
}

.record-content {
	padding: 30rpx;
}

.meals-list {
	margin-bottom: 20rpx;
}

.meal-item {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.meal-item:last-child {
	margin-bottom: 0;
}

.meal-thumb {
	width: 80rpx;
	height: 80rpx;
	border-radius: 12rpx;
	margin-right: 20rpx;
}

.meal-info {
	flex: 1;
}

.meal-name {
	display: block;
	font-size: 26rpx;
	font-weight: 500;
	color: #333;
	margin-bottom: 8rpx;
}

.meal-rating {
	display: flex;
	align-items: center;
}

.rating-stars {
	font-size: 20rpx;
	margin-right: 8rpx;
}

.rating-number {
	font-size: 22rpx;
	color: #FF6B95;
	font-weight: 500;
}

.record-summary {
	display: flex;
	justify-content: space-between;
	padding-top: 20rpx;
	border-top: 1rpx solid #F5F5F5;
}

.summary-text, .time-spent {
	font-size: 22rpx;
	color: #999;
}

.empty-state {
	text-align: center;
	padding: 120rpx 60rpx;
}

.empty-icon {
	font-size: 120rpx;
	margin-bottom: 30rpx;
}

.empty-title {
	display: block;
	font-size: 32rpx;
	color: #333;
	margin-bottom: 16rpx;
}

.empty-desc {
	font-size: 24rpx;
	color: #999;
}

.achievements-section {
	margin: 30rpx;
}

.section-title {
	margin-bottom: 20rpx;
}

.title-text {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
}

.achievements-grid {
	background: white;
	border-radius: 20rpx;
	padding: 30rpx;
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 30rpx;
}

.achievement-item {
	text-align: center;
	opacity: 0.3;
}

.achievement-item.unlocked {
	opacity: 1;
}

.achievement-icon {
	display: block;
	font-size: 40rpx;
	margin-bottom: 12rpx;
}

.achievement-name {
	font-size: 20rpx;
	color: #333;
}
</style>
