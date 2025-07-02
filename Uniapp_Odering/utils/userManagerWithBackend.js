/**
 * 集成后端API的用户管理器 - 修改版本
 * 基于原有的userManager.js，添加了Django后端API集成
 */

// 引入API配置 (需要先确保api.js存在)
import { AuthAPI, CONFIG } from './api.js'

class UserManagerWithBackend {
	constructor() {
		this.storageKey = 'userInfo';
		this.familyStorageKey = 'familyData';
		this.loginExpireDays = 7; // 登录过期天数
	}
	
	/**
	 * 检查用户是否已登录
	 * @returns {boolean}
	 */
	isLoggedIn() {
		const userInfo = this.getUserInfo();
		if (!userInfo || !userInfo.openid) {
			return false;
		}
		
		// 检查登录是否过期
		const loginTime = userInfo.loginTime || 0;
		const now = Date.now();
		const daysDiff = (now - loginTime) / (1000 * 60 * 60 * 24);
		
		if (daysDiff >= this.loginExpireDays) {
			// 登录已过期，清除数据
			this.logout();
			return false;
		}
		
		return true;
	}
	
	/**
	 * 获取用户信息
	 * @returns {Object|null}
	 */
	getUserInfo() {
		try {
			return uni.getStorageSync(this.storageKey);
		} catch (error) {
			console.error('获取用户信息失败:', error);
			return null;
		}
	}
	
	/**
	 * 微信小程序登录（集成后端API）
	 * @returns {Promise<Object>} 用户信息
	 */
	async wechatLogin() {
		try {
			console.log('开始微信登录流程...');
			
			// 1. 获取微信登录code
			const loginRes = await this.getWechatLoginCode();
			console.log('获取到微信登录码:', loginRes.code);
			
			// 2. 获取用户信息 (需要用户授权)
			const userProfileRes = await this.getWechatUserProfile();
			console.log('获取到用户信息:', userProfileRes.userInfo);
			
			// 3. 调用后端登录接口
			const backendRes = await AuthAPI.login(loginRes.code, userProfileRes.userInfo);
			console.log('后端登录成功:', backendRes.data);
			
			// 4. 保存用户信息到本地
			const userInfo = {
				...backendRes.data,
				loginTime: Date.now(),
				lastActiveTime: Date.now()
			};
			
			this.saveUserInfo(userInfo);
			
			// 5. 初始化家庭数据
			this.initFamilyData(userInfo);
			
			console.log('微信登录成功:', userInfo);
			return userInfo;
			
		} catch (error) {
			console.error('微信登录失败:', error);
			
			// 开发环境下，如果微信登录失败，使用测试登录
			if (CONFIG.debug) {
				console.log('微信登录失败，尝试测试登录...');
				return await this.testLogin();
			}
			
			throw new Error(error.message || '登录失败');
		}
	}
	
	/**
	 * 获取微信登录码
	 * @returns {Promise<Object>}
	 */
	getWechatLoginCode() {
		return new Promise((resolve, reject) => {
			uni.login({
				success: (res) => {
					if (res.code) {
						resolve(res);
					} else {
						reject(new Error('获取微信登录码失败'));
					}
				},
				fail: (err) => {
					reject(new Error(err.errMsg || '微信登录失败'));
				}
			});
		});
	}
	
	/**
	 * 获取微信用户信息
	 * @returns {Promise<Object>}
	 */
	getWechatUserProfile() {
		return new Promise((resolve, reject) => {
			uni.getUserProfile({
				desc: '用于完善用户资料',
				success: (res) => {
					resolve(res);
				},
				fail: (err) => {
					reject(new Error(err.errMsg || '获取用户信息失败'));
				}
			});
		});
	}
	
	/**
	 * 测试登录（开发环境使用）
	 * @param {string} testOpenid 测试用户标识
	 * @param {string} nickname 昵称
	 * @returns {Promise<Object>}
	 */
	async testLogin(testOpenid = null, nickname = null) {
		try {
			// 生成随机测试用户ID
			const randomId = testOpenid || `test_user_${Date.now()}`;
			const testNickname = nickname || `测试用户${Math.floor(Math.random() * 1000)}`;
			
			console.log('使用测试登录:', randomId, testNickname);
			
			// 调用后端测试登录接口
			const backendRes = await AuthAPI.testLogin(randomId, testNickname);
			console.log('测试登录成功:', backendRes.data);
			
			// 保存用户信息
			const userInfo = {
				...backendRes.data,
				loginTime: Date.now(),
				lastActiveTime: Date.now()
			};
			
			this.saveUserInfo(userInfo);
			this.initFamilyData(userInfo);
			
			return userInfo;
			
		} catch (error) {
			console.error('测试登录失败:', error);
			throw new Error('测试登录失败: ' + error.message);
		}
	}
	
	/**
	 * 快速登录（使用已保存的用户信息）
	 * @returns {Promise<Object>}
	 */
	async quickLogin() {
		try {
			const userInfo = this.getUserInfo();
			if (!userInfo || !userInfo.openid) {
				throw new Error('没有保存的用户信息');
			}
			
			// 检查登录是否过期
			if (!this.isLoggedIn()) {
				throw new Error('登录已过期');
			}
			
			console.log('尝试快速登录...');
			
			// 调用后端验证用户信息
			const backendRes = await AuthAPI.getUserInfo();
			console.log('快速登录验证成功:', backendRes.data);
			
			// 更新本地用户信息
			const updatedUserInfo = {
				...userInfo,
				...backendRes.data,
				lastActiveTime: Date.now()
			};
			
			this.saveUserInfo(updatedUserInfo);
			
			return updatedUserInfo;
			
		} catch (error) {
			console.error('快速登录失败:', error);
			// 清除过期或无效的用户信息
			this.logout();
			throw new Error('快速登录失败，请重新登录');
		}
	}
	
	/**
	 * 更新用户信息（同步到后端）
	 * @param {Object} userInfo 要更新的用户信息
	 * @returns {Promise<boolean>}
	 */
	async updateUserInfo(userInfo) {
		try {
			console.log('更新用户信息:', userInfo);
			
			// 调用后端更新接口
			await AuthAPI.updateUserInfo(userInfo);
			console.log('后端用户信息更新成功');
			
			// 更新本地存储
			const localUserInfo = this.getUserInfo() || {};
			const updatedUserInfo = {
				...localUserInfo,
				...userInfo,
				lastActiveTime: Date.now()
			};
			
			this.saveUserInfo(updatedUserInfo);
			console.log('本地用户信息更新成功');
			
			return true;
			
		} catch (error) {
			console.error('用户信息更新失败:', error);
			throw new Error('更新用户信息失败: ' + error.message);
		}
	}
	
	/**
	 * 保存用户信息到本地存储
	 * @param {Object} userInfo 用户信息
	 */
	saveUserInfo(userInfo) {
		try {
			const completeUserInfo = {
				...userInfo,
				loginTime: userInfo.loginTime || Date.now(),
				lastActiveTime: Date.now()
			};
			
			uni.setStorageSync(this.storageKey, completeUserInfo);
			console.log('用户信息保存成功');
			return true;
		} catch (error) {
			console.error('保存用户信息失败:', error);
			return false;
		}
	}
	
	/**
	 * 初始化家庭数据
	 * @param {Object} userInfo 用户信息
	 */
	initFamilyData(userInfo) {
		try {
			const existingFamilyData = uni.getStorageSync(this.familyStorageKey);
			if (!existingFamilyData) {
				const defaultFamilyData = {
					currentFamily: null,
					familyList: [],
					inviteHistory: [],
					lastSyncTime: Date.now()
				};
				uni.setStorageSync(this.familyStorageKey, defaultFamilyData);
				console.log('家庭数据初始化完成');
			}
		} catch (error) {
			console.error('家庭数据初始化失败:', error);
		}
	}
	
	/**
	 * 更新用户活跃时间
	 */
	updateActiveTime() {
		const userInfo = this.getUserInfo();
		if (userInfo) {
			userInfo.lastActiveTime = Date.now();
			uni.setStorageSync(this.storageKey, userInfo);
		}
	}
	
	/**
	 * 用户登出
	 */
	logout() {
		try {
			uni.removeStorageSync(this.storageKey);
			console.log('用户登出成功');
			
			// 可选：是否保留家庭数据
			// uni.removeStorageSync(this.familyStorageKey);
		} catch (error) {
			console.error('用户登出失败:', error);
		}
	}
	
	/**
	 * 获取家庭数据
	 * @returns {Object|null}
	 */
	getFamilyData() {
		try {
			return uni.getStorageSync(this.familyStorageKey);
		} catch (error) {
			console.error('获取家庭数据失败:', error);
			return null;
		}
	}
}

// 创建实例并导出
const userManagerWithBackend = new UserManagerWithBackend();

export default userManagerWithBackend;

// 使用示例：
/*
// 在页面中引入
import userManager from '@/utils/userManagerWithBackend.js'

// 登录
try {
  const userInfo = await userManager.wechatLogin()
  console.log('登录成功:', userInfo)
} catch (error) {
  console.error('登录失败:', error.message)
}

// 快速登录
try {
  const userInfo = await userManager.quickLogin()
  console.log('快速登录成功:', userInfo)
} catch (error) {
  console.log('需要重新登录')
}

// 更新用户信息
try {
  await userManager.updateUserInfo({
    nickname: '新昵称',
    phone: '13800138000'
  })
  console.log('用户信息更新成功')
} catch (error) {
  console.error('更新失败:', error.message)
}
*/
