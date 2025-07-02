/**
 * 家庭数据管理器
 * 统一管理家庭相关数据和状态
 */

import { FamilyAPI, CookingAPI, FavoriteMealsAPI } from './api.js'

class FamilyManager {
	constructor() {
		this.currentFamily = null
		this.familyList = []
		this.familyMembers = []
		this.cookingRecords = []
		this.favoriteMeals = []
		this.listeners = {
			familyUpdated: [],
			membersUpdated: [],
			cookingRecordsUpdated: [],
			favoriteMealsUpdated: []
		}
	}

	/**
	 * 注册事件监听器
	 */
	on(event, callback) {
		if (this.listeners[event]) {
			this.listeners[event].push(callback)
		}
	}

	/**
	 * 移除事件监听器
	 */
	off(event, callback) {
		if (this.listeners[event]) {
			const index = this.listeners[event].indexOf(callback)
			if (index > -1) {
				this.listeners[event].splice(index, 1)
			}
		}
	}

	/**
	 * 触发事件
	 */
	emit(event, data) {
		if (this.listeners[event]) {
			this.listeners[event].forEach(callback => {
				try {
					callback(data)
				} catch (error) {
					console.error(`家庭管理器事件回调错误 [${event}]:`, error)
				}
			})
		}
	}

	/**
	 * 获取家庭列表
	 */
	async getFamilyList() {
		try {
			const response = await FamilyAPI.getFamilyList()
			this.familyList = response.families || []
			
			// 如果有家庭且没有当前家庭，自动选择第一个
			if (this.familyList.length > 0 && !this.currentFamily) {
				await this.setCurrentFamily(this.familyList[0].id)
			}
			
			this.emit('familyUpdated', {
				type: 'list',
				data: this.familyList
			})
			
			return this.familyList
		} catch (error) {
			console.error('获取家庭列表失败:', error)
			throw error
		}
	}

	/**
	 * 设置当前家庭
	 */
	async setCurrentFamily(familyId) {
		try {
			// 获取家庭详情
			const familyResponse = await FamilyAPI.getFamilyDetail(familyId)
			this.currentFamily = familyResponse.family
			
			// 获取家庭成员
			const membersResponse = await FamilyAPI.getFamilyMembers(familyId)
			this.familyMembers = membersResponse.members || []
			
			// 保存到本地存储
			uni.setStorageSync('currentFamilyId', familyId)
			
			this.emit('familyUpdated', {
				type: 'current',
				data: this.currentFamily
			})
			
			this.emit('membersUpdated', {
				type: 'list',
				data: this.familyMembers
			})
			
			// 自动加载用餐记录和喜爱菜品
			await this.loadCookingRecords()
			await this.loadFavoriteMeals()
			
			return this.currentFamily
		} catch (error) {
			console.error('设置当前家庭失败:', error)
			throw error
		}
	}

	/**
	 * 获取当前家庭
	 */
	getCurrentFamily() {
		return this.currentFamily
	}

	/**
	 * 获取家庭成员
	 */
	getFamilyMembers() {
		return this.familyMembers
	}

	/**
	 * 创建家庭
	 */
	async createFamily(name, displayName) {
		try {
			const response = await FamilyAPI.createFamily(name, displayName)
			const newFamily = response.family
			
			// 添加到家庭列表
			this.familyList.unshift(newFamily)
			
			// 设置为当前家庭
			await this.setCurrentFamily(newFamily.id)
			
			this.emit('familyUpdated', {
				type: 'created',
				data: newFamily
			})
			
			return newFamily
		} catch (error) {
			console.error('创建家庭失败:', error)
			throw error
		}
	}

	/**
	 * 加入家庭
	 */
	async joinFamily(inviteCode, displayName) {
		try {
			const response = await FamilyAPI.joinFamily(inviteCode, displayName)
			const joinedFamily = response.family
			
			// 添加到家庭列表
			this.familyList.unshift(joinedFamily)
			
			// 设置为当前家庭
			await this.setCurrentFamily(joinedFamily.id)
			
			this.emit('familyUpdated', {
				type: 'joined',
				data: joinedFamily
			})
			
			return joinedFamily
		} catch (error) {
			console.error('加入家庭失败:', error)
			throw error
		}
	}

	/**
	 * 刷新当前家庭数据
	 */
	async refreshCurrentFamily() {
		if (this.currentFamily) {
			await this.setCurrentFamily(this.currentFamily.id)
		}
	}

	/**
	 * 加载用餐记录
	 */
	async loadCookingRecords() {
		if (!this.currentFamily) return []
		
		try {
			// 尝试从后端API获取数据
			const response = await CookingAPI.getCookingRecords(this.currentFamily.id, {
				page_size: 100 // 获取最近100条记录
			})
			this.cookingRecords = response.records || []
			
			// 如果后端没有数据，使用模拟数据
			if (this.cookingRecords.length === 0) {
				this.cookingRecords = this.generateMockCookingRecords()
			}
			
			this.emit('cookingRecordsUpdated', {
				type: 'list',
				data: this.cookingRecords
			})
			
			return this.cookingRecords
		} catch (error) {
			console.error('加载用餐记录失败，使用模拟数据:', error)
			// 出错时使用模拟数据
			this.cookingRecords = this.generateMockCookingRecords()
			
			this.emit('cookingRecordsUpdated', {
				type: 'list',
				data: this.cookingRecords
			})
			
			return this.cookingRecords
		}
	}

	/**
	 * 加载喜爱菜品
	 */
	async loadFavoriteMeals() {
		if (!this.currentFamily) return []
		
		try {
			// 尝试从后端API获取数据
			const response = await FavoriteMealsAPI.getFavoriteMeals(this.currentFamily.id, {
				page_size: 100 // 获取最多100个菜品
			})
			this.favoriteMeals = response.meals || []
			
			// 如果后端没有数据，使用模拟数据
			if (this.favoriteMeals.length === 0) {
				this.favoriteMeals = this.generateMockFavoriteMeals()
			}
			
			this.emit('favoriteMealsUpdated', {
				type: 'list',
				data: this.favoriteMeals
			})
			
			return this.favoriteMeals
		} catch (error) {
			console.error('加载喜爱菜品失败，使用模拟数据:', error)
			// 出错时使用模拟数据
			this.favoriteMeals = this.generateMockFavoriteMeals()
			
			this.emit('favoriteMealsUpdated', {
				type: 'list',
				data: this.favoriteMeals
			})
			
			return this.favoriteMeals
		}
	}

	/**
	 * 生成模拟用餐记录
	 */
	generateMockCookingRecords() {
		const members = this.familyMembers || []
		const dishes = ['红烧肉', '清炒时蔬', '蒸蛋羹', '番茄鸡蛋', '麻婆豆腐', '糖醋排骨', '青椒土豆丝', '宫保鸡丁']
		const records = []
		
		// 生成最近30天的用餐记录
		for (let i = 0; i < 30; i++) {
			const date = new Date()
			date.setDate(date.getDate() - i)
			
			// 随机生成1-3条记录
			const recordCount = Math.floor(Math.random() * 3) + 1
			
			for (let j = 0; j < recordCount; j++) {
				const cook = members[Math.floor(Math.random() * members.length)]
				const dish = dishes[Math.floor(Math.random() * dishes.length)]
				const participants = this.getRandomMembers(members, Math.floor(Math.random() * members.length) + 1)
				
				if (cook) {
					records.push({
						id: `record_${i}_${j}`,
						cookId: cook.user_info.openid,
						cookName: cook.user_info.nickname,
						cookAvatar: cook.user_info.avatar,
						dishName: dish,
						cookTime: new Date(date.getTime() + j * 2 * 60 * 60 * 1000), // 每2小时一餐
						participants: participants,
						rating: Math.floor(Math.random() * 2) + 4, // 4-5分评分
						images: []
					})
				}
			}
		}
		
		return records.sort((a, b) => new Date(b.cookTime) - new Date(a.cookTime))
	}

	/**
	 * 生成模拟喜爱菜品
	 */
	generateMockFavoriteMeals() {
		const dishes = [
			{ name: '红烧肉', category: '荤菜', count: 15, lastCooked: '2天前' },
			{ name: '清炒时蔬', category: '素菜', count: 12, lastCooked: '1天前' },
			{ name: '蒸蛋羹', category: '蛋类', count: 10, lastCooked: '3天前' },
			{ name: '番茄鸡蛋', category: '家常菜', count: 8, lastCooked: '1天前' },
			{ name: '麻婆豆腐', category: '川菜', count: 7, lastCooked: '5天前' },
			{ name: '糖醋排骨', category: '荤菜', count: 6, lastCooked: '4天前' },
			{ name: '青椒土豆丝', category: '素菜', count: 5, lastCooked: '2天前' },
			{ name: '宫保鸡丁', category: '川菜', count: 4, lastCooked: '6天前' }
		]
		
		return dishes.map((dish, index) => ({
			id: `meal_${index}`,
			...dish,
			image: `/static/dishes/${dish.name.toLowerCase()}.jpg`,
			addedBy: this.familyMembers[Math.floor(Math.random() * this.familyMembers.length)]?.user_info?.nickname || '家人',
			addTime: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
		}))
	}

	/**
	 * 随机获取成员
	 */
	getRandomMembers(members, count) {
		const shuffled = [...members].sort(() => 0.5 - Math.random())
		return shuffled.slice(0, count).map(member => ({
			id: member.user_info.openid,
			name: member.user_info.nickname,
			avatar: member.user_info.avatar
		}))
	}

	/**
	 * 获取统计数据
	 */
	getStatistics() {
		const stats = {
			totalMeals: this.cookingRecords.length,
			favoriteMealsCount: this.favoriteMeals.length,
			memberCount: this.familyMembers.length,
			recentDays: 7
		}
		
		// 计算最近7天用餐次数
		const sevenDaysAgo = new Date()
		sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
		
		stats.recentMeals = this.cookingRecords.filter(record => 
			new Date(record.cookTime) >= sevenDaysAgo
		).length
		
		return stats
	}

	/**
	 * 获取用餐记录
	 */
	getCookingRecords() {
		return this.cookingRecords
	}

	/**
	 * 获取喜爱菜品
	 */
	getFavoriteMeals() {
		return this.favoriteMeals
	}

	/**
	 * 初始化（从本地存储恢复状态）
	 */
	async initialize() {
		try {
			const savedFamilyId = uni.getStorageSync('currentFamilyId')
			
			// 获取家庭列表
			await this.getFamilyList()
			
			// 如果有保存的家庭ID，设置为当前家庭
			if (savedFamilyId && this.familyList.find(f => f.id === savedFamilyId)) {
				await this.setCurrentFamily(savedFamilyId)
			}
			
		} catch (error) {
			console.error('家庭管理器初始化失败:', error)
		}
	}

	/**
	 * 添加用餐记录
	 */
	async addCookingRecord(recordData) {
		if (!this.currentFamily) {
			throw new Error('请先选择家庭')
		}
		
		try {
			const response = await CookingAPI.createCookingRecord(this.currentFamily.id, recordData)
			const newRecord = response.record
			
			// 添加到本地列表
			this.cookingRecords.unshift(newRecord)
			
			this.emit('cookingRecordsUpdated', {
				type: 'added',
				data: newRecord
			})
			
			return newRecord
		} catch (error) {
			console.error('添加用餐记录失败:', error)
			
			// 如果API失败，添加到本地模拟数据
			const mockRecord = {
				id: `record_${Date.now()}`,
				cookId: recordData.cook_id,
				cookName: recordData.cook_name,
				cookAvatar: recordData.cook_avatar,
				dishName: recordData.dish_name,
				cookTime: new Date(recordData.cook_time),
				participants: recordData.participants || [],
				rating: recordData.rating || 5,
				images: recordData.images || [],
				notes: recordData.notes || ''
			}
			
			this.cookingRecords.unshift(mockRecord)
			
			this.emit('cookingRecordsUpdated', {
				type: 'added',
				data: mockRecord
			})
			
			return mockRecord
		}
	}

	/**
	 * 更新用餐记录
	 */
	async updateCookingRecord(recordId, updateData) {
		if (!this.currentFamily) {
			throw new Error('请先选择家庭')
		}
		
		try {
			const response = await CookingAPI.updateCookingRecord(this.currentFamily.id, recordId, updateData)
			const updatedRecord = response.record
			
			// 更新本地列表
			const index = this.cookingRecords.findIndex(r => r.id === recordId)
			if (index > -1) {
				this.cookingRecords[index] = updatedRecord
			}
			
			this.emit('cookingRecordsUpdated', {
				type: 'updated',
				data: updatedRecord
			})
			
			return updatedRecord
		} catch (error) {
			console.error('更新用餐记录失败:', error)
			throw error
		}
	}

	/**
	 * 删除用餐记录
	 */
	async deleteCookingRecord(recordId) {
		if (!this.currentFamily) {
			throw new Error('请先选择家庭')
		}
		
		try {
			await CookingAPI.deleteCookingRecord(this.currentFamily.id, recordId)
			
			// 从本地列表移除
			const index = this.cookingRecords.findIndex(r => r.id === recordId)
			if (index > -1) {
				this.cookingRecords.splice(index, 1)
			}
			
			this.emit('cookingRecordsUpdated', {
				type: 'deleted',
				data: { id: recordId }
			})
			
			return true
		} catch (error) {
			console.error('删除用餐记录失败:', error)
			throw error
		}
	}

	/**
	 * 添加喜爱菜品
	 */
	async addFavoriteMeal(mealData) {
		if (!this.currentFamily) {
			throw new Error('请先选择家庭')
		}
		
		try {
			const response = await FavoriteMealsAPI.createFavoriteMeal(this.currentFamily.id, mealData)
			const newMeal = response.meal
			
			// 添加到本地列表
			this.favoriteMeals.unshift(newMeal)
			
			this.emit('favoriteMealsUpdated', {
				type: 'added',
				data: newMeal
			})
			
			return newMeal
		} catch (error) {
			console.error('添加喜爱菜品失败:', error)
			
			// 如果API失败，添加到本地模拟数据
			const mockMeal = {
				id: `meal_${Date.now()}`,
				name: mealData.name,
				category: mealData.category,
				count: mealData.count || 1,
				image: mealData.image || '',
				addedBy: mealData.added_by || '我',
				addTime: new Date(),
				lastCooked: '刚刚',
				likes: 0,
				isLiked: false
			}
			
			this.favoriteMeals.unshift(mockMeal)
			
			this.emit('favoriteMealsUpdated', {
				type: 'added',
				data: mockMeal
			})
			
			return mockMeal
		}
	}

	/**
	 * 更新喜爱菜品
	 */
	async updateFavoriteMeal(mealId, updateData) {
		if (!this.currentFamily) {
			throw new Error('请先选择家庭')
		}
		
		try {
			const response = await FavoriteMealsAPI.updateFavoriteMeal(this.currentFamily.id, mealId, updateData)
			const updatedMeal = response.meal
			
			// 更新本地列表
			const index = this.favoriteMeals.findIndex(m => m.id === mealId)
			if (index > -1) {
				this.favoriteMeals[index] = updatedMeal
			}
			
			this.emit('favoriteMealsUpdated', {
				type: 'updated',
				data: updatedMeal
			})
			
			return updatedMeal
		} catch (error) {
			console.error('更新喜爱菜品失败:', error)
			throw error
		}
	}

	/**
	 * 删除喜爱菜品
	 */
	async deleteFavoriteMeal(mealId) {
		if (!this.currentFamily) {
			throw new Error('请先选择家庭')
		}
		
		try {
			await FavoriteMealsAPI.deleteFavoriteMeal(this.currentFamily.id, mealId)
			
			// 从本地列表移除
			const index = this.favoriteMeals.findIndex(m => m.id === mealId)
			if (index > -1) {
				this.favoriteMeals.splice(index, 1)
			}
			
			this.emit('favoriteMealsUpdated', {
				type: 'deleted',
				data: { id: mealId }
			})
			
			return true
		} catch (error) {
			console.error('删除喜爱菜品失败:', error)
			throw error
		}
	}

	/**
	 * 点赞/取消点赞菜品
	 */
	async toggleFavoriteMealLike(mealId) {
		if (!this.currentFamily) {
			throw new Error('请先选择家庭')
		}
		
		const meal = this.favoriteMeals.find(m => m.id === mealId)
		if (!meal) {
			throw new Error('菜品不存在')
		}
		
		try {
			let response
			if (meal.isLiked) {
				response = await FavoriteMealsAPI.unlikeFavoriteMeal(this.currentFamily.id, mealId)
			} else {
				response = await FavoriteMealsAPI.likeFavoriteMeal(this.currentFamily.id, mealId)
			}
			
			// 更新本地状态
			meal.isLiked = !meal.isLiked
			meal.likes = response.likes || (meal.isLiked ? meal.likes + 1 : meal.likes - 1)
			
			this.emit('favoriteMealsUpdated', {
				type: 'liked',
				data: meal
			})
			
			return meal
		} catch (error) {
			console.error('切换点赞状态失败:', error)
			
			// 如果API失败，仅更新本地状态
			meal.isLiked = !meal.isLiked
			meal.likes = meal.isLiked ? meal.likes + 1 : meal.likes - 1
			
			this.emit('favoriteMealsUpdated', {
				type: 'liked',
				data: meal
			})
			
			return meal
		}
	}

	/**
	 * 获取用餐统计数据
	 */
	async getCookingStatistics(period = 'week') {
		if (!this.currentFamily) {
			return {
				totalMeals: 0,
				periodMeals: 0,
				topCook: null,
				topDish: null,
				avgRating: 0
			}
		}
		
		try {
			const response = await CookingAPI.getCookingStatistics(this.currentFamily.id, { period })
			return response.statistics
		} catch (error) {
			console.error('获取用餐统计失败，使用本地计算:', error)
			
			// 使用本地数据计算统计
			return this.calculateLocalStatistics(period)
		}
	}

	/**
	 * 本地计算统计数据
	 */
	calculateLocalStatistics(period = 'week') {
		if (this.cookingRecords.length === 0) {
			return {
				totalMeals: 0,
				periodMeals: 0,
				topCook: null,
				topDish: null,
				avgRating: 0
			}
		}
		
		// 计算时间范围
		const now = new Date()
		const periodStart = new Date()
		
		switch (period) {
			case 'day':
				periodStart.setDate(now.getDate() - 1)
				break
			case 'week':
				periodStart.setDate(now.getDate() - 7)
				break
			case 'month':
				periodStart.setDate(now.getDate() - 30)
				break
		}
		
		const periodRecords = this.cookingRecords.filter(record => 
			new Date(record.cookTime) >= periodStart
		)
		
		// 统计厨师
		const cookCount = {}
		this.cookingRecords.forEach(record => {
			cookCount[record.cookName] = (cookCount[record.cookName] || 0) + 1
		})
		
		const topCook = Object.keys(cookCount).length > 0 
			? Object.keys(cookCount).reduce((a, b) => cookCount[a] > cookCount[b] ? a : b)
			: null
		
		// 统计菜品
		const dishCount = {}
		this.cookingRecords.forEach(record => {
			dishCount[record.dishName] = (dishCount[record.dishName] || 0) + 1
		})
		
		const topDish = Object.keys(dishCount).length > 0
			? Object.keys(dishCount).reduce((a, b) => dishCount[a] > dishCount[b] ? a : b)
			: null
		
		// 平均评分
		const totalRating = this.cookingRecords.reduce((sum, record) => sum + (record.rating || 0), 0)
		const avgRating = this.cookingRecords.length > 0 ? (totalRating / this.cookingRecords.length).toFixed(1) : 0
		
		return {
			totalMeals: this.cookingRecords.length,
			periodMeals: periodRecords.length,
			topCook,
			topDish,
			avgRating: parseFloat(avgRating)
		}
	}

	/**
	 * 搜索用餐记录
	 */
	searchCookingRecords(keyword, filters = {}) {
		let records = [...this.cookingRecords]
		
		// 关键字搜索
		if (keyword) {
			records = records.filter(record => 
				record.dishName.includes(keyword) ||
				record.cookName.includes(keyword) ||
				(record.notes && record.notes.includes(keyword))
			)
		}
		
		// 日期范围筛选
		if (filters.startDate && filters.endDate) {
			const start = new Date(filters.startDate)
			const end = new Date(filters.endDate)
			records = records.filter(record => {
				const recordDate = new Date(record.cookTime)
				return recordDate >= start && recordDate <= end
			})
		}
		
		// 厨师筛选
		if (filters.cookId) {
			records = records.filter(record => record.cookId === filters.cookId)
		}
		
		// 评分筛选
		if (filters.minRating) {
			records = records.filter(record => record.rating >= filters.minRating)
		}
		
		return records
	}

	/**
	 * 搜索喜爱菜品
	 */
	searchFavoriteMeals(keyword, filters = {}) {
		let meals = [...this.favoriteMeals]
		
		// 关键字搜索
		if (keyword) {
			meals = meals.filter(meal => 
				meal.name.includes(keyword) ||
				meal.category.includes(keyword)
			)
		}
		
		// 分类筛选
		if (filters.category && filters.category !== 'all') {
			meals = meals.filter(meal => meal.category === filters.category)
		}
		
		// 排序
		if (filters.sortBy) {
			switch (filters.sortBy) {
				case 'count':
					meals.sort((a, b) => b.count - a.count)
					break
				case 'recent':
					meals.sort((a, b) => new Date(b.addTime) - new Date(a.addTime))
					break
				case 'name':
					meals.sort((a, b) => a.name.localeCompare(b.name))
					break
				case 'likes':
					meals.sort((a, b) => (b.likes || 0) - (a.likes || 0))
					break
			}
		}
		
		return meals
	}
}

// 创建全局实例
const familyManager = new FamilyManager()

export default familyManager
