<template>
	<view class="container">
		<!-- 头部统计卡片 -->
		<view class="header-card">
			<view class="card-icon">
				<text class="icon">❤️</text>
			</view>
			<view class="card-info">
				<text class="title">我的喜爱菜品</text>
				<text class="subtitle">共收藏了 {{ favoriteMealsCount }} 道美味</text>
			</view>
		</view>

		<!-- 筛选和排序 -->
		<view class="filter-section">
			<view class="filter-tabs">
				<view class="tab-item" :class="{ active: activeTab === 'all' }" @click="switchTab('all')">
					<text class="tab-text">全部</text>
				</view>
				<view class="tab-item" :class="{ active: activeTab === 'recent' }" @click="switchTab('recent')">
					<text class="tab-text">最近</text>
				</view>
				<view class="tab-item" :class="{ active: activeTab === 'popular' }" @click="switchTab('popular')">
					<text class="tab-text">最受欢迎</text>
				</view>
			</view>
		</view>

		<!-- 菜品列表 -->
		<view class="meals-section">
			<view class="meal-card" v-for="meal in filteredMeals" :key="meal.id" @click="viewMealDetail(meal)">
				<image class="meal-image" :src="meal.image" mode="aspectFill"></image>
				<view class="meal-info">
					<view class="meal-header">
						<text class="meal-name">{{ meal.name }}</text>
						<view class="meal-rating">
							<text class="rating-text">{{ meal.rating }}</text>
							<text class="star">⭐</text>
						</view>
					</view>
					<text class="meal-desc">{{ meal.description }}</text>
					<view class="meal-tags">
						<text class="tag" v-for="tag in meal.tags" :key="tag">{{ tag }}</text>
					</view>
					<view class="meal-footer">
						<text class="favorite-date">收藏于 {{ meal.favoriteDate }}</text>
						<view class="action-buttons">
							<text class="action-btn" @click.stop="removeFavorite(meal)">取消收藏</text>
							<text class="action-btn primary" @click.stop="orderMeal(meal)">立即点餐</text>
						</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 空状态 -->
		<view class="empty-state" v-if="filteredMeals.length === 0">
			<text class="empty-icon">🍽️</text>
			<text class="empty-title">暂无喜爱的菜品</text>
			<text class="empty-desc">快去首页发现更多美味吧～</text>
			<button class="explore-btn" @click="goToIndex">去点餐</button>
		</view>

		<!-- 底部统计信息 -->
		<view class="stats-footer">
			<view class="stat-item">
				<text class="stat-number">{{ getTotalTags() }}</text>
				<text class="stat-label">口味偏好</text>
			</view>
			<view class="stat-item">
				<text class="stat-number">{{ getAverageRating() }}</text>
				<text class="stat-label">平均评分</text>
			</view>
			<view class="stat-item">
				<text class="stat-number">{{ getThisMonthCount() }}</text>
				<text class="stat-label">本月新增</text>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			favoriteMealsCount: 0,
			activeTab: 'all',
			favoriteMeals: [
				{
					id: 1,
					name: '红烧肉',
					description: '肥而不腻，香甜可口的经典家常菜',
					image: '/static/dishes/hongshaorou.jpg',
					rating: 4.8,
					tags: ['家常菜', '下饭菜', '甜味'],
					favoriteDate: '2024-01-15',
					addTime: new Date('2024-01-15').getTime(),
					orderCount: 12
				},
				{
					id: 2,
					name: '清炒时蔬',
					description: '新鲜蔬菜，清淡爽口，营养丰富',
					image: '/static/dishes/qingchaoshishu.jpg',
					rating: 4.5,
					tags: ['素食', '清淡', '营养'],
					favoriteDate: '2024-01-20',
					addTime: new Date('2024-01-20').getTime(),
					orderCount: 8
				},
				{
					id: 3,
					name: '蒸蛋羹',
					description: '嫩滑香甜，老少皆宜的营养美食',
					image: '/static/dishes/zhengdangeng.jpg',
					rating: 4.7,
					tags: ['营养', '嫩滑', '易消化'],
					favoriteDate: '2024-01-25',
					addTime: new Date('2024-01-25').getTime(),
					orderCount: 15
				}
			]
		}
	},
	
	computed: {
		filteredMeals() {
			let meals = [...this.favoriteMeals];
			
			switch (this.activeTab) {
				case 'recent':
					// 按收藏时间排序
					meals.sort((a, b) => b.addTime - a.addTime);
					break;
				case 'popular':
					// 按点餐次数排序
					meals.sort((a, b) => b.orderCount - a.orderCount);
					break;
				default:
					// 默认按评分排序
					meals.sort((a, b) => b.rating - a.rating);
			}
			
			return meals;
		}
	},
	
	onLoad(options) {
		if (options.count) {
			this.favoriteMealsCount = parseInt(options.count);
		} else {
			this.favoriteMealsCount = this.favoriteMeals.length;
		}
	},
	
	methods: {
		switchTab(tab) {
			this.activeTab = tab;
		},
		
		viewMealDetail(meal) {
			uni.showModal({
				title: meal.name,
				content: `${meal.description}\n\n评分：${meal.rating}⭐\n标签：${meal.tags.join('、')}\n点餐次数：${meal.orderCount}次`,
				showCancel: true,
				cancelText: '关闭',
				confirmText: '立即点餐',
				success: (res) => {
					if (res.confirm) {
						this.orderMeal(meal);
					}
				}
			});
		},
		
		removeFavorite(meal) {
			uni.showModal({
				title: '取消收藏',
				content: `确定要取消收藏"${meal.name}"吗？`,
				success: (res) => {
					if (res.confirm) {
						const index = this.favoriteMeals.findIndex(m => m.id === meal.id);
						if (index > -1) {
							this.favoriteMeals.splice(index, 1);
							this.favoriteMealsCount--;
							uni.showToast({
								title: '已取消收藏',
								icon: 'success'
							});
						}
					}
				}
			});
		},
		
		orderMeal(meal) {
			uni.showToast({
				title: `正在为您准备${meal.name}`,
				icon: 'success'
			});
			// 这里可以跳转到点餐页面或直接下单
		},
		
		goToIndex() {
			uni.switchTab({
				url: '/pages/index/index'
			});
		},
		
		getTotalTags() {
			const allTags = this.favoriteMeals.flatMap(meal => meal.tags);
			return new Set(allTags).size;
		},
		
		getAverageRating() {
			if (this.favoriteMeals.length === 0) return '0.0';
			const total = this.favoriteMeals.reduce((sum, meal) => sum + meal.rating, 0);
			return (total / this.favoriteMeals.length).toFixed(1);
		},
		
		getThisMonthCount() {
			const now = new Date();
			const thisMonth = now.getMonth();
			const thisYear = now.getFullYear();
			
			return this.favoriteMeals.filter(meal => {
				const mealDate = new Date(meal.addTime);
				return mealDate.getMonth() === thisMonth && mealDate.getFullYear() === thisYear;
			}).length;
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

.filter-section {
	padding: 30rpx;
}

.filter-tabs {
	display: flex;
	background: white;
	border-radius: 50rpx;
	padding: 8rpx;
}

.tab-item {
	flex: 1;
	text-align: center;
	padding: 16rpx;
	border-radius: 44rpx;
	transition: all 0.3s ease;
}

.tab-item.active {
	background: #FF6B95;
}

.tab-text {
	font-size: 24rpx;
	color: #666;
}

.tab-item.active .tab-text {
	color: white;
	font-weight: 500;
}

.meals-section {
	padding: 0 30rpx;
}

.meal-card {
	background: white;
	border-radius: 20rpx;
	margin-bottom: 20rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 149, 0.1);
}

.meal-image {
	width: 100%;
	height: 300rpx;
}

.meal-info {
	padding: 30rpx;
}

.meal-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 16rpx;
}

.meal-name {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.meal-rating {
	display: flex;
	align-items: center;
}

.rating-text {
	font-size: 24rpx;
	color: #FF6B95;
	font-weight: 500;
	margin-right: 4rpx;
}

.star {
	font-size: 20rpx;
}

.meal-desc {
	font-size: 24rpx;
	color: #666;
	line-height: 1.5;
	margin-bottom: 20rpx;
}

.meal-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
	margin-bottom: 20rpx;
}

.tag {
	background: #FFF0F5;
	color: #FF6B95;
	padding: 8rpx 16rpx;
	border-radius: 16rpx;
	font-size: 20rpx;
}

.meal-footer {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.favorite-date {
	font-size: 20rpx;
	color: #999;
}

.action-buttons {
	display: flex;
	gap: 16rpx;
}

.action-btn {
	padding: 12rpx 20rpx;
	border-radius: 20rpx;
	font-size: 22rpx;
	border: 1rpx solid #FF6B95;
	color: #FF6B95;
}

.action-btn.primary {
	background: #FF6B95;
	color: white;
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
	margin-bottom: 40rpx;
}

.explore-btn {
	background: #FF6B95;
	color: white;
	border: none;
	border-radius: 50rpx;
	padding: 20rpx 60rpx;
	font-size: 26rpx;
}

.stats-footer {
	background: white;
	margin: 30rpx;
	border-radius: 20rpx;
	padding: 40rpx;
	display: flex;
	justify-content: space-around;
}

.stat-item {
	text-align: center;
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
</style>
