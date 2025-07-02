// 菜谱管理器
import { RecipeAPI } from './api.js'
import userManager from './userManager.js'

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

// 模拟菜谱数据
const FILTERED_RECIPES = [
	{
		id: 1,
		name: '红烧肉',
		description: '软糯香甜的经典家常菜，肥而不腻，入口即化',
		category: 'meat',
		difficulty: 3,
		cook_time: 60,
		servings: 4,
		cover_image: '/static/dishes/hongshaorou.jpg',
		tags: ['荤菜', '热菜', '下饭', '经典'],
		is_public: true,
		success_count: 8,
		total_attempts: 10,
		success_rate: 80,
		rating: 4.5,
		likes: 15,
		author: {
			openid: 'test_user_recipe',
			nickname: '美食达人',
			avatar: '/static/default-avatar.png'
		},
		can_edit: false,
		created_at: '2024-01-15T10:30:00',
		updated_at: '2024-01-15T10:30:00'
	},
	{
		id: 2,
		name: '清炒时蔬',
		description: '清淡健康的素食料理，保持蔬菜的原汁原味',
		category: 'vegetable',
		difficulty: 1,
		cook_time: 15,
		servings: 2,
		cover_image: '/static/dishes/qingchaoshishu.jpg',
		tags: ['素菜', '清淡', '健康', '快手'],
		is_public: true,
		success_count: 12,
		total_attempts: 12,
		success_rate: 100,
		rating: 4.2,
		likes: 8,
		author: {
			openid: 'test_user_recipe',
			nickname: '美食达人',
			avatar: '/static/default-avatar.png'
		},
		can_edit: false,
		created_at: '2024-01-10T14:20:00',
		updated_at: '2024-01-10T14:20:00'
	},
	{
		id: 3,
		name: '蒸蛋羹',
		description: '嫩滑如豆腐的营养蒸蛋，老少皆宜',
		category: 'other',
		difficulty: 2,
		cook_time: 20,
		servings: 2,
		cover_image: '/static/dishes/zhengdangeng.jpg',
		tags: ['蛋类', '嫩滑', '营养', '蒸制'],
		is_public: false,
		success_count: 5,
		total_attempts: 6,
		success_rate: 83,
		rating: 4.0,
		likes: 6,
		author: {
			openid: 'test_user_recipe',
			nickname: '美食达人',
			avatar: '/static/default-avatar.png'
		},
		can_edit: false,
		created_at: '2024-01-08T16:45:00',
		updated_at: '2024-01-08T16:45:00'
	},
	{
		id: 4,
		name: '鸡蛋葱油饼',
		description: '外酥内软的经典早餐，香气扑鼻',
		category: 'staple',
		difficulty: 2,
		cook_time: 25,
		servings: 3,
		cover_image: '/static/dishes/jidanconglyoubing.jpg',
		tags: ['主食', '早餐', '香酥', '家常'],
		is_public: true,
		success_count: 6,
		total_attempts: 8,
		success_rate: 75,
		rating: 4.3,
		likes: 10,
		author: {
			openid: 'another_user',
			nickname: '早餐专家',
			avatar: '/static/default-avatar.png'
		},
		can_edit: false,
		created_at: '2024-01-05T08:15:00',
		updated_at: '2024-01-05T08:15:00'
	},
	{
		id: 5,
		name: '麻婆豆腐',
		description: '川菜经典，麻辣鲜香，下饭神器',
		category: 'meat',
		difficulty: 3,
		cook_time: 30,
		servings: 3,
		cover_image: '/static/dishes/mapodoufu.jpg',
		tags: ['川菜', '麻辣', '下饭', '经典'],
		is_public: true,
		success_count: 7,
		total_attempts: 9,
		success_rate: 78,
		rating: 4.6,
		likes: 18,
		author: {
			openid: 'another_user',
			nickname: '早餐专家',
			avatar: '/static/default-avatar.png'
		},
		can_edit: false,
		created_at: '2024-01-03T18:30:00',
		updated_at: '2024-01-03T18:30:00'
	},
	{
		id: 6,
		name: '糖醋排骨',
		description: '酸甜可口的经典菜肴，老少皆宜',
		category: 'meat',
		difficulty: 3,
		cook_time: 45,
		servings: 4,
		cover_image: '/static/dishes/tangcupaigu.jpg',
		tags: ['荤菜', '酸甜', '下饭', '家常'],
		is_public: true,
		success_count: 4,
		total_attempts: 5,
		success_rate: 80,
		rating: 4.4,
		likes: 12,
		author: {
			openid: 'third_user',
			nickname: '厨房新手',
			avatar: '/static/default-avatar.png'
		},
		can_edit: false,
		created_at: '2024-01-01T12:00:00',
		updated_at: '2024-01-01T12:00:00'
	}
];

class RecipeManager {
	constructor() {
		this.recipes = []
		this.currentRecipe = null
		this.categories = [
			{ label: '全部', value: 'all' },
			{ label: '荤菜', value: 'meat' },
			{ label: '素菜', value: 'vegetable' },
			{ label: '汤品', value: 'soup' },
			{ label: '主食', value: 'staple' },
			{ label: '小食', value: 'snack' },
			{ label: '甜品', value: 'dessert' }
		]
		
		// 模拟数据开关
		this.useSimulatedData = false
	}
	
	// ==================== 菜谱列表管理 ====================
	
	/**
	 * 获取菜谱列表
	 * @param {Object} params - 查询参数
	 * @param {string} params.mode - 显示模式：'all'(菜谱大全) 或 'user'(我的菜谱)
	 * @param {string} params.category - 分类筛选
	 * @param {string} params.keyword - 搜索关键词
	 * @param {string} params.author - 作者openid（仅在user模式或特定筛选时使用）
	 * @returns {Promise}
	 */
	async getRecipes(params = {}) {
		try {
			if (this.useSimulatedData) {
				return this.getSimulatedRecipes(params)
			}
			
			// 构建API参数
			const apiParams = {
				mode: params.mode || 'all',
				category: params.category || '',
				keyword: params.keyword || '',
				page: params.page || 1
			}
			
			// 获取当前用户信息用于权限判断
			const userInfo = userManager.getUserInfo()
			if (userInfo && userInfo.openid) {
				apiParams.current_user = userInfo.openid
			}
			
			// 在我的菜谱模式下，设置author参数
			if (params.mode === 'user') {
				if (userInfo && userInfo.openid) {
					apiParams.author = userInfo.openid
				} else {
					throw new Error('用户未登录，无法查看我的菜谱')
				}
			} else if (params.author) {

				// 在大全模式下按作者筛选
				apiParams.author = params.author
			}
			
			const headers = {}
			if (userInfo && userInfo.token) {
				headers.Authorization = `Bearer ${userInfo.token}`
			}

			const result = await RecipeAPI.getRecipes(apiParams, headers)
			console.log('菜谱请求参数:', apiParams);
			console.log('菜谱返回结果:', result);
			if (result.success) {
				this.recipes = result.data || []
				return result
			} else {
				throw new Error(result.error || '获取菜谱列表失败')
			}
		} catch (error) {
			console.error('获取菜谱列表失败:', error)
			// 降级使用模拟数据
			return this.getSimulatedRecipes(params)
		}
	}
	
	/**
	 * 获取菜谱详情
	 * @param {number} recipeId - 菜谱ID
	 * @returns {Promise}
	 */
	async getRecipeDetail(recipeId) {
		try {
			if (this.useSimulatedData) {
				return this.getSimulatedRecipeDetail(recipeId)
			}
			
			const result = await RecipeAPI.getRecipeDetail(recipeId)
			if (result.success) {
				this.currentRecipe = result.data
				return result
			} else {
				throw new Error(result.error || '获取菜谱详情失败')
			}
		} catch (error) {
			console.error('获取菜谱详情失败:', error)
			// 降级使用模拟数据
			return this.getSimulatedRecipeDetail(recipeId)
		}
	}
	
	/**
	 * 创建菜谱
	 * @param {Object} recipeData - 菜谱数据
	 * @returns {Promise}
	 */
	async createRecipe(recipeData) {
		try {
			// 添加作者信息
			const userInfo = userManager.getUserInfo()
			if (!userInfo.openid) {
				throw new Error('用户未登录')
			}
			
			recipeData.author_openid = userInfo.openid
			
			if (this.useSimulatedData) {
				return this.createSimulatedRecipe(recipeData)
			}
			
			const result = await RecipeAPI.createRecipe(recipeData)
			if (result.success) {
				// 刷新列表
				await this.getRecipes()
				return result
			} else {
				throw new Error(result.error || '创建菜谱失败')
			}
		} catch (error) {
			console.error('创建菜谱失败:', error)
			// 降级使用模拟数据
			return this.createSimulatedRecipe(recipeData)
		}
	}
	
	/**
	 * 更新菜谱
	 * @param {number} recipeId - 菜谱ID
	 * @param {Object} recipeData - 更新数据
	 * @returns {Promise}
	 */
	async updateRecipe(recipeId, recipeData) {
		try {
			if (this.useSimulatedData) {
				return this.updateSimulatedRecipe(recipeId, recipeData)
			}
			
			const result = await RecipeAPI.updateRecipe(recipeId, recipeData)
			if (result.success) {
				// 刷新当前菜谱
				await this.getRecipeDetail(recipeId)
				return result
			} else {
				throw new Error(result.error || '更新菜谱失败')
			}
		} catch (error) {
			console.error('更新菜谱失败:', error)
			// 降级使用模拟数据
			return this.updateSimulatedRecipe(recipeId, recipeData)
		}
	}
	
	/**
	 * 删除菜谱
	 * @param {number} recipeId - 菜谱ID
	 * @returns {Promise}
	 */
	async deleteRecipe(recipeId) {
		try {
			if (this.useSimulatedData) {
				return this.deleteSimulatedRecipe(recipeId)
			}
			
			const result = await RecipeAPI.deleteRecipe(recipeId)
			if (result.success) {
				// 从列表中移除
				this.recipes = this.recipes.filter(recipe => recipe.id !== recipeId)
				return result
			} else {
				throw new Error(result.error || '删除菜谱失败')
			}
		} catch (error) {
			console.error('删除菜谱失败:', error)
			// 降级使用模拟数据
			return this.deleteSimulatedRecipe(recipeId)
		}
	}
	
	// ==================== 制作笔记和收藏功能 ====================
	
	/**
	 * 创建制作笔记
	 * @param {number} recipeId - 菜谱ID
	 * @param {Object} noteData - 笔记数据
	 * @returns {Promise}
	 */
	async createRecipeNote(recipeId, noteData) {
		try {
			// 添加作者信息
			const userInfo = userManager.getUserInfo()
			if (!userInfo.openid) {
				throw new Error('用户未登录')
			}
			
			noteData.author_openid = userInfo.openid
			
			if (this.useSimulatedData) {
				return this.createSimulatedRecipeNote(recipeId, noteData)
			}
			
			const result = await RecipeAPI.createRecipeNote(recipeId, noteData)
			if (result.success) {
				return result
			} else {
				throw new Error(result.error || '创建笔记失败')
			}
		} catch (error) {
			console.error('创建制作笔记失败:', error)
			// 降级使用模拟数据
			return this.createSimulatedRecipeNote(recipeId, noteData)
		}
	}
	
	/**
	 * 收藏/取消收藏菜谱
	 * @param {number} recipeId - 菜谱ID
	 * @returns {Promise}
	 */
	async toggleFavorite(recipeId) {
		try {
			if (this.useSimulatedData) {
				return this.toggleSimulatedFavorite(recipeId)
			}
			
			const result = await RecipeAPI.toggleFavorite(recipeId)
			if (result.success) {
				// 如果当前有详情数据，更新点赞数
				if (this.currentRecipe && this.currentRecipe.id == recipeId) {
					this.currentRecipe.likes = result.data.likes
				}
				return result
			} else {
				throw new Error(result.error || '操作失败')
			}
		} catch (error) {
			console.error('收藏操作失败:', error)
			// 降级使用模拟数据
			return this.toggleSimulatedFavorite(recipeId)
		}
	}

	// ==================== 工具方法 ====================
	
	/**
	 * 获取分类列表
	 * @returns {Array}
	 */
	getCategories() {
		return this.categories
	}
	
	/**
	 * 根据分类值获取分类标签
	 * @param {string} value - 分类值
	 * @returns {string}
	 */
	getCategoryLabel(value) {
		const category = this.categories.find(cat => cat.value === value)
		return category ? category.label : '其他'
	}
	
	/**
	 * 格式化难度
	 * @param {number} difficulty - 难度值(1-5)
	 * @returns {string}
	 */
	formatDifficulty(difficulty) {
		const levels = ['', '简单', '一般', '中等', '困难', '大师级']
		return levels[difficulty] || '未知'
	}
	
	// ==================== 模拟数据方法 ====================
	
	/**
	 * 获取模拟菜谱列表
	 * @param {Object} params - 查询参数
	 * @returns {Promise}
	 */
	async getSimulatedRecipes(params = {}) {
		// 使用buildQueryString替代URLSearchParams处理参数
		const queryString = buildQueryString(params);
		console.log('模拟请求参数:', queryString);
		
		// 直接从params对象获取参数
		const { mode, category, keyword, page = 1 } = params;
		
		// 模拟分页和筛选逻辑
		let simulatedRecipes = [...FILTERED_RECIPES];
		
		// 分类筛选
		if (category && category !== 'all') {
			simulatedRecipes = simulatedRecipes.filter(recipe => recipe.category === category);
		}
		
		// 关键词搜索
		if (keyword) {
			const lowerKeyword = keyword.toLowerCase();
			simulatedRecipes = simulatedRecipes.filter(recipe => 
				recipe.name.toLowerCase().includes(lowerKeyword) || 
				recipe.description.toLowerCase().includes(lowerKeyword)
			);
		}
		
		// 模式筛选（我的菜谱）
		if (mode === 'user') {
			const userInfo = userManager.getUserInfo();
			if (userInfo && userInfo.openid) {
				simulatedRecipes = simulatedRecipes.filter(recipe => recipe.author.openid === userInfo.openid);
			}
		}
		
		// 模拟分页
		const pageSize = 10;
		const startIndex = (page - 1) * pageSize;
		const paginatedRecipes = simulatedRecipes.slice(startIndex, startIndex + pageSize);
		
		return {
			success: true,
			data: paginatedRecipes,
			total_available: simulatedRecipes.length
		};
	}
	
	/**
	 * 获取模拟菜谱详情
	 * @param {number} recipeId - 菜谱ID
	 * @returns {Promise}
	 */
	async getSimulatedRecipeDetail(recipeId) {
		// 模拟网络延迟
		await new Promise(resolve => setTimeout(resolve, 200))
		
		const recipes = await this.getSimulatedRecipes()
		const recipe = recipes.data.find(r => r.id == recipeId)
		
		if (!recipe) {
			throw new Error('菜谱不存在')
		}
		
		// 添加详细信息
		recipe.ingredients = [
			{ id: 1, name: '五花肉', amount: '500', unit: '克', category: 'main', notes: '选择肥瘦相间的', order: 1 },
			{ id: 2, name: '生抽', amount: '2', unit: '勺', category: 'seasoning', notes: '', order: 2 },
			{ id: 3, name: '老抽', amount: '1', unit: '勺', category: 'seasoning', notes: '上色用', order: 3 },
			{ id: 4, name: '冰糖', amount: '适量', unit: '', category: 'seasoning', notes: '', order: 4 }
		]
		
		recipe.steps = [
			{
				id: 1,
				step_number: 1,
				title: '准备食材',
				description: '将五花肉切成合适大小的块状，准备好各种调料。',
				images: [],
				time_required: 10,
				temperature: '',
				tips: '肉块不要切太小，以免炖煮后过于软烂'
			},
			{
				id: 2,
				step_number: 2,
				title: '炒糖色',
				description: '锅中放入少量油，小火加热，放入冰糖炒至焦糖色。',
				images: [],
				time_required: 5,
				temperature: '小火',
				tips: '一定要小火，避免炒糊'
			},
			{
				id: 3,
				step_number: 3,
				title: '炖煮',
				description: '加入肉块翻炒上色，然后加入生抽、老抽和适量热水，大火烧开后转小火炖40分钟。',
				images: [],
				time_required: 45,
				temperature: '先大火后小火',
				tips: '水要没过肉块，中途可以尝味调整'
			}
		]
		
		recipe.notes = [
			{
				id: 1,
				content: '第一次做成功了！肉很软烂，味道很好。',
				images: [],
				rating: 5,
				success: true,
				modifications: '下次可以加点八角增香',
				cooking_date: '2025-01-01T18:30:00',
				author: {
					openid: 'test_user_1',
					nickname: '小厨师',
					avatar: '/static/default-avatar.png'
				}
			}
		]
		
		return {
			success: true,
			data: recipe
		}
	}
	
	/**
	 * 创建模拟菜谱
	 * @param {Object} recipeData - 菜谱数据
	 * @returns {Promise}
	 */
	async createSimulatedRecipe(recipeData) {
		// 模拟网络延迟
		await new Promise(resolve => setTimeout(resolve, 500))
		
		const newRecipe = {
			id: Date.now(), // 使用时间戳作为ID
			...recipeData,
			author: {
				openid: recipeData.author_openid,
				nickname: '用户',
				avatar: '/static/default-avatar.png'
			},
			success_count: 0,
			total_attempts: 0,
			success_rate: 0,
			rating: 0,
			likes: 0,
			created_at: new Date().toISOString(),
			updated_at: new Date().toISOString()
		}
		
		return {
			success: true,
			data: newRecipe,
			message: '菜谱创建成功'
		}
	}
	
	/**
	 * 更新模拟菜谱
	 * @param {number} recipeId - 菜谱ID
	 * @param {Object} recipeData - 更新数据
	 * @returns {Promise}
	 */
	async updateSimulatedRecipe(recipeId, recipeData) {
		// 模拟网络延迟
		await new Promise(resolve => setTimeout(resolve, 300))
		
		return {
			success: true,
			message: '菜谱更新成功'
		}
	}
	
	/**
	 * 删除模拟菜谱
	 * @param {number} recipeId - 菜谱ID
	 * @returns {Promise}
	 */
	async deleteSimulatedRecipe(recipeId) {
		// 模拟网络延迟
		await new Promise(resolve => setTimeout(resolve, 200))
		
		return {
			success: true,
			message: '菜谱删除成功'
		}
	}
	
	/**
	 * 创建模拟制作笔记
	 * @param {number} recipeId - 菜谱ID
	 * @param {Object} noteData - 笔记数据
	 * @returns {Promise}
	 */
	async createSimulatedRecipeNote(recipeId, noteData) {
		// 模拟网络延迟
		await new Promise(resolve => setTimeout(resolve, 300))
		
		const newNote = {
			id: Date.now(),
			recipe_id: recipeId,
			content: noteData.content,
			images: noteData.images || [],
			rating: noteData.rating || 5,
			success: noteData.success !== undefined ? noteData.success : true,
			modifications: noteData.modifications || '',
			cooking_date: noteData.cooking_date || new Date().toISOString(),
			author: {
				openid: noteData.author_openid,
				nickname: '用户',
				avatar: '/static/default-avatar.png'
			}
		}
		
		return {
			success: true,
			data: newNote,
			message: '制作笔记保存成功'
		}
	}
	
	/**
	 * 模拟收藏切换
	 * @param {number} recipeId - 菜谱ID
	 * @returns {Promise}
	 */
	async toggleSimulatedFavorite(recipeId) {
		// 模拟网络延迟
		await new Promise(resolve => setTimeout(resolve, 200))
		
		// 随机增减点赞数
		const currentLikes = this.currentRecipe?.likes || 0
		const newLikes = Math.max(0, currentLikes + (Math.random() > 0.5 ? 1 : -1))
		
		return {
			success: true,
			data: {
				likes: newLikes,
				favorited: Math.random() > 0.5 // 随机状态
			},
			message: '操作成功'
		}
	}
	
	/**
	 * 检查菜谱名称是否重复
	 * @param {string} name - 菜谱名称
	 * @returns {Promise}
	 */
	async checkRecipeName(name) {
		try {
			// 添加作者信息
			const userInfo = userManager.getUserInfo()
			if (!userInfo.openid) {
				throw new Error('用户未登录')
			}
			
			if (this.useSimulatedData) {
				// 模拟检查：简单检查名称长度
				const exists = name.length < 2
				return {
					success: true,
					exists: exists,
					message: exists ? `名称"${name}"已存在，请使用不同的名称` : `名称"${name}"可以使用`
				}
			}
			
			const result = await RecipeAPI.checkRecipeName(name, userInfo.openid)
			return result
			
		} catch (error) {
			console.error('检查菜谱名称失败:', error)
			// 降级：允许继续使用
			return {
				success: true,
				exists: false,
				message: '无法检查名称重复性，请谨慎使用'
			}
		}
	}
}

// 创建全局实例
const recipeManager = new RecipeManager()

export default recipeManager
