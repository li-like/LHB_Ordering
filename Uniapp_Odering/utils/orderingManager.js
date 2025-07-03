/**
 * 点餐功能API管理器
 */

import { request, CONFIG } from './api.js'

class OrderingManager {
	constructor() {
		this.baseUrl = `${CONFIG.baseUrl}/api/ordering`
	}

	// ==================== 餐品分类相关 ====================
	
	/**
	 * 获取餐品分类列表
	 */
	async getCategories() {
		return await request(`${this.baseUrl}/categories/`, 'GET')
	}
	
	/**
	 * 获取简化的分类列表
	 */
	async getCategoriesSimple() {
		return await request(`${this.baseUrl}/categories/simple_list/`, 'GET')
	}
	
	/**
	 * 创建餐品分类
	 */
	async createCategory(categoryData) {
		return await request(`${this.baseUrl}/categories/`, 'POST', categoryData)
	}
	
	/**
	 * 更新餐品分类
	 */
	async updateCategory(categoryId, categoryData) {
		return await request(`${this.baseUrl}/categories/${categoryId}/`, 'PUT', categoryData)
	}
	
	/**
	 * 删除餐品分类
	 */
	async deleteCategory(categoryId) {
		return await request(`${this.baseUrl}/categories/${categoryId}/`, 'DELETE')
	}

	// ==================== 餐品相关 ====================
	
	/**
	 * 获取餐品列表
	 * @param {Object} params - 查询参数
	 * @param {string} params.category - 分类ID
	 * @param {string} params.meal_type - 餐品类型
	 * @param {string} params.difficulty - 难度
	 * @param {string} params.search - 搜索关键词
	 * @param {boolean} params.available_only - 只显示可点餐的
	 */
	async getMeals(params = {}) {
		return await request(`${this.baseUrl}/items/`, 'GET', null, params)
	}
	
	/**
	 * 获取餐品详情
	 */
	async getMealDetail(mealId) {
		return await request(`${this.baseUrl}/items/${mealId}/`, 'GET')
	}
	
	/**
	 * 创建餐品
	 */
	async createMeal(mealData) {
		return await request(`${this.baseUrl}/items/`, 'POST', mealData)
	}
	
	/**
	 * 更新餐品
	 */
	async updateMeal(mealId, mealData) {
		return await request(`${this.baseUrl}/items/${mealId}/`, 'PUT', mealData)
	}
	
	/**
	 * 删除餐品
	 */
	async deleteMeal(mealId) {
		return await request(`${this.baseUrl}/items/${mealId}/`, 'DELETE')
	}
	
	/**
	 * 获取热门餐品
	 */
	async getPopularMeals() {
		return await request(`${this.baseUrl}/items/popular/`, 'GET')
	}
	
	/**
	 * 切换餐品可用状态
	 */
	async toggleMealAvailability(mealId) {
		return await request(`${this.baseUrl}/items/${mealId}/toggle_availability/`, 'POST')
	}

	// ==================== 点餐需求相关 ====================
	
	/**
	 * 获取点餐需求列表
	 * @param {Object} params - 查询参数
	 * @param {string} params.status - 状态筛选
	 * @param {string} params.requester - 点餐人筛选
	 * @param {string} params.date - 日期筛选
	 * @param {boolean} params.my_requests - 只显示我的点餐
	 */
	async getMealRequests(params = {}) {
		return await request(`${this.baseUrl}/requests/`, 'GET', null, params)
	}
	
	/**
	 * 获取点餐需求详情
	 */
	async getMealRequestDetail(requestId) {
		return await request(`${this.baseUrl}/requests/${requestId}/`, 'GET')
	}
	
	/**
	 * 创建点餐需求
	 */
	async createMealRequest(requestData) {
		return await request(`${this.baseUrl}/requests/`, 'POST', requestData)
	}
	
	/**
	 * 更新点餐需求
	 */
	async updateMealRequest(requestId, requestData) {
		return await request(`${this.baseUrl}/requests/${requestId}/`, 'PUT', requestData)
	}
	
	/**
	 * 取消点餐需求
	 */
	async cancelMealRequest(requestId) {
		return await request(`${this.baseUrl}/requests/${requestId}/cancel/`, 'POST')
	}
	
	/**
	 * 获取待处理的点餐需求
	 */
	async getPendingRequests() {
		return await request(`${this.baseUrl}/requests/pending/`, 'GET')
	}
	
	/**
	 * 获取点餐需求汇总统计
	 */
	async getRequestsSummary() {
		return await request(`${this.baseUrl}/requests/summary/`, 'GET')
	}

	// ==================== 制作确认相关 ====================
	
	/**
	 * 获取制作确认列表
	 */
	async getConfirmations() {
		return await request(`${this.baseUrl}/confirmations/`, 'GET')
	}
	
	/**
	 * 创建制作确认
	 */
	async createConfirmation(confirmationData) {
		return await request(`${this.baseUrl}/confirmations/`, 'POST', confirmationData)
	}
	
	/**
	 * 开始制作
	 */
	async startCooking(confirmationId) {
		return await request(`${this.baseUrl}/confirmations/${confirmationId}/start_cooking/`, 'POST')
	}
	
	/**
	 * 完成制作
	 */
	async completeCooking(confirmationId, ratings = {}) {
		return await request(`${this.baseUrl}/confirmations/${confirmationId}/complete_cooking/`, 'POST', ratings)
	}

	// ==================== 批量点餐相关 ====================
	
	/**
	 * 获取批量点餐列表
	 */
	async getBatches() {
		return await request(`${this.baseUrl}/batches/`, 'GET')
	}
	
	/**
	 * 创建批量点餐
	 */
	async createBatch(batchData) {
		return await request(`${this.baseUrl}/batches/`, 'POST', batchData)
	}
	
	/**
	 * 向批次添加点餐需求
	 */
	async addRequestsToBatch(batchId, requestIds) {
		return await request(`${this.baseUrl}/batches/${batchId}/add_requests/`, 'POST', {
			request_ids: requestIds
		})
	}

	// ==================== 统计相关 ====================
	
	/**
	 * 获取家庭用餐统计
	 */
	async getFamilyStats() {
		return await request(`${this.baseUrl}/stats/`, 'GET')
	}
	
	/**
	 * 更新统计数据
	 */
	async updateStats(statsId) {
		return await request(`${this.baseUrl}/stats/${statsId}/update_stats/`, 'POST')
	}

	// ==================== 便捷方法 ====================
	
	/**
	 * 快速点餐
	 * @param {number} mealId - 餐品ID
	 * @param {number} quantity - 数量
	 * @param {string} priority - 优先级
	 * @param {string} specialRequests - 特殊要求
	 */
	async quickOrder(mealId, quantity = 1, priority = 'normal', specialRequests = '') {
		const requestData = {
			meal_item: mealId,
			quantity: quantity,
			priority: priority,
			special_requests: specialRequests
		}
		return await this.createMealRequest(requestData)
	}
	
	/**
	 * 获取今日点餐需求
	 */
	async getTodayRequests() {
		const today = new Date().toISOString().split('T')[0]
		return await this.getMealRequests({ date: today })
	}
	
	/**
	 * 获取我的点餐需求
	 */
	async getMyRequests() {
		return await this.getMealRequests({ my_requests: 'true' })
	}
	
	/**
	 * 获取我的点餐需求（分页版本）
	 */
	async getMyMealRequests(params = {}) {
		const requestParams = {
			my_requests: 'true',
			...params
		}
		return await request(`${this.baseUrl}/requests/`, 'GET', null, requestParams)
	}
	
	/**
	 * 获取我的点餐统计
	 */
	async getMyRequestStats() {
		try {
			const summary = await this.getRequestsSummary()
			// 这里应该根据实际API返回的数据结构调整
			return {
				success: true,
				data: {
					total: summary.total || 0,
					confirmed: summary.confirmed || 0,
					rejected: summary.cancelled || 0 // 使用cancelled作为rejected的替代
				}
			}
		} catch (error) {
			return {
				success: false,
				message: error.message || '获取统计失败'
			}
		}
	}
	
	/**
	 * 获取指定状态的点餐需求
	 */
	async getRequestsByStatus(status) {
		return await this.getMealRequests({ status: status })
	}
	
	/**
	 * 批量操作：确认多个点餐需求
	 */
	async batchConfirmRequests(requestIds, estimatedTime = null) {
		const confirmations = []
		for (const requestId of requestIds) {
			try {
				const confirmation = await this.createConfirmation({
					meal_request: requestId,
					status: 'accepted',
					estimated_time: estimatedTime
				})
				confirmations.push(confirmation)
			} catch (error) {
				console.error(`确认点餐需求 ${requestId} 失败:`, error)
			}
		}
		return confirmations
	}
	
	// ==================== 新增API方法 ====================
	
	/**
	 * 获取餐品分类列表（用于页面选择器）
	 */
	async getMealCategories() {
		return await this.getCategories()
	}
	
	/**
	 * 获取餐品详情（用于详情页面）
	 */
	async getMealItem(mealId) {
		return await this.getMealDetail(mealId)
	}
	
	/**
	 * 创建餐品项目（用于添加餐品页面）
	 */
	async createMealItem(mealData) {
		return await this.createMeal(mealData)
	}
	
	/**
	 * 更新餐品项目（用于编辑餐品页面）
	 */
	async updateMealItem(mealId, mealData) {
		return await this.updateMeal(mealId, mealData)
	}
	
	/**
	 * 删除餐品项目（用于管理页面）
	 */
	async deleteMealItem(mealId) {
		return await this.deleteMeal(mealId)
	}
	
	/**
	 * 确认点餐请求（用于管理员确认）
	 */
	async confirmMealRequest(requestId, confirmData) {
		return await this.createConfirmation({
			meal_request: requestId,
			...confirmData
		})
	}
	
	/**
	 * 获取餐品统计数据（用于详情页和汇总页）
	 */
	async getMealStats(params = {}) {
		return await request(`${this.baseUrl}/stats/meal_stats/`, 'GET', null, params)
	}
	
	/**
	 * 上传图片文件
	 */
	async uploadImage(imagePath) {
		// 这里需要根据实际的上传API实现
		// 临时返回本地路径
		return imagePath
	}
	
	/**
	 * 获取餐品的所有点餐记录
	 */
	async getMealOrders(mealId, params = {}) {
		return await this.getMealRequests({
			meal_id: mealId,
			...params
		})
	}
	
	/**
	 * 添加/移除餐品收藏
	 */
	async toggleMealFavorite(mealId) {
		return await request(`${this.baseUrl}/items/${mealId}/toggle_favorite/`, 'POST')
	}
	
	/**
	 * 检查餐品是否已收藏
	 */
	async checkFavorite(mealId) {
		const response = await request(`${this.baseUrl}/items/${mealId}/check_favorite/`, 'GET')
		return response.is_favorite || false
	}
}

// 创建并导出单例
const orderingManager = new OrderingManager()
export default orderingManager
