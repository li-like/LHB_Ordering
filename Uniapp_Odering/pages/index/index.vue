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
				<text class="action-label">家庭点餐</text>
				<text class="action-desc">点餐下单</text>
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
	</view>
</template>

<script>
import userManager from '../../utils/userManager.js'

export default {
	data() {
		return {
			userInfo: {},
			familyData: {},
			greeting: '',
			activeCategory: 1, // 当前选中的分类ID
			nextFoodId: 1000, // 下一个商品ID
			nextCategoryId: 10, // 下一个分类ID
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
			// 食物分类及对应商品
			foodCategories: [
				{
					id: 1,
					name: '荤菜',
					emoji: '🥩',
					items: [
						{
							id: 101,
							name: '红烧肉',
							description: '肥瘦相间，软糯香甜，色泽红亮',
							image: '/static/dishes/hongshaorou.jpg',
							tags: ['经典', '下饭', '节日'],
							cookTime: 45,
							difficulty: 2
						},
						{
							id: 102,
							name: '糖醋排骨',
							description: '酸甜开胃，色泽诱人，老少皆宜',
							image: '/static/dishes/tangcupaigu.jpg',
							tags: ['酸甜', '开胃', '家常'],
							cookTime: 35,
							difficulty: 2
						},
						{
							id: 103,
							name: '可乐鸡翅',
							description: '嫩滑多汁，香甜可口，孩子最爱',
							image: '/static/dishes/kelejichi.jpg',
							tags: ['香甜', '嫩滑', '简单'],
							cookTime: 25,
							difficulty: 1
						},
						{
							id: 104,
							name: '蒜蓉蒸排骨',
							description: '蒜香浓郁，嫩滑爽口，营养丰富',
							image: '/static/dishes/suanrongpaigu.jpg',
							tags: ['蒜香', '清蒸', '营养'],
							cookTime: 30,
							difficulty: 1
						}
					]
				},
				{
					id: 2,
					name: '素菜',
					emoji: '🥬',
					items: [
						{
							id: 201,
							name: '清炒菠菜',
							description: '鲜嫩爽脆，清香淡雅，营养丰富',
							image: '/static/dishes/qingchaobocai.jpg',
							tags: ['清淡', '快手', '营养'],
							cookTime: 5,
							difficulty: 1
						},
						{
							id: 202,
							name: '麻婆豆腐',
							description: '麻辣鲜香，嫩滑爽口，经典川菜',
							image: '/static/dishes/mapodoufu.jpg',
							tags: ['麻辣', '经典', '下饭'],
							cookTime: 15,
							difficulty: 2
						},
						{
							id: 203,
							name: '蒜蓉西兰花',
							description: '翠绿爽脆，蒜香浓郁，健康美味',
							image: '/static/dishes/suanrongxilanhua.jpg',
							tags: ['健康', '爽脆', '蒜香'],
							cookTime: 8,
							difficulty: 1
						}
					]
				},
				{
					id: 3,
					name: '汤品',
					emoji: '🍲',
					items: [
						{
							id: 301,
							name: '番茄鸡蛋汤',
							description: '酸甜开胃，营养丰富，家常必备',
							image: '/static/dishes/fanqiejidantang.jpg',
							tags: ['酸甜', '营养', '家常'],
							cookTime: 10,
							difficulty: 1
						},
						{
							id: 302,
							name: '冬瓜排骨汤',
							description: '清淡鲜美，消暑解腻，营养滋补',
							image: '/static/dishes/dongguapaigu.jpg',
							tags: ['清淡', '滋补', '消暑'],
							cookTime: 60,
							difficulty: 1
						},
						{
							id: 303,
							name: '紫菜蛋花汤',
							description: '鲜香清淡，制作简单，营养美味',
							image: '/static/dishes/zicaidanhua.jpg',
							tags: ['清淡', '简单', '快手'],
							cookTime: 5,
							difficulty: 1
						}
					]
				},
				{
					id: 4,
					name: '主食',
					emoji: '🍚',
					items: [
						{
							id: 401,
							name: '蛋炒饭',
							description: '粒粒分明，香滑可口，经典主食',
							image: '/static/dishes/danchaofan.jpg',
							tags: ['经典', '香滑', '主食'],
							cookTime: 10,
							difficulty: 1
						},
						{
							id: 402,
							name: '煲仔饭',
							description: '米饭香糯，配菜丰富，一锅出菜',
							image: '/static/dishes/baozaifan.jpg',
							tags: ['香糯', '丰富', '一锅出'],
							cookTime: 40,
							difficulty: 2
						}
					]
				},
				{
					id: 5,
					name: '小食',
					emoji: '🥟',
					items: [
						{
							id: 501,
							name: '煎饺',
							description: '外酥内嫩，鲜美多汁，早餐首选',
							image: '/static/dishes/jianjiao.jpg',
							tags: ['酥脆', '多汁', '早餐'],
							cookTime: 15,
							difficulty: 2
						},
						{
							id: 502,
							name: '小笼包',
							description: '皮薄馅嫩，汤汁丰富，精致美味',
							image: '/static/dishes/xiaolongbao.jpg',
							tags: ['精致', '汤汁', '美味'],
							cookTime: 30,
							difficulty: 3
						}
					]
				},
				{
					id: 6,
					name: '甜品',
					emoji: '🍰',
					items: [
						{
							id: 601,
							name: '红豆汤',
							description: '香甜润燥，温暖贴心，营养丰富',
							image: '/static/dishes/hongdoutang.jpg',
							tags: ['香甜', '温暖', '营养'],
							cookTime: 45,
							difficulty: 1
						},
						{
							id: 602,
							name: '银耳莲子汤',
							description: '滋润养颜，清甜爽口，美容佳品',
							image: '/static/dishes/yinerlianzi.jpg',
							tags: ['滋润', '养颜', '清甜'],
							cookTime: 50,
							difficulty: 1
						}
					]
				}
			]
		}
	},
	
	computed: {
		// 当前选中分类的商品列表
		currentCategoryItems() {
			const category = this.foodCategories.find(cat => cat.id === this.activeCategory);
			return category ? category.items : [];
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
		}
	},
	
	onLoad() {
		this.checkLogin();
		this.loadUserData();
		this.setGreeting();
		// 注册用户信息更新监听
		this.userInfoUpdateHandler = (updatedUserInfo) => {
			console.log('index页面收到用户信息更新通知:', updatedUserInfo);
			this.userInfo = updatedUserInfo;
		};
		userManager.onUserInfoUpdated(this.userInfoUpdateHandler);
	},
	
	onShow() {
		this.checkLogin(); // 每次显示时都检查登录状态
		this.loadUserData();
		this.updateActiveTime(); // 更新用户活跃时间
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
			uni.showModal({
				title: item.name,
				content: `${item.description}\n\n准备时间：${item.cookTime}分钟\n难度：${this.getDifficultyText(item.difficulty)}\n标签：${item.tags.join('、')}`,
				confirmText: '点餐',
				cancelText: '取消',
				success: (res) => {
					if (res.confirm) {
						this.addToOrder(item);
					}
				}
			});
		},
		
		// 添加到点餐车
		addToOrder(item) {
			uni.showToast({
				title: `已添加${item.name}到点餐车`,
				icon: 'success',
				duration: 1500
			});
			// 这里后续可以添加到点餐车的逻辑
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
		
		// 跳转到点餐页面
		goToOrdering() {
			uni.navigateTo({
				url: '/pages/ordering/index'
			});
		},
		
		// === 管理员功能 ===
		
		// 编辑菜品
		editFoodItem(item) {
			uni.showModal({
				title: '编辑菜品',
				content: '跳转到菜品编辑页面',
				confirmText: '编辑',
				cancelText: '取消',
				success: (res) => {
					if (res.confirm) {
						// 跳转到编辑页面，传递菜品信息
						uni.navigateTo({
							url: `/pages/food/edit?id=${item.id}&categoryId=${this.activeCategory}&mode=edit`
						});
					}
				}
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
		performDeleteFood(item) {
			const categoryIndex = this.foodCategories.findIndex(cat => cat.id === this.activeCategory);
			if (categoryIndex !== -1) {
				const itemIndex = this.foodCategories[categoryIndex].items.findIndex(food => food.id === item.id);
				if (itemIndex !== -1) {
					this.foodCategories[categoryIndex].items.splice(itemIndex, 1);
					uni.showToast({
						title: '删除成功',
						icon: 'success'
					});
				}
			}
		},
		
		// 添加新菜品
		addNewFoodItem() {
			uni.showModal({
				title: '添加菜品',
				content: '跳转到菜品添加页面',
				confirmText: '添加',
				cancelText: '取消',
				success: (res) => {
					if (res.confirm) {
						// 跳转到添加页面
						uni.navigateTo({
							url: `/pages/food/edit?categoryId=${this.activeCategory}&mode=add`
						});
					}
				}
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
		
		// 编辑分类
		editCategory(category) {
			uni.showModal({
				title: '编辑分类',
				editable: true,
				placeholderText: category.name,
				success: (res) => {
					if (res.confirm && res.content && res.content.trim()) {
						const categoryIndex = this.foodCategories.findIndex(cat => cat.id === category.id);
						if (categoryIndex !== -1) {
							this.foodCategories[categoryIndex].name = res.content.trim();
							uni.showToast({
								title: '修改成功',
								icon: 'success'
							});
						}
					}
				}
			});
		},
		
		// 删除分类
		deleteCategory(category) {
			if (category.items.length > 0) {
				uni.showModal({
					title: '无法删除',
					content: '该分类下还有菜品，请先删除所有菜品后再删除分类',
					showCancel: false
				});
				return;
			}
			
			uni.showModal({
				title: '确认删除',
				content: `确定要删除"${category.name}"分类吗？`,
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
		performDeleteCategory(category) {
			const categoryIndex = this.foodCategories.findIndex(cat => cat.id === category.id);
			if (categoryIndex !== -1) {
				this.foodCategories.splice(categoryIndex, 1);
				
				// 如果删除的是当前选中的分类，切换到第一个分类
				if (this.activeCategory === category.id) {
					this.activeCategory = this.foodCategories.length > 0 ? this.foodCategories[0].id : null;
				}
				
				uni.showToast({
					title: '删除成功',
					icon: 'success'
				});
			}
		},
		
		// 添加新分类
		addNewCategory() {
			uni.showModal({
				title: '添加分类',
				editable: true,
				placeholderText: '请输入分类名称',
				success: (res) => {
					if (res.confirm && res.content && res.content.trim()) {
						const newCategory = {
							id: this.nextCategoryId++,
							name: res.content.trim(),
							emoji: '🍽️', // 默认emoji，可以后续支持选择
							items: []
						};
						
						this.foodCategories.push(newCategory);
						uni.showToast({
							title: '添加成功',
							icon: 'success'
						});
					}
				}
			});
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
			uni.showToast({
				title: this.familyData.role === 'admin' ? '已开启管理员模式' : '已关闭管理员模式',
				icon: 'success'
			});
		}
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

.add-icon {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
	background: rgba(255, 107, 149, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 36rpx;
	font-weight: bold;
	margin-right: 20rpx;
}

.add-text {
	font-size: 28rpx;
	font-weight: 500;
}
</style>
