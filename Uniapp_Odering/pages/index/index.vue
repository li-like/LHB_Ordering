<template>
	<view class="container">
		<!-- 顶部用户信息栏 -->
		<view class="header">
			<view class="user-info">
				<image class="avatar" :src="userInfo.avatarUrl || '../../static/default-avatar.png'" mode="aspectFill"></image>
				<view class="greeting">
					<text class="welcome">你好，{{ userInfo.nickName || '家庭用户' }}</text>
					<text class="time-text">{{ greeting }}</text>
				</view>
			</view>
			<view class="family-info" @click="goToFamily">
				<text class="family-name">{{ familyData.familyName + '的小家' || '我的家庭' }}</text>
				<text class="member-count">{{ familyData.members?.length || 1 }}位成员</text>
				<text class="arrow">></text>
			</view>
		</view>
		
		<!-- 快速操作区域 -->
		<view class="quick-actions">
			<view class="action-item" @click="goToOrdering">
				<view class="action-icon ordering-icon">
					<text class="icon-text">🍽️</text>
				</view>
				<text class="action-label">家庭餐厅</text>
				<text class="action-desc">查看点餐</text>
			</view>
			
			<view class="action-item" @click="randomOrder">
				<view class="action-icon random-icon">
					<text class="icon-text">🎲</text>
				</view>
				<text class="action-label">随便来点</text>
				<text class="action-desc">不知道吃什么</text>
			</view>
			
			<view class="action-item" @click="goToRecipes">
				<view class="action-icon recipe-icon">
					<text class="icon-text">📖</text>
				</view>
				<text class="action-label">菜谱大全</text>
				<text class="action-desc">记录做菜</text>
			</view>
			
			<view class="action-item" @click="goToHistory">
				<view class="action-icon history-icon">
					<text class="icon-text">📊</text>
				</view>
				<text class="action-label">饮食记录</text>
				<text class="action-desc">查看偏好</text>
			</view>
		</view>
		
		<!-- 今日推荐轮播 -->
		<view class="recommendation-banner">
			<swiper class="swiper" circular="true" autoplay="true" interval="3000" duration="500" indicator-dots="true" indicator-color="rgba(255,255,255,0.5)" indicator-active-color="#FF6B95">
				<swiper-item v-for="(item, index) in recommendations" :key="index" @click="selectDish(item)">
					<view class="banner-item">
						<image class="banner-image" :src="item.image" mode="aspectFill"></image>
						<view class="banner-overlay">
							<text class="banner-title">{{ item.name }}</text>
							<text class="banner-desc">{{ item.tags.join(' · ') }} · {{ item.cookTime }}分钟</text>
						</view>
					</view>
				</swiper-item>
			</swiper>
		</view>
		
		<!-- 点餐区域 -->
		<view class="ordering-section">
			<view class="section-header">
				<view class="section-title-row">
					<view class="section-title-left">
						<text class="section-title">开始点餐</text>
						<text class="section-subtitle">选择你想要的美食</text>
					</view>
					<!-- 管理员权限切换按钮（仅管理员可见） -->
					<view v-if="canToggleAdminMode" class="admin-toggle-compact" @click="toggleAdminMode">
						<text class="admin-toggle-icon">{{ isAdmin ? '👑' : '👤' }}</text>
						<text class="admin-toggle-label">{{ isAdmin ? '管理员' : '普通用户' }}</text>
					</view>
				</view>
			</view>
			
			<view class="ordering-container">
				<!-- 左侧分类列表 -->
				<scroll-view class="category-sidebar" scroll-y="true">
					<view 
						class="category-tab" 
						:class="{ 'active': activeCategory === category.id }" 
						v-for="category in foodCategories" 
						:key="category.id"
						@click="selectFoodCategory(category.id)"
						@longpress="isAdmin ? manageCategoryOptions(category) : null"
					>
						<text class="category-icon">{{ category.emoji }}</text>
						<text class="category-name">{{ category.name }}</text>
						<text class="item-count">({{ category.items.length }})</text>
						<!-- 管理员：分类管理小图标 -->
						<view v-if="isAdmin && activeCategory === category.id" class="category-manage" @click.stop="manageCategoryOptions(category)">
							<text class="manage-icon">⚙️</text>
						</view>
					</view>
					
					<!-- 管理员：添加新分类按钮 -->
					<view v-if="isAdmin" class="add-category-btn" @click="addNewCategory">
						<view class="add-icon-small">+</view>
						<text class="add-text-small">新分类</text>
					</view>
				</scroll-view>
				
				<!-- 右侧商品列表 -->
				<scroll-view class="food-list" scroll-y="true">
					<view class="food-item" v-for="item in currentCategoryItems" :key="item.id" @click="selectFoodItem(item)">
						<image class="food-image" :src="item.image" mode="aspectFill"></image>
						<view class="food-info">
							<text class="food-name">{{ item.name }}</text>
							<text class="food-desc">{{ item.description }}</text>
							<view class="food-tags">
								<text class="food-tag" v-for="tag in item.tags" :key="tag">{{ tag }}</text>
							</view>
							<view class="food-footer">
								<view class="food-meta">
									<text class="cook-time">🕒 {{ item.cookTime }}分钟</text>
									<text class="difficulty">{{ getDifficultyText(item.difficulty) }}</text>
								</view>
								<view class="food-actions">
									<!-- 普通用户：点餐按钮 -->
									<view v-if="!isAdmin" class="order-btn" @click.stop="addToOrder(item)">
										<text class="order-text">点餐</text>
									</view>
									<!-- 管理员：管理按钮 -->
									<view v-else class="admin-actions">
										<view class="admin-btn edit-btn" @click.stop="editFoodItem(item)">
											<text class="admin-text">编辑</text>
										</view>
										<view class="admin-btn delete-btn" @click.stop="deleteFoodItem(item)">
											<text class="admin-text">删除</text>
										</view>
									</view>
								</view>
							</view>
						</view>
					</view>
					
					<!-- 管理员：添加新菜品按钮 -->
					<view v-if="isAdmin" class="add-food-btn" @click="addNewFoodItem">
						<view class="add-icon">+</view>
						<text class="add-text">添加新菜品</text>
					</view>
				</scroll-view>
			</view>
		</view>
		
		<!-- 点餐车浮动按钮 -->
		<view v-if="hasCartItems" class="cart-float-btn" @click="showCartModal">
			<view class="cart-icon">🛒</view>
			<view class="cart-badge">{{ cartItemCount }}</view>
		</view>
			<!-- 点餐车弹窗 - 美化版本 -->
			<view v-if="showCart" class="cart-modal-overlay" @click="hideCartModal">
				<view class="cart-modal" @click.stop="">
					<!-- 美化的头部区域 -->
					<view class="cart-header">
						<view class="cart-header-left">
							<text class="cart-icon-large">🍽️</text>
							<view class="cart-title-group">
								<text class="cart-title">我的点餐</text>
								<text class="cart-subtitle">{{ cartItemCount }}个美味等着您</text>
							</view>
						</view>
						<view class="cart-header-actions">
							<view class="action-btn clear-btn" @click="clearCart" v-if="hasCartItems">
								<text class="action-icon">🗑️</text>
								<text class="action-text">清空</text>
							</view>
							<view class="close-btn" @click="hideCartModal">
								<text class="close-icon">×</text>
							</view>
						</view>
					</view>
					<!-- 商品列表区域 -->
					<scroll-view class="cart-content" scroll-y="true">
						<!-- 空状态 -->
						<view v-if="cartItems.length === 0" class="cart-empty">
							<view class="empty-icon-wrapper">
								<text class="empty-icon">🛒</text>
								<view class="empty-sparkles">✨</view>
							</view>
							<text class="empty-text">点餐车是空的</text>
							<text class="empty-desc">快去选择您喜欢的美食吧</text>
							<view class="empty-action" @click="hideCartModal">
								<text class="empty-action-text">去点餐</text>
								<text class="empty-action-arrow">→</text>
							</view>
						</view>
						
						<!-- 商品列表 -->
						<view v-else class="cart-items-list">
							<view class="cart-item" v-for="item in cartItems" :key="item.id">
								<!-- 商品图片和数量徽章 -->
								<view class="item-image-wrapper">
									<image class="item-image" :src="item.image || '/static/food-decoration.png'" mode="aspectFill"></image>
									<view class="item-quantity-badge">{{ item.quantity }}</view>
								</view>
								
								<!-- 商品详细信息 -->
								<view class="item-content">
									<view class="item-main-info">
										<text class="item-name">{{ item.name }}</text>
										<view class="item-tags" v-if="item.tags && item.tags.length > 0">
											<text class="item-tag" v-for="tag in item.tags.slice(0, 3)" :key="tag">{{ tag }}</text>
										</view>
									</view>
									
									<view class="item-meta-info">
										<view class="meta-item">
											<text class="meta-icon">⏱️</text>
											<text class="meta-text">{{ item.cookTime || 30 }}分钟</text>
										</view>
										<view class="meta-item">
											<text class="meta-icon">⭐</text>
											<text class="meta-text">{{ getDifficultyText(item.difficulty) }}</text>
										</view>
									</view>
									
									<text class="item-desc">{{ item.description || '暂无描述' }}</text>
								</view>
								
								<!-- 操作区域 -->
								<view class="item-actions">
									<view class="quantity-controls">
										<view class="quantity-btn decrease" @click="decreaseQuantity(item)">
											<text class="btn-icon">−</text>
										</view>
										<text class="quantity-display">{{ item.quantity }}</text>
										<view class="quantity-btn increase" @click="increaseQuantity(item)">
											<text class="btn-icon">＋</text>
										</view>
									</view>
									<view class="remove-btn" @click="removeFromCart(item)">
										<text class="remove-icon">🗑️</text>
									</view>
								</view>
							</view>
						</view>
					</scroll-view>
					<!-- 美化的底部操作区域 -->
					<view class="cart-footer" v-if="cartItems.length > 0">
						<!-- 小贴士区域 -->
						<view class="cart-tips">
							<text class="tips-icon">💡</text>
							<text class="tips-text">{{ getCurrentTip() }}</text>
						</view>
						
						<view class="cart-summary">
							<view class="summary-row main">
								<text class="summary-label">商品数量</text>
								<text class="summary-value">{{ cartItemCount }} 个</text>
							</view>
							<view class="summary-row">
								<text class="summary-label">预计用时</text>
								<text class="summary-value">{{ estimatedTime }} 分钟</text>
							</view>
							<view class="summary-row">
								<text class="summary-label">烹饪难度</text>
								<text class="summary-value">{{ overallDifficulty }}</text>
							</view>
						</view>
						<view class="submit-area">
							<view class="submit-btn" @click="submitOrder">
								<text class="submit-icon">🍽️</text>
								<text class="submit-text">提交订单</text>
								<text class="submit-arrow">→</text>
							</view>
						</view>
					</view>
			</view>
		</view>
	</view>
</template>

<script>
import userManager from '../../utils/userManager.js'
import orderingManager from '../../utils/orderingManager.js'

export default {
	data() {
		return {
			userInfo: {},
			familyData: {},
			greeting: '',
			activeCategory: null, // 当前选中的分类ID，将在数据加载后设置
			nextFoodId: 1000, // 下一个商品ID
			nextCategoryId: 10, // 下一个分类ID
			loading: false, // 加载状态
			recommendations: [
				{
					id: 1,
					name: '红烧肉',
					image: '/static/dishes/hongshaorou.jpg',
					tags: ['荤菜', '热菜', '下饭'],
					cookTime: 45
				},
				{
					id: 2,
					name: '清炒时蔬',
					image: '/static/dishes/qingchaoshishu.jpg',
					tags: ['素菜', '清淡', '健康'],
					cookTime: 15
				},
				{
					id: 3,
					name: '蒸蛋羹',
					image: '/static/dishes/zhengdangeng.jpg',
					tags: ['蛋类', '嫩滑', '营养'],
					cookTime: 20
				}
			],
			// 食物分类及对应商品（初始为空，从后端加载）
			foodCategories: [],
			
			// 点餐车相关数据
			cartItems: [], // 点餐车商品列表
			showCart: false, // 是否显示点餐车浮窗
			cartTotal: 0, // 点餐车总价（如果有价格的话）
			// 小贴士列表
			tips: [
				"点击食物可以查看详情和添加到点餐车",
				"家庭成员可以一起在线点餐",
				"长按商品可以快速添加到点餐车",
				"可以在'家庭餐厅'中查看所有成员的点餐",
				"左右滑动可以浏览不同分类的食物"
			]
		}
	},
	
	computed: {
		// 当前选中分类的商品列表
		currentCategoryItems() {
			if (!this.activeCategory) {
				return [];
			}
			
			const category = this.foodCategories.find(cat => cat.id === this.activeCategory);
			return category ? (category.items || []) : [];
		},
		
		// 判断是否为管理员（基于用户角色或家庭权限）
		isAdmin() {
			// 临时逻辑：检查用户是否为家庭创建者或管理员
			// 后续可以根据实际的权限系统调整
			return this.familyData.role === 'admin' || 
				   this.familyData.role === 'creator' || 
				   this.userInfo.role === 'admin' ||
				   this.userInfo.isAdmin === true;
		},
		
		// 判断是否有管理员权限切换功能（仅限超级管理员或开发者）
		canToggleAdminMode() {
			// 只有特定权限的用户才能切换管理员模式
			// 这里可以设置为开发者模式或特定用户
			return this.userInfo.isDeveloper === true || 
				   this.userInfo.role === 'super_admin' ||
				   this.familyData.role === 'creator'; // 家庭创建者可以切换
		},
		
		// 点餐车商品数量
		cartItemCount() {
			return this.cartItems.reduce((total, item) => total + item.quantity, 0);
		},
		
		// 点餐车是否有商品
		hasCartItems() {
			return this.cartItems.length > 0;
		},
		
		// 预计总用时
		estimatedTime() {
			if (!this.hasCartItems) return 0;
			// 取最长的烹饪时间作为预计用时
			return Math.max(...this.cartItems.map(item => item.cookTime || 30));
		},
		
		// 整体烹饪难度
		overallDifficulty() {
			if (!this.hasCartItems) return '简单';
			
			// 计算平均难度
			const difficulties = this.cartItems.map(item => {
				switch (item.difficulty) {
					case 'easy': return 1;
					case 'medium': return 2;
					case 'hard': return 3;
					default: return 1;
				}
			});
			
			const avgDifficulty = difficulties.reduce((sum, val) => sum + val, 0) / difficulties.length;
			
			if (avgDifficulty <= 1.3) return '简单';
			if (avgDifficulty <= 2.3) return '中等';
			return '困难';
		}
	},
	
	onLoad() {
		// 获取用户信息
		this.userInfo = userManager.getUserInfo();
		
		// 获取家庭信息
		this.familyData = this.userInfo.family || {};
		
		// 设置问候语
		this.setGreeting();
		
		// 从后端加载分类和菜品数据
		this.loadBackendData();
		
		// 加载点餐车数据
		this.loadCartFromStorage();
	},
	
	onShow() {
		this.checkLogin(); // 每次显示时都检查登录状态
		this.loadUserData();
		this.updateActiveTime(); // 更新用户活跃时间
		
		// 确保每次返回页面时都恢复管理员模式状态
		this.restoreAdminMode();
	},
	
	onUnload() {
		// 移除用户信息更新监听
		if (this.userInfoUpdateHandler) {
			userManager.offUserInfoUpdated(this.userInfoUpdateHandler);
		}
	},
	
	methods: {
		// 检查登录状态
		async checkLogin() {
			if (!userManager.isLoggedIn()) {
				// 未登录，跳转到登录页
				uni.redirectTo({
					url: '/pages/login/login'
				});
				return;
			}
			
			// #ifdef MP-WEIXIN
			// 检查微信session状态
			try {
				const sessionValid = await userManager.checkWechatSession();
				if (!sessionValid) {
					// 微信session无效，但本地有登录信息，跳转到登录页进行快速登录
					console.log('微信session无效，跳转到登录页');
					uni.redirectTo({
						url: '/pages/login/login'
					});
					return;
				}
			} catch (error) {
				console.error('检查微信session失败:', error);
				// 发生错误时也跳转到登录页
				uni.redirectTo({
					url: '/pages/login/login'
				});
				return;
			}
			// #endif
		},
		
		// 加载用户数据
		async loadUserData() {
			try {
				// 优先尝试从后端获取最新数据
				if (userManager.isLoggedIn()) {
					const backendUserInfo = await userManager.fetchUserCompleteData();
					this.userInfo = backendUserInfo;
				} else {
					// 如果未登录，从本地获取
					this.userInfo = userManager.getUserInfo() || {};
				}
			} catch (error) {
				console.error('从后端加载用户数据失败，使用本地数据:', error);
				// 降级使用本地数据
				this.userInfo = userManager.getUserInfo() || {};
			}
			
			// 加载家庭数据，如果没有role则设置默认值
			this.familyData = userManager.getFamilyData() || {};
			if (!this.familyData.role) {
				this.familyData.role = 'member'; // 默认为普通成员
			}
			
			// 临时：为了测试设置开发者权限（后续删除）
			// 这里可以根据实际需求设置特定用户为开发者
			if (!this.userInfo.isDeveloper) {
				this.userInfo.isDeveloper = true; // 临时设置为开发者，便于测试
			}
			
			// 注意：分类数据在onLoad中通过loadBackendData()加载，这里不需要单独加载
		},
		
		// 更新用户活跃时间
		updateActiveTime() {
			if (userManager.isLoggedIn()) {
				userManager.updateActiveTime();
			}
		},
		
		// 设置问候语
		setGreeting() {
			const hour = new Date().getHours();
			if (hour < 6) {
				this.greeting = '夜深了，注意休息';
			} else if (hour < 9) {
				this.greeting = '早上好，准备早餐吧';
			} else if (hour < 12) {
				this.greeting = '上午好，元气满满';
			} else if (hour < 14) {
				this.greeting = '午餐时间到啦';
			} else if (hour < 18) {
				this.greeting = '下午好，来点下午茶';
			} else if (hour < 22) {
				this.greeting = '晚上好，准备晚餐吧';
			} else {
				this.greeting = '夜宵时间，要不要来点';
			}
		},
		
		// 随机点餐
		randomOrder() {
			uni.showModal({
				title: '随便来点',
				content: '功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 跳转到菜谱页面
		goToRecipes() {
			uni.navigateTo({
				url: '/pages/recipe/index'
			});
		},
		
		// 跳转到饮食记录
		goToHistory() {
			uni.showModal({
				title: '饮食记录',
				content: '功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 跳转到家庭管理
		goToFamily() {
			uni.switchTab({
				url: '/pages/family/family'
			});
		},
		
		// 选择分类
		selectFoodCategory(categoryId) {
			this.activeCategory = categoryId;
		},
		
		// 选择商品
		selectFoodItem(item) {
			// 跳转到菜品详情页面
			const itemData = encodeURIComponent(JSON.stringify(item));
			uni.navigateTo({
				url: `/pages/food/detail?data=${itemData}`
			});
		},
		
		// 添加到点餐车
		addToOrder(item) {
			// 检查商品是否已在点餐车中
			const existingItemIndex = this.cartItems.findIndex(cartItem => cartItem.id === item.id);
			
			if (existingItemIndex !== -1) {
				// 如果已存在，增加数量
				this.cartItems[existingItemIndex].quantity += 1;
			} else {
				// 如果不存在，添加新商品
				this.cartItems.push({
					...item,
					quantity: 1,
					addTime: new Date().getTime() // 添加时间戳
				});
			}
			
			uni.showToast({
				title: `已添加${item.name}到点餐车`,
				icon: 'success',
				duration: 1500
			});
			
			// 保存到本地存储
			this.saveCartToStorage();
		},
		
		// 获取难度文本
		getDifficultyText(difficulty) {
			const difficultyMap = {
				1: '⭐ 简单',
				2: '⭐⭐ 中等', 
				3: '⭐⭐⭐ 困难'
			};
			return difficultyMap[difficulty] || '⭐ 简单';
		},
		
		// 选择菜品（轮播图点击）
		selectDish(dish) {
			// 找到对应的详细商品信息
			let foundItem = null;
			for (let category of this.foodCategories) {
				foundItem = category.items.find(item => item.name === dish.name);
				if (foundItem) break;
			}
			
			if (foundItem) {
				this.selectFoodItem(foundItem);
			} else {
				uni.showModal({
					title: dish.name,
					content: `准备时间：${dish.cookTime}分钟\n标签：${dish.tags.join('、')}`,
					showCancel: false
				});
			}
		},
		
		// 选择分类（删除原来的方法）
		selectCategory(category) {
			// 这个方法已经不需要了，被selectFoodCategory替代
		},
		
		// 跳转到家庭餐厅页面
		goToOrdering() {
			uni.navigateTo({
				url: '/pages/ordering/index'
			});
		},
		
		// === 管理员功能 ===
		
		// 编辑菜品
		editFoodItem(item) {
			// 跳转到菜品编辑页面
			uni.navigateTo({
				url: `/pages/food/edit?id=${item.id}&categoryId=${this.activeCategory}&mode=edit`
			});
		},
		
		// 删除菜品
		deleteFoodItem(item) {
			uni.showModal({
				title: '确认删除',
				content: `确定要删除"${item.name}"吗？`,
				confirmText: '删除',
				cancelText: '取消',
				confirmColor: '#FF6B95',
				success: (res) => {
					if (res.confirm) {
						this.performDeleteFood(item);
					}
				}
			});
		},
		
		// 执行删除菜品
		async performDeleteFood(item) {
			try {
				// 调用后端API删除菜品
				await orderingManager.deleteMeal(item.id);
				
				// 删除成功后，从本地数据中移除
				const categoryIndex = this.foodCategories.findIndex(cat => cat.id === this.activeCategory);
				if (categoryIndex !== -1) {
					const itemIndex = this.foodCategories[categoryIndex].items.findIndex(food => food.id === item.id);
					if (itemIndex !== -1) {
						this.foodCategories[categoryIndex].items.splice(itemIndex, 1);
					}
				}
				
				uni.showToast({
					title: '删除成功',
					icon: 'success'
				});
			} catch (error) {
				console.error('删除菜品失败:', error);
				uni.showToast({
					title: '删除失败',
					icon: 'error'
				});
			}
		},
		
		// 添加新菜品
		addNewFoodItem() {
			// 跳转到菜品添加页面
			uni.navigateTo({
				url: `/pages/food/edit?categoryId=${this.activeCategory}&mode=add`
			});
		},
		
		// 管理分类选项
		manageCategoryOptions(category) {
			uni.showActionSheet({
				itemList: ['编辑分类', '删除分类'],
				success: (res) => {
					if (res.tapIndex === 0) {
						this.editCategory(category);
					} else if (res.tapIndex === 1) {
						this.deleteCategory(category);
					}
				}
			});
		},
		
		// 编辑分类（更新为跳转到分类编辑页面）
		editCategory(category) {
			// 跳转到分类编辑页面
			uni.navigateTo({
				url: `/pages/category/edit?mode=edit&categoryData=${encodeURIComponent(JSON.stringify(category))}`
			});
		},
		
		// 删除分类
		deleteCategory(category) {
			uni.showModal({
				title: '确认删除',
				content: `确定要删除"${category.name}"分类吗？删除后该分类下的所有菜品也将被删除，此操作不可恢复。`,
				confirmText: '删除',
				cancelText: '取消',
				confirmColor: '#FF6B95',
				success: (res) => {
					if (res.confirm) {
						this.performDeleteCategory(category);
					}
				}
			});
		},
		
		// 执行删除分类
		async performDeleteCategory(category) {
			try {
				// 调用后端API删除分类
				await orderingManager.deleteCategory(category.id);
				
				// 删除成功后，从本地数据中移除
				const categoryIndex = this.foodCategories.findIndex(cat => cat.id === category.id);
				if (categoryIndex !== -1) {
					this.foodCategories.splice(categoryIndex, 1);
				}
				
				// 如果删除的是当前选中的分类，切换到第一个分类
				if (this.activeCategory === category.id) {
					// 选择第一个可用分类
					if (this.foodCategories.length > 0) {
						this.selectFoodCategory(this.foodCategories[0].id);
					} else {
						this.activeCategory = null;
					}
				}
				
				uni.showToast({
					title: '删除成功',
					icon: 'success'
				});
			} catch (error) {
				console.error('删除分类失败:', error);
				uni.showToast({
					title: '删除失败',
					icon: 'error'
				});
			}
		},
		
		// 保存更新后的分类列表到缓存（模拟持久化）
		saveFoodCategories() {
			try {
				uni.setStorageSync('foodCategories', JSON.stringify(this.foodCategories));
				console.log('分类数据已保存');
			} catch(e) {
				console.error('保存分类数据失败:', e);
			}
		},
		
		// 从后端加载分类和菜品数据
		async loadBackendData() {
			this.loading = true;
			try {
				// 加载分类
				await this.loadCategoriesFromBackend();
				// 加载菜品
				await this.loadMealsFromBackend();
			} catch (error) {
				console.error('加载后端数据失败:', error);
				uni.showToast({
					title: '加载数据失败',
					icon: 'error'
				});
				// 降级策略：如果后端加载失败，显示空数据或重试
				// 不再调用已删除的loadFoodCategories方法
			} finally {
				this.loading = false;
			}
		},
		
		// 从后端加载分类
		async loadCategoriesFromBackend() {
			try {
				const categories = await orderingManager.getCategoriesSimple();
				console.log('获取到的分类:', categories);
				
				// 转换数据格式以适配前端
				this.foodCategories = categories.map(cat => ({
					id: cat.id,
					name: cat.name,
					emoji: cat.icon || '🍽️',
					items: [] // 初始为空，后续加载菜品
				}));
				
				// 如果有分类，设置第一个分类为默认选中
				if (this.foodCategories.length > 0 && !this.activeCategory) {
					this.activeCategory = this.foodCategories[0].id;
				}
				
			} catch (error) {
				console.error('加载分类失败:', error);
				throw error;
			}
		},
		
		// 从后端加载菜品
		async loadMealsFromBackend() {
			try {
				const meals = await orderingManager.getMeals({ available_only: 'true' });
				console.log('获取到的菜品:', meals);
				
				// 按分类组织菜品数据
				meals.forEach(meal => {
					// 转换数据格式
					const mealItem = {
						id: meal.id,
						name: meal.name,
						description: meal.description || '暂无描述',
						image: meal.image || '/static/food-decoration.png',
						tags: meal.tags || [],
						cookTime: meal.prep_time || 30,
						difficulty: this.mapDifficulty(meal.difficulty),
						categoryId: meal.category
					};
					
					// 找到对应的分类并添加菜品
					const category = this.foodCategories.find(cat => cat.id === meal.category);
					if (category) {
						if (!category.items) {
							category.items = [];
						}
						category.items.push(mealItem);
					}
				});
				
			} catch (error) {
				console.error('加载菜品失败:', error);
				throw error;
			}
		},
		
		// 映射难度值
		mapDifficulty(difficulty) {
			const difficultyMap = {
				'easy': 1,
				'medium': 2,
				'hard': 3
			};
			return difficultyMap[difficulty] || 1;
		},
		
		// 临时设置管理员权限（用于测试）
		toggleAdminMode() {
			// 检查是否有权限切换
			if (!this.canToggleAdminMode) {
				uni.showToast({
					title: '没有权限切换',
					icon: 'none'
				});
				return;
			}
			
			this.familyData.role = this.familyData.role === 'admin' ? 'member' : 'admin';
			
			// 保存管理员模式状态到本地存储
			try {
				uni.setStorageSync('adminModeEnabled', this.familyData.role === 'admin');
				console.log('管理员模式状态已保存:', this.familyData.role === 'admin');
			} catch(e) {
				console.error('保存管理员模式状态失败:', e);
			}
			
			uni.showToast({
				title: this.familyData.role === 'admin' ? '已开启管理员模式' : '已关闭管理员模式',
				icon: 'success'
			});
		},
		
		// 添加新分类
		addNewCategory() {
			// 跳转到分类添加页面
			uni.navigateTo({
				url: '/pages/category/edit?mode=add'
			});
		},
		
		// 处理菜品更新
		handleFoodUpdate(eventData) {
			console.log('接收到菜品更新:', eventData);
			
			const categoryIndex = this.foodCategories.findIndex(cat => cat.id === eventData.categoryId);
			if (categoryIndex === -1) return;
			
			if (eventData.mode === 'add') {
				// 添加新菜品
				const newFood = {
					...eventData.data,
					id: this.nextFoodId++ // 设置新ID
				};
				this.foodCategories[categoryIndex].items.push(newFood);
				
			} else if (eventData.mode === 'edit') {
				// 更新已有菜品
				const itemIndex = this.foodCategories[categoryIndex].items.findIndex(item => item.id === eventData.data.id);
				if (itemIndex !== -1) {
					this.$set(this.foodCategories[categoryIndex].items, itemIndex, eventData.data);
				}
				
			} else if (eventData.mode === 'delete') {
				// 删除菜品
				const itemIndex = this.foodCategories[categoryIndex].items.findIndex(item => item.id === eventData.foodId);
				if (itemIndex !== -1) {
					this.foodCategories[categoryIndex].items.splice(itemIndex, 1);
				}
			}
			
			// 保存更新后的数据到缓存
			this.saveFoodCategories();
		},
		
		// 恢复管理员模式状态
		restoreAdminMode() {
			try {
				const adminModeEnabled = uni.getStorageSync('adminModeEnabled');
				if (adminModeEnabled !== '') {
					// 只有在用户有权限切换管理员模式时才应用存储的状态
					if (this.canToggleAdminMode) {
						const newRole = adminModeEnabled ? 'admin' : 'member';
						if (this.familyData.role !== newRole) {
							this.familyData.role = newRole;
							console.log('从缓存恢复管理员模式状态:', adminModeEnabled);
						}
					}
				}
			} catch(e) {
				console.error('恢复管理员模式状态失败:', e);
			}
		},
		
		// === 点餐车管理功能 ===
		
		// 显示点餐车
		showCartModal() {
			if (!this.hasCartItems) {
				uni.showToast({
					title: '点餐车为空',
					icon: 'none'
				});
				return;
			}
			this.showCart = true;
		},
		
		// 隐藏点餐车
		hideCartModal() {
			this.showCart = false;
		},
		
		// 增加商品数量
		increaseQuantity(item) {
			const cartItem = this.cartItems.find(cartItem => cartItem.id === item.id);
			if (cartItem) {
				cartItem.quantity += 1;
				this.saveCartToStorage();
			}
		},
		
		// 减少商品数量
		decreaseQuantity(item) {
			const cartItemIndex = this.cartItems.findIndex(cartItem => cartItem.id === item.id);
			if (cartItemIndex !== -1) {
				if (this.cartItems[cartItemIndex].quantity > 1) {
					this.cartItems[cartItemIndex].quantity -= 1;
				} else {
					// 数量为1时，移除商品
					this.cartItems.splice(cartItemIndex, 1);
				}
				this.saveCartToStorage();
			}
		},
		
		// 从点餐车移除商品
		removeFromCart(item) {
			const cartItemIndex = this.cartItems.findIndex(cartItem => cartItem.id === item.id);
			if (cartItemIndex !== -1) {
				this.cartItems.splice(cartItemIndex, 1);
				this.saveCartToStorage();
				uni.showToast({
					title: '已移除',
					icon: 'success'
				});
			}
		},
		
		// 清空点餐车
		clearCart() {
			uni.showModal({
				title: '确认清空',
				content: `确定要清空点餐车中的 ${this.cartItemCount} 个商品吗？`,
				success: (res) => {
					if (res.confirm) {
						this.cartItems = [];
						this.saveCartToStorage();
						uni.showToast({
							title: '已清空点餐车',
							icon: 'success',
							duration: 2000
						});
					}
				}
			});
		},
		
		// 提交订单
		submitOrder() {
			if (!this.hasCartItems) {
				uni.showToast({
					title: '点餐车为空',
					icon: 'none',
					duration: 2000
				});
				return;
			}
			
			// 显示确认对话框
			uni.showModal({
				title: '确认提交',
				content: `将提交 ${this.cartItemCount} 个商品的订单，预计用时 ${this.estimatedTime} 分钟`,
				success: async (res) => {
					if (res.confirm) {
						// 显示加载提示
						uni.showLoading({
							title: '正在提交...',
							mask: true
						});
						
						try {
							// 模拟提交订单的过程
							// 这里可以调用后端API提交订单
							await new Promise(resolve => setTimeout(resolve, 1500));
							
							// 提交成功
							uni.hideLoading();
							uni.showToast({
								title: '订单提交成功！',
								icon: 'success',
								duration: 2000
							});
							
							// 清空购物车
							this.clearCart();
							
							// 关闭弹窗
							this.hideCartModal();
							
						} catch (error) {
							uni.hideLoading();
							uni.showToast({
								title: '提交失败，请重试',
								icon: 'none',
								duration: 2000
							});
							console.error('提交订单失败:', error);
						}
					}
				}
			});
		},
		
		// 保存点餐车到本地存储
		saveCartToStorage() {
			try {
				uni.setStorageSync('cartItems', JSON.stringify(this.cartItems));
			} catch (e) {
				console.error('保存点餐车数据失败:', e);
			}
		},
		
		// 从本地存储加载点餐车
		loadCartFromStorage() {
			try {
				const cartData = uni.getStorageSync('cartItems');
				if (cartData) {
					this.cartItems = JSON.parse(cartData);
				}
			} catch (e) {
				console.error('加载点餐车数据失败:', e);
				this.cartItems = [];
			}
		},
		
		// 获取随机提示信息
		getCurrentTip() {
			if (!this.tips || this.tips.length === 0) return "欢迎使用家庭点餐系统";
			const randomIndex = Math.floor(Math.random() * this.tips.length);
			return this.tips[randomIndex];
		},
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #FFF5F8;
	display: flex;
	flex-direction: column;
}

.header {
	background: linear-gradient(135deg, #FF6B95, #FFB6C1);
	padding: 40rpx 30rpx 30rpx;
	border-radius: 0 0 40rpx 40rpx;
}

.user-info {
	display: flex;
	align-items: center;
	margin-bottom: 30rpx;
}

.avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	margin-right: 20rpx;
	border: 3rpx solid rgba(255, 255, 255, 0.3);
}

.greeting {
	flex: 1;
}

.welcome {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #FFFFFF;
	margin-bottom: 8rpx;
}

.time-text {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.9);
}

.family-info {
	background: rgba(255, 255, 255, 0.15);
	padding: 20rpx;
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.family-name {
	font-size: 28rpx;
	color: #FFFFFF;
	font-weight: 500;
}

.member-count {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.8);
	margin-left: 20rpx;
}

.arrow {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.quick-actions {
	padding: 40rpx 30rpx;
	display: flex;
	justify-content: space-between;
}

.action-item {
	flex: 1;
	text-align: center;
	margin: 0 15rpx;
}

.action-icon {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	margin: 0 auto 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 20rpx rgba(255, 107, 149, 0.2);
}

.ordering-icon {
	background: linear-gradient(135deg, #FF6B95, #FF8C94);
}

.random-icon {
	background: linear-gradient(135deg, #FF6B95, #FF8A80);
}

.recipe-icon {
	background: linear-gradient(135deg, #4CAF50, #66BB6A);
}

.history-icon {
	background: linear-gradient(135deg, #2196F3, #42A5F5);
}

.icon-text {
	font-size: 44rpx;
}

.action-label {
	display: block;
	font-size: 26rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 8rpx;
}

.action-desc {
	font-size: 22rpx;
	color: #999999;
}

/* 轮播推荐区域 */
.recommendation-banner {
	margin: 30rpx;
	border-radius: 20rpx;
	overflow: hidden;
	box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.1);
}

.swiper {
	height: 300rpx;
}

.banner-item {
	position: relative;
	height: 100%;
}

.banner-image {
	width: 100%;
	height: 100%;
}

.banner-overlay {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
	padding: 40rpx 30rpx 30rpx;
	color: white;
}

.banner-title {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	margin-bottom: 8rpx;
}

.banner-desc {
	font-size: 24rpx;
	opacity: 0.9;
}

/* 点餐区域 */
.ordering-section {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.section-header {
	padding: 0 30rpx 20rpx;
}

.section-title-row {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
}

.section-title-left {
	flex: 1;
}

.section-title {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 8rpx;
}

.section-subtitle {
	font-size: 24rpx;
	color: #666666;
}

/* 紧凑版管理员切换按钮 */
.admin-toggle-compact {
	background: rgba(255, 107, 149, 0.1);
	border: 1rpx solid rgba(255, 107, 149, 0.2);
	border-radius: 20rpx;
	padding: 8rpx 16rpx;
	display: flex;
	align-items: center;
	gap: 8rpx;
	min-width: 120rpx;
	justify-content: center;
}

.admin-toggle-icon {
	font-size: 20rpx;
}

.admin-toggle-label {
	font-size: 20rpx;
	color: #FF6B95;
	font-weight: 500;
}

.ordering-container {
	flex: 1;
	display: flex;
	background: #FFFFFF;
	border-radius: 20rpx 20rpx 0 0;
	margin-top: 20rpx;
	overflow: hidden;
	height: 800rpx; /* 固定高度，确保滚动正常 */
}

/* 左侧分类栏 */
.category-sidebar {
	width: 200rpx;
	background: #F8F9FA;
	border-right: 1rpx solid #E9ECEF;
}

.category-tab {
	padding: 30rpx 20rpx;
	text-align: center;
	border-bottom: 1rpx solid #E9ECEF;
	position: relative;
}

.category-tab.active {
	background: #FFFFFF;
	color: #FF6B95;
}

.category-tab.active::before {
	content: '';
	position: absolute;
	left: 0;
	top: 50%;
	transform: translateY(-50%);
	width: 6rpx;
	height: 60rpx;
	background: #FF6B95;
	border-radius: 0 6rpx 6rpx 0;
}

.category-icon {
	display: block;
	font-size: 32rpx;
	margin-bottom: 8rpx;
}

.category-name {
	display: block;
	font-size: 24rpx;
	font-weight: 500;
	margin-bottom: 4rpx;
}

.item-count {
	font-size: 20rpx;
	color: #999999;
}

.category-tab.active .item-count {
	color: #FF6B95;
}

.category-manage {
	position: absolute;
	top: 8rpx;
	right: 8rpx;
	width: 32rpx;
	height: 32rpx;
	border-radius: 50%;
	background: rgba(255, 107, 149, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
}

.manage-icon {
	font-size: 16rpx;
}

.add-category-btn {
	padding: 20rpx;
	text-align: center;
	border-top: 2rpx dashed #E9ECEF;
	margin-top: 20rpx;
}

.add-icon-small {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: rgba(255, 107, 149, 0.1);
	color: #FF6B95;
	display: flex;
	align-items: center;
	justify-content: center;
	margin: 0 auto 8rpx;
	font-size: 24rpx;
	font-weight: bold;
}

.add-text-small {
	font-size: 20rpx;
	color: #FF6B95;
}

/* 右侧商品列表 */
.food-list {
	flex: 1;
	padding: 20rpx;
}

.food-item {
	display: flex;
	background: #FFFFFF;
	border-radius: 16rpx;
	margin-bottom: 20rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
	border: 1rpx solid #F0F0F0;
}

.food-image {
	width: 160rpx;
	height: 160rpx;
	flex-shrink: 0;
}

.food-info {
	flex: 1;
	padding: 20rpx;
	display: flex;
	flex-direction: column;
}

.food-name {
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 8rpx;
}

.food-desc {
	font-size: 22rpx;
	color: #666666;
	margin-bottom: 12rpx;
	line-height: 1.4;
}

.food-tags {
	margin-bottom: 12rpx;
}

.food-tag {
	display: inline-block;
	font-size: 20rpx;
	color: #FF6B95;
	background: rgba(255, 107, 149, 0.1);
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
	margin-right: 8rpx;
}

.food-footer {
	margin-top: auto;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.food-meta {
	display: flex;
	flex-direction: column;
	gap: 4rpx;
}

.cook-time,
.difficulty {
	font-size: 20rpx;
	color: #999999;
}

.food-actions {
	display: flex;
	gap: 12rpx;
}

.order-btn {
	background: linear-gradient(135deg, #FF6B95, #FF8C94);
	color: white;
	padding: 12rpx 24rpx;
	border-radius: 20rpx;
	font-size: 22rpx;
	font-weight: 500;
}

.order-text {
	color: white;
}

/* 管理员功能样式 */
.admin-actions {
	display: flex;
	gap: 8rpx;
}

.admin-btn {
	padding: 8rpx 16rpx;
	border-radius: 16rpx;
	font-size: 20rpx;
	font-weight: 500;
}

.edit-btn {
	background: linear-gradient(135deg, #4CAF50, #66BB6A);
	color: white;
}

.delete-btn {
	background: linear-gradient(135deg, #F44336, #EF5350);
	color: white;
}

.admin-text {
	color: white;
}

.add-food-btn {
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(255, 107, 149, 0.05);
	border: 2rpx dashed #FF6B95;
	border-radius: 16rpx;
	margin: 20rpx 0;
	padding: 40rpx 20rpx;
	color: #FF6B95;
}

/* 点餐车弹窗 - 美化版本 */
.cart-modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.6);
	backdrop-filter: blur(8rpx);
	display: flex;
	align-items: flex-end;
	z-index: 1000;
	animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
	from { opacity: 0; }
	to { opacity: 1; }
}

.cart-modal {
	background: linear-gradient(135deg, #FFFFFF, #FAFBFC);
	border-radius: 30rpx 30rpx 0 0;
	width: 100%;
	max-height: 85vh;
	display: flex;
	flex-direction: column;
	box-shadow: 0 -10rpx 30rpx rgba(0, 0, 0, 0.15);
	animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
	from { transform: translateY(100%); }
	to { transform: translateY(0); }
}

/* 美化的头部区域 */
.cart-header {
	background: linear-gradient(135deg, #FF6B95, #FF8FB3);
	padding: 30rpx;
	border-radius: 30rpx 30rpx 0 0;
	display: flex;
	justify-content: space-between;
	align-items: center;
	position: relative;
}

.cart-header::after {
	content: '';
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	height: 1rpx;
	background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
}

.cart-header-left {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.cart-icon-large {
	font-size: 24rpx;
	padding: 16rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	backdrop-filter: blur(10rpx);
}

.cart-title-group {
	display: flex;
	flex-direction: column;
}

.cart-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #FFFFFF;
	text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.1);
}

.cart-subtitle {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.9);
	margin-top: 4rpx;
}

.cart-header-actions {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.action-btn {
	display: flex;
	align-items: center;
	gap: 8rpx;
	background: rgba(255, 255, 255, 0.2);
	padding: 12rpx 16rpx;
	border-radius: 20rpx;
	backdrop-filter: blur(10rpx);
}

.action-icon {
	font-size: 20rpx;
}

.action-text {
	font-size: 22rpx;
	color: #FFFFFF;
	font-weight: 500;
}

.close-btn {
	width: 48rpx;
	height: 48rpx;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.2);
	backdrop-filter: blur(10rpx);
	display: flex;
	align-items: center;
	justify-content: center;
}

.close-icon {
	font-size: 32rpx;
	color: #FFFFFF;
	font-weight: bold;
}

/* 商品列表区域 */
.cart-content {
  flex: 1;
  padding: 20rpx 30rpx;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch; /* 优化移动端滚动体验 */
}

.cart-empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 80rpx 30rpx;
	text-align: center;
}

.empty-icon {
	font-size: 80rpx;
	margin-bottom: 20rpx;
	opacity: 0.3;
}

.empty-text {
	font-size: 28rpx;
	color: #666666;
	font-weight: 500;
	margin-bottom: 12rpx;
}

.empty-desc {
	font-size: 24rpx;
	color: #999999;
}

.cart-items-list {
	display: flex;
	flex-direction: column;
	gap: 4rpx;
}

.cart-item {
	background: #FFFFFF;
	border-radius: 20rpx;
	padding: 4rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
	border: 1rpx solid rgba(255, 107, 149, 0.1);
	position: relative;
	overflow: hidden;
}

.cart-item::before {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	width: 6rpx;
	height: 100%;
	background: linear-gradient(135deg, #FF6B95, #FF8FB3);
}

/* 商品图片和数量徽章 */
.item-image-wrapper {
	position: relative;
	margin-right: 20rpx;
	flex-shrink: 0;
}

.item-image {
	width: 100rpx;
	height: 100rpx;
	border-radius: 16rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.item-quantity-badge {
	position: absolute;
	top: -8rpx;
	right: -8rpx;
	background: linear-gradient(135deg, #FF6B95, #FF8FB3);
	color: white;
	border-radius: 50%;
	width: 32rpx;
	height: 32rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 20rpx;
	font-weight: bold;
	box-shadow: 0 2rpx 8rpx rgba(255, 107, 149, 0.4);
}

/* 商品详细信息 */
.item-content {
	flex: 1;
	margin-right: 20rpx;
}

.item-main-info {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 8rpx;
}

.item-name {
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
	flex: 1;
	margin-right: 12rpx;
}

.item-tags {
	display: flex;
	gap: 6rpx;
	flex-wrap: wrap;
}

.item-tag {
	font-size: 18rpx;
	color: #FF6B95;
	background: linear-gradient(135deg, rgba(255, 107, 149, 0.1), rgba(255, 143, 179, 0.1));
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
	border: 1rpx solid rgba(255, 107, 149, 0.2);
}

.item-meta-info {
	display: flex;
	gap: 20rpx;
	margin-bottom: 8rpx;
}

.meta-item {
	display: flex;
	align-items: center;
	gap: 4rpx;
}

.meta-icon {
	font-size: 20rpx;
}

.meta-text {
	font-size: 22rpx;
	color: #666666;
}

.item-desc {
	font-size: 22rpx;
	color: #999999;
	line-height: 1.4;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

/* 操作区域 */
.item-actions {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 12rpx;
}

.quantity-controls {
	display: flex;
	align-items: center;
	background: linear-gradient(135deg, #F8F9FA, #FFFFFF);
	border-radius: 25rpx;
	padding: 6rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
	border: 1rpx solid #E9ECEF;
}

.quantity-btn {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #FF6B95, #FF8FB3);
	color: white;
	display: flex;
	align-items: center;
	justify-content: center;
	font-weight: bold;
	box-shadow: 0 2rpx 8rpx rgba(255, 107, 149, 0.3);
	transition: all 0.2s ease;
}

.quantity-btn.decrease {
	background: linear-gradient(135deg, #6C757D, #8E9BA7);
	box-shadow: 0 2rpx 8rpx rgba(108, 117, 125, 0.3);
}

.quantity-btn:active {
	transform: scale(0.95);
}

.btn-icon {
	font-size: 24rpx;
	color: white;
}

.quantity-display {
	font-size: 24rpx;
	font-weight: bold;
	color: #333333;
	min-width: 40rpx;
	text-align: center;
	margin: 0 8rpx;
}

.remove-btn {
	background: linear-gradient(135deg, rgba(255, 68, 68, 0.1), rgba(255, 99, 99, 0.1));
	border: 1rpx solid rgba(255, 68, 68, 0.2);
	padding: 8rpx 12rpx;
	border-radius: 16rpx;
	transition: all 0.2s ease;
}

.remove-btn:active {
	transform: scale(0.95);
}

.remove-icon {
	font-size: 20rpx;
}

/* 美化的底部操作区域 */
.cart-footer {
	background: linear-gradient(135deg, #FAFBFC, #FFFFFF);
	padding: 30rpx;
	border-top: 1rpx solid rgba(255, 107, 149, 0.1);
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.cart-summary {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.summary-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.summary-row.main {
	padding-bottom: 12rpx;
	border-bottom: 1rpx solid rgba(255, 107, 149, 0.1);
}

.summary-label {
	font-size: 26rpx;
	color: #666666;
}

.summary-row.main .summary-label {
	font-weight: 500;
	color: #333333;
}

.summary-value {
	font-size: 26rpx;
	font-weight: bold;
	color: #FF6B95;
}

.summary-row.main .summary-value {
	font-size: 28rpx;
}

.submit-area {
	display: flex;
	justify-content: center;
}

.submit-btn {
	background: linear-gradient(135deg, #FF6B95, #FF8FB3);
	padding: 20rpx 40rpx;
	border-radius: 30rpx;
	display: flex;
	align-items: center;
	gap: 12rpx;
	box-shadow: 0 8rpx 25rpx rgba(255, 107, 149, 0.4);
	transition: all 0.3s ease;
	flex: 1;
	justify-content: center;
	max-width: 300rpx;
}

.submit-btn:active {
	transform: translateY(2rpx);
	box-shadow: 0 4rpx 15rpx rgba(255, 107, 149, 0.3);
}

.submit-icon {
	font-size: 24rpx;
}

.submit-text {
	color: white;
	font-size: 28rpx;
	font-weight: bold;
	text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.1);
}

.submit-arrow {
	font-size: 24rpx;
	color: white;
	font-weight: bold;
}

/* 购物车弹窗相关样式 */
.cart-modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: flex-end;
	z-index: 1000;
	animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
	from {
		opacity: 0;
	}
	to {
		opacity: 1;
	}
}

.cart-modal {
	background: white;
	border-radius: 30rpx 30rpx 0 0;
	width: 100%;
	max-height: 80vh;
	display: flex;
	flex-direction: column;
	animation: slideUp 0.3s ease;
	box-shadow: 0 -10rpx 30rpx rgba(0, 0, 0, 0.1);
}

@keyframes slideUp {
	from {
		transform: translateY(100%);
	}
	to {
		transform: translateY(0);
	}
}

/* 购物车头部 */
.cart-header {
	padding: 30rpx;
	border-bottom: 1rpx solid rgba(255, 107, 149, 0.1);
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: linear-gradient(135deg, #FAFBFC, #FFFFFF);
}

.cart-header-left {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.cart-icon-large {
	font-size: 48rpx;
	padding: 12rpx;
	background: linear-gradient(135deg, rgba(255, 107, 149, 0.1), rgba(255, 143, 179, 0.1));
	border-radius: 20rpx;
	border: 2rpx solid rgba(255, 107, 149, 0.2);
}

.cart-title-group {
	display: flex;
	flex-direction: column;
	gap: 4rpx;
}

.cart-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.cart-subtitle {
	font-size: 24rpx;
	color: #666666;
	opacity: 0.8;
}

.cart-header-actions {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.action-btn {
	display: flex;
	align-items: center;
	gap: 8rpx;
	padding: 12rpx 20rpx;
	border-radius: 20rpx;
	transition: all 0.2s ease;
}

.clear-btn {
	background: linear-gradient(135deg, rgba(255, 68, 68, 0.1), rgba(255, 99, 99, 0.1));
	border: 1rpx solid rgba(255, 68, 68, 0.2);
}

.clear-btn:active {
	transform: scale(0.95);
}

.action-icon {
	font-size: 20rpx;
}

.action-text {
	color: #FF4444;
	font-size: 24rpx;
	font-weight: 500;
}

.close-btn {
	width: 50rpx;
	height: 50rpx;
	border-radius: 50%;
	background: rgba(153, 153, 153, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.2s ease;
}

.close-btn:active {
	transform: scale(0.9);
	background: rgba(153, 153, 153, 0.2);
}

.close-icon {
	font-size: 32rpx;
	color: #999999;
	font-weight: bold;
}

/* 购物车内容区域 */
.cart-content {
	flex: 1;
	padding: 0 30rpx;
	max-height: 50vh;
}

/* 空状态样式 */
.cart-empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 100rpx 40rpx;
	text-align: center;
}

.empty-icon-wrapper {
	position: relative;
	margin-bottom: 30rpx;
}

.empty-icon {
	font-size: 100rpx;
	color: #E9ECEF;
	display: block;
}

.empty-sparkles {
	position: absolute;
	top: -20rpx;
	right: -20rpx;
	font-size: 30rpx;
	color: #FFD700;
	animation: sparkle 2s infinite;
}

@keyframes sparkle {
	0%, 100% {
		opacity: 0.3;
		transform: scale(0.8);
	}
	50% {
		opacity: 1;
		transform: scale(1.2);
	}
}

.empty-text {
	font-size: 32rpx;
	color: #666666;
	font-weight: 500;
	margin-bottom: 12rpx;
}

.empty-desc {
	font-size: 24rpx;
	color: #999999;
	line-height: 1.4;
	margin-bottom: 40rpx;
}

.empty-action {
	display: flex;
	align-items: center;
	gap: 8rpx;
	padding: 16rpx 32rpx;
	background: linear-gradient(135deg, #FF6B95, #FF8FB3);
	border-radius: 25rpx;
	box-shadow: 0 6rpx 20rpx rgba(255, 107, 149, 0.3);
	transition: all 0.2s ease;
}

.empty-action:active {
	transform: scale(0.95);
}

.empty-action-text {
	color: white;
	font-size: 26rpx;
	font-weight: 500;
}

.empty-action-arrow {
	color: white;
	font-size: 24rpx;
	font-weight: bold;
}

/* 购物车商品列表 */
.cart-items-list {
	padding: 20rpx 0;
}

.cart-item {
    display: flex;
    align-items: flex-start;
    gap: 15rpx; /* 减小间距 */
    padding: 20rpx 15rpx; /* 调整内边距 */
    border-bottom: 1rpx solid #F8F9FA;
    position: relative;
    width: 95%;
    box-sizing: border-box; /* 确保padding不会增加宽度 */
}

.cart-item:last-child {
	border-bottom: none;
}

/* 修改图片容器的尺寸 */
.item-image-wrapper {
    position: relative;
    flex-shrink: 0;
    width: 100rpx; /* 减小宽度 */
}

.item-image {
    width: 100%;
    height: 100rpx; /* 保持宽高比 */
    border-radius: 12rpx;
    object-fit: cover;
}

.item-quantity-badge {
	position: absolute;
	top: -8rpx;
	right: -8rpx;
	background: linear-gradient(135deg, #FF6B95, #FF8FB3);
	color: white;
	border-radius: 50%;
	width: 32rpx;
	height: 32rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 20rpx;
	font-weight: bold;
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 149, 0.4);
	border: 2rpx solid white;
}

/* 商品内容区域 */
.item-content {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.item-main-info {
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.item-name {
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
	line-height: 1.3;
}

.item-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 8rpx;
}

.item-tag {
	font-size: 20rpx;
	color: #FF6B95;
	background: rgba(255, 107, 149, 0.1);
	padding: 4rpx 10rpx;
	border-radius: 12rpx;
	border: 1rpx solid rgba(255, 107, 149, 0.2);
}

.item-meta-info {
	display: flex;
	gap: 16rpx;
}

.meta-item {
	display: flex;
	align-items: center;
	gap: 4rpx;
}

.meta-icon {
	font-size: 20rpx;
}

.meta-text {
	font-size: 22rpx;
	color: #666666;
}

.item-desc {
	font-size: 22rpx;
	color: #999999;
	line-height: 1.4;
	overflow: hidden;
	text-overflow: ellipsis;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	line-clamp: 2;
	-webkit-box-orient: vertical;
}

/* 操作区域 */
.item-actions {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 12rpx;
}

.quantity-controls {
	display: flex;
	align-items: center;
	background: linear-gradient(135deg, #F8F9FA, #FFFFFF);
	border-radius: 25rpx;
	padding: 6rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
	border: 1rpx solid #E9ECEF;
}

.quantity-btn {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #FF6B95, #FF8FB3);
	color: white;
	display: flex;
	align-items: center;
	justify-content: center;
	font-weight: bold;
	box-shadow: 0 2rpx 8rpx rgba(255, 107, 149, 0.3);
	transition: all 0.2s ease;
}

.quantity-btn.decrease {
	background: linear-gradient(135deg, #6C757D, #8E9BA7);
	box-shadow: 0 2rpx 8rpx rgba(108, 117, 125, 0.3);
}

.quantity-btn:active {
	transform: scale(0.95);
}

.btn-icon {
	font-size: 24rpx;
	color: white;
}

.quantity-display {
	font-size: 24rpx;
	font-weight: bold;
	color: #333333;
	min-width: 40rpx;
	text-align: center;
	margin: 0 8rpx;
}

.remove-btn {
	background: linear-gradient(135deg, rgba(255, 68, 68, 0.1), rgba(255, 99, 99, 0.1));
	border: 1rpx solid rgba(255, 68, 68, 0.2);
	padding: 8rpx 12rpx;
	border-radius: 16rpx;
	transition: all 0.2s ease;
}

.remove-btn:active {
	transform: scale(0.95);
}

.remove-icon {
	font-size: 20rpx;
}

/* 美化的底部操作区域 */
.cart-footer {
	background: linear-gradient(135deg, #FAFBFC, #FFFFFF);
	padding: 30rpx;
	border-top: 1rpx solid rgba(255, 107, 149, 0.1);
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.cart-summary {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.summary-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.summary-row.main {
	padding-bottom: 12rpx;
	border-bottom: 1rpx solid rgba(255, 107, 149, 0.1);
}

.summary-label {
	font-size: 26rpx;
	color: #666666;
}

.summary-row.main .summary-label {
	font-weight: 500;
	color: #333333;
}

.summary-value {
	font-size: 26rpx;
	font-weight: bold;
	color: #FF6B95;
}

.summary-row.main .summary-value {
	font-size: 28rpx;
}

.submit-area {
	display: flex;
	justify-content: center;
}

.submit-btn {
	background: linear-gradient(135deg, #FF6B95, #FF8FB3);
	padding: 20rpx 40rpx;
	border-radius: 30rpx;
	display: flex;
	align-items: center;
	gap: 12rpx;
	box-shadow: 0 8rpx 25rpx rgba(255, 107, 149, 0.4);
	transition: all 0.3s ease;
	flex: 1;
	justify-content: center;
	max-width: 300rpx;
}

.submit-btn:active {
	transform: translateY(2rpx);
	box-shadow: 0 4rpx 15rpx rgba(255, 107, 149, 0.3);
}

.submit-icon {
	font-size: 24rpx;
}

.submit-text {
	color: white;
	font-size: 28rpx;
	font-weight: bold;
	text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.1);
}

.submit-arrow {
	font-size: 24rpx;
	color: white;
	font-weight: bold;
}

/* 点餐车浮动按钮 */
.cart-float-btn {
	position: fixed;
	right: 30rpx;
	bottom: 100rpx;
	width: 100rpx;
	height: 100rpx;
	background: linear-gradient(135deg, #FF6B95, #FF8C94);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 20rpx rgba(255, 107, 149, 0.3);
	z-index: 100;
	transition: all 0.3s ease;
}

.cart-float-btn:active {
	transform: scale(0.9);
}

.cart-icon {
	font-size: 40rpx;
	color: white;
}

.cart-badge {
	position: absolute;
	top: -8rpx;
	right: -8rpx;
	background: linear-gradient(135deg, #FF4444, #FF6666);
	color: white;
	border-radius: 50%;
	width: 36rpx;
	height: 36rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 20rpx;
	font-weight: bold;
	box-shadow: 0 4rpx 12rpx rgba(255, 68, 68, 0.4);
	border: 2rpx solid white;
	animation: bounce 2s infinite;
}

@keyframes bounce {
	0%, 20%, 50%, 80%, 100% {
		transform: translateY(0);
	}
	40% {
		transform: translateY(-6rpx);
	}
	60% {
		transform: translateY(-3rpx);
	}
}
</style>
