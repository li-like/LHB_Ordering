/**
 * 用户信息管理工具类
 * 统一管理用户登录状态、用户信息存储等功能
 */
import { AuthAPI } from './api';
class UserManager {
	constructor() {
		this.storageKey = 'userInfo';//用于存储用户信息的本地存储键名。
		this.familyStorageKey = 'familyData';//用于存储家庭数据的本地存储键名
		this.loginExpireDays = 7; // 登录过期天数
		this.updateCallbacks = []; // 用户信息更新回调函数列表
	}
	
	/**
	 * 检查用户是否已登录
	 * @returns {boolean}
	 */
	async isLoggedIn() {
		const userInfo = this.getUserInfo();//获取用户信息
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
	
		try {
			// 验证后端登录状态并获取最新用户信息
			console.log('AuthAPI_login:', AuthAPI);
			const res = await AuthAPI.getUserInfo();
			
			// 合并后端数据与本地数据，优先使用后端的最新数据
			const mergedUserInfo = {
				...userInfo, // 保留本地的loginTime等字段
				...res,      // 覆盖后端的最新数据
				openid: userInfo.openid, // 确保openid不被覆盖
				loginTime: userInfo.loginTime // 保持原有登录时间
			};
			
			// 部分更新本地存储，不重置loginTime
			this.saveUserInfo(mergedUserInfo, true);
			return true;
		} catch (error) {
			console.error('验证后端登录状态失败:', error);
			// 如果后端验证失败，但本地有有效登录信息，仍然认为已登录
			// 这样可以支持离线使用
			return true;
		}
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
	 * 保存用户信息
	 * @param {Object} userInfo 用户信息
	 * @param {boolean} isPartialUpdate 是否为部分更新（默认false）
	 */
	saveUserInfo(userInfo, isPartialUpdate = false) {
		try {
			let completeUserInfo;
			
			if (isPartialUpdate) {
				// 部分更新：合并现有信息，保持关键字段不变
				const existingInfo = this.getUserInfo() || {};
				completeUserInfo = {
					...existingInfo,
					...userInfo,
					lastActiveTime: Date.now(),
					// 保持原有的loginTime，除非明确要更新
					loginTime: existingInfo.loginTime || userInfo.loginTime || Date.now(),
					// 确保openid不丢失
					openid: userInfo.openid || existingInfo.openid
				};
				console.log('部分更新用户信息，保持原有登录时间:', existingInfo.loginTime);
			} else {
				// 完整更新：使用新的loginTime
				completeUserInfo = {
					...userInfo,
					loginTime: Date.now(),
					lastActiveTime: Date.now()
				};
				console.log('完整更新用户信息，重置登录时间');
			}
			
			uni.setStorageSync(this.storageKey, completeUserInfo);
			
			// 只在完整更新时初始化家庭数据
			if (!isPartialUpdate) {
				this.initFamilyData(completeUserInfo);
			}
			
			// 触发全局用户信息更新事件
			this.notifyUserInfoUpdated(completeUserInfo);
			
			console.log('用户信息保存成功', isPartialUpdate ? '(部分更新)' : '(完整更新)');
			return true;
		} catch (error) {
			console.error('保存用户信息失败:', error);
			return false;
		}
	}
	
	/**
	 * 确保用户已通过后端认证
	 */
	async ensureBackendAuth() {
		const userInfo = this.getUserInfo();
		if (!userInfo || !userInfo.openid) {
			throw new Error('用户未登录');
		}
		
		// 由于后端已经修改为基于 openid 的简单认证，这里只需要确保有 openid
		console.log('用户认证检查通过:', userInfo.openid);
		return true;
	}

	/**
	 * 异步获取用户完整数据，包含统计信息
	 */
	async fetchUserCompleteData() {
		try {
			// 先检查本地是否有基本的登录信息
			const localUserInfo = this.getUserInfo();
			if (!localUserInfo || !localUserInfo.openid) {
				throw new Error('用户未登录');
			}
			
			// 确保用户已通过后端认证
			await this.ensureBackendAuth();
			
			console.log('AuthAPI:', AuthAPI);
			// 获取后端最新用户数据
			const userData = await AuthAPI.getUserInfo();
			
			// 合并本地信息和后端数据
			const completeUserInfo = {
				...localUserInfo,  // 保留本地的loginTime等字段
				...userData,       // 覆盖后端的最新数据
				openid: localUserInfo.openid, // 确保openid不丢失
				loginTime: localUserInfo.loginTime // 保持登录时间
			};
			
			// 部分更新本地存储
			this.saveUserInfo(completeUserInfo, true);
			
			// 可以扩展获取其他统计信息，如喜爱菜品数量、下厨天数等
			// 假设后端提供了对应接口
			// completeUserInfo.favoriteMeals = await AuthAPI.getFavoriteMealsCount();
			// completeUserInfo.cookingDays = await AuthAPI.getCookingDaysCount();
			// completeUserInfo.sharedRecipes = await AuthAPI.getSharedRecipesCount();

			return completeUserInfo;
		} catch (error) {
			console.error('获取用户完整数据失败:', error);
			// 如果后端获取失败，返回本地数据
			const localUserInfo = this.getUserInfo();
			if (localUserInfo) {
				return localUserInfo;
			}
			throw error;
		}
	}

	/**
	 * 获取用户统计信息
	 */
	async fetchUserStats() {
		try {
			// 首先确保后端认证
			await this.ensureBackendAuth();
			
			console.log('AuthAPI:', AuthAPI);
			// 获取用户统计信息
			const stats = await AuthAPI.getUserStats();
			return stats;
		} catch (error) {
			console.error('获取用户统计信息失败:', error);
			// 返回默认统计信息
			return {
				daysJoined: 0,
				favoriteMeals: 0,
				cookingDays: 0,
				sharedRecipes: 0
			};
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
			// 可选：是否保留家庭数据
			// uni.removeStorageSync(this.familyStorageKey);
			console.log('用户登出成功');
		} catch (error) {
			console.error('用户登出失败:', error);
		}
	}
	
	/**
	 * 初始化家庭数据
	 * @param {Object} userInfo 用户信息
	 */
	initFamilyData(userInfo) {
		try {
			const existingFamily = uni.getStorageSync(this.familyStorageKey);
			if (existingFamily && existingFamily.familyId) {
				// 检查当前用户是否已在家庭中
				const isMember = existingFamily.members.some(member => member.id === userInfo.openid);
				if (!isMember) {
					// 将当前用户添加到现有家庭
					existingFamily.members.push({
						id: userInfo.openid,
						name: userInfo.nickName,
						avatar: userInfo.avatarUrl,
						role: 'member',
						joinTime: Date.now(),
						preferences: {
							taste: [],
							allergies: [],
							dislikes: []
						}
					});
					uni.setStorageSync(this.familyStorageKey, existingFamily);
				}
				return;
			}
			
			// 创建新的家庭数据
			const familyData = {
				familyId: 'family_' + Date.now(),
				familyName: userInfo.nickName + '的家庭',
				createTime: Date.now(),
				members: [
					{
						id: userInfo.openid,
						name: userInfo.nickName,
						avatar: userInfo.avatarUrl,
						role: 'admin', // 创建者为管理员
						joinTime: Date.now(),
						preferences: {
							taste: ['清淡', '家常'],
							allergies: [],
							dislikes: []
						}
					}
				],
				settings: {
					mealTimes: {
						breakfast: '08:00',
						lunch: '12:00',
						dinner: '18:00'
					},
					preferences: {
						spicyLevel: 'medium',
						cookingStyle: 'home',
						dietType: 'normal'
					}
				}
			};
			
			uni.setStorageSync(this.familyStorageKey, familyData);
			console.log('家庭数据初始化成功');
		} catch (error) {
			console.error('初始化家庭数据失败:', error);
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
	
	/**
	 * 更新家庭数据
	 * @param {Object} familyData 家庭数据
	 */
	saveFamilyData(familyData) {
		try {
			uni.setStorageSync(this.familyStorageKey, familyData);
			return true;
		} catch (error) {
			console.error('保存家庭数据失败:', error);
			return false;
		}
	}
	
	/**
	 * 检查微信登录session是否有效
	 * @returns {Promise<boolean>}
	 */
	checkWechatSession() {
		return new Promise((resolve) => {
			// #ifdef MP-WEIXIN
			uni.checkSession({
				success: () => {
					console.log('微信session有效');
					resolve(true);
				},
				fail: () => {
					console.log('微信session无效');
					resolve(false);
				}
			});
			// #endif
			
			// #ifndef MP-WEIXIN
			resolve(true);
			// #endif
		});
	}
	
	/**
	 * 静默登录 - 尝试使用现有session自动登录
	 * @returns {Promise<Object>} 返回登录结果
	 */
	async silentLogin() {
		try {
			// 检查本地登录状态
			if (!this.isLoggedIn()) {
				return { success: false, reason: 'no_local_login' };
			}
			
			// #ifdef MP-WEIXIN
			// 检查微信session
			const sessionValid = await this.checkWechatSession();
			if (!sessionValid) {
				return { success: false, reason: 'session_expired' };
			}
			
			// 更新活跃时间
			this.updateActiveTime();
			return { success: true, reason: 'session_valid' };
			// #endif
			
			// #ifndef MP-WEIXIN
			this.updateActiveTime();
			return { success: true, reason: 'local_valid' };
			// #endif
			
		} catch (error) {
			console.error('静默登录失败:', error);
			return { success: false, reason: 'error', error };
		}
	}
	
	/**
	 * 微信自动登录 - 获取新的登录凭证
	 * @returns {Promise<Object>}
	 */
	async wechatAutoLogin() {
		return new Promise((resolve, reject) => {
			// #ifdef MP-WEIXIN
			uni.login({
				provider: 'weixin',
				success: (loginRes) => {
					if (loginRes.code) {
						console.log('微信登录凭证获取成功:', loginRes.code);
						resolve({
							success: true,
							code: loginRes.code,
							reason: 'code_obtained'
						});
					} else {
						reject(new Error('获取登录凭证失败'));
					}
				},
				fail: (error) => {
					console.error('微信登录凭证获取失败:', error);
					reject(error);
				}
			});
			// #endif
			
			// #ifndef MP-WEIXIN
			resolve({
				success: true,
				code: 'mock_code_' + Date.now(),
				reason: 'mock_login'
			});
			// #endif
		});
	}
	
	/**
	 * 获取用户角色
	 * @returns {string}
	 */
	getUserRole() {
		const userInfo = this.getUserInfo();
		const familyData = this.getFamilyData();
		
		if (!userInfo || !familyData) {
			return 'guest';
		}
		
		const member = familyData.members.find(m => m.id === userInfo.openid);
		return member ? member.role : 'guest';
	}
	
	/**
	 * 检查用户权限
	 * @param {string} permission 权限名称
	 * @returns {boolean}
	 */
	hasPermission(permission) {
		const role = this.getUserRole();
		
		const permissions = {
			admin: ['all'],
			member: ['view', 'order', 'comment'],
			guest: ['view']
		};
		
		const userPermissions = permissions[role] || [];
		return userPermissions.includes('all') || userPermissions.includes(permission);
	}
	
	/**
	 * 注册用户信息更新回调
	 * @param {Function} callback 回调函数
	 */
	onUserInfoUpdated(callback) {
		if (typeof callback === 'function') {
			this.updateCallbacks.push(callback);
		}
	}
	
	/**
	 * 移除用户信息更新回调
	 * @param {Function} callback 要移除的回调函数
	 */
	offUserInfoUpdated(callback) {
		const index = this.updateCallbacks.indexOf(callback);
		if (index > -1) {
			this.updateCallbacks.splice(index, 1);
		}
	}
	
	/**
	 * 通知所有监听者用户信息已更新
	 * @param {Object} userInfo 更新后的用户信息
	 */
	notifyUserInfoUpdated(userInfo) {
		this.updateCallbacks.forEach(callback => {
			try {
				callback(userInfo);
			} catch (error) {
				console.error('用户信息更新回调执行失败:', error);
			}
		});
	}
	
	/**
	 * 检查昵称是否已存在
	 * @param {string} nickname 要检查的昵称
	 * @param {string} currentOpenid 当前用户的openid（可选，用于排除自己）
	 * @returns {Promise<boolean>} 昵称是否可用
	 */
	async checkNicknameAvailable(nickname, currentOpenid = null) {
		try {
			if (!nickname || nickname.trim() === '') {
				return false;
			}
			
			// 调用后端接口检查昵称
			const response = await AuthAPI.checkNickname({
				nickname: nickname.trim(),
				exclude_openid: currentOpenid
			});
			
			return response.available === true;
		} catch (error) {
			console.error('检查昵称可用性失败:', error);
			// 如果后端检查失败，暂时允许使用
			return true;
		}
	}
	
	/**
	 * 更新用户信息（包含重复检查）
	 * @param {Object} updateData 要更新的数据
	 * @returns {Promise<Object>} 更新后的用户信息
	 */
	async updateUserInfo(updateData) {
		try {
			const currentUserInfo = this.getUserInfo();
			if (!currentUserInfo || !currentUserInfo.openid) {
				throw new Error('用户未登录');
			}
			
			// 如果要更新昵称，先检查是否重复
			if (updateData.nickName) {
				const isAvailable = await this.checkNicknameAvailable(
					updateData.nickName, 
					currentUserInfo.openid
				);
				if (!isAvailable) {
					throw new Error('昵称已被使用，请选择其他昵称');
				}
			}
			
			// 准备更新数据
			const dataWithOpenid = {
				...updateData,
				openid: currentUserInfo.openid
			};
			
			// 调用后端API更新
			const response = await AuthAPI.updateUserInfo(dataWithOpenid);
			
			// 更新本地用户信息
			const newUserInfo = {
				...currentUserInfo,
				...updateData,
				// 如果后端返回了更新后的数据，使用后端数据
				...(response.data && {
					nickName: response.data.nickname || updateData.nickName,
					avatarUrl: response.data.avatar || updateData.avatarUrl
				})
			};
			
			// 保存到本地存储（使用部分更新模式）
			this.saveUserInfo(newUserInfo, true);
			
			return newUserInfo;
		} catch (error) {
			console.error('更新用户信息失败:', error);
			throw error;
		}
	}
}

// 创建单例实例
const userManager = new UserManager();

export default userManager;
