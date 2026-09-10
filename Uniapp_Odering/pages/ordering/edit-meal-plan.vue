<template>
	<view class="container">
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">编辑用餐计划</text>
		</view>
		
		<!-- 离线模式提示 -->
		<view class="offline-notice" v-if="offlineMode">
			<text class="offline-icon">⚠️</text>
			<text class="offline-text">网络连接失败，当前使用本地缓存数据</text>
		</view>
		
		<!-- 编辑表单 -->
		<view class="edit-form">
			<!-- 基本信息 -->
			<view class="form-section">
				<text class="section-title">基本信息</text>
				
				<view class="form-item">
					<text class="form-label">日期</text>
					<view class="date-picker" @click="showDatePicker">
						<view class="date-info">
							<text class="date-value">{{ formatDate(planForm.date) }}</text>
							<text class="date-week">{{ getDayOfWeek(planForm.date) }}</text>
							<text class="date-relative" v-if="getRelativeDateText(planForm.date)">
								({{ getRelativeDateText(planForm.date) }})
							</text>
						</view>
						<text class="picker-icon">📅</text>
					</view>
				</view>
				
				<view class="form-item">
					<text class="form-label">餐次</text>
					<picker :value="sessionIndex" :range="mealSessions" range-key="label" @change="onSessionChange">
						<view class="picker-view">
							<view class="session-info">
								<text class="session-icon">{{ getSessionIcon(planForm.meal_session) }}</text>
								<text class="session-label">{{ getSessionLabel(planForm.meal_session) }}</text>
							</view>
							<text class="picker-icon">▼</text>
						</view>
					</picker>
				</view>
				
				<view class="form-item">
					<text class="form-label">备注</text>
					<textarea 
						v-model="planForm.note" 
						class="form-textarea" 
						placeholder="添加计划备注信息..."
						maxlength="200"
					></textarea>
				</view>
			</view>
			
			<!-- 日期选择器弹窗 -->
			<uni-calendar 
				v-if="showCalendar"
				:insert="false" 
				@change="dateChange" 
				@confirm="dateConfirm"
				:selected="[planForm.date]"
			/>
			
			<!-- 确认餐品列表 -->
			<view class="form-section">
				<view class="section-header">
					<text class="section-title">确认餐品</text>
					<button class="add-btn" @click="showAddMealItem">添加餐品</button>
				</view>
				
				<view class="meal-items-list">
					<view v-if="planForm.confirmed_items.length === 0" class="empty-items">
						<text>暂无确认餐品，请添加</text>
					</view>
					
					<view v-else>
						<view class="meal-item" v-for="(item, index) in planForm.confirmed_items" :key="index">
							<image 
								class="item-image" 
								:src="item.image || '/static/food-decoration.png'" 
								mode="aspectFill"
							></image>
							<view class="item-info">
								<text class="item-name">{{ item.name }}</text>
								<view class="item-quantity">
									<button class="quantity-btn" @click="decreaseQuantity(index)" :disabled="item.quantity <= 1">-</button>
									<text class="quantity-value">{{ item.quantity }}</text>
									<button class="quantity-btn" @click="increaseQuantity(index)">+</button>
								</view>
							</view>
							<button class="remove-btn" @click="removeItem(index)">删除</button>
						</view>
						
						<!-- 餐品统计 -->
						<view class="meal-summary">
							<text class="summary-text">共计 {{ planForm.confirmed_items.length }} 种餐品，{{ totalQuantity }} 份</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 添加餐品弹窗 -->
			<uni-popup ref="addMealPopup" type="bottom">
				<view class="popup-content">
					<view class="popup-header">
						<text class="popup-title">选择餐品</text>
						<text class="close-icon" @click="hideAddMealItem">×</text>
					</view>
					
					<view class="search-bar">
						<input 
							type="text" 
							v-model="searchKeyword" 
							placeholder="搜索餐品..." 
							class="search-input"
							@input="searchMeals"
						/>
						<text class="search-icon">🔍</text>
					</view>
					
					<scroll-view class="meal-select-list" scroll-y="true">
						<view class="meal-select-item" v-for="meal in availableMeals" :key="meal.id" @click="selectMeal(meal)">
							<image class="meal-image" :src="meal.image || '/static/food-decoration.png'" mode="aspectFill"></image>
							<view class="meal-info">
								<text class="meal-name">{{ meal.name }}</text>
								<text class="meal-description">{{ meal.description || '暂无描述' }}</text>
							</view>
							<text class="add-icon">+</text>
						</view>
						
						<view v-if="availableMeals.length === 0" class="no-results">
							<text>未找到相关餐品</text>
						</view>
					</scroll-view>
				</view>
			</uni-popup>
		</view>
		
		<!-- 底部操作栏 -->
		<view class="bottom-actions">
			<button class="action-btn cancel" @click="goBack">取消</button>
			<button class="action-btn save" @click="savePlan">保存</button>
		</view>
	</view>
</template>

<script>
import orderingManager from '../../utils/orderingManager.js'
import { formatDate, getDayOfWeek, getRelativeDate, isToday } from '../../utils/dateUtils.js'

export default {
	data() {
		return {
			planId: null,
			planForm: {
				date: new Date().toISOString().split('T')[0],
				meal_session: 'lunch',
				confirmed_items: [],
				note: ''
			},
			mealSessions: [
				{ value: 'breakfast', label: '早餐', icon: '🍳' },
				{ value: 'lunch', label: '午餐', icon: '🍲' },
				{ value: 'dinner', label: '晚餐', icon: '🍖' },
				{ value: 'snack', label: '加餐', icon: '🍰' }
			],
			sessionIndex: 1, // 默认午餐
			showCalendar: false,
			
			// 餐品相关
			availableMeals: [],
			allMeals: [],
			searchKeyword: '',
			
			// 家庭相关
			familyId: null,
			
			// 状态控制
			loadingMeals: false,
			networkError: false,
			offlineMode: false
		}
	},
	
	computed: {
		// 计算餐品总数量
		totalQuantity() {
			return this.planForm.confirmed_items.reduce((total, item) => {
				return total + (item.quantity || 0)
			}, 0)
		}
	},
	
	onLoad(options) {
		if (options.id) {
			this.planId = options.id
			this.loadPlanData()
		}
		
		this.loadFamilyInfo()
		this.loadMeals()
	},
	
	methods: {
		formatDate,
		getDayOfWeek,
		
		// 获取相对日期文本
		getRelativeDateText(date) {
			// 如果是今天、明天或昨天，返回对应文本
			// 否则返回空字符串（不显示相对日期提示）
			return getRelativeDate(date);
		},
		
		// 加载用餐计划数据
		async loadPlanData() {
			try {
				uni.showLoading({ title: '加载中...' })
				const plan = await orderingManager.getDailyMealPlanDetail(this.planId)
				
				this.planForm.date = plan.date
				this.planForm.meal_session = plan.meal_session
				this.planForm.confirmed_items = plan.confirmed_items || []
				this.planForm.note = plan.note || ''
				
				// 更新餐次索引
				this.sessionIndex = this.mealSessions.findIndex(s => s.value === plan.meal_session)
				if (this.sessionIndex < 0) this.sessionIndex = 0
				
				uni.hideLoading()
			} catch (error) {
				uni.hideLoading()
				console.error('加载用餐计划失败:', error)
				uni.showToast({
					title: '加载失败: ' + (error.message || '未知错误'),
					icon: 'none'
				})
			}
		},
		
		// 加载家庭信息
		async loadFamilyInfo() {
			try {
				const familyInfo = await uni.getStorageSync('currentFamily')
				if (familyInfo) {
					this.familyId = familyInfo.id
				}
			} catch (error) {
				console.error('获取家庭信息失败:', error)
			}
		},
		
		// 加载可用餐品
		async loadMeals() {
			if (this.loadingMeals) return;
			
			this.loadingMeals = true;
			this.networkError = false;
			
			try {
				// 尝试从本地缓存加载(以防网络连接失败)
				const cachedMeals = uni.getStorageSync('cached_available_meals');
				if (cachedMeals) {
					this.allMeals = JSON.parse(cachedMeals);
					this.availableMeals = [...this.allMeals];
				}
				
				// 从服务器获取最新数据
				const meals = await orderingManager.getMeals({ available_only: true });
				this.allMeals = meals || [];
				this.availableMeals = [...this.allMeals];
				
				// 缓存到本地存储
				if (meals && meals.length > 0) {
					uni.setStorageSync('cached_available_meals', JSON.stringify(meals));
				}
				
				this.offlineMode = false;
			} catch (error) {
				console.error('加载餐品失败:', error);
				this.networkError = true;
				
				// 检查是否有本地缓存数据
				if (this.allMeals.length === 0) {
					uni.showToast({
						title: '网络连接失败，无本地数据',
						icon: 'none',
						duration: 3000
					});
				} else {
					this.offlineMode = true;
					uni.showToast({
						title: '使用缓存数据 (离线模式)',
						icon: 'none',
						duration: 2000
					});
				}
			} finally {
				this.loadingMeals = false;
			}
		},
		
		// 搜索餐品
		searchMeals() {
			if (!this.searchKeyword) {
				this.availableMeals = [...this.allMeals]
				return
			}
			
			const keyword = this.searchKeyword.toLowerCase()
			this.availableMeals = this.allMeals.filter(meal => {
				return meal.name.toLowerCase().includes(keyword) || 
					(meal.description && meal.description.toLowerCase().includes(keyword))
			})
		},
		
		// 餐次标签获取
		getSessionLabel(value) {
			const session = this.mealSessions.find(s => s.value === value)
			return session ? session.label : '未知'
		},
		
		// 餐次图标获取
		getSessionIcon(value) {
			const session = this.mealSessions.find(s => s.value === value)
			return session ? session.icon : '🍽️'
		},
		
		// 显示日期选择器
		showDatePicker() {
			this.showCalendar = true
		},
		
		// 日期变化
		dateChange(e) {
			console.log('日期变化:', e)
		},
		
		// 日期确认
		dateConfirm(e) {
			this.showCalendar = false
			this.planForm.date = e.fulldate
		},
		
		// 餐次变化
		onSessionChange(e) {
			const index = e.detail.value
			this.sessionIndex = index
			this.planForm.meal_session = this.mealSessions[index].value
		},
		
		// 显示添加餐品弹窗
		showAddMealItem() {
			this.searchKeyword = ''
			this.availableMeals = [...this.allMeals]
			this.$refs.addMealPopup.open()
		},
		
		// 隐藏添加餐品弹窗
		hideAddMealItem() {
			this.$refs.addMealPopup.close()
		},
		
		// 选择餐品
		selectMeal(meal) {
			// 检查是否已添加
			const existingIndex = this.planForm.confirmed_items.findIndex(item => item.meal_item_id === meal.id)
			
			if (existingIndex >= 0) {
				// 已存在，增加数量
				this.planForm.confirmed_items[existingIndex].quantity++
			} else {
				// 新增项目
				this.planForm.confirmed_items.push({
					meal_item_id: meal.id,
					name: meal.name,
					quantity: 1,
					image: meal.image
				})
			}
			
			uni.showToast({
				title: '已添加',
				icon: 'success'
			})
			
			this.hideAddMealItem()
		},
		
		// 增加餐品数量
		increaseQuantity(index) {
			this.planForm.confirmed_items[index].quantity++
		},
		
		// 减少餐品数量
		decreaseQuantity(index) {
			if (this.planForm.confirmed_items[index].quantity > 1) {
				this.planForm.confirmed_items[index].quantity--
			}
		},
		
		// 删除餐品
		removeItem(index) {
			this.planForm.confirmed_items.splice(index, 1)
		},
		
		// 返回上一页
		goBack() {
			uni.navigateBack()
		},
		
		// 保存用餐计划
		async savePlan() {
			if (!this.familyId) {
				uni.showToast({
					title: '请先选择家庭',
					icon: 'none'
				})
				return
			}
			
			if (this.planForm.confirmed_items.length === 0) {
				uni.showToast({
					title: '请至少添加一个餐品',
					icon: 'none'
				})
				return
			}
			
			try {
				uni.showLoading({ title: '保存中...' })
				
				const planData = {
					...this.planForm,
					family_id: this.familyId
				}
				
				if (this.offlineMode) {
					// 离线模式：保存到本地暂存
					const offlineDrafts = uni.getStorageSync('offline_meal_plans') || []
					const drafts = JSON.parse(Array.isArray(offlineDrafts) ? JSON.stringify(offlineDrafts) : '[]')
					
					// 检查是否为更新
					let updated = false
					if (this.planId) {
						const index = drafts.findIndex(p => p.id === this.planId)
						if (index >= 0) {
							drafts[index] = {
								...planData,
								id: this.planId,
								_offline: true,
								_updated: new Date().toISOString()
							}
							updated = true
						}
					}
					
					if (!updated) {
						// 添加新的草稿
						drafts.push({
							...planData,
							id: `offline_${Date.now()}`,
							_offline: true,
							_created: new Date().toISOString()
						})
					}
					
					uni.setStorageSync('offline_meal_plans', drafts)
					
					uni.hideLoading()
					uni.showModal({
						title: '离线模式',
						content: '您当前处于离线模式，数据已保存到本地。恢复网络连接后将自动上传。',
						showCancel: false,
						success: () => {
							uni.navigateBack()
						}
					})
				} else {
					// 在线模式：直接保存到服务器
					if (this.planId) {
						// 更新
						await orderingManager.updateDailyMealPlan(this.planId, planData)
					} else {
						// 新增
						await orderingManager.createDailyMealPlan(planData)
					}
					
					uni.hideLoading()
					uni.showToast({
						title: '保存成功',
						icon: 'success'
					})
					
					setTimeout(() => {
						uni.navigateBack()
					}, 1500)
				}
			} catch (error) {
				uni.hideLoading()
				console.error('保存用餐计划失败:', error)
				
				// 询问是否要离线保存
				uni.showModal({
					title: '保存失败',
					content: '网络连接失败，是否保存到本地草稿？',
					success: (res) => {
						if (res.confirm) {
							this.offlineMode = true
							this.savePlan() // 递归调用，但现在是离线模式
						}
					}
				})
			}
		}
	}
}
</script>

<style lang="scss">
.container {
	padding: 20rpx;
}

.page-header {
	margin-bottom: 20rpx;
	
	.page-title {
		font-size: 36rpx;
		font-weight: bold;
	}
}

.offline-notice {
	background-color: #fff8e6;
	padding: 10rpx 20rpx;
	margin-bottom: 20rpx;
	border-radius: 8rpx;
	display: flex;
	align-items: center;
	
	.offline-icon {
		margin-right: 10rpx;
	}
	
	.offline-text {
		font-size: 24rpx;
		color: #f59a23;
	}
}

.edit-form {
	.form-section {
		background-color: #fff;
		border-radius: 12rpx;
		padding: 20rpx;
		margin-bottom: 30rpx;
		box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
		
		.section-title {
			font-size: 30rpx;
			font-weight: bold;
			margin-bottom: 20rpx;
			display: block;
		}
		
		.section-header {
			display: flex;
			justify-content: space-between;
			align-items: center;
			margin-bottom: 20rpx;
			
			.add-btn {
				background-color: #FF6B95;
				color: #fff;
				font-size: 24rpx;
				padding: 8rpx 20rpx;
				border-radius: 30rpx;
				line-height: 1.5;
			}
		}
		
		.form-item {
			margin-bottom: 30rpx;
			
			&:last-child {
				margin-bottom: 0;
			}
			
			.form-label {
				font-size: 28rpx;
				color: #666;
				margin-bottom: 10rpx;
				display: block;
			}
			
			.date-picker, .picker-view {
				display: flex;
				justify-content: space-between;
				align-items: center;
				min-height: 80rpx;
				padding: 10rpx 20rpx;
				border: 1px solid #eee;
				border-radius: 8rpx;
				
				.date-info {
					display: flex;
					flex-wrap: wrap;
					align-items: center;
					
					.date-value {
						font-size: 28rpx;
						margin-right: 10rpx;
					}
					
					.date-week {
						font-size: 24rpx;
						color: #666;
						background-color: #f5f5f5;
						padding: 2rpx 10rpx;
						border-radius: 4rpx;
						margin-right: 10rpx;
					}
					
					.date-relative {
						font-size: 24rpx;
						color: #FF6B95;
					}
				}
				
				.session-info {
					display: flex;
					align-items: center;
					
					.session-icon {
						margin-right: 10rpx;
						font-size: 28rpx;
					}
					
					.session-label {
						font-size: 28rpx;
					}
				}
				
				.picker-icon {
					color: #999;
				}
			}
			
			.form-textarea {
				width: 100%;
				height: 160rpx;
				padding: 20rpx;
				border: 1px solid #eee;
				border-radius: 8rpx;
				box-sizing: border-box;
			}
		}
		
		.meal-items-list {
			.empty-items {
				padding: 40rpx 0;
				text-align: center;
				color: #999;
			}
			
			.meal-item {
				display: flex;
				justify-content: space-between;
				align-items: center;
				padding: 20rpx 0;
				border-bottom: 1px solid #f0f0f0;
				
				&:last-child {
					border-bottom: none;
				}
				
				.item-image {
					width: 80rpx;
					height: 80rpx;
					border-radius: 8rpx;
					margin-right: 20rpx;
					object-fit: cover;
				}
				
				.item-info {
					flex: 1;
					display: flex;
					justify-content: space-between;
					align-items: center;
					margin-right: 20rpx;
					
					.item-name {
						font-size: 28rpx;
					}
					
					.item-quantity {
						display: flex;
						align-items: center;
						
						.quantity-btn {
							width: 50rpx;
							height: 50rpx;
							line-height: 46rpx;
							text-align: center;
							background-color: #f5f5f5;
							border-radius: 50%;
							font-size: 28rpx;
							padding: 0;
							
							&[disabled] {
								opacity: 0.5;
							}
						}
						
						.quantity-value {
							margin: 0 20rpx;
							font-size: 28rpx;
							min-width: 40rpx;
							text-align: center;
						}
					}
				}
				
				.remove-btn {
					font-size: 24rpx;
					color: #FF6B95;
					background: none;
					padding: 10rpx 20rpx;
					line-height: 1;
				}
			}
		}
	}
}

.popup-content {
	background-color: #fff;
	border-top-left-radius: 20rpx;
	border-top-right-radius: 20rpx;
	padding: 30rpx;
	max-height: 70vh;
	
	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30rpx;
		
		.popup-title {
			font-size: 32rpx;
			font-weight: bold;
		}
		
		.close-icon {
			font-size: 40rpx;
			line-height: 1;
			color: #999;
			padding: 10rpx;
		}
	}
	
	.search-bar {
		position: relative;
		margin-bottom: 20rpx;
		
		.search-input {
			width: 100%;
			height: 80rpx;
			background-color: #f5f5f5;
			border-radius: 40rpx;
			padding: 0 80rpx 0 30rpx;
			font-size: 28rpx;
		}
		
		.search-icon {
			position: absolute;
			right: 30rpx;
			top: 50%;
			transform: translateY(-50%);
			color: #999;
		}
	}
	
	.meal-select-list {
		max-height: 60vh;
		
		.meal-select-item {
			display: flex;
			align-items: center;
			padding: 20rpx 0;
			border-bottom: 1px solid #f0f0f0;
			
			&:last-child {
				border-bottom: none;
			}
			
			.meal-image {
				width: 80rpx;
				height: 80rpx;
				border-radius: 8rpx;
				margin-right: 20rpx;
			}
			
			.meal-info {
				flex: 1;
				
				.meal-name {
					font-size: 28rpx;
					margin-bottom: 6rpx;
					display: block;
				}
				
				.meal-description {
					font-size: 24rpx;
					color: #999;
					display: block;
					white-space: nowrap;
					overflow: hidden;
					text-overflow: ellipsis;
					max-width: 400rpx;
				}
			}
			
			.add-icon {
				font-size: 40rpx;
				color: #FF6B95;
				width: 60rpx;
				text-align: center;
			}
		}
		
		.no-results {
			padding: 40rpx 0;
			text-align: center;
			color: #999;
		}
	}
}

.meal-summary {
	padding: 30rpx 0 10rpx;
	text-align: right;
	border-top: 1px dashed #eee;
	margin-top: 20rpx;
	
	.summary-text {
		font-size: 26rpx;
		color: #666;
		background-color: #f8f8f8;
		padding: 8rpx 16rpx;
		border-radius: 20rpx;
	}
}

.bottom-actions {
	position: fixed;
	left: 0;
	right: 0;
	bottom: 0;
	display: flex;
	padding: 20rpx;
	background-color: #fff;
	box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
	
	.action-btn {
		flex: 1;
		height: 90rpx;
		line-height: 90rpx;
		margin: 0 10rpx;
		border-radius: 45rpx;
		font-size: 30rpx;
		
		&.cancel {
			background-color: #f5f5f5;
			color: #666;
		}
		
		&.save {
			background-color: #FF6B95;
			color: #fff;
		}
	}
}

// 添加底部安全间距（防止内容被底部按钮遮挡）
.container {
	padding-bottom: 150rpx;
}
</style>
