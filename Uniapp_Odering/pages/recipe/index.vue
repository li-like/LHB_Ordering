<template>
	<view class="container">
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">{{ showUserRecipes ? '我的菜谱' : '菜谱大全' }}</text>
			<view class="header-actions">
				<button v-if="showUserRecipes" class="create-btn" @click="goToCreate">
					<text class="create-icon">➕</text>
					<text class="create-text">创建菜谱</text>
				</button>
			</view>
		</view>
		
		<!-- 顶部搜索栏 -->
		<view class="search-bar">
			<view class="search-input-wrapper">
				<input 
					class="search-input" 
					v-model="searchKeyword" 
					placeholder="搜索菜谱..."
					@input="onSearchInput"
					confirm-type="search"
					@confirm="onSearchInput"
					adjust-position="true"
					cursor-spacing="10"
				/>
				<text class="search-icon">🔍</text>
			</view>
		</view>
		
		<!-- 分类标签栏 -->
		<scroll-view class="category-tabs" scroll-x="true" show-scrollbar="false">
			<view class="category-tab" 
				v-for="(category, index) in categories" 
				:key="index"
				:class="{ active: currentCategory === category.value }"
				@click="selectCategory(category.value)"
			>
				<text class="category-text">{{ category.label }}</text>
			</view>
		</scroll-view>
		
		<!-- 菜谱列表 -->
		<scroll-view 
			class="recipe-list" 
			scroll-y="true" 
			@scrolltolower="loadMore"
			refresher-enabled="true"
			:refresher-triggered="refreshing"
			@refresherrefresh="onRefresh"
		>				<!-- 空数据提示 -->
			<view v-if="!loading && recipes.length === 0" class="empty-state">
				<text class="empty-text" v-if="showUserRecipes">您还没有创建菜谱哦~</text>
				<text class="empty-text" v-else>暂无菜谱数据</text>
				<button v-if="showUserRecipes" class="empty-action-btn" @click="goToCreate">
					立即创建菜谱
				</button>
			</view>
			
			<!-- 菜谱列表项 -->
			<view class="recipe-count" v-if="!loading && recipes.length > 0">
				找到 {{ recipes.length }} 个菜谱
			</view>
			
			<view class="recipe-item" 
				v-for="recipe in recipes" 
				:key="recipe.id"
				@click="goToDetail(recipe.id)"
			>
				<image class="recipe-cover" :src="recipe.cover_image || '/static/food-decoration.png'" mode="aspectFill"></image>
				<view class="recipe-info">
					<view class="recipe-header">
						<text class="recipe-name">{{ recipe.name }}</text>
						<!-- 显示作者信息（在菜谱大全模式下） -->
						<view v-if="!showUserRecipes && recipe.author" class="recipe-author">
							<text class="author-text">by {{ recipe.author.nickname || '未知作者' }}</text>
							<view v-if="recipe.is_public" class="public-badge">公开</view>
						</view>
						<!-- 显示可编辑标识（在我的菜谱模式下或者用户可编辑时） -->
						<view v-if="showUserRecipes || recipe.can_edit" class="edit-badge">
							<text class="edit-icon">✏️</text>
						</view>
					</view>
					<text class="recipe-desc">{{ recipe.description || '暂无描述' }}</text>
					<view class="recipe-meta">
						<view class="meta-item">
							<text class="meta-icon">⏱️</text>
							<text class="meta-text">{{ recipe.cook_time }}分钟</text>
						</view>
						<view class="meta-item">
							<text class="meta-icon">👥</text>
							<text class="meta-text">{{ recipe.servings }}人份</text>
						</view>
						<view class="meta-item">
							<text class="meta-icon">⭐</text>
							<text class="meta-text">{{ recipe.difficulty }}/5</text>
						</view>
					</view>
					<view class="recipe-tags">
						<text class="tag" v-for="tag in recipe.tags" :key="tag">{{ tag }}</text>
					</view>
				</view>
				<view class="recipe-stats">
					<view class="stat-item">
						<text class="stat-number">{{ recipe.likes }}</text>
						<text class="stat-label">点赞</text>
					</view>
					<view class="stat-item">
						<text class="stat-number">{{ recipe.success_rate }}%</text>
						<text class="stat-label">成功率</text>
					</view>
				</view>
			</view>
			
			<!-- 加载更多提示 -->
			<view class="load-more" v-if="hasMore">
				<text class="load-text">{{ loading ? '加载中...' : '上拉加载更多' }}</text>
			</view>
			
			<!-- 空状态 -->
			<view class="empty-state" v-if="!loading && recipes.length === 0">
				<text class="empty-icon">📝</text>
				<text class="empty-text">还没有菜谱，快来创建第一个吧！</text>
				<button class="create-btn" @click="goToCreate">创建菜谱</button>
			</view>
		</scroll-view>
		
		<!-- 底部添加按钮 -->
		<view class="fab" @click="goToCreate">
			<text class="fab-icon">+</text>
		</view>
	</view>
</template>

<script>
import recipeManager from '../../utils/recipeManager.js'

export default {
	data() {
		return {
			searchKeyword: '',
			currentCategory: 'all',
			recipes: [],
			loading: false,
			refreshing: false,
			hasMore: true,
			page: 1,
			pageMode: 'all', // 页面模式：'all' 显示所有菜谱, 'user' 显示用户菜谱
			showUserRecipes: false, // 是否只显示用户自己的菜谱
			categories: [
				{ label: '全部', value: 'all' },
				{ label: '荤菜', value: 'meat' },
				{ label: '素菜', value: 'vegetable' },
				{ label: '汤品', value: 'soup' },
				{ label: '主食', value: 'staple' },
				{ label: '小食', value: 'snack' },
				{ label: '甜品', value: 'dessert' }
			]
		}
	},
	
	onLoad(options) {
		// 检查页面模式
		this.pageMode = options.mode || 'all'; // 'all' | 'user'
		this.showUserRecipes = this.pageMode === 'user';
		this.loadRecipes();
	},
	
	methods: {
		// 加载菜谱列表
		async loadRecipes(isRefresh = false) {
			if (this.loading) return;
			
			this.loading = true;
			
			try {
				if (isRefresh) {
					this.page = 1;
					this.recipes = [];
				}
				
				const params = {
					page: this.page,
					mode: this.pageMode, // 'all' 或 'user'
					category: this.currentCategory === 'all' ? '' : this.currentCategory,
					keyword: this.searchKeyword
				};
				
				const result = await recipeManager.getRecipes(params);
				
				if (isRefresh) {
					this.recipes = result.data || [];
				} else {
					this.recipes = [...this.recipes, ...(result.data || [])];
				}
				
				// 修改分页判断逻辑：
				// 1. 对于返回数据少于阈值（默认20条）的情况，检查是否已获取全部数据
				// 2. 当result.total_available存在时，比较当前加载的总数与可用总数
				if (result.total_available !== undefined) {
					// 如果后端返回了总数据量信息，直接比较
					this.hasMore = this.recipes.length < result.total_available;
				} else {
					// 否则根据本次返回的数据判断
					this.hasMore = result.data && result.data.length > 0;
				}
				
				this.page++;
				
			} catch (error) {
				console.error('加载菜谱失败:', error);
				uni.showToast({
					title: '加载失败',
					icon: 'error'
				});
			} finally {
				this.loading = false;
			}
		},
		
		// 搜索输入
		onSearchInput() {
			// 防抖处理
			clearTimeout(this.searchTimer);
			this.searchTimer = setTimeout(() => {
				this.loadRecipes(true);
			}, 500);
		},
		
		// 下拉刷新
		async onRefresh() {
			this.refreshing = true;
			try {
				await this.loadRecipes(true);
			} finally {
				this.refreshing = false;
			}
		},
		
		// 选择分类
		selectCategory(category) {
			if (this.currentCategory === category) return;
			
			this.currentCategory = category;
			this.loadRecipes(true);
		},
		
		// 加载更多
		loadMore() {
			if (this.hasMore && !this.loading) {
				this.loadRecipes();
			}
		},
		
		// 跳转到详情页
		goToDetail(recipeId) {
			uni.navigateTo({
				url: `/pages/recipe/detail?id=${recipeId}`
			});
		},
		
		// 跳转到创建页
		goToCreate() {
			uni.navigateTo({
				url: '/pages/recipe/create'
			});
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #FFF5F8;
	padding-bottom: 120rpx;
}

.page-header {
	background: #FFFFFF;
	padding: 30rpx;
	border-bottom: 1rpx solid #F0F0F0;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.page-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333333;
}

.header-actions {
	display: flex;
	align-items: center;
}

.create-btn {
	background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
	color: white;
	border: none;
	border-radius: 25rpx;
	padding: 16rpx 24rpx;
	font-size: 24rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 107, 0.3);
}

.create-icon {
	margin-right: 8rpx;
	font-size: 20rpx;
}

.create-text {
	font-size: 24rpx;
}

.search-bar {
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	border-bottom: 1rpx solid #F0F0F0;
}

.search-input-wrapper {
	position: relative;
	background: #F8F8F8;
	border-radius: 25rpx;
	padding: 20rpx 50rpx 20rpx 30rpx;
	border: 1rpx solid #E0E0E0;
}

.search-input {
	width: 100%;
	font-size: 28rpx;
	color: #333333;
	background-color: transparent;
	border: none;
	outline: none;
	box-sizing: border-box;
	padding: 0;
	margin: 0;
	height: auto;
	line-height: normal;
}

.search-icon {
	position: absolute;
	right: 20rpx;
	top: 50%;
	transform: translateY(-50%);
	font-size: 24rpx;
	color: #999999;
}

.category-tabs {
	background: #FFFFFF;
	white-space: nowrap;
	padding: 20rpx 30rpx;
	border-bottom: 1rpx solid #F0F0F0;
}

.category-tab {
	display: inline-block;
	padding: 16rpx 32rpx;
	margin-right: 20rpx;
	background: #F8F8F8;
	border-radius: 20rpx;
	font-size: 26rpx;
	color: #666666;
	transition: all 0.3s;
}

.category-tab.active {
	background: #FF6B95;
	color: #FFFFFF;
}

.recipe-list {
	flex: 1;
	height: calc(100vh - 200rpx);
	padding: 20rpx 30rpx;
}

.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 100rpx 30rpx;
	text-align: center;
}

.empty-icon {
	width: 200rpx;
	height: 200rpx;
	opacity: 0.3;
	margin-bottom: 30rpx;
}

.empty-text {
	font-size: 28rpx;
	color: #999999;
	margin-bottom: 40rpx;
}

.empty-action-btn {
	background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
	color: white;
	border: none;
	border-radius: 25rpx;
	padding: 20rpx 40rpx;
	font-size: 28rpx;
}

.recipe-item {
	background: #FFFFFF;
	border-radius: 20rpx;
	margin-bottom: 20rpx;
	padding: 20rpx;
	display: flex;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.recipe-cover {
	width: 120rpx;
	height: 120rpx;
	border-radius: 15rpx;
	margin-right: 20rpx;
}

.recipe-info {
	flex: 1;
}

/* 新增样式：支持菜谱头部布局 */
.recipe-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 8rpx;
}

.recipe-name {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 8rpx;
	flex: 1;
	margin-right: 16rpx;
}

/* 新增样式：作者信息 */
.recipe-author {
	display: flex;
	align-items: center;
	gap: 8rpx;
	flex-shrink: 0;
}

.author-text {
	font-size: 22rpx;
	color: #666666;
	background: #F5F5F5;
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
}

.public-badge {
	background: linear-gradient(45deg, #4CAF50, #66BB6A);
	color: white;
	font-size: 20rpx;
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
	font-weight: 500;
}

.edit-badge {
	background: #FF6B95;
	color: white;
	font-size: 20rpx;
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
	display: flex;
	align-items: center;
}

.edit-icon {
	font-size: 18rpx;
}

.recipe-desc {
	display: block;
	font-size: 24rpx;
	color: #666666;
	margin-bottom: 12rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.recipe-meta {
	display: flex;
	margin-bottom: 12rpx;
}

.meta-item {
	display: flex;
	align-items: center;
	margin-right: 20rpx;
}

.meta-icon {
	font-size: 20rpx;
	margin-right: 6rpx;
}

.meta-text {
	font-size: 22rpx;
	color: #999999;
}

.recipe-tags {
	display: flex;
	flex-wrap: wrap;
}

.tag {
	display: inline-block;
	font-size: 20rpx;
	color: #FF6B95;
	background: rgba(255, 107, 149, 0.1);
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
	margin-right: 8rpx;
	margin-bottom: 4rpx;
}

.recipe-stats {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	width: 100rpx;
}

.stat-item {
	text-align: center;
	margin-bottom: 8rpx;
}

.stat-number {
	display: block;
	font-size: 24rpx;
	font-weight: bold;
	color: #FF6B95;
}

.stat-label {
	font-size: 20rpx;
	color: #999999;
}

.load-more {
	padding: 40rpx;
	text-align: center;
}

.load-text {
	font-size: 26rpx;
	color: #999999;
}

.empty-state {
	text-align: center;
	padding: 100rpx 40rpx;
}

.empty-icon {
	display: block;
	font-size: 80rpx;
	margin-bottom: 20rpx;
}

.empty-text {
	display: block;
	font-size: 28rpx;
	color: #999999;
	margin-bottom: 40rpx;
}

.create-btn {
	background: #FF6B95;
	color: #FFFFFF;
	border: none;
	border-radius: 25rpx;
	padding: 20rpx 40rpx;
	font-size: 28rpx;
}

.fab {
	position: fixed;
	bottom: 30rpx;
	right: 30rpx;
	width: 100rpx;
	height: 100rpx;
	background: #FF6B95;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 20rpx rgba(255, 107, 149, 0.3);
	z-index: 999;
}

.fab-icon {
	font-size: 48rpx;
	color: #FFFFFF;
	font-weight: bold;
}
</style>
