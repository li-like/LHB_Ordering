<template>
	<view class="container">
		<!-- 顶部用户信息栏 -->
		<view class="header">
			<view class="user-info">
				<image class="avatar" :src="userInfo.avatarUrl || '../../static/default-avatar.png'" mode="aspectFill"></image>
				<view class="greeting">
					<text class="welcome">你好，{{ userInfo.nickName || '家庭用户' }}</text>
					<text class="time-text">{{ greeting }}</text>
				</view>
			</view>
			<view class="family-info" @click="goToFamily">
				<text class="family-name">{{ familyData.familyName + '的小家' || '我的家庭' }}</text>
				<text class="member-count">{{ familyData.members?.length || 1 }}位成员</text>
				<text class="arrow">></text>
			</view>
		</view>
		
		<!-- 快速操作区域 -->
		<view class="quick-actions">
			<view class="action-item" @click="randomOrder">
				<view class="action-icon random-icon">
					<text class="icon-text">🎲</text>
				</view>
				<text class="action-label">随便来点</text>
				<text class="action-desc">不知道吃什么</text>
			</view>
			
			<view class="action-item" @click="goToRecipes">
				<view class="action-icon recipe-icon">
					<text class="icon-text">📖</text>
				</view>
				<text class="action-label">菜谱大全</text>
				<text class="action-desc">记录做菜</text>
			</view>
			
			<view class="action-item" @click="goToHistory">
				<view class="action-icon history-icon">
					<text class="icon-text">📊</text>
				</view>
				<text class="action-label">饮食记录</text>
				<text class="action-desc">查看偏好</text>
			</view>
		</view>
		
		<!-- 今日推荐 -->
		<view class="recommendation-section">
			<view class="section-header">
				<text class="section-title">今日推荐</text>
				<text class="section-subtitle">根据家庭喜好为您推荐</text>
			</view>
			
			<scroll-view class="recommendation-list" scroll-x="true" show-scrollbar="false">
				<view class="recommendation-item" v-for="(item, index) in recommendations" :key="index" @click="selectDish(item)">
					<image class="dish-image" :src="item.image" mode="aspectFill"></image>
					<view class="dish-info">
						<text class="dish-name">{{ item.name }}</text>
						<view class="dish-tags">
							<text class="tag" v-for="tag in item.tags" :key="tag">{{ tag }}</text>
						</view>
						<text class="dish-time">{{ item.cookTime }}分钟</text>
					</view>
				</view>
			</scroll-view>
		</view>
		
		<!-- 分类菜单 -->
		<view class="category-section">
			<view class="section-header">
				<text class="section-title">菜品分类</text>
			</view>
			
			<view class="category-grid">
				<view class="category-item" v-for="(category, index) in categories" :key="index" @click="selectCategory(category)">
					<view class="category-icon" :style="{ backgroundColor: category.color }">
						<text class="category-emoji">{{ category.emoji }}</text>
					</view>
					<text class="category-name">{{ category.name }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import userManager from '../../utils/userManager.js'

export default {
	data() {
		return {
			userInfo: {},
			familyData: {},
			greeting: '',
			recommendations: [
				{
					id: 1,
					name: '红烧肉',
					image: '/static/dishes/hongshaorou.jpg',
					tags: ['荤菜', '热菜', '下饭'],
					cookTime: 45
				},
				{
					id: 2,
					name: '清炒时蔬',
					image: '/static/dishes/qingchaoshishu.jpg',
					tags: ['素菜', '清淡', '健康'],
					cookTime: 15
				},
				{
					id: 3,
					name: '蒸蛋羹',
					image: '/static/dishes/zhengdangeng.jpg',
					tags: ['蛋类', '嫩滑', '营养'],
					cookTime: 20
				}
			],
			categories: [
				{ name: '荤菜', emoji: '🥩', color: '#FF6B95' },
				{ name: '素菜', emoji: '🥬', color: '#4CAF50' },
				{ name: '汤品', emoji: '🍲', color: '#2196F3' },
				{ name: '主食', emoji: '🍚', color: '#FF9800' },
				{ name: '小食', emoji: '🥟', color: '#9C27B0' },
				{ name: '甜品', emoji: '🍰', color: '#E91E63' }
			]
		}
	},
	
	onLoad() {
		this.checkLogin();
		this.loadUserData();
		this.setGreeting();
		// 注册用户信息更新监听
		this.userInfoUpdateHandler = (updatedUserInfo) => {
			console.log('index页面收到用户信息更新通知:', updatedUserInfo);
			this.userInfo = updatedUserInfo;
		};
		userManager.onUserInfoUpdated(this.userInfoUpdateHandler);
	},
	
	onShow() {
		this.checkLogin(); // 每次显示时都检查登录状态
		this.loadUserData();
		this.updateActiveTime(); // 更新用户活跃时间
	},
	
	onUnload() {
		// 移除用户信息更新监听
		if (this.userInfoUpdateHandler) {
			userManager.offUserInfoUpdated(this.userInfoUpdateHandler);
		}
	},
	
	methods: {
		// 检查登录状态
		async checkLogin() {
			if (!userManager.isLoggedIn()) {
				// 未登录，跳转到登录页
				uni.redirectTo({
					url: '/pages/login/login'
				});
				return;
			}
			
			// #ifdef MP-WEIXIN
			// 检查微信session状态
			try {
				const sessionValid = await userManager.checkWechatSession();
				if (!sessionValid) {
					// 微信session无效，但本地有登录信息，跳转到登录页进行快速登录
					console.log('微信session无效，跳转到登录页');
					uni.redirectTo({
						url: '/pages/login/login'
					});
					return;
				}
			} catch (error) {
				console.error('检查微信session失败:', error);
				// 发生错误时也跳转到登录页
				uni.redirectTo({
					url: '/pages/login/login'
				});
				return;
			}
			// #endif
		},
		
		// 加载用户数据
		async loadUserData() {
			try {
				// 优先尝试从后端获取最新数据
				if (userManager.isLoggedIn()) {
					const backendUserInfo = await userManager.fetchUserCompleteData();
					this.userInfo = backendUserInfo;
				} else {
					// 如果未登录，从本地获取
					this.userInfo = userManager.getUserInfo() || {};
				}
			} catch (error) {
				console.error('从后端加载用户数据失败，使用本地数据:', error);
				// 降级使用本地数据
				this.userInfo = userManager.getUserInfo() || {};
			}
			
			this.familyData = userManager.getFamilyData() || {};
		},
		
		// 更新用户活跃时间
		updateActiveTime() {
			if (userManager.isLoggedIn()) {
				userManager.updateActiveTime();
			}
		},
		
		// 设置问候语
		setGreeting() {
			const hour = new Date().getHours();
			if (hour < 6) {
				this.greeting = '夜深了，注意休息';
			} else if (hour < 9) {
				this.greeting = '早上好，准备早餐吧';
			} else if (hour < 12) {
				this.greeting = '上午好，元气满满';
			} else if (hour < 14) {
				this.greeting = '午餐时间到啦';
			} else if (hour < 18) {
				this.greeting = '下午好，来点下午茶';
			} else if (hour < 22) {
				this.greeting = '晚上好，准备晚餐吧';
			} else {
				this.greeting = '夜宵时间，要不要来点';
			}
		},
		
		// 随机点餐
		randomOrder() {
			uni.showModal({
				title: '随便来点',
				content: '功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 跳转到菜谱页面
		goToRecipes() {
			uni.navigateTo({
				url: '/pages/recipe/index'
			});
		},
		
		// 跳转到饮食记录
		goToHistory() {
			uni.showModal({
				title: '饮食记录',
				content: '功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 跳转到家庭管理
		goToFamily() {
			uni.switchTab({
				url: '/pages/family/family'
			});
		},
		
		// 选择菜品
		selectDish(dish) {
			uni.showModal({
				title: dish.name,
				content: `准备时间：${dish.cookTime}分钟\n标签：${dish.tags.join('、')}`,
				showCancel: false
			});
		},
		
		// 选择分类
		selectCategory(category) {
			uni.showModal({
				title: category.name,
				content: '分类菜单功能开发中，敬请期待！',
				showCancel: false
			});
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #FFF5F8;
}

.header {
	background: linear-gradient(135deg, #FF6B95, #FFB6C1);
	padding: 40rpx 30rpx 30rpx;
	border-radius: 0 0 40rpx 40rpx;
}

.user-info {
	display: flex;
	align-items: center;
	margin-bottom: 30rpx;
}

.avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	margin-right: 20rpx;
	border: 3rpx solid rgba(255, 255, 255, 0.3);
}

.greeting {
	flex: 1;
}

.welcome {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #FFFFFF;
	margin-bottom: 8rpx;
}

.time-text {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.9);
}

.family-info {
	background: rgba(255, 255, 255, 0.15);
	padding: 20rpx;
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.family-name {
	font-size: 28rpx;
	color: #FFFFFF;
	font-weight: 500;
}

.member-count {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.8);
	margin-left: 20rpx;
}

.arrow {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.quick-actions {
	padding: 40rpx 30rpx;
	display: flex;
	justify-content: space-between;
}

.action-item {
	flex: 1;
	text-align: center;
	margin: 0 15rpx;
}

.action-icon {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	margin: 0 auto 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 20rpx rgba(255, 107, 149, 0.2);
}

.random-icon {
	background: linear-gradient(135deg, #FF6B95, #FF8A80);
}

.recipe-icon {
	background: linear-gradient(135deg, #4CAF50, #66BB6A);
}

.history-icon {
	background: linear-gradient(135deg, #2196F3, #42A5F5);
}

.icon-text {
	font-size: 44rpx;
}

.action-label {
	display: block;
	font-size: 26rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 8rpx;
}

.action-desc {
	font-size: 22rpx;
	color: #999999;
}

.recommendation-section,
.category-section {
	margin: 40rpx 0;
}

.section-header {
	padding: 0 30rpx 20rpx;
}

.section-title {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 8rpx;
}

.section-subtitle {
	font-size: 24rpx;
	color: #666666;
}

.recommendation-list {
	white-space: nowrap;
	padding-left: 30rpx;
}

.recommendation-item {
	display: inline-block;
	width: 280rpx;
	background: #FFFFFF;
	border-radius: 20rpx;
	margin-right: 20rpx;
	overflow: hidden;
	box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.08);
}

.dish-image {
	width: 100%;
	height: 180rpx;
}

.dish-info {
	padding: 20rpx;
}

.dish-name {
	display: block;
	font-size: 28rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 12rpx;
}

.dish-tags {
	margin-bottom: 12rpx;
}

.tag {
	display: inline-block;
	font-size: 20rpx;
	color: #FF6B95;
	background: rgba(255, 107, 149, 0.1);
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
	margin-right: 8rpx;
}

.dish-time {
	font-size: 22rpx;
	color: #999999;
}

.category-grid {
	padding: 0 30rpx;
	display: flex;
	flex-wrap: wrap;
	justify-content: space-between;
}

.category-item {
	text-align: center;
	width: 30%;
	margin-bottom: 30rpx;
}

.category-icon {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	margin: 0 auto 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.1);
}

.category-emoji {
	font-size: 40rpx;
}

.category-name {
	font-size: 26rpx;
	color: #333333;
	font-weight: 500;
}
</style>
