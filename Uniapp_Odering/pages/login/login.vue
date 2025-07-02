<template>
	<view class="login-container">
		<!-- 顶部装饰背景 -->
		<view class="top-decoration">
			<view class="decoration-circle circle1"></view>
			<view class="decoration-circle circle2"></view>
			<view class="decoration-circle circle3"></view>
		</view>
		
		<!-- 主要内容区域 -->
		<view class="main-content">
			<!-- Logo和标题 -->
			<view class="header-section">
				<image class="app-logo" src="../../static/XiaokeLogo.png" mode="aspectFit"></image>
				<text class="app-title">家庭点餐</text>
				<text class="app-subtitle">温馨家庭，美味共享</text>
			</view>
			
			<!-- 自动登录提示 ，如果已经登录且不在登录过程中 -->
			<view class="auto-login-section" v-if="hasLoggedIn && !isLogging">
				<view class="auto-login-card">
					<image 
						class="auto-login-avatar" 
						:src="lastUserInfo.avatarUrl || '../../static/XiaokeLogo.png'" 
						mode="aspectFill"
					></image>
					<text class="auto-login-text">欢迎回来，{{ lastUserInfo.nickName}}</text>
					<button class="quick-login-btn" @click="quickLogin">
						<text class="quick-login-text">快速登录</text>
					</button>
				</view>
			</view>
			
			<!-- 登录按钮区域 -->
			<view class="login-section">
				<button 
					class="wechat-login-btn" 
					@click="wechatLogin"
					:loading="isLogging"
				>
					<view class="wechat-icon-wrapper">
						<text class="wechat-icon-text">💬</text>
					</view>
					<text class="login-text">微信一键登录</text>
				</button>
				
				<view class="login-tips">
					<text class="tips-text">登录即表示同意</text>
					<text class="link-text" @click="showPrivacy">《隐私政策》</text>
					<text class="tips-text">和</text>
					<text class="link-text" @click="showTerms">《用户协议》</text>
				</view>
			</view>
		</view>
		
		<!-- 底部装饰 -->
		<view class="bottom-decoration">
			<!-- <image class="food-decoration" src="/static/food-decoration.png" mode="aspectFit"></image> -->
		</view>
	</view>
</template>

<script>
import userManager from '../../utils/userManager.js'
import { AuthAPI } from '../../utils/api.js'
import { API, request } from '../../utils/api.js'

export default {
	data() {
		return {
			isLogging: false,
			canIUseGetUserProfile: false,
			hasLoggedIn: false,
			lastUserInfo: {} // 存储上次登录的用户信息
		}
	},
	
	async onLoad() {
		// 检查是否已经登录
		await this.checkLoginStatus();
		// 检查微信版本是否支持getUserProfile
		this.checkUserProfileSupport();
	},
	
	methods: {
		// 检查登录状态
		async checkLoginStatus() {
			const userInfo = userManager.getUserInfo();

			const isLoggedIn = await userManager.isLoggedIn();
			
			if (isLoggedIn) {
				this.hasLoggedIn = true;
				this.lastUserInfo = userInfo;
				
				// #ifdef MP-WEIXIN
				// 在微信小程序环境下检查session有效性
				userManager.checkWechatSession().then(sessionValid => {
					if (sessionValid) {
						// session有效，直接跳转
						console.log('session有效，进行快速登录');
						// this.quickLogin()
						// this.isLogging = true;
					} else {
						// session无效但本地有登录记录，显示快速登录选项
						console.log('微信session无效，但本地有登录记录，说明以前登录过，可以快速登录');
					}
				});
				// #endif
				
				// #ifndef MP-WEIXIN
				// 非微信环境直接跳转
				uni.switchTab({
					url: '/pages/index/index'
				});
				// #endif
			} else {
				// 检查是否有历史登录记录（用于显示快速登录选项）
				if (userInfo && userInfo.nickName) {
					this.hasLoggedIn = true;
					this.lastUserInfo = userInfo;
				}
			}
		},
		
		// 检查是否支持getUserProfile
	 	checkUserProfileSupport() {
			// #ifdef MP-WEIXIN
			if (uni.getUserProfile) {
				this.canIUseGetUserProfile = true;
				console.log('当前环境支持getUserProfile');
			}
			// #endif
		},
		
		// 微信登录
		async wechatLogin() {
			if (this.isLogging) return;
			this.isLogging = true;
			
			try {
				// 微信小程序环境
				// #ifdef MP-WEIXIN
				
				// 第一步：获取登录凭证
				const loginRes = await this.wxLogin();
				if (!loginRes.code) {
					throw new Error('获取登录凭证失败');
				}
				
				console.log('登录凭证获取成功:', loginRes.code);
				
				// 第二步：弹出授权确认弹窗
				let userInfo = null;
				try {
					const confirmRes = await new Promise((resolve) => {
						uni.showModal({
							title: '授权提示',
							content: '是否允许获取您的微信头像和昵称？',
							success: (res) => resolve(res)
						});
					});
					
					if (confirmRes.confirm && this.canIUseGetUserProfile) {
						// 用户同意且支持 getUserProfile 接口
						const profileRes = await uni.getUserProfile({
							desc: '用于完善会员资料',
							lang: 'zh_CN'
						});
						userInfo = profileRes.userInfo;
						console.log("用户同意授权获取用户信息,但是当前信息为测试信息", userInfo);
					} else {
						// 用户拒绝或不支持接口，使用默认信息
						userInfo = {
							nickName: '微信用户',
							avatarUrl: '../../static/logo.png'
						};
					}
				} catch (profileError) {
					console.log('获取用户信息失败，使用默认信息:', profileError);
					userInfo = {
						nickName: '微信用户',
						avatarUrl: '../../static/logo.png'
					};
				}
				
				// 第三步：发送code到后端换取用户的OpenID
				const openid = await this.getOpenid(loginRes.code);
				
				// 第四步：构建完整用户信息
				const completeUserInfo = {
					...userInfo,
					openid: openid,
					loginTime: Date.now(),
					sessionKey: 'mock_session_key', // 实际项目中由后端返回
					unionId: '', // 如果有开放平台账号
					code: loginRes.code
				};
				
				// 第五步：保存用户信息并初始化数据
				await this.saveUserInfo(completeUserInfo);
				
				// 登录成功，跳转首页
				uni.showToast({
					title: '登录成功',
					icon: 'success',
					duration: 1500
				});
				
				setTimeout(() => {
					uni.switchTab({
						url: '/pages/index/index'
					});
				}, 1500);
				
				// #endif
				
				// #ifndef MP-WEIXIN
				// 非微信环境的模拟登录
				await this.mockLogin();
				// #endif
				
			} catch (error) {
				console.error('登录失败:', error);
				this.handleLoginError(error);
			} finally {
				this.isLogging = false;
			}
		},
		
		// 微信登录凭证获取
		wxLogin() {
			return new Promise((resolve, reject) => {
				uni.login({
					provider: 'weixin',
					success: (res) => {
						resolve(res);
					},
					fail: (err) => {
						reject(err);
					}
				});
			});
		},
		
		// 获取用户信息
		wxGetUserProfile() {
			return new Promise((resolve, reject) => {
				uni.getUserProfile({
					desc: '用于完善用户资料',
					success: (res) => {
						resolve(res);
					},
					fail: (err) => {
						reject(err);
					}
				});
			});
		},
		
		

		// 获取openid，调用后端接口发送code换取OpenID
		async getOpenid(code) {
			try {
				const response = await request(API.auth.login, 'POST', { code });
				if (response && response.openid) {
					return response.openid;
				}
				throw new Error('获取openid失败');
			} catch (error) {
				console.error('获取openid失败:', error);
				throw error;
			}
			// 实际项目中的代码示例：
			// const response = await uni.request({
			//     url: 'https://your-api.com/wechat/login',
			//     method: 'POST',
			//     data: { code: code }
			// });
			// return response.data.openid;
			
			// 当前使用模拟数据
			// return 'wx_openid_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
		},
		
		// 检测是否为测试/默认数据
		isTestData(userInfo) {
			if (!userInfo) return true;
			
			// 定义测试数据特征
			const testNicknames = ['微信用户', '可乐', 'User', 'WeChat User'];
			const testAvatarPatterns = [
				'../../static/logo.png',
				'/static/default-avatar.png',
				'/static/logo.png',
				'default-avatar',
				'logo.png'
			];
			
			// 检查昵称是否为测试数据
			const isTestNickname = testNicknames.includes(userInfo.nickName);
			
			// 检查头像是否为测试数据
			const isTestAvatar = testAvatarPatterns.some(pattern => 
				userInfo.avatarUrl && userInfo.avatarUrl.includes(pattern)
			);
			
			const result = isTestNickname || isTestAvatar;
			if (result) {
				console.log('检测到测试数据:', {
					nickName: userInfo.nickName,
					avatarUrl: userInfo.avatarUrl,
					isTestNickname,
					isTestAvatar
				});
			}
			
			return result;
		},
		
		// 保存用户信息
		async saveUserInfo(userInfo) {
			try {
				// 检查是否为重新登录（本地已有用户数据）
				const existingUserInfo = userManager.getUserInfo();
				let finalUserInfo = userInfo;
				let isReLogin = false;
				let usePartialUpdate = false;
				
				if (existingUserInfo && existingUserInfo.openid === userInfo.openid) {
					// 是同一用户重新登录
					isReLogin = true;
					console.log('检测到同一用户重新登录，开始智能数据合并');
					
					// 检查当前登录获取的是否为测试数据
					const isCurrentDataTest = this.isTestData(userInfo);
					
					if (isCurrentDataTest) {
						console.log('当前登录数据为测试数据，优先使用已保存的用户自定义信息');
						
						try {
							// 尝试从后端获取最新用户信息
							const backendUserInfo = await AuthAPI.getUserInfo();
							console.log('从后端获取到用户信息:', backendUserInfo);
							
							// 使用后端保存的自定义信息，忽略测试数据
							finalUserInfo = {
								...userInfo,           // 基础登录信息（openid, loginTime等）
								nickName: backendUserInfo.nickName || existingUserInfo.nickName || '家庭用户',
								avatarUrl: backendUserInfo.avatarUrl || existingUserInfo.avatarUrl || '/static/default-avatar.png',
								// 保留后端的其他自定义信息
								...(backendUserInfo.preferences && { preferences: backendUserInfo.preferences }),
								...(backendUserInfo.settings && { settings: backendUserInfo.settings })
							};
							
							console.log('使用后端数据合并成功:', finalUserInfo);
						} catch (backendError) {
							console.warn('从后端获取用户信息失败，使用本地数据合并:', backendError);
							
							// 后端获取失败，使用本地保存的自定义信息，完全忽略测试数据
							finalUserInfo = {
								...userInfo,                    // 基础登录信息
								nickName: existingUserInfo.nickName || '家庭用户',
								avatarUrl: existingUserInfo.avatarUrl || '/static/default-avatar.png',
								// 保留本地的其他信息
								preferences: existingUserInfo.preferences,
								settings: existingUserInfo.settings
							};
						}
						
						// 重新登录且是测试数据时，使用部分更新保持原有loginTime相关信息
						usePartialUpdate = true;
						
					} else {
						console.log('当前登录数据为真实微信数据，进行正常合并');
						
						try {
							// 获取后端数据进行智能合并
							const backendUserInfo = await AuthAPI.getUserInfo();
							
							// 真实微信数据与后端数据的智能合并
							finalUserInfo = {
								...userInfo,           // 基础登录信息和真实微信数据
								...backendUserInfo,    // 后端保存的自定义信息（如果用户修改过）
								openid: userInfo.openid,
								loginTime: userInfo.loginTime,
								code: userInfo.code,
								// 如果后端有更新的昵称/头像，优先使用后端的
								nickName: backendUserInfo.nickName || userInfo.nickName,
								avatarUrl: backendUserInfo.avatarUrl || userInfo.avatarUrl
							};
							
							console.log('真实数据合并成功:', finalUserInfo);
						} catch (backendError) {
							console.warn('从后端获取用户信息失败，使用微信数据:', backendError);
							// 后端失败时使用微信数据，但尽量保留本地的自定义信息
							finalUserInfo = {
								...userInfo,
								// 如果本地有自定义的昵称/头像且不是测试数据，保留它们
								nickName: (!this.isTestData(existingUserInfo) && existingUserInfo.nickName !== userInfo.nickName) 
										  ? existingUserInfo.nickName : userInfo.nickName,
								avatarUrl: (!this.isTestData(existingUserInfo) && existingUserInfo.avatarUrl !== userInfo.avatarUrl) 
										   ? existingUserInfo.avatarUrl : userInfo.avatarUrl
							};
						}
					}
				} else {
					console.log('首次登录或不同用户，使用完整登录流程');
					// 首次登录，正常保存数据
					finalUserInfo = userInfo;
				}
				
				// 根据情况选择更新模式
				// 重新登录且是测试数据时使用部分更新，其他情况使用完整更新
				const success = userManager.saveUserInfo(finalUserInfo, usePartialUpdate);
				if (!success) {
					throw new Error('保存用户信息失败');
				}
				
				console.log(`用户信息保存成功 (${usePartialUpdate ? '部分更新' : '完整更新'}):`, finalUserInfo);
			} catch (error) {
				console.error('保存用户信息失败:', error);
				throw error;
			}
		},
		
		// 模拟登录（开发环境）
		async mockLogin() {
			const mockUserInfo = {
				nickName: '家庭用户' + Math.floor(Math.random() * 100),
				avatarUrl: '/static/default-avatar.png',
				openid: 'mock_openid_' + Date.now(),
				loginTime: Date.now(),
				sessionKey: 'mock_session_key',
				unionId: '',
				code: 'mock_code'
			};
			
			// 模拟登录也应用相同的智能保存逻辑
			await this.saveUserInfo(mockUserInfo);
			
			uni.showToast({
				title: '模拟登录成功',
				icon: 'success',
				duration: 1500
			});
			
			setTimeout(() => {
				uni.switchTab({
					url: '/pages/index/index'
				});
			}, 1500);
		},
		
		// 处理登录错误
		handleLoginError(error) {
			let errorMessage = '登录失败，请重试';
			let showRetryButton = true;
			
			if (error.errMsg) {
				if (error.errMsg.includes('getUserProfile:fail auth deny')) {
					errorMessage = '您取消了授权，可稍后重试';
					showRetryButton = true;
				} else if (error.errMsg.includes('login:fail')) {
					errorMessage = '网络连接失败，请检查网络后重试';
					showRetryButton = true;
				} else if (error.errMsg.includes('timeout')) {
					errorMessage = '网络超时，请重试';
					showRetryButton = true;
				} else if (error.errMsg.includes('scope unauthorized')) {
					errorMessage = '未授权访问，请重新授权';
					showRetryButton = true;
				} else {
					errorMessage = '登录异常: ' + error.errMsg;
					showRetryButton = false;
				}
			} else if (error.message) {
				errorMessage = error.message;
			}
			
			const modalOptions = {
				title: '登录失败',
				content: errorMessage,
				showCancel: showRetryButton,
				cancelText: '稍后再试',
				confirmText: showRetryButton ? '重新登录' : '确定',
				success: (res) => {
					if (res.confirm && showRetryButton) {
						// 用户选择重新登录
						setTimeout(() => {
							this.wechatLogin();
						}, 500);
					}
				}
			};
			
			uni.showModal(modalOptions);
		},
		
		// 初始化家庭数据 - 已迁移到userManager中
		// initFamilyData方法已被userManager.initFamilyData替代
		
		// 显示隐私政策
		showPrivacy() {
			uni.showModal({
				title: '隐私政策',
				content: '我们重视您的隐私，仅会收集必要的用户信息用于提供服务。',
				showCancel: false
			});
		},
		
		// 显示用户协议
		showTerms() {
			uni.showModal({
				title: '用户协议',
				content: '欢迎使用家庭点餐小程序，请遵守相关使用规定。',
				showCancel: false
			});
		},
		
		// 快速登录
		async quickLogin() {
			this.isLogging = true;
			console.log('开始快速登录');
			
			try {
				const isLoggedIn = await userManager.isLoggedIn();
				// 检查本地登录状态
				if (!isLoggedIn) {
					console.log('用户未登录，执行完整登录流程');
					await this.wechatLogin();
					return;
				}
				console.log('用户已登录，继续快速登录流程');
				
				// #ifdef MP-WEIXIN
				// 检查微信session状态
				const sessionValid = await userManager.checkWechatSession();
				
				if (sessionValid) {
					// session有效，直接跳转
					uni.showToast({
						title: '登录成功',
						icon: 'success',
						duration: 1000
					});
					
					// 更新活跃时间
					userManager.updateActiveTime();
					
					setTimeout(() => {
						uni.switchTab({
							url: '/pages/index/index'
						});
					}, 1000);
				} else {
					// session无效，重新登录
					uni.showToast({
						title: '登录状态已过期，重新登录中...',
						icon: 'loading',
						duration: 1000
					});
					setTimeout(async () => {
						await this.wechatLogin();
					}, 1000);
				}
				// #endif
				
				// #ifndef MP-WEIXIN
				// 非微信环境直接跳转
				userManager.updateActiveTime();
				uni.switchTab({
					url: '/pages/index/index'
				});
				// #endif
				
			} catch (error) {
				console.error('快速登录失败:', error);
				// 失败时执行完整登录流程
				uni.showToast({
					title: '快速登录失败，正在重新登录...',
					icon: 'loading',
					duration: 1500
				});
				setTimeout(async () => {
					await this.wechatLogin();
				}, 1500);
			} finally {
				this.isLogging = false;
			}
		},
		
	}
}
</script>

<style scoped>
.login-container {
	min-height: 100vh;
	background: linear-gradient(135deg, #FF6B95 0%, #FFB6C1 50%, #FFF0F5 100%);
	position: relative;
	overflow: hidden;
}

.top-decoration {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 300rpx;
}

.decoration-circle {
	position: absolute;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.1);
}

.circle1 {
	width: 200rpx;
	height: 200rpx;
	top: -100rpx;
	right: 100rpx;
	animation: float 6s ease-in-out infinite;
}

.circle2 {
	width: 150rpx;
	height: 150rpx;
	top: 50rpx;
	left: 50rpx;
	animation: float 4s ease-in-out infinite reverse;
}

.circle3 {
	width: 100rpx;
	height: 100rpx;
	top: 150rpx;
	right: 300rpx;
	animation: float 5s ease-in-out infinite;
}

@keyframes float {
	0%, 100% { transform: translateY(0px); }
	50% { transform: translateY(-20px); }
}

.main-content {
	padding: 200rpx 60rpx 100rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	min-height: calc(100vh - 300rpx);
}

.header-section {
	text-align: center;
	margin-bottom: 200rpx;
}

.app-logo {
	width: 180rpx;
	height: 180rpx;
	border-radius: 50%;
	box-shadow: 0 10rpx 30rpx rgba(255, 107, 149, 0.3);
	margin-bottom: 40rpx;
}

.app-title {
	display: block;
	font-size: 48rpx;
	font-weight: bold;
	color: #FFFFFF;
	margin-bottom: 16rpx;
	text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.1);
}

.app-subtitle {
	display: block;
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.9);
	line-height: 1.4;
}

/* 自动登录样式 */
.auto-login-section {
	width: 100%;
	max-width: 500rpx;
	margin-bottom: 40rpx;
}

.auto-login-card {
	background: rgba(255, 255, 255, 0.9);
	border-radius: 24rpx;
	padding: 40rpx;
	text-align: center;
	backdrop-filter: blur(10rpx);
	border: 1rpx solid rgba(255, 255, 255, 0.3);
}

.auto-login-avatar {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
	margin-bottom: 20rpx;
}

.auto-login-text {
	display: block;
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 30rpx;
}

.quick-login-btn {
	width: 100%;
	height: 72rpx;
	background: linear-gradient(135deg, #FF6B95, #FFB6C1);
	border-radius: 36rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border: none;
	box-shadow: 0 6rpx 20rpx rgba(255, 107, 149, 0.3);
	transition: all 0.3s ease;
}

.quick-login-btn:active {
	transform: scale(0.98);
	box-shadow: 0 3rpx 10rpx rgba(255, 107, 149, 0.4);
}

.quick-login-text {
	font-size: 28rpx;
	color: #FFFFFF;
	font-weight: 500;
}

.login-section {
	width: 100%;
	max-width: 500rpx;
}

.wechat-login-btn {
	width: 100%;
	height: 88rpx;
	background: #FFFFFF;
	border-radius: 44rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
	border: none;
	margin-bottom: 40rpx;
	transition: all 0.3s ease;
}

.wechat-login-btn:active {
	transform: scale(0.98);
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
}

.wechat-icon-wrapper {
	width: 40rpx;
	height: 40rpx;
	margin-right: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.wechat-icon-text {
	font-size: 32rpx;
	color: #07C160;
}

.login-text {
	font-size: 32rpx;
	color: #333333;
	font-weight: 500;
}

.login-tips {
	text-align: center;
	line-height: 1.6;
}

.tips-text {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.link-text {
	font-size: 24rpx;
	color: #FFFFFF;
	text-decoration: underline;
}

.bottom-decoration {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	height: 200rpx;
	display: flex;
	justify-content: center;
	align-items: flex-end;
}

.food-decoration {
	width: 300rpx;
	height: 150rpx;
	opacity: 0.3;
}
</style>
