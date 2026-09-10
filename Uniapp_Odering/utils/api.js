/**
 * 后端API配置
 * 用于微信小程序连接Django后端
 */

/**
 * 构建查询字符串 - 替代URLSearchParams
 * @param {Object} params - 参数对象
 * @returns {string} 查询字符串
 */
function buildQueryString(params = {}) {
  const queryParts = [];
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      queryParts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
    }
  }
  return queryParts.join('&');
}

// 开发环境配置
const DEV_CONFIG = {
  baseUrl: 'http://192.168.189.240:8000',  // 当前局域网IP地址
  timeout: 10000,
  debug: true
}

// 生产环境配置
const PROD_CONFIG = {
  baseUrl: 'https://your-domain.com',  // 生产环境域名
  timeout: 10000,
  debug: false
}

// 当前使用的配置
const CONFIG = DEV_CONFIG

/**
 * API接口地址
 */
const API = {
  // 用户认证相关
  auth: {
    login: `${CONFIG.baseUrl}/api/wechat/login/`,           // 微信登录
    testLogin: `${CONFIG.baseUrl}/api/auth/test-login/`,  // 测试登录
    userInfo: `${CONFIG.baseUrl}/api/wechat/user-info/`,    // 用户信息
    userStats: `${CONFIG.baseUrl}/api/wechat/user-stats/`,  // 用户统计信息
    uploadAvatar: `${CONFIG.baseUrl}/api/wechat/upload-avatar/`,  // 头像上传
    checkNickname: `${CONFIG.baseUrl}/api/wechat/check-nickname/`,  // 昵称检查
  },
  
  // 餐厅相关 (待开发)
  restaurant: {
    categories: `${CONFIG.baseUrl}/api/restaurant/categories/`,  // 菜品分类
    dishes: `${CONFIG.baseUrl}/api/restaurant/dishes/`,          // 菜品列表
    cart: `${CONFIG.baseUrl}/api/restaurant/cart/`,              // 购物车
    orders: `${CONFIG.baseUrl}/api/restaurant/orders/`,          // 订单
  },
  
  // 点餐相关
  ordering: {
    uploadMealImage: `${CONFIG.baseUrl}/api/ordering/upload-meal-image/`,  // 菜品图片上传
  },
  
  // 家庭相关
  family: {
    list: `${CONFIG.baseUrl}/api/wechat/families/`,                    // 获取家庭列表
    create: `${CONFIG.baseUrl}/api/wechat/families/create/`,           // 创建家庭
    join: `${CONFIG.baseUrl}/api/wechat/families/join/`,               // 加入家庭
    detail: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/`,           // 家庭详情
    members: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/members/`,  // 家庭成员
    removeMember: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/remove-member/`,  // 移除成员
    transferAdmin: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/transfer-admin/`,  // 转让管理员
    leave: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/leave/`,      // 退出家庭
    dismiss: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/dismiss/`,  // 解散家庭
    settings: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/settings/` // 家庭设置
  },
  
  // 用餐记录相关
  cooking: {
    list: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-records/`,         // 获取用餐记录列表
    create: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-records/create/`, // 创建用餐记录
    detail: (familyId, recordId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-records/${recordId}/`, // 记录详情
    update: (familyId, recordId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-records/${recordId}/update/`, // 更新记录
    delete: (familyId, recordId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-records/${recordId}/delete/`, // 删除记录
    statistics: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-statistics/`  // 用餐统计
  },
  
  // 喜爱菜品相关
  // 用餐记录相关
  cooking: {
    list: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-records/`,         // 获取用餐记录列表
    create: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-records/create/`, // 创建用餐记录
    detail: (familyId, recordId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-records/${recordId}/`, // 记录详情
    update: (familyId, recordId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-records/${recordId}/update/`, // 更新记录
    delete: (familyId, recordId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-records/${recordId}/delete/`, // 删除记录
    statistics: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/cooking-statistics/`  // 用餐统计
  },
  
  // 喜爱菜品相关
  favoriteMeals: {
    list: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/favorite-meals/`,         // 获取喜爱菜品列表
    create: (familyId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/favorite-meals/create/`, // 添加喜爱菜品
    detail: (familyId, mealId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/favorite-meals/${mealId}/`, // 菜品详情
    update: (familyId, mealId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/favorite-meals/${mealId}/update/`, // 更新菜品
    delete: (familyId, mealId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/favorite-meals/${mealId}/delete/`, // 删除菜品
    like: (familyId, mealId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/favorite-meals/${mealId}/like/`,     // 点赞菜品
    unlike: (familyId, mealId) => `${CONFIG.baseUrl}/api/wechat/families/${familyId}/favorite-meals/${mealId}/unlike/`  // 取消点赞
  },
  
  // 菜谱相关
  recipes: {
    list: `${CONFIG.baseUrl}/api/recipes/`,                              // 获取菜谱列表
    create: `${CONFIG.baseUrl}/api/recipes/`,                            // 创建菜谱
    detail: (recipeId) => `${CONFIG.baseUrl}/api/recipes/${recipeId}/`,  // 菜谱详情
    update: (recipeId) => `${CONFIG.baseUrl}/api/recipes/${recipeId}/`,  // 更新菜谱
    delete: (recipeId) => `${CONFIG.baseUrl}/api/recipes/${recipeId}/`,  // 删除菜谱
    checkName: `${CONFIG.baseUrl}/api/recipes/check-name/`,              // 检查菜谱名称
    ingredients: (recipeId) => `${CONFIG.baseUrl}/api/recipes/${recipeId}/ingredients/`,  // 食材管理
    steps: (recipeId) => `${CONFIG.baseUrl}/api/recipes/${recipeId}/steps/`,              // 步骤管理
    notes: (recipeId) => `${CONFIG.baseUrl}/api/recipes/${recipeId}/notes/`,              // 制作笔记
    like: (recipeId) => `${CONFIG.baseUrl}/api/recipes/${recipeId}/like/`,                // 点赞菜谱
    collect: (recipeId) => `${CONFIG.baseUrl}/api/recipes/${recipeId}/collect/`           // 收藏菜谱
  },
}

/**
 * 统一的HTTP请求方法
 * @param {string} url 请求地址
 * @param {string} method 请求方法
 * @param {object} data 请求数据
 * @param {object} header 请求头
 */
function request(url, method = 'GET', data = {}, header = {}) {
  return new Promise((resolve, reject) => {
    // 获取用户信息以添加认证头
    let userInfo = null;
    try {
      userInfo = uni.getStorageSync('userInfo');
    } catch (error) {
      console.log('获取本地用户信息失败:', error);
    }
    
    const defaultHeader = {
      'content-type': 'application/json'
    }
    
    // 如果有用户信息，添加认证头
    if (userInfo && userInfo.openid) {
      defaultHeader['Authorization'] = `Bearer ${userInfo.openid}`;
      // 或者使用其他认证方式，如：
      // defaultHeader['X-User-OpenId'] = userInfo.openid;
    }
    
    console.log(`[API Request] ${method} ${url}`, {
      params: data,
      headers: { ...defaultHeader, ...header }
    });
    
    uni.request({
      url: url,
      method: method,
      data: data,
      header: { ...defaultHeader, ...header },
      timeout: CONFIG.timeout,
      success: (res) => {
        if (CONFIG.debug) {
          console.log(`[API] ${method} ${url}`, {
            request: data,
            response: res.data,
            statusCode: res.statusCode,
            headers: res.header
          })
        }
        
        // 统一处理响应
        if (res.statusCode === 200) {
          if (res.data && res.data.success !== undefined) {
            if (res.data.success) {
              resolve(res.data)
            } else {
              reject(new Error(res.data.message || '请求失败'))
            }
          } else {
            resolve(res.data)
          }
        } else {
          console.error(`[API Error] ${method} ${url} - HTTP ${res.statusCode}:`, res.data);
          reject(new Error(`HTTP ${res.statusCode}: ${res.data.message || res.data.error || '网络请求失败'}`))
        }
      },
      fail: (err) => {
        if (CONFIG.debug) {
          console.error(`[API Error] ${method} ${url}`, err)
        }
        reject(new Error(err.errMsg || '网络连接失败'))
      }
    })
  })
}

/**
 * 用户认证相关API
 */
const AuthAPI = {
  /**
   * 微信登录
   * @param {string} code 微信授权码
   * @param {object} userInfo 用户信息，包含昵称和头像信息
   */
  async login(code, userInfo) {
    return request(API.auth.login, 'POST', {
      code,
      userInfo
    })
  },
  
  /**
   * 测试登录 (仅开发环境)
   * @param {string} testOpenid 测试用户标识
   * @param {string} nickname 昵称
   */
  async testLogin(testOpenid = 'test_user_001', nickname = '测试用户') {
    return request(API.auth.testLogin, 'POST', {
      test_openid: testOpenid,
      nickname
    })
  },
  
  /**
   * 获取用户信息
   */
  async getUserInfo() {
    return request(API.auth.userInfo, 'GET')
  },
  
  /**
   * 更新用户信息
   * @param {object} userInfo 用户信息
   */
  async updateUserInfo(userInfo) {
    return request(API.auth.userInfo, 'POST', userInfo)
  },
  
  /**
   * 检查昵称是否可用
   * @param {object} data 包含nickname和exclude_openid的对象
   */
  async checkNickname(data) {
    return request(API.auth.checkNickname, 'POST', data)
  },

  /**
   * 获取用户统计信息
   */
  async getUserStats() {
    return request(API.auth.userStats, 'GET')
  },

  /**
   * 上传头像
   * @param {string} filePath 文件路径
   * @param {string} openid 用户openid
   */
  async uploadAvatar(filePath, openid) {
    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: API.auth.uploadAvatar,
        filePath: filePath,
        name: 'avatar',
        formData: {
          'openid': openid
        },
        header: {
          'Authorization': `Bearer ${openid}`
        },
        success: (res) => {
          if (CONFIG.debug) {
            console.log(`[API] UPLOAD ${API.auth.uploadAvatar}`, {
              filePath: filePath,
              response: res.data
            })
          }
          
          try {
            const data = JSON.parse(res.data)
            if (data.success) {
              resolve(data)
            } else {
              reject(new Error(data.error || '上传失败'))
            }
          } catch (error) {
            reject(new Error('解析响应失败'))
          }
        },
        fail: (err) => {
          if (CONFIG.debug) {
            console.error(`[API Error] UPLOAD ${API.auth.uploadAvatar}`, err)
          }
          reject(new Error(err.errMsg || '上传失败'))
        }
      })
    })
  },

  async uploadMealImage(filePath) {
    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: API.ordering.uploadMealImage,
        filePath: filePath,
        name: 'image',
        success: (res) => {
          if (CONFIG.debug) {
            console.log(`[API] UPLOAD ${API.ordering.uploadMealImage}`, {
              filePath: filePath,
              response: res.data
            })
          }
          
          try {
            const data = JSON.parse(res.data)
            console.log('图片上传响应数据:', data)
            
            if (data.success) {
              // 确保返回完整的数据对象，包含image_url字段
              if (!data.image_url) {
                console.warn('服务器返回成功但缺少image_url字段', data)
              }
              resolve(data)
            } else {
              reject(new Error(data.error || '上传失败'))
            }
          } catch (error) {
            console.error('解析上传响应失败:', error, res.data)
            reject(new Error('解析响应失败'))
          }
        },
        fail: (err) => {
          if (CONFIG.debug) {
            console.error(`[API Error] UPLOAD ${API.ordering.uploadMealImage}`, err)
          }
          reject(new Error(err.errMsg || '上传失败'))
        }
      })
    })
  },
}

/**
 * 家庭功能相关API
 */
const FamilyAPI = {
  /**
   * 获取用户的家庭列表
   */
  async getFamilyList() {
    return request(API.family.list, 'GET')
  },
  
  /**
   * 创建家庭
   * @param {string} name 家庭名称
   * @param {string} displayName 创建者在家庭中的显示名称
   */
  async createFamily(name, displayName = '家长') {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.family.create, 'POST', {
      openid: userInfo?.openid,
      name,
      display_name: displayName
    })
  },
  
  /**
   * 通过邀请码加入家庭
   * @param {string} inviteCode 邀请码
   * @param {string} displayName 在家庭中的显示名称
   */
  async joinFamily(inviteCode, displayName) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.family.join, 'POST', {
      openid: userInfo?.openid,
      invite_code: inviteCode,
      display_name: displayName
    })
  },
  
  /**
   * 获取家庭详情
   * @param {number} familyId 家庭ID
   */
  async getFamilyDetail(familyId) {
    return request(API.family.detail(familyId), 'GET')
  },
  
  /**
   * 获取家庭成员列表
   * @param {number} familyId 家庭ID
   */
  async getFamilyMembers(familyId) {
    return request(API.family.members(familyId), 'GET')
  },
  
  /**
   * 移除家庭成员
   * @param {number} familyId 家庭ID
   * @param {string} targetUserOpenid 目标用户openid
   */
  async removeFamilyMember(familyId, targetUserOpenid) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.family.removeMember(familyId), 'POST', {
      openid: userInfo?.openid,
      target_user_openid: targetUserOpenid
    })
  },
  
  /**
   * 转让管理员权限
   * @param {number} familyId 家庭ID
   * @param {string} targetUserOpenid 目标用户openid
   */
  async transferAdmin(familyId, targetUserOpenid) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.family.transferAdmin(familyId), 'POST', {
      openid: userInfo?.openid,
      target_user_openid: targetUserOpenid
    })
  },
  
  /**
   * 退出家庭
   * @param {number} familyId 家庭ID
   */
  async leaveFamily(familyId) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.family.leave(familyId), 'POST', {
      openid: userInfo?.openid
    })
  },
  
  /**
   * 解散家庭
   * @param {number} familyId 家庭ID
   */
  async dismissFamily(familyId) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.family.dismiss(familyId), 'POST', {
      openid: userInfo?.openid
    })
  },
  
  /**
   * 修改家庭设置
   * @param {number} familyId 家庭ID
   * @param {object} settings 设置对象 {name?, code_enabled?, max_members?}
   */
  async updateFamilySettings(familyId, settings) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.family.settings(familyId), 'PUT', {
      openid: userInfo?.openid,
      ...settings
    })
  },

  /**
   * 获取用餐记录
   * @param {number} familyId 家庭ID
   */
  async getCookingRecords(familyId) {
    return request(API.cooking.list(familyId), 'GET')
  },
  
  /**
   * 创建用餐记录
   * @param {number} familyId 家庭ID
   * @param {object} record 用餐记录对象
   */
  async createCookingRecord(familyId, record) {
    return request(API.cooking.create(familyId), 'POST', record)
  },
  
  /**
   * 获取用餐记录详情
   * @param {number} familyId 家庭ID
   * @param {number} recordId 记录ID
   */
  async getCookingRecordDetail(familyId, recordId) {
    return request(API.cooking.detail(familyId, recordId), 'GET')
  },
  
  /**
   * 更新用餐记录
   * @param {number} familyId 家庭ID
   * @param {number} recordId 记录ID
   * @param {object} record 更新的用餐记录对象
   */
  async updateCookingRecord(familyId, recordId, record) {
    return request(API.cooking.update(familyId, recordId), 'POST', record)
  },
  
  /**
   * 删除用餐记录
   * @param {number} familyId 家庭ID
   * @param {number} recordId 记录ID
   */
  async deleteCookingRecord(familyId, recordId) {
    return request(API.cooking.delete(familyId, recordId), 'POST')
  },
  
  /**
   * 获取用餐统计
   * @param {number} familyId 家庭ID
   */
  async getCookingStatistics(familyId) {
    return request(API.cooking.statistics(familyId), 'GET')
  },
  
  /**
   * 获取喜爱菜品列表
   * @param {number} familyId 家庭ID
   */
  async getFavoriteMeals(familyId) {
    return request(API.favoriteMeals.list(familyId), 'GET')
  },
  
  /**
   * 添加喜爱菜品
   * @param {number} familyId 家庭ID
   * @param {object} meal 菜品对象
   */
  async addFavoriteMeal(familyId, meal) {
    return request(API.favoriteMeals.create(familyId), 'POST', meal)
  },
  
  /**
   * 获取菜品详情
   * @param {number} familyId 家庭ID
   * @param {number} mealId 菜品ID
   */
  async getFavoriteMealDetail(familyId, mealId) {
    return request(API.favoriteMeals.detail(familyId, mealId), 'GET')
  },
  
  /**
   * 更新菜品
   * @param {number} familyId 家庭ID
   * @param {number} mealId 菜品ID
   * @param {object} meal 更新的菜品对象
   */
  async updateFavoriteMeal(familyId, mealId, meal) {
    return request(API.favoriteMeals.update(familyId, mealId), 'POST', meal)
  },
  
  /**
   * 删除菜品
   * @param {number} familyId 家庭ID
   * @param {number} mealId 菜品ID
   */
  async deleteFavoriteMeal(familyId, mealId) {
    return request(API.favoriteMeals.delete(familyId, mealId), 'POST')
  },
  
  /**
   * 点赞菜品
   * @param {number} familyId 家庭ID
   * @param {number} mealId 菜品ID
   */
  async likeFavoriteMeal(familyId, mealId) {
    return request(API.favoriteMeals.like(familyId, mealId), 'POST')
  },
  
  /**
   * 取消点赞菜品
   * @param {number} familyId 家庭ID
   * @param {number} mealId 菜品ID
   */
  async unlikeFavoriteMeal(familyId, mealId) {
    return request(API.favoriteMeals.unlike(familyId, mealId), 'POST')
  },
}

/**
 * 用餐记录相关API
 */
const CookingAPI = {
  /**
   * 获取家庭用餐记录列表
   * @param {number} familyId 家庭ID
   * @param {object} params 查询参数 {page?, page_size?, start_date?, end_date?, cook_id?}
   */
  async getCookingRecords(familyId, params = {}) {
    const query = buildQueryString(params)
    const url = `${API.cooking.list(familyId)}${query ? '?' + query : ''}`
    return request(url, 'GET')
  },
  
  /**
   * 创建用餐记录
   * @param {number} familyId 家庭ID
   * @param {object} recordData 用餐记录数据
   */
  async createCookingRecord(familyId, recordData) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.cooking.create(familyId), 'POST', {
      openid: userInfo?.openid,
      ...recordData
    })
  },
  
  /**
   * 获取用餐记录详情
   * @param {number} familyId 家庭ID
   * @param {number} recordId 记录ID
   */
  async getCookingRecordDetail(familyId, recordId) {
    return request(API.cooking.detail(familyId, recordId), 'GET')
  },
  
  /**
   * 更新用餐记录
   * @param {number} familyId 家庭ID
   * @param {number} recordId 记录ID
   * @param {object} updateData 更新数据
   */
  async updateCookingRecord(familyId, recordId, updateData) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.cooking.update(familyId, recordId), 'PUT', {
      openid: userInfo?.openid,
      ...updateData
    })
  },
  
  /**
   * 删除用餐记录
   * @param {number} familyId 家庭ID
   * @param {number} recordId 记录ID
   */
  async deleteCookingRecord(familyId, recordId) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.cooking.delete(familyId, recordId), 'DELETE', {
      openid: userInfo?.openid
    })
  },
  
  /**
   * 获取用餐统计数据
   * @param {number} familyId 家庭ID
   * @param {object} params 查询参数 {period?, start_date?, end_date?}
   */
  async getCookingStatistics(familyId, params = {}) {
    const query = buildQueryString(params)
    const url = `${API.cooking.statistics(familyId)}${query ? '?' + query : ''}`
    return request(url, 'GET')
  }
}

/**
 * 喜爱菜品相关API
 */
const FavoriteMealsAPI = {
  /**
   * 获取家庭喜爱菜品列表
   * @param {number} familyId 家庭ID
   * @param {object} params 查询参数 {category?, sort_by?, page?, page_size?}
   */
  async getFavoriteMeals(familyId, params = {}) {
    const query = buildQueryString(params)
    const url = `${API.favoriteMeals.list(familyId)}${query ? '?' + query : ''}`
    return request(url, 'GET')
  },
  
  /**
   * 添加喜爱菜品
   * @param {number} familyId 家庭ID
   * @param {object} mealData 菜品数据
   */
  async createFavoriteMeal(familyId, mealData) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.favoriteMeals.create(familyId), 'POST', {
      openid: userInfo?.openid,
      ...mealData
    })
  },
  
  /**
   * 获取菜品详情
   * @param {number} familyId 家庭ID
   * @param {number} mealId 菜品ID
   */
  async getFavoriteMealDetail(familyId, mealId) {
    return request(API.favoriteMeals.detail(familyId, mealId), 'GET')
  },
  
  /**
   * 更新菜品信息
   * @param {number} familyId 家庭ID
   * @param {number} mealId 菜品ID
   * @param {object} updateData 更新数据
   */
  async updateFavoriteMeal(familyId, mealId, updateData) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.favoriteMeals.update(familyId, mealId), 'PUT', {
      openid: userInfo?.openid,
      ...updateData
    })
  },
  
  /**
   * 删除菜品
   * @param {number} familyId 家庭ID
   * @param {number} mealId 菜品ID
   */
  async deleteFavoriteMeal(familyId, mealId) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.favoriteMeals.delete(familyId, mealId), 'DELETE', {
      openid: userInfo?.openid
    })
  },
  
  /**
   * 点赞菜品
   * @param {number} familyId 家庭ID
   * @param {number} mealId 菜品ID
   */
  async likeFavoriteMeal(familyId, mealId) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.favoriteMeals.like(familyId, mealId), 'POST', {
      openid: userInfo?.openid
    })
  },
  
  /**
   * 取消点赞菜品
   * @param {number} familyId 家庭ID
   * @param {number} mealId 菜品ID
   */
  async unlikeFavoriteMeal(familyId, mealId) {
    const userInfo = uni.getStorageSync('userInfo')
    return request(API.favoriteMeals.unlike(familyId, mealId), 'POST', {
      openid: userInfo?.openid
    })
  }
}

/**
 * 菜谱相关API
 */
const RecipeAPI = {
  /**
   * 获取菜谱列表
   * @param {Object} params - 查询参数
   * @param {Object} headers - 请求头
   */
  async getRecipes(params = {}, headers = {}) {
    const queryString = buildQueryString(params);
    const url = `${API.recipes.list}${queryString ? `?${queryString}` : ''}`;
    return request(url, 'GET', {}, headers);
  },

  /**
   * 获取菜谱详情
   * @param {number} recipeId 菜谱ID
   */
  async getRecipeDetail(recipeId) {
    return request(API.recipes.detail(recipeId), 'GET')
  },

  /**
   * 创建菜谱
   * @param {Object} recipeData 菜谱数据
   */
  async createRecipe(recipeData) {
    return request(API.recipes.create, 'POST', recipeData)
  },

  /**
   * 检查菜谱名称是否重复
   * @param {string} name 菜谱名称
   * @param {string} authorOpenid 作者openid
   */
  async checkRecipeName(name, authorOpenid) {
    return request(API.recipes.checkName, 'POST', {
      name: name,
      author_openid: authorOpenid
    })
  },

  /**
   * 更新菜谱
   * @param {number} recipeId 菜谱ID
   * @param {Object} recipeData 更新数据
   */
  async updateRecipe(recipeId, recipeData) {
    return request(API.recipes.update(recipeId), 'PUT', recipeData)
  },

  /**
   * 删除菜谱
   * @param {number} recipeId 菜谱ID
   */
  async deleteRecipe(recipeId) {
    return request(API.recipes.delete(recipeId), 'DELETE')
  },

  /**
   * 创建制作笔记
   * @param {number} recipeId 菜谱ID
   * @param {Object} noteData 笔记数据
   */
  async createRecipeNote(recipeId, noteData) {
    return request(API.recipes.notes(recipeId), 'POST', noteData)
  },

  /**
   * 收藏/取消收藏菜谱
   * @param {number} recipeId 菜谱ID
   */
  async toggleFavorite(recipeId) {
    return request(`${API.recipes.detail(recipeId)}/favorite/`, 'POST')
  }
}

// 导出配置和API
console.log('export AuthAPI', AuthAPI);
export {
  CONFIG,
  API,
  request,
  AuthAPI,
  FamilyAPI,
  CookingAPI,
  FavoriteMealsAPI,
  RecipeAPI,
  buildQueryString
}
