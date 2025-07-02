// 用户管理器集成后端API的示例代码
// 您可以参考这段代码来修改 utils/userManager.js

const { AuthAPI, CONFIG } = require('./api.js')

/**
 * 微信小程序登录流程
 */
async function wechatLogin() {
	try {
		// 1. 获取微信登录code
		const loginRes = await uni.login()
		if (!loginRes.code) {
			throw new Error('获取微信登录码失败')
		}
		
		// 2. 获取用户信息 (需要用户授权)
		const userProfileRes = await uni.getUserProfile({
			desc: '用于完善用户资料'
		})
		
		// 3. 调用后端登录接口
		const backendRes = await AuthAPI.login(loginRes.code, userProfileRes.userInfo)
		
		// 4. 保存用户信息到本地
		const userInfo = {
			...backendRes.data,
			loginTime: Date.now()
		}
		uni.setStorageSync('userInfo', userInfo)
		
		console.log('登录成功:', userInfo)
		return userInfo
		
	} catch (error) {
		console.error('登录失败:', error)
		
		// 开发环境下，如果微信登录失败，使用测试登录
		if (CONFIG.debug) {
			console.log('使用测试登录...')
			try {
				const testRes = await AuthAPI.testLogin()
				const userInfo = {
					...testRes.data,
					loginTime: Date.now()
				}
				uni.setStorageSync('userInfo', userInfo)
				return userInfo
			} catch (testError) {
				console.error('测试登录也失败:', testError)
				throw testError
			}
		}
		
		throw error
	}
}

/**
 * 快速登录 (使用已保存的用户信息)
 */
async function quickLogin() {
	try {
		const userInfo = uni.getStorageSync('userInfo')
		if (!userInfo || !userInfo.openid) {
			throw new Error('没有保存的用户信息')
		}
		
		// 检查登录是否过期 (7天)
		const now = Date.now()
		const daysDiff = (now - userInfo.loginTime) / (1000 * 60 * 60 * 24)
		if (daysDiff >= 7) {
			throw new Error('登录已过期')
		}
		
		// 验证用户信息是否有效
		const backendRes = await AuthAPI.getUserInfo()
		
		console.log('快速登录成功:', backendRes.data)
		return backendRes.data
		
	} catch (error) {
		console.error('快速登录失败:', error)
		// 清除过期的用户信息
		uni.removeStorageSync('userInfo')
		throw error
	}
}

/**
 * 更新用户信息
 */
async function updateUserInfo(userInfo) {
	try {
		await AuthAPI.updateUserInfo(userInfo)
		
		// 更新本地存储
		const localUserInfo = uni.getStorageSync('userInfo') || {}
		const updatedUserInfo = { ...localUserInfo, ...userInfo }
		uni.setStorageSync('userInfo', updatedUserInfo)
		
		console.log('用户信息更新成功')
		return updatedUserInfo
		
	} catch (error) {
		console.error('用户信息更新失败:', error)
		throw error
	}
}

/**
 * 登出
 */
function logout() {
	uni.removeStorageSync('userInfo')
	console.log('用户已登出')
}

// 示例：在页面中使用
/*
// pages/login/login.vue
export default {
	methods: {
		async handleWechatLogin() {
			uni.showLoading({ title: '登录中...' })
			try {
				const userInfo = await wechatLogin()
				uni.hideLoading()
				
				// 登录成功，跳转到首页
				uni.switchTab({
					url: '/pages/index/index'
				})
				
				uni.showToast({
					title: '登录成功',
					icon: 'success'
				})
				
			} catch (error) {
				uni.hideLoading()
				uni.showToast({
					title: error.message || '登录失败',
					icon: 'none'
				})
			}
		},
		
		async handleQuickLogin() {
			uni.showLoading({ title: '登录中...' })
			try {
				await quickLogin()
				uni.hideLoading()
				
				// 快速登录成功，跳转到首页
				uni.switchTab({
					url: '/pages/index/index'
				})
				
			} catch (error) {
				uni.hideLoading()
				// 快速登录失败，显示正常登录界面
				console.log('需要重新登录')
			}
		}
	},
	
	onLoad() {
		// 页面加载时尝试快速登录
		this.handleQuickLogin()
	}
}
*/

module.exports = {
	wechatLogin,
	quickLogin,
	updateUserInfo,
	logout
}
