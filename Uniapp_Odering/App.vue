<script>
	import userManager from './utils/userManager.js'
	
	export default {
		onLaunch: function() {
			console.log('App Launch')
			// 应用启动时的逻辑
			this.initApp()
		},
		onShow: function() {
			console.log('App Show')
			// 应用显示时更新用户活跃时间
			if (userManager.isLoggedIn()) {
				userManager.updateActiveTime()
			}
		},
		onHide: function() {
			console.log('App Hide')
		},
		methods: {
			// 初始化应用
			initApp() {
				// 设置全局用户管理器
				uni.$userManager = userManager
				
				// 检查登录状态
				this.checkLoginStatus()
				
				// 初始化应用设置
				this.initAppSettings()
			},
			
			// 检查登录状态
			checkLoginStatus() {
				// 不在这里直接跳转，让各个页面自己处理
				const isLoggedIn = userManager.isLoggedIn()
				console.log('用户登录状态:', isLoggedIn)
				
				// 设置全局登录状态
				uni.$isLoggedIn = isLoggedIn
			},
			
			// 初始化应用设置
			initAppSettings() {
				// 设置状态栏样式
				// #ifdef MP-WEIXIN
				uni.setNavigationBarColor({
					frontColor: '#ffffff',
					backgroundColor: '#FF6B95'
				})
				// #endif
				
				// 其他初始化设置
				console.log('应用初始化完成')
			}
		}
	}
</script>

<style lang="scss">
	/* 全局公共样式 */
	@import './uni.scss';
	
	/* 重置样式 */
	page {
		background-color: #FFF5F8;
		font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', SimSun, sans-serif;
	}
	
	/* 通用按钮样式 */
	.btn-primary {
		background: linear-gradient(135deg, #FF6B95, #FFB6C1);
		color: white;
		border: none;
		border-radius: 44rpx;
		font-size: 28rpx;
		font-weight: 500;
		box-shadow: 0 8rpx 24rpx rgba(255, 107, 149, 0.3);
	}
	
	.btn-primary:active {
		transform: scale(0.98);
		box-shadow: 0 4rpx 12rpx rgba(255, 107, 149, 0.4);
	}
	
	.btn-secondary {
		background: white;
		color: #FF6B95;
		border: 2rpx solid #FF6B95;
		border-radius: 44rpx;
		font-size: 28rpx;
		font-weight: 500;
	}
	
	.btn-secondary:active {
		background: #FF6B95;
		color: white;
	}
	
	/* 通用卡片样式 */
	.card {
		background: white;
		border-radius: 20rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
		overflow: hidden;
	}
	
	/* 通用文本样式 */
	.text-primary {
		color: #FF6B95;
	}
	
	.text-secondary {
		color: #666666;
	}
	
	.text-muted {
		color: #999999;
	}
	
	/* 通用间距 */
	.mt-10 { margin-top: 10rpx; }
	.mt-20 { margin-top: 20rpx; }
	.mt-30 { margin-top: 30rpx; }
	
	.mb-10 { margin-bottom: 10rpx; }
	.mb-20 { margin-bottom: 20rpx; }
	.mb-30 { margin-bottom: 30rpx; }
	
	.ml-10 { margin-left: 10rpx; }
	.ml-20 { margin-left: 20rpx; }
	.ml-30 { margin-left: 30rpx; }
	
	.mr-10 { margin-right: 10rpx; }
	.mr-20 { margin-right: 20rpx; }
	.mr-30 { margin-right: 30rpx; }
	
	.p-10 { padding: 10rpx; }
	.p-20 { padding: 20rpx; }
	.p-30 { padding: 30rpx; }
	
	/* 通用布局 */
	.flex {
		display: flex;
	}
	
	.flex-center {
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.flex-between {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	
	.flex-column {
		display: flex;
		flex-direction: column;
	}
	
	/* 动画效果 - 微信小程序兼容版本 */
	.animate-fade-in {
		animation: fadeIn 0.3s ease-in;
	}
	
	@keyframes fadeIn {
		0% { 
			opacity: 0; 
			transform: translateY(20rpx); 
		}
		100% { 
			opacity: 1; 
			transform: translateY(0); 
		}
	}
	
	.animate-scale {
		transition: transform 0.2s ease;
	}
	
	.animate-scale:active {
		transform: scale(0.98);
	}
	
	/* 微信小程序专用样式 */
	/* #ifdef MP-WEIXIN */
	page {
		height: 100%;
		background-color: #FFF5F8;
	}
	/* #endif */
</style>
