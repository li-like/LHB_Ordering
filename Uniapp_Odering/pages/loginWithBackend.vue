<!-- 
集成后端API的登录页面示例
基于原有的 pages/login/login.vue，添加了后端API调用
您可以参考这个文件来修改原有的登录页面
-->

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
				<image class="app-logo" src="/static/logo.png" mode="aspectFit"></image>
				<text class="app-title">家庭点餐</text>
				<text class="app-subtitle">温馨家庭，美味共享</text>
			</view>
			
			<!-- 开发环境提示 -->
			<view class="dev-notice" v-if="isDevelopment">
				<text class="dev-text">🔧 开发环境模式</text>
				<text class="dev-desc">连接到Django后端: {{backendUrl}}</text>
			</view>
			
			<!-- 自动登录提示 -->
			<view class="auto-login-section" v-if="hasLoggedIn && !isLogging">
				<view class="auto-login-card">
					<image 
						class="auto-login-avatar" 
						:src="lastUserInfo.avatar_url || '/static/default-avatar.png'" 
						mode="aspectFill"
					></image>
					<text class="auto-login-text">欢迎回来, {{ lastUserInfo.nickname || '用户' }}</text>
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
				
				<!-- 开发环境测试登录 -->
				<button 
					v-if="isDevelopment"
					class="test-login-btn" 
					@click="testLogin"
					:loading="isLogging"
				>
					<view class="test-icon-wrapper">
						<text class="test-icon-text">🧪</text>
					</view>
					<text class="login-text">测试登录 (仅开发)</text>
				</button>
				
				<view class="login-tips">
					<text class="tips-text">登录即表示同意</text>
					<text class="link-text" @click="showPrivacy">《隐私政策》</text>
					<text class="tips-text">和</text>
					<text class="link-text" @click="showTerms">《服务条款》</text>
				</view>
			</view>
			
			<!-- 连接状态提示 -->
			<view class="connection-status">
				<text class="status-text" :class="[connectionStatus]">
					{{ connectionStatusText }}
				</text>
			</view>
		</view>
		
		<!-- 隐私政策弹窗 -->
		<uni-popup ref="privacyPopup" type="center">
			<view class="popup-content">
				<text class="popup-title">隐私政策</text>
				<text class="popup-text">我们重视您的隐私...</text>
				<button class="popup-btn" @click="$refs.privacyPopup.close()">知道了</button>
			</view>
		</uni-popup>
		
		<!-- 服务条款弹窗 -->
		<uni-popup ref="termsPopup" type="center">
			<view class="popup-content">
				<text class="popup-title">服务条款</text>
				<text class="popup-text">使用本服务前请仔细阅读...</text>
				<button class="popup-btn" @click="$refs.termsPopup.close()">知道了</button>
			</view>
		</uni-popup>
	</view>
</template>

<script>
	// 引入后端API集成的用户管理器
	import userManager from '@/utils/userManagerWithBackend.js'
	import { CONFIG } from '@/utils/api.js'
	
	export default {
		name: 'LoginWithBackend',
		data() {
			return {
				isLogging: false,
				hasLoggedIn: false,
				lastUserInfo: {},
				isDevelopment: CONFIG.debug,
				backendUrl: CONFIG.baseUrl,
				connectionStatus: 'checking', // checking, connected, disconnected
				connectionStatusText: '检查后端连接中...'
			}
		},
		
		onLoad() {
			console.log('登录页面加载');
			this.checkBackendConnection();
			this.checkLastLogin();
		},
		
		onShow() {
			this.updateActiveTime();
		},
		
		methods: {
			/**
			 * 检查后端连接状态
			 */
			async checkBackendConnection() {
				try {
					const response = await uni.request({
						url: `${CONFIG.baseUrl}/`,
						method: 'GET',
						timeout: 5000
					});
					
					if (response.statusCode === 200) {
						this.connectionStatus = 'connected';
						this.connectionStatusText = '✅ 后端连接正常';
					} else {
						throw new Error('连接异常');
					}
				} catch (error) {
					console.error('后端连接检查失败:', error);
					this.connectionStatus = 'disconnected';
					this.connectionStatusText = '❌ 后端连接失败';
					
					if (this.isDevelopment) {
						uni.showModal({
							title: '后端连接失败',
							content: `无法连接到Django服务器 (${CONFIG.baseUrl})。请确保后端服务器已启动。`,
							showCancel: false
						});
					}
				}
			},
			
			/**
			 * 检查上次登录信息
			 */
			checkLastLogin() {
				try {
					const userInfo = userManager.getUserInfo();
					if (userInfo && userManager.isLoggedIn()) {
						this.hasLoggedIn = true;
						this.lastUserInfo = userInfo;
						console.log('发现已登录用户:', userInfo.nickname);
					}
				} catch (error) {
					console.error('检查登录状态失败:', error);
				}
			},
			
			/**
			 * 微信登录
			 */
			async wechatLogin() {
				if (this.isLogging) return;
				
				this.isLogging = true;
				uni.showLoading({ title: '登录中...', mask: true });
				
				try {
					console.log('开始微信登录流程...');
					
					// 调用集成后端API的登录方法
					const userInfo = await userManager.wechatLogin();
					
					uni.hideLoading();
					this.isLogging = false;
					
					console.log('登录成功:', userInfo);
					
					// 登录成功提示
					uni.showToast({
						title: '登录成功',
						icon: 'success',
						duration: 1500
					});
					
					// 延迟跳转，让用户看到成功提示
					setTimeout(() => {
						this.navigateToHome();
					}, 1500);
					
				} catch (error) {
					uni.hideLoading();
					this.isLogging = false;
					
					console.error('微信登录失败:', error);
					
					uni.showModal({
						title: '登录失败',
						content: error.message || '登录过程中发生错误，请重试',
						showCancel: false,
						confirmText: '重试'
					});
				}
			},
			
			/**
			 * 测试登录（仅开发环境）
			 */
			async testLogin() {
				if (this.isLogging || !this.isDevelopment) return;
				
				this.isLogging = true;
				uni.showLoading({ title: '测试登录中...', mask: true });
				
				try {
					console.log('开始测试登录...');
					
					// 调用测试登录方法
					const userInfo = await userManager.testLogin();
					
					uni.hideLoading();
					this.isLogging = false;
					
					console.log('测试登录成功:', userInfo);
					
					uni.showToast({
						title: '测试登录成功',
						icon: 'success',
						duration: 1500
					});
					
					setTimeout(() => {
						this.navigateToHome();
					}, 1500);
					
				} catch (error) {
					uni.hideLoading();
					this.isLogging = false;
					
					console.error('测试登录失败:', error);
					
					uni.showToast({
						title: '测试登录失败: ' + error.message,
						icon: 'none',
						duration: 3000
					});
				}
			},
			
			/**
			 * 快速登录
			 */
			async quickLogin() {
				if (this.isLogging) return;
				
				this.isLogging = true;
				uni.showLoading({ title: '快速登录中...', mask: true });
				
				try {
					console.log('尝试快速登录...');
					
					// 调用快速登录方法
					const userInfo = await userManager.quickLogin();
					
					uni.hideLoading();
					this.isLogging = false;
					
					console.log('快速登录成功:', userInfo);
					
					uni.showToast({
						title: '欢迎回来',
						icon: 'success',
						duration: 1500
					});
					
					setTimeout(() => {
						this.navigateToHome();
					}, 1500);
					
				} catch (error) {
					uni.hideLoading();
					this.isLogging = false;
					
					console.error('快速登录失败:', error);
					
					// 快速登录失败，清除过期信息，显示正常登录界面
					this.hasLoggedIn = false;
					this.lastUserInfo = {};
					
					uni.showToast({
						title: '登录已过期，请重新登录',
						icon: 'none',
						duration: 2000
					});
				}
			},
			
			/**
			 * 跳转到首页
			 */
			navigateToHome() {
				uni.switchTab({
					url: '/pages/index/index',
					fail: (error) => {
						console.error('跳转失败:', error);
						// 如果switchTab失败，尝试navigateTo
						uni.navigateTo({
							url: '/pages/index/index'
						});
					}
				});
			},
			
			/**
			 * 显示隐私政策
			 */
			showPrivacy() {
				this.$refs.privacyPopup.open();
			},
			
			/**
			 * 显示服务条款
			 */
			showTerms() {
				this.$refs.termsPopup.open();
			},
			
			/**
			 * 更新用户活跃时间
			 */
			updateActiveTime() {
				if (userManager.isLoggedIn()) {
					userManager.updateActiveTime();
				}
			}
		}
	}
</script>

<style scoped>
	/* 基础样式保持原有设计 */
	.login-container {
		min-height: 100vh;
		background: linear-gradient(135deg, #FF6B95 0%, #FFE4E9 100%);
		position: relative;
		overflow: hidden;
	}
	
	/* 开发环境提示样式 */
	.dev-notice {
		background: rgba(255, 255, 255, 0.9);
		border-radius: 15px;
		padding: 10px 15px;
		margin: 20px 40px;
		border-left: 4px solid #409EFF;
	}
	
	.dev-text {
		font-size: 14px;
		color: #409EFF;
		font-weight: bold;
		display: block;
		margin-bottom: 5px;
	}
	
	.dev-desc {
		font-size: 12px;
		color: #666;
		display: block;
	}
	
	/* 测试登录按钮样式 */
	.test-login-btn {
		width: 280px;
		height: 50px;
		background: linear-gradient(45deg, #67C23A, #85CE61);
		border-radius: 25px;
		border: none;
		color: white;
		font-size: 16px;
		font-weight: bold;
		margin: 15px auto;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
	}
	
	.test-icon-wrapper {
		margin-right: 8px;
	}
	
	.test-icon-text {
		font-size: 18px;
	}
	
	/* 连接状态样式 */
	.connection-status {
		text-align: center;
		margin-top: 20px;
	}
	
	.status-text {
		font-size: 12px;
		padding: 5px 10px;
		border-radius: 10px;
	}
	
	.status-text.connected {
		color: #67C23A;
		background: rgba(103, 194, 58, 0.1);
	}
	
	.status-text.disconnected {
		color: #F56C6C;
		background: rgba(245, 108, 108, 0.1);
	}
	
	.status-text.checking {
		color: #E6A23C;
		background: rgba(230, 162, 60, 0.1);
	}
	
	/* 保持原有样式... */
	.main-content {
		padding: 50px 0;
		z-index: 10;
		position: relative;
	}
	
	.wechat-login-btn {
		width: 280px;
		height: 50px;
		background: linear-gradient(45deg, #1AAD19, #2DC653);
		border-radius: 25px;
		border: none;
		color: white;
		font-size: 16px;
		font-weight: bold;
		margin: 0 auto 20px;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 4px 12px rgba(26, 173, 25, 0.4);
	}
	
	/* 其他样式保持不变... */
</style>
