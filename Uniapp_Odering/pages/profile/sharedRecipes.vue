<template>
	<view class="container">
		<!-- 头部统计卡片 -->
		<view class="header-card">
			<view class="card-icon">
				<text class="icon">📖</text>
			</view>
			<view class="card-info">
				<text class="title">我的分享菜谱</text>
				<text class="subtitle">已分享 {{ sharedRecipesCount }} 个菜谱</text>
			</view>
			<view class="add-button" @click="createNewRecipe">
				<text class="add-icon">+</text>
			</view>
		</view>

		<!-- 统计概览 -->
		<view class="stats-overview">
			<view class="stat-item">
				<text class="stat-number">{{ totalLikes }}</text>
				<text class="stat-label">获得点赞</text>
			</view>
			<view class="stat-item">
				<text class="stat-number">{{ totalViews }}</text>
				<text class="stat-label">总浏览量</text>
			</view>
			<view class="stat-item">
				<text class="stat-number">{{ totalCollections }}</text>
				<text class="stat-label">被收藏</text>
			</view>
		</view>

		<!-- 排序筛选 -->
		<view class="filter-section">
			<view class="sort-tabs">
				<view class="tab-item" :class="{ active: sortBy === 'latest' }" @click="setSortBy('latest')">
					<text class="tab-text">最新发布</text>
				</view>
				<view class="tab-item" :class="{ active: sortBy === 'popular' }" @click="setSortBy('popular')">
					<text class="tab-text">最受欢迎</text>
				</view>
				<view class="tab-item" :class="{ active: sortBy === 'views' }" @click="setSortBy('views')">
					<text class="tab-text">浏览最多</text>
				</view>
			</view>
		</view>

		<!-- 菜谱列表 -->
		<view class="recipes-section">
			<view class="recipe-card" v-for="recipe in sortedRecipes" :key="recipe.id" @click="viewRecipeDetail(recipe)">
				<image class="recipe-image" :src="recipe.image" mode="aspectFill"></image>
				<view class="recipe-overlay">
					<view class="recipe-stats">
						<view class="stat-badge">
							<text class="badge-icon">👁️</text>
							<text class="badge-text">{{ recipe.views }}</text>
						</view>
						<view class="stat-badge">
							<text class="badge-icon">❤️</text>
							<text class="badge-text">{{ recipe.likes }}</text>
						</view>
					</view>
				</view>
				<view class="recipe-info">
					<text class="recipe-title">{{ recipe.title }}</text>
					<text class="recipe-desc">{{ recipe.description }}</text>
					<view class="recipe-meta">
						<view class="recipe-tags">
							<text class="tag" v-for="tag in recipe.tags" :key="tag">{{ tag }}</text>
						</view>
						<text class="publish-date">{{ formatDate(recipe.publishDate) }}</text>
					</view>
					<view class="recipe-actions">
						<text class="action-btn" @click.stop="editRecipe(recipe)">编辑</text>
						<text class="action-btn" @click.stop="shareRecipe(recipe)">分享</text>
						<text class="action-btn danger" @click.stop="deleteRecipe(recipe)">删除</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 空状态 -->
		<view class="empty-state" v-if="sharedRecipes.length === 0">
			<text class="empty-icon">📝</text>
			<text class="empty-title">还没有分享过菜谱</text>
			<text class="empty-desc">分享您的拿手好菜，让更多人享受美味～</text>
			<button class="create-btn" @click="createNewRecipe">创建第一个菜谱</button>
		</view>

		<!-- 浮动创建按钮 -->
		<view class="floating-add" @click="createNewRecipe" v-if="sharedRecipes.length > 0">
			<text class="floating-icon">+</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			sharedRecipesCount: 0,
			sortBy: 'latest',
			sharedRecipes: [
				{
					id: 1,
					title: '家传红烧肉',
					description: '肥而不腻，香甜可口的经典做法，传承三代的家庭秘方',
					image: '/static/dishes/hongshaorou.jpg',
					likes: 15,
					views: 128,
					collections: 8,
					tags: ['家常菜', '下饭菜', '传统'],
					publishDate: new Date('2024-01-20'),
					difficulty: '中等',
					cookingTime: '1小时30分钟'
				},
				{
					id: 2,
					title: '秘制蒸蛋羹',
					description: '嫩滑如丝，入口即化，老少皆宜的营养美食',
					image: '/static/dishes/zhengdangeng.jpg',
					likes: 12,
					views: 96,
					collections: 6,
					tags: ['营养', '简单', '嫩滑'],
					publishDate: new Date('2024-01-15'),
					difficulty: '简单',
					cookingTime: '30分钟'
				},
				{
					id: 3,
					title: '清香时蔬',
					description: '保持蔬菜原味，清淡爽口，营养丰富的健康料理',
					image: '/static/dishes/qingchaoshishu.jpg',
					likes: 8,
					views: 72,
					collections: 4,
					tags: ['素食', '健康', '清淡'],
					publishDate: new Date('2024-01-10'),
					difficulty: '简单',
					cookingTime: '15分钟'
				}
			]
		}
	},
	
	computed: {
		sortedRecipes() {
			let recipes = [...this.sharedRecipes];
			
			switch (this.sortBy) {
				case 'popular':
					recipes.sort((a, b) => b.likes - a.likes);
					break;
				case 'views':
					recipes.sort((a, b) => b.views - a.views);
					break;
				default: // latest
					recipes.sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate));
			}
			
			return recipes;
		},
		
		totalLikes() {
			return this.sharedRecipes.reduce((total, recipe) => total + recipe.likes, 0);
		},
		
		totalViews() {
			return this.sharedRecipes.reduce((total, recipe) => total + recipe.views, 0);
		},
		
		totalCollections() {
			return this.sharedRecipes.reduce((total, recipe) => total + recipe.collections, 0);
		}
	},
	
	onLoad(options) {
		if (options.count) {
			this.sharedRecipesCount = parseInt(options.count);
		} else {
			this.sharedRecipesCount = this.sharedRecipes.length;
		}
	},
	
	methods: {
		setSortBy(sortType) {
			this.sortBy = sortType;
		},
		
		viewRecipeDetail(recipe) {
			uni.showModal({
				title: recipe.title,
				content: `${recipe.description}\n\n难度：${recipe.difficulty}\n用时：${recipe.cookingTime}\n\n❤️ ${recipe.likes}  👁️ ${recipe.views}  📑 ${recipe.collections}`,
				showCancel: true,
				cancelText: '关闭',
				confirmText: '查看详情',
				success: (res) => {
					if (res.confirm) {
						// 这里可以跳转到菜谱详情页
						uni.showToast({
							title: '菜谱详情页开发中',
							icon: 'none'
						});
					}
				}
			});
		},
		
		createNewRecipe() {
			uni.showModal({
				title: '创建菜谱',
				content: '菜谱创建功能正在开发中，敬请期待！\n\n即将支持：\n• 图文并茂的制作步骤\n• 食材清单和用量\n• 烹饪技巧和小贴士\n• 营养成分分析',
				showCancel: false,
				confirmText: '知道了'
			});
		},
		
		editRecipe(recipe) {
			uni.showModal({
				title: `编辑"${recipe.title}"`,
				content: '菜谱编辑功能开发中...',
				showCancel: false
			});
		},
		
		shareRecipe(recipe) {
			uni.showActionSheet({
				itemList: ['分享到微信', '复制链接', '生成海报'],
				success: (res) => {
					const actions = ['分享到微信', '链接已复制', '海报生成中'];
					uni.showToast({
						title: actions[res.tapIndex],
						icon: 'success'
					});
				}
			});
		},
		
		deleteRecipe(recipe) {
			uni.showModal({
				title: '删除菜谱',
				content: `确定要删除"${recipe.title}"吗？删除后无法恢复。`,
				success: (res) => {
					if (res.confirm) {
						const index = this.sharedRecipes.findIndex(r => r.id === recipe.id);
						if (index > -1) {
							this.sharedRecipes.splice(index, 1);
							this.sharedRecipesCount--;
							uni.showToast({
								title: '已删除菜谱',
								icon: 'success'
							});
						}
					}
				}
			});
		},
		
		formatDate(date) {
			return new Date(date).toLocaleDateString('zh-CN', {
				month: 'long',
				day: 'numeric'
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

.header-card {
	background: linear-gradient(135deg, #FF6B95, #FFB6C1);
	padding: 40rpx 30rpx;
	display: flex;
	align-items: center;
}

.card-icon {
	width: 80rpx;
	height: 80rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
}

.card-icon .icon {
	font-size: 36rpx;
}

.card-info {
	flex: 1;
}

.title {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: white;
	margin-bottom: 8rpx;
}

.subtitle {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.add-button {
	width: 60rpx;
	height: 60rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.add-icon {
	font-size: 32rpx;
	color: white;
	font-weight: bold;
}

.stats-overview {
	display: flex;
	padding: 30rpx;
	gap: 20rpx;
}

.stat-item {
	flex: 1;
	background: white;
	padding: 30rpx 20rpx;
	border-radius: 20rpx;
	text-align: center;
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 149, 0.1);
}

.stat-number {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	color: #FF6B95;
	margin-bottom: 8rpx;
}

.stat-label {
	font-size: 22rpx;
	color: #666;
}

.filter-section {
	padding: 0 30rpx 30rpx;
}

.sort-tabs {
	display: flex;
	background: white;
	border-radius: 50rpx;
	padding: 8rpx;
}

.tab-item {
	flex: 1;
	text-align: center;
	padding: 16rpx;
	border-radius: 44rpx;
	transition: all 0.3s ease;
}

.tab-item.active {
	background: #FF6B95;
}

.tab-text {
	font-size: 24rpx;
	color: #666;
}

.tab-item.active .tab-text {
	color: white;
	font-weight: 500;
}

.recipes-section {
	padding: 0 30rpx;
}

.recipe-card {
	background: white;
	border-radius: 20rpx;
	margin-bottom: 30rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 149, 0.1);
	position: relative;
}

.recipe-image {
	width: 100%;
	height: 400rpx;
}

.recipe-overlay {
	position: absolute;
	top: 20rpx;
	right: 20rpx;
	display: flex;
	gap: 12rpx;
}

.stat-badge {
	background: rgba(0, 0, 0, 0.6);
	padding: 8rpx 12rpx;
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	gap: 6rpx;
}

.badge-icon {
	font-size: 20rpx;
}

.badge-text {
	font-size: 20rpx;
	color: white;
}

.recipe-info {
	padding: 30rpx;
}

.recipe-title {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 12rpx;
}

.recipe-desc {
	font-size: 24rpx;
	color: #666;
	line-height: 1.5;
	margin-bottom: 20rpx;
}

.recipe-meta {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 20rpx;
}

.recipe-tags {
	display: flex;
	gap: 12rpx;
}

.tag {
	background: #FFF0F5;
	color: #FF6B95;
	padding: 6rpx 12rpx;
	border-radius: 12rpx;
	font-size: 20rpx;
}

.publish-date {
	font-size: 20rpx;
	color: #999;
}

.recipe-actions {
	display: flex;
	gap: 20rpx;
	padding-top: 20rpx;
	border-top: 1rpx solid #F5F5F5;
}

.action-btn {
	padding: 12rpx 20rpx;
	border-radius: 20rpx;
	font-size: 22rpx;
	border: 1rpx solid #FF6B95;
	color: #FF6B95;
}

.action-btn.danger {
	border-color: #FF4757;
	color: #FF4757;
}

.empty-state {
	text-align: center;
	padding: 120rpx 60rpx;
}

.empty-icon {
	font-size: 120rpx;
	margin-bottom: 30rpx;
}

.empty-title {
	display: block;
	font-size: 32rpx;
	color: #333;
	margin-bottom: 16rpx;
}

.empty-desc {
	font-size: 24rpx;
	color: #999;
	margin-bottom: 40rpx;
	line-height: 1.5;
}

.create-btn {
	background: #FF6B95;
	color: white;
	border: none;
	border-radius: 50rpx;
	padding: 20rpx 60rpx;
	font-size: 26rpx;
}

.floating-add {
	position: fixed;
	bottom: 40rpx;
	right: 40rpx;
	width: 100rpx;
	height: 100rpx;
	background: #FF6B95;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 24rpx rgba(255, 107, 149, 0.3);
	z-index: 100;
}

.floating-icon {
	font-size: 48rpx;
	color: white;
	font-weight: bold;
}
</style>
