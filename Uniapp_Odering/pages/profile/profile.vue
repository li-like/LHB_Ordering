<template>
	<view class="container">
		<!-- 用户信息卡片 -->
		<view class="user-card">
			<view class="user-header">
				<image class="user-avatar" :src="userInfo.avatarUrl || '/static/default-avatar.png'" mode="aspectFill" @click="editAvatar"></image>
				<view class="user-info">
					<text class="user-name" @click="editNickname">{{ userInfo.nickName || '家庭用户' }}</text>
					<text class="user-id">ID: {{ formatUserId(userInfo.openid) }}</text>
					<view class="user-badges">
						<text class="badge">{{ getUserRole() }}</text>
						<text class="badge member-badge">家庭成员</text>
					</view>
				</view>
				<view class="edit-profile" @click="editProfile">
					<text class="edit-icon">✏️</text>
				</view>
			</view>
		</view>

		<!-- 统计信息 -->
		<view class="stats-section">
			<view class="stats-grid">
				<view class="stat-card" @click="goToJoinedDaysDetail">
					<text class="stat-number">{{ getDaysJoined() }}</text>
					<text class="stat-label">加入天数</text>
				</view>
				<view class="stat-card" @click="goToFavoriteMealsDetail">
					<text class="stat-number">{{ getFavoriteMeals() }}</text>
					<text class="stat-label">喜爱菜品</text>
				</view>
				<view class="stat-card" @click="goToCookingDaysDetail">
					<text class="stat-number">{{ getCookingDays() }}</text>
					<text class="stat-label">下厨天数</text>
				</view>
				<view class="stat-card" @click="goToSharedRecipesDetail">
					<text class="stat-number">{{ getSharedRecipes() }}</text>
					<text class="stat-label">分享菜谱</text>
				</view>
			</view>
		</view>

		<!-- 功能菜单 -->
		<view class="menu-section">
			<view class="menu-group">
				<view class="group-title">
					<text class="title-text">个人设置</text>
				</view>
				<view class="menu-list">
					<view class="menu-item" @click="goToPreferences">
						<view class="menu-icon">
							<text class="icon-text">🍽️</text>
						</view>
						<view class="menu-info">
							<text class="menu-name">饮食偏好</text>
							<text class="menu-desc">设置口味、过敏等偏好</text>
						</view>
						<text class="menu-arrow">></text>
					</view>

					<view class="menu-item" @click="goToHistory">
						<view class="menu-icon">
							<text class="icon-text">📊</text>
						</view>
						<view class="menu-info">
							<text class="menu-name">饮食记录</text>
							<text class="menu-desc">查看我的饮食历史</text>
						</view>
						<text class="menu-arrow">></text>
					</view>

					<view class="menu-item" @click="goToRecipes">
						<view class="menu-icon">
							<text class="icon-text">📖</text>
						</view>
						<view class="menu-info">
							<text class="menu-name">我的菜谱</text>
							<text class="menu-desc">管理收藏和创建的菜谱</text>
						</view>
						<text class="menu-arrow">></text>
					</view>
				</view>
			</view>

			<view class="menu-group">
				<view class="group-title">
					<text class="title-text">应用设置</text>
				</view>
				<view class="menu-list">
					<view class="menu-item" @click="setNotifications">
						<view class="menu-icon">
							<text class="icon-text">🔔</text>
						</view>
						<view class="menu-info">
							<text class="menu-name">消息通知</text>
							<text class="menu-desc">用餐提醒、新菜谱通知</text>
						</view>
						<text class="menu-arrow">></text>
					</view>

					<view class="menu-item" @click="setPrivacy">
						<view class="menu-icon">
							<text class="icon-text">🔒</text>
						</view>
						<view class="menu-info">
							<text class="menu-name">隐私设置</text>
							<text class="menu-desc">数据安全与隐私保护</text>
						</view>
						<text class="menu-arrow">></text>
					</view>

					<view class="menu-item" @click="aboutApp">
						<view class="menu-icon">
							<text class="icon-text">ℹ️</text>
						</view>
						<view class="menu-info">
							<text class="menu-name">关于我们</text>
							<text class="menu-desc">版本信息与反馈</text>
						</view>
						<text class="menu-arrow">></text>
					</view>
				</view>
			</view>
		</view>

		<!-- 退出按钮 -->
		<view class="logout-section">
			<button class="logout-btn" @click="logout">退出登录</button>
		</view>
	</view>
</template>

<script>
import userManager from '../../utils/userManager.js'
import { AuthAPI } from '../../utils/api.js'

export default {
	data() {
		return {
			userInfo: {},
			familyData: {},
			// 添加统计信息
			stats: {
				daysJoined: 0,
				favoriteMeals: 0,
				cookingDays: 0,
				sharedRecipes: 0
			},
			// 添加标记，防止重复加载
			isDataLoaded: false,
			lastUpdateTime: 0
		}
	},
	
	onLoad() {
		this.checkLogin();
		this.loadUserData();
		
		// 注册用户信息更新监听
		userManager.onUserInfoUpdated(this.handleUserInfoUpdated);
	},
	
	onShow() {
		// 只在必要时重新加载数据
		// 如果是首次加载或者距离上次更新超过5分钟，才重新加载
		const now = Date.now();
		const shouldReload = !this.isDataLoaded || (now - this.lastUpdateTime > 5 * 60 * 1000);
		
		if (shouldReload) {
			this.checkLogin();
			this.loadUserData();
		} else {
			// 只检查登录状态，不重新加载数据
			this.checkLogin();
		}
	},
	
	onUnload() {
		// 移除用户信息更新监听
		userManager.offUserInfoUpdated(this.handleUserInfoUpdated);
	},
	
	methods: {
		// 检查登录状态
		async checkLogin() {
			if (!await userManager.isLoggedIn()) {
				uni.redirectTo({
					url: '/pages/login/login'
				});
				return;
			}
			
			// #ifdef MP-WEIXIN
			try {
				const sessionValid = await userManager.checkWechatSession();
				if (!sessionValid) {
					uni.redirectTo({
						url: '/pages/login/login'
					});
					return;
				}
			} catch (error) {
				console.error('检查微信session失败:', error);
				uni.redirectTo({
					url: '/pages/login/login'
				});
				return;
			}
			// #endif
		},
		
		// 加载用户数据
		async loadUserData() {
			console.log('userManager:', userManager);
			
			// 首先尝试从本地存储获取用户信息
			const localUserInfo = userManager.getUserInfo();
			if (localUserInfo) {
				this.userInfo = localUserInfo;
				console.log('使用本地用户信息:', localUserInfo);
			}
			
			try {
				// 尝试从后端获取最新用户数据
				const userData = await userManager.fetchUserCompleteData();
				
				// 智能合并数据：比较本地和后端的数据新旧程度
				const mergedUserInfo = this.mergeUserData(localUserInfo, userData);
				
				console.log('合并后的用户信息:', mergedUserInfo);
				this.userInfo = mergedUserInfo;
				
				// 更新本地存储以保持同步
				userManager.saveUserInfo(mergedUserInfo, true); // 使用部分更新模式

				// 获取用户统计信息
				const stats = await userManager.fetchUserStats();
				this.stats.daysJoined = stats.daysJoined;
				this.stats.favoriteMeals = stats.favoriteMeals;
				this.stats.cookingDays = stats.cookingDays;
				this.stats.sharedRecipes = stats.sharedRecipes;
				
				// 标记数据已加载
				this.isDataLoaded = true;
				this.lastUpdateTime = Date.now();
			} catch (error) {
				console.error('加载用户数据失败:', error);
				
				// 如果是403错误，说明需要重新登录
				if (error.message.includes('403')) {
					console.log('用户认证失败，可能需要重新登录');
					// 使用默认统计信息
					this.stats = {
						daysJoined: localUserInfo ? Math.floor((Date.now() - localUserInfo.loginTime) / (1000 * 60 * 60 * 24)) : 0,
						favoriteMeals: 0,
						cookingDays: 0,
						sharedRecipes: 0
					};
				}
				
				// 即使失败也标记为已尝试加载，避免重复请求
				this.isDataLoaded = true;
				this.lastUpdateTime = Date.now();
			}
		},
		
		// 智能合并本地和后端的用户数据
		mergeUserData(localData, backendData) {
			if (!localData) return backendData;
			if (!backendData) return localData;
			
			// 获取最近的活跃时间
			const localActiveTime = localData.lastActiveTime || localData.loginTime || 0;
			const backendActiveTime = backendData.lastActiveTime || backendData.loginTime || 0;
			
			// 基本策略：使用后端数据作为基础，但保留本地较新的修改
			const merged = {
				...backendData,
				// 保留本地的登录时间和活跃时间
				loginTime: localData.loginTime || backendData.loginTime,
				lastActiveTime: Math.max(localActiveTime, backendActiveTime)
			};
			
			// 对于用户可编辑的字段，优先使用较新的数据
			// 如果本地数据较新（5分钟内修改过），则优先使用本地数据
			const recentUpdateThreshold = 5 * 60 * 1000; // 5分钟
			const isLocalRecent = (Date.now() - localActiveTime) < recentUpdateThreshold;
			
			if (isLocalRecent) {
				console.log('本地数据较新，优先使用本地的昵称和头像');
				if (localData.nickName && localData.nickName !== backendData.nickName) {
					merged.nickName = localData.nickName;
				}
				if (localData.avatarUrl && localData.avatarUrl !== backendData.avatarUrl) {
					merged.avatarUrl = localData.avatarUrl;
				}
			}
			
			return merged;
		},
		
		// 强制刷新用户数据（用于特定场景）
		async forceRefreshUserData() {
			this.isDataLoaded = false;
			this.lastUpdateTime = 0;
			await this.loadUserData();
		},
		
		// 计算加入天数
		getDaysJoined() {
			return this.stats.daysJoined;
		},
		
		// 获取喜爱菜品数量
		getFavoriteMeals() {
			return this.stats.favoriteMeals;
		},
		
		// 获取下厨天数
		getCookingDays() {
			return this.stats.cookingDays;
		},
		
		// 获取分享菜谱数量
		getSharedRecipes() {
			return this.stats.sharedRecipes;
		},
		
		// 格式化用户ID
		formatUserId(openid) {
			if (!openid) return '未知';
			return openid.slice(-8).toUpperCase();
		},
		
		// 获取用户角色
		getUserRole() {
			const currentMember = this.familyData.members?.find(m => m.id === this.userInfo.openid);
			return currentMember?.role === 'admin' ? '管理员' : '普通成员';
		},
		
		// 获取加入天数
		getDaysJoined() {
			if (!this.userInfo.loginTime) return 0;
			const days = Math.floor((Date.now() - this.userInfo.loginTime) / (1000 * 60 * 60 * 24));
			return Math.max(1, days);
		},
		
		// // 获取喜爱菜品数量（模拟）
		// getFavoriteMeals() {
		// 	return Math.floor(Math.random() * 20) + 5;
		// },
		
		// // 获取下厨天数（模拟）
		// getCookingDays() {
		// 	return Math.floor(Math.random() * 30) + 10;
		// },
		
		// // 获取分享菜谱数量（模拟）
		// getSharedRecipes() {
		// 	return Math.floor(Math.random() * 10) + 2;
		// },
		
		// 编辑个人资料
		editProfile() {
			uni.showActionSheet({
				itemList: ['修改昵称', '修改头像'],
				success: (res) => {
					if (res.tapIndex === 0) {
						// 修改昵称
						this.editNickname();
					} else if (res.tapIndex === 1) {
						// 修改头像
						this.editAvatar();
					}
				},
				fail: (err) => {
					console.log('用户取消操作');
				}
			});
		},
		editNickname() {
			uni.showModal({
				title: '修改昵称',
				editable: true,
				content: this.userInfo.nickName || '',
				placeholderText: '请输入新昵称',
				success: async (res) => {
					if (res.confirm && res.content.trim()) {
						const newNickname = res.content.trim();
						if (newNickname.length > 20) {
							uni.showToast({
								title: '昵称不能超过20个字符',
								icon: 'none'
							});
							return;
						}
						
						// 检查昵称是否与当前相同
						if (newNickname === this.userInfo.nickName) {
							uni.showToast({
								title: '昵称未发生变化',
								icon: 'none'
							});
							return;
						}
						
						try {
							uni.showLoading({ title: '保存中...' });
							
							// 使用userManager的统一更新方法
							const updatedInfo = await userManager.updateUserInfo({ 
								nickName: newNickname 
							});
							
							uni.showToast({
								title: '昵称修改成功',
								icon: 'success'
							});
							
						} catch (error) {
							console.error('修改昵称失败:', error);
							uni.showToast({
								title: error.message || '修改失败，请重试',
								icon: 'none'
							});
						} finally {
							uni.hideLoading();
						}
					}
				}
			});
		},
		// 修改头像
		editAvatar() {
			uni.showActionSheet({
				itemList: ['从相册选择', '拍照'],
				success: (res) => {
					let sourceType;
					if (res.tapIndex === 0) {
						sourceType = ['album'];
					} else {
						sourceType = ['camera'];
					}
					
					uni.chooseImage({
						count: 1,
						sourceType: sourceType,
						success: (res) => {
							const tempFilePath = res.tempFilePaths[0];
							this.uploadAvatar(tempFilePath);
						},
						fail: (err) => {
							console.error('选择图片失败:', err);
							uni.showToast({
								title: '选择图片失败',
								icon: 'none'
							});
						}
					});
				}
			});
		},
		// 上传头像
		async uploadAvatar(filePath) {
			try {
				uni.showLoading({ title: '上传中...' });
				
				const userInfo = userManager.getUserInfo();
				if (!userInfo || !userInfo.openid) {
					throw new Error('用户未登录');
				}
				
				// 使用真实的文件上传接口
				const uploadResult = await AuthAPI.uploadAvatar(filePath, userInfo.openid);
				
				console.log('头像上传结果:', uploadResult);
				
				// 使用userManager的统一更新方法
				const updatedInfo = await userManager.updateUserInfo({ 
					avatarUrl: uploadResult.avatar_url 
				});
				
				uni.showToast({
					title: '头像更新成功',
					icon: 'success'
				});
				
			} catch (error) {
				console.error('上传头像失败:', error);
				uni.showToast({
					title: error.message || '上传失败，请重试',
					icon: 'none'
				});
			} finally {
				uni.hideLoading();
			}
		},
		// 更新用户信息到后端
		async updateUserInfo(updateData) {
			try {
				uni.showLoading({
					title: '保存中...'
				});
				
				// 获取当前用户信息
				const currentUserInfo = userManager.getUserInfo();
				if (!currentUserInfo || !currentUserInfo.openid) {
					throw new Error('用户未登录');
				}
				
				// 添加 openid 到更新数据中
				const dataWithOpenid = {
					...updateData,
					openid: currentUserInfo.openid
				};
				
				console.log('发送更新请求:', dataWithOpenid);
				
				// 调用 AuthAPI 更新用户信息
				const response = await AuthAPI.updateUserInfo(dataWithOpenid);
				
				console.log('后端响应:', response);
				
				// 更新本地用户信息
				const newUserInfo = {
					...currentUserInfo,
					...updateData
				};
				
				// 如果后端返回了更新后的数据，使用后端数据
				if (response.data) {
					// 注意：后端返回的字段名可能与前端不同
					if (response.data.nickname) {
						newUserInfo.nickName = response.data.nickname; // 后端是nickname，前端是nickName
					}
					if (response.data.avatar) {
						newUserInfo.avatarUrl = response.data.avatar; // 后端是avatar，前端是avatarUrl
					}
				}
				
				console.log('更新后的用户信息:', newUserInfo);
				
				// 保存到本地存储
				userManager.saveUserInfo(newUserInfo, true); // 使用部分更新模式
				
				// 更新页面显示
				this.userInfo = newUserInfo;
				
				// 更新数据加载标记，表示本地数据是最新的
				this.lastUpdateTime = Date.now();
				
				uni.showToast({
					title: '保存成功',
					icon: 'success'
				});
				
			} catch (error) {
				console.error('更新用户信息失败:', error);
				uni.showToast({
					title: error.message || '保存失败，请重试',
					icon: 'none'
				});
			} finally {
				uni.hideLoading();
			}
		},
		
		// 饮食偏好设置
		goToPreferences() {
			uni.showModal({
				title: '饮食偏好',
				content: '偏好设置功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 饮食记录
		goToHistory() {
			uni.showModal({
				title: '饮食记录',
				content: '饮食记录功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 我的菜谱
		goToRecipes() {
			uni.navigateTo({
				url: '/pages/recipe/index?mode=user'
			});
		},
		
		// 消息通知设置
		setNotifications() {
			uni.showModal({
				title: '消息通知',
				content: '通知设置功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 隐私设置
		setPrivacy() {
			uni.showModal({
				title: '隐私设置',
				content: '隐私设置功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 关于应用
		aboutApp() {
			uni.showModal({
				title: '关于家庭点餐',
				content: '版本：1.0.0\n\n一个温馨的家庭点餐小程序\n让美食连接每个家庭成员',
				showCancel: false
			});
		},
		
		// 统计详情页跳转方法
		goToJoinedDaysDetail() {
			uni.navigateTo({
				url: `/pages/profile/userStats?type=joinedDays&days=${this.getDaysJoined()}&joinTime=${this.userInfo.loginTime || Date.now()}`
			});
		},
		
		goToFavoriteMealsDetail() {
			uni.navigateTo({
				url: `/pages/profile/favoriteMeals?count=${this.getFavoriteMeals()}`
			});
		},
		
		goToCookingDaysDetail() {
			uni.navigateTo({
				url: `/pages/profile/cookingHistory?days=${this.getCookingDays()}`
			});
		},
		
		goToSharedRecipesDetail() {
			uni.navigateTo({
				url: `/pages/profile/sharedRecipes?count=${this.getSharedRecipes()}`
			});
		},
		
		// 退出登录
		logout() {
			uni.showModal({
				title: '确认退出',
				content: '确定要退出登录吗？',
				success: (res) => {
					if (res.confirm) {
						// 使用userManager清除登录状态
						userManager.logout();
						
						// 跳转到登录页面
						uni.redirectTo({
							url: '/pages/login/login'
						});
						
						uni.showToast({
							title: '已退出登录',
							icon: 'success'
						});
					}
				}
			});
		},
		
		// 处理全局用户信息更新
		handleUserInfoUpdated(newUserInfo) {
			console.log('收到用户信息更新通知:', newUserInfo);
			this.userInfo = newUserInfo;
			// 更新数据加载标记
			this.lastUpdateTime = Date.now();
		},
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #FFF5F8;
	padding-bottom: 40rpx;
}

.user-card {
	background: linear-gradient(135deg, #FF6B95, #FFB6C1);
	margin: 30rpx;
	border-radius: 24rpx;
	padding: 40rpx;
	color: white;
}

.user-header {
	display: flex;
	align-items: center;
}

.user-avatar {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	border: 3rpx solid rgba(255, 255, 255, 0.3);
	margin-right: 20rpx;
	cursor: pointer;
	transition: all 0.3s ease;
}

.user-avatar:active {
	transform: scale(0.95);
	border-color: rgba(255, 255, 255, 0.6);
}

.user-info {
	flex: 1;
}

.user-name {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	margin-bottom: 8rpx;
	cursor: pointer;
	transition: all 0.3s ease;
}

.user-name:active {
	opacity: 0.8;
	transform: scale(0.98);
}

.user-id {
	display: block;
	font-size: 22rpx;
	opacity: 0.8;
	margin-bottom: 16rpx;
}

.user-badges {
	display: flex;
	gap: 12rpx;
}

.badge {
	background: rgba(255, 255, 255, 0.2);
	padding: 6rpx 12rpx;
	border-radius: 12rpx;
	font-size: 20rpx;
}

.member-badge {
	background: rgba(255, 255, 255, 0.3);
}

.edit-profile {
	width: 60rpx;
	height: 60rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.edit-icon {
	font-size: 24rpx;
}

.stats-section {
	margin: 30rpx;
}

.stats-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
}

.stat-card {
	background: white;
	padding: 30rpx;
	border-radius: 20rpx;
	text-align: center;
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 149, 0.1);
	cursor: pointer;
	transition: all 0.3s ease;
}

.stat-card:active {
	transform: translateY(2rpx);
	box-shadow: 0 2rpx 8rpx rgba(255, 107, 149, 0.15);
}

.stat-number {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	color: #FF6B95;
	margin-bottom: 8rpx;
}

.stat-label {
	font-size: 24rpx;
	color: #666666;
}

.menu-section {
	margin: 30rpx;
}

.menu-group {
	margin-bottom: 40rpx;
}

.group-title {
	margin-bottom: 20rpx;
}

.title-text {
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
}

.menu-list {
	background: white;
	border-radius: 20rpx;
	overflow: hidden;
}

.menu-item {
	display: flex;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #F5F5F5;
}

.menu-item:last-child {
	border-bottom: none;
}

.menu-icon {
	width: 60rpx;
	height: 60rpx;
	background: #FFF0F5;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 20rpx;
}

.icon-text {
	font-size: 28rpx;
}

.menu-info {
	flex: 1;
}

.menu-name {
	display: block;
	font-size: 28rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 8rpx;
}

.menu-desc {
	font-size: 22rpx;
	color: #999999;
}

.menu-arrow {
	font-size: 24rpx;
	color: #C0C4CC;
}

.logout-section {
	margin: 60rpx 30rpx 30rpx;
}

.logout-btn {
	width: 100%;
	height: 88rpx;
	background: #FFFFFF;
	color: #FF6B95;
	border: 2rpx solid #FF6B95;
	border-radius: 44rpx;
	font-size: 28rpx;
	font-weight: 500;
	line-height: 84rpx;
}

.logout-btn:active {
	background: #FF6B95;
	color: #FFFFFF;
}
</style>
