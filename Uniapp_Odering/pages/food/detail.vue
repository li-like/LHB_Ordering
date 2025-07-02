<template>
	<view class="container">
		<!-- 菜品图片区域 -->
		<view class="image-section">
			<image 
				class="food-image" 
				:src="foodDetail.image" 
				mode="aspectFill"
				@click="previewImage"
			></image>
			<view class="image-overlay">
				<view class="food-title">{{ foodDetail.name }}</view>
				<view class="food-subtitle">{{ foodDetail.description }}</view>
			</view>
		</view>
		
		<!-- 菜品信息区域 -->
		<view class="info-section">
			<!-- 基本信息 -->
			<view class="info-card">
				<view class="card-header">
					<text class="card-title">基本信息</text>
				</view>
				<view class="info-grid">
					<view class="info-item">
						<view class="info-icon">🕒</view>
						<view class="info-content">
							<text class="info-label">制作时间</text>
							<text class="info-value">{{ foodDetail.cookTime }}分钟</text>
						</view>
					</view>
					<view class="info-item">
						<view class="info-icon">{{ getDifficultyIcon(foodDetail.difficulty) }}</view>
						<view class="info-content">
							<text class="info-label">难度等级</text>
							<text class="info-value">{{ getDifficultyText(foodDetail.difficulty) }}</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 标签 -->
			<view class="info-card" v-if="foodDetail.tags && foodDetail.tags.length > 0">
				<view class="card-header">
					<text class="card-title">特色标签</text>
				</view>
				<view class="tags-container">
					<view class="tag-item" v-for="tag in foodDetail.tags" :key="tag">
						{{ tag }}
					</view>
				</view>
			</view>
			
			<!-- 详细介绍 -->
			<view class="info-card" v-if="foodDetail.detailedDescription">
				<view class="card-header">
					<text class="card-title">详细介绍</text>
				</view>
				<view class="description-content">
					<text class="description-text">{{ foodDetail.detailedDescription }}</text>
				</view>
			</view>
			
			<!-- 营养信息 -->
			<view class="info-card" v-if="foodDetail.nutrition">
				<view class="card-header">
					<text class="card-title">营养信息</text>
				</view>
				<view class="nutrition-grid">
					<view class="nutrition-item" v-for="(value, key) in foodDetail.nutrition" :key="key">
						<text class="nutrition-label">{{ getNutritionLabel(key) }}</text>
						<text class="nutrition-value">{{ value }}</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 底部操作栏 -->
		<view class="action-bar">
			<view class="action-btn secondary" @click="goBack">
				<text class="action-text">返回</text>
			</view>
			<view class="action-btn primary" @click="addToOrder">
				<text class="action-text">点餐</text>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			foodDetail: {
				id: null,
				name: '',
				description: '',
				detailedDescription: '',
				image: '',
				tags: [],
				cookTime: 0,
				difficulty: 1,
				nutrition: null
			}
		}
	},
	
	onLoad(options) {
		if (options.data) {
			// 从URL参数中获取菜品数据
			try {
				this.foodDetail = JSON.parse(decodeURIComponent(options.data));
			} catch (error) {
				console.error('解析菜品数据失败:', error);
				this.loadDefaultData();
			}
		} else {
			this.loadDefaultData();
		}
	},
	
	methods: {
		// 加载默认数据（用于测试）
		loadDefaultData() {
			this.foodDetail = {
				id: 101,
				name: '红烧肉',
				description: '肥瘦相间，软糯香甜，色泽红亮',
				detailedDescription: '红烧肉是一道著名的大众菜肴，属于热菜。其以五花肉为制作主料，最好选用肥瘦相间的三层肉来做。红烧肉的烹饪技巧以砂锅为主，肥瘦相间，香甜松软，入口即化。红烧肉在我国各地流传甚广，是一道著名的大众菜肴。',
				image: '/static/dishes/hongshaorou.jpg',
				tags: ['经典', '下饭', '节日', '传统'],
				cookTime: 45,
				difficulty: 2,
				nutrition: {
					calories: '500',
					protein: '25g',
					fat: '35g',
					carbs: '15g'
				}
			};
		},
		
		// 预览图片
		previewImage() {
			uni.previewImage({
				urls: [this.foodDetail.image],
				current: this.foodDetail.image
			});
		},
		
		// 获取难度图标
		getDifficultyIcon(difficulty) {
			const icons = {
				1: '😊',
				2: '🤔',
				3: '😰'
			};
			return icons[difficulty] || '😊';
		},
		
		// 获取难度文本
		getDifficultyText(difficulty) {
			const texts = {
				1: '简单',
				2: '中等',
				3: '困难'
			};
			return texts[difficulty] || '简单';
		},
		
		// 获取营养标签
		getNutritionLabel(key) {
			const labels = {
				calories: '热量',
				protein: '蛋白质',
				fat: '脂肪',
				carbs: '碳水化合物'
			};
			return labels[key] || key;
		},
		
		// 返回上一页
		goBack() {
			uni.navigateBack();
		},
		
		// 添加到点餐
		addToOrder() {
			uni.showToast({
				title: `已添加${this.foodDetail.name}到点餐车`,
				icon: 'success'
			});
			// 这里可以添加到点餐车的逻辑
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #F5F7FA;
	padding-bottom: 120rpx;
}

/* 图片区域 */
.image-section {
	position: relative;
	height: 500rpx;
	overflow: hidden;
}

.food-image {
	width: 100%;
	height: 100%;
}

.image-overlay {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
	padding: 60rpx 30rpx 30rpx;
	color: white;
}

.food-title {
	font-size: 36rpx;
	font-weight: bold;
	margin-bottom: 12rpx;
}

.food-subtitle {
	font-size: 26rpx;
	opacity: 0.9;
	line-height: 1.4;
}

/* 信息区域 */
.info-section {
	padding: 30rpx;
}

.info-card {
	background: white;
	border-radius: 20rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
	margin-bottom: 24rpx;
}

.card-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
}

/* 基本信息网格 */
.info-grid {
	display: flex;
	gap: 30rpx;
}

.info-item {
	flex: 1;
	display: flex;
	align-items: center;
	padding: 20rpx;
	background: #F8F9FA;
	border-radius: 16rpx;
}

.info-icon {
	font-size: 32rpx;
	margin-right: 16rpx;
}

.info-content {
	flex: 1;
}

.info-label {
	display: block;
	font-size: 22rpx;
	color: #666;
	margin-bottom: 4rpx;
}

.info-value {
	font-size: 26rpx;
	font-weight: 500;
	color: #333;
}

/* 标签容器 */
.tags-container {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
}

.tag-item {
	background: linear-gradient(135deg, #FF6B95, #FF8C94);
	color: white;
	padding: 8rpx 16rpx;
	border-radius: 20rpx;
	font-size: 22rpx;
	font-weight: 500;
}

/* 详细介绍 */
.description-content {
	line-height: 1.6;
}

.description-text {
	font-size: 26rpx;
	color: #555;
}

/* 营养信息网格 */
.nutrition-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 16rpx;
}

.nutrition-item {
	background: #F8F9FA;
	padding: 20rpx;
	border-radius: 12rpx;
	text-align: center;
}

.nutrition-label {
	display: block;
	font-size: 22rpx;
	color: #666;
	margin-bottom: 8rpx;
}

.nutrition-value {
	font-size: 28rpx;
	font-weight: bold;
	color: #FF6B95;
}

/* 底部操作栏 */
.action-bar {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background: white;
	padding: 20rpx 30rpx;
	border-top: 1rpx solid #E9ECEF;
	display: flex;
	gap: 20rpx;
	box-shadow: 0 -4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.action-btn {
	flex: 1;
	padding: 24rpx;
	border-radius: 25rpx;
	text-align: center;
	font-weight: 500;
	font-size: 28rpx;
}

.action-btn.secondary {
	background: #F8F9FA;
	color: #666;
}

.action-btn.primary {
	background: linear-gradient(135deg, #FF6B95, #FF8C94);
	color: white;
}

.action-text {
	color: inherit;
}
</style>
