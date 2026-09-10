<template>
	<view class="container">
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">每日用餐计划</text>
			<view class="header-actions">
				<button class="action-btn" @click="showDatePicker">
					<text class="calendar-icon">📅</text>
					<text>{{ formatDate(selectedDate) }}</text>
				</button>
			</view>
		</view>
		
		<!-- 日期选择器 -->
		<uni-calendar 
			v-if="showCalendar"
			:insert="false" 
			@change="dateChange" 
			@confirm="dateConfirm"
			:selected="[selectedDate]"
		/>
		
		<!-- 餐次导航 -->
		<view class="meal-session-tabs">
			<view 
				class="meal-session-tab" 
				v-for="session in mealSessions" 
				:key="session.value"
				:class="{ active: currentSession === session.value }"
				@click="changeSession(session.value)"
			>
				<text class="session-icon">{{ session.icon }}</text>
				<text class="session-label">{{ session.label }}</text>
			</view>
		</view>
		
		<!-- 没有计划时显示创建按钮 -->
		<view class="no-plan" v-if="!currentPlan">
			<view class="no-plan-content">
				<text class="no-plan-icon">🍽️</text>
				<text class="no-plan-text">当前餐次还没有用餐计划</text>
				<button class="create-plan-btn" @click="showCreatePlanModal" v-if="isAdmin">创建用餐计划</button>
				<button class="create-plan-btn" @click="showRequestMealModal" v-else>点餐请求</button>
			</view>
		</view>
		
		<!-- 用餐计划内容 -->
		<view class="meal-plan" v-else>
			<!-- 计划信息头部 -->
			<view class="plan-header">
				<view class="plan-info">
					<text class="plan-title">{{ getSessionLabel(currentSession) }} 用餐计划</text>
					<text class="plan-coordinator">协调人: {{ currentPlan.coordinator?.nickname || '未指定' }}</text>
				</view>
				
				<view class="plan-actions" v-if="isAdmin">
					<button class="edit-plan-btn" @click="editPlan">编辑</button>
				</view>
			</view>
			
			<!-- 餐品列表 -->
			<view class="plan-items">
				<view class="plan-item" v-for="(item, index) in currentPlan.confirmed_items" :key="index">
					<view class="item-info">
						<text class="item-name">{{ item.name }}</text>
						<text class="item-quantity">x{{ item.quantity }}</text>
					</view>
				</view>
			</view>
			
			<!-- 备注 -->
			<view class="plan-note" v-if="currentPlan.note">
				<text class="note-label">备注:</text>
				<text class="note-content">{{ currentPlan.note }}</text>
			</view>
		</view>
		
		<!-- 底部功能栏 - 管理员可见 -->
		<view class="bottom-toolbar" v-if="isAdmin">
			<button class="toolbar-btn" @click="viewPendingRequests">
				<text class="btn-icon">📋</text>
				<text class="btn-text">待处理请求</text>
				<text class="btn-badge" v-if="pendingCount > 0">{{ pendingCount }}</text>
			</button>
			
			<button class="toolbar-btn primary" @click="generatePlanFromRequests" v-if="!currentPlan">
				<text class="btn-icon">✅</text>
				<text class="btn-text">一键生成计划</text>
			</button>
		</view>
		
		<!-- 创建计划模态框 -->
		<uni-popup ref="createPlanPopup" type="center">
			<view class="popup-content">
				<view class="popup-header">
					<text class="popup-title">创建用餐计划</text>
					<text class="close-icon" @click="hideCreatePlanModal">×</text>
				</view>
				
				<view class="popup-body">
					<view class="form-item">
						<text class="form-label">日期</text>
						<text class="form-value">{{ formatDate(selectedDate) }}</text>
					</view>
					
					<view class="form-item">
						<text class="form-label">餐次</text>
						<text class="form-value">{{ getSessionLabel(currentSession) }}</text>
					</view>
					
					<view class="form-item">
						<text class="form-label">备注</text>
						<textarea class="form-textarea" v-model="planNote" placeholder="添加备注"></textarea>
					</view>
					
					<view class="form-item">
						<checkbox-group @change="onOverwriteChange">
							<label class="checkbox-label">
								<checkbox :checked="overwriteExisting" />
								<text>覆盖已存在的计划</text>
							</label>
						</checkbox-group>
					</view>
				</view>
				
				<view class="popup-footer">
					<button class="popup-btn" @click="hideCreatePlanModal">取消</button>
					<button class="popup-btn primary" @click="createPlan">确认创建</button>
				</view>
			</view>
		</uni-popup>
	</view>
</template>

<script>
import orderingManager from '@/utils/orderingManager.js'
import userManager from '@/utils/userManager.js'
import familyManager from '@/utils/familyManager.js'

export default {
	data() {
		return {
			selectedDate: new Date().toISOString().split('T')[0],
			showCalendar: false,
			mealSessions: [
				{ value: 'breakfast', label: '早餐', icon: '🍳' },
				{ value: 'lunch', label: '午餐', icon: '🍲' },
				{ value: 'dinner', label: '晚餐', icon: '🍖' },
				{ value: 'snack', label: '加餐', icon: '🍰' }
			],
			currentSession: 'lunch', // 默认显示午餐
			dailyPlans: [], // 当日所有餐次的计划
			currentPlan: null, // 当前显示的计划
			isAdmin: false,
			pendingCount: 0,
			
			// 创建计划相关
			planNote: '',
			overwriteExisting: false,
			
			// 当前家庭
			currentFamily: null
		}
	},
	
	onShow() {
		this.loadDailyPlans()
	},
	
	onLoad() {
		this.checkAdminStatus()
		this.loadCurrentFamily()
		this.loadDailyPlans()
		this.loadPendingCount()
	},
	
	methods: {
		formatDate(date) {
			if (!date) return ''
			const d = new Date(date)
			const year = d.getFullYear()
			const month = String(d.getMonth() + 1).padStart(2, '0')
			const day = String(d.getDate()).padStart(2, '0')
			return `${year}-${month}-${day}`
		},
		
		getSessionLabel(value) {
			const session = this.mealSessions.find(s => s.value === value)
			return session ? session.label : '未知'
		},
		
		// 检查当前用户是否是管理员
		async checkAdminStatus() {
			try {
				const userData = await userManager.getUserInfo()
				const familyData = await familyManager.getCurrentFamily()
				
				if (familyData && familyData.id) {
					const members = await familyManager.getFamilyMembers(familyData.id)
					const currentMember = members.find(m => m.user_id === userData.id)
					this.isAdmin = currentMember && currentMember.is_admin
				}
			} catch (error) {
				console.error('检查管理员状态失败:', error)
				this.isAdmin = false
			}
		},
		
		// 加载当前家庭信息
		async loadCurrentFamily() {
			try {
				this.currentFamily = await familyManager.getCurrentFamily()
			} catch (error) {
				console.error('加载家庭信息失败:', error)
				uni.showToast({
					title: '加载家庭信息失败',
					icon: 'none'
				})
			}
		},
		
		// 加载日期对应的用餐计划
		async loadDailyPlans() {
			try {
				uni.showLoading({ title: '加载中...' })
				this.dailyPlans = await orderingManager.getMealPlansByDate(this.selectedDate)
				this.updateCurrentPlan()
				uni.hideLoading()
			} catch (error) {
				uni.hideLoading()
				console.error('加载用餐计划失败:', error)
				uni.showToast({
					title: '加载用餐计划失败',
					icon: 'none'
				})
			}
		},
		
		// 加载待处理点餐请求数量
		async loadPendingCount() {
			if (this.isAdmin) {
				try {
					const requests = await orderingManager.getPendingRequests()
					this.pendingCount = requests.length || 0
				} catch (error) {
					console.error('加载待处理请求失败:', error)
					this.pendingCount = 0
				}
			}
		},
		
		// 更新当前显示的计划
		updateCurrentPlan() {
			if (this.dailyPlans && this.dailyPlans.length > 0) {
				this.currentPlan = this.dailyPlans.find(p => p.meal_session === this.currentSession) || null
			} else {
				this.currentPlan = null
			}
		},
		
		// 显示日期选择器
		showDatePicker() {
			this.showCalendar = true
		},
		
		// 日期变化处理
		dateChange(e) {
			console.log('日期变化:', e)
		},
		
		// 日期确认处理
		dateConfirm(e) {
			this.showCalendar = false
			this.selectedDate = e.fulldate
			this.loadDailyPlans()
		},
		
		// 切换餐次
		changeSession(session) {
			this.currentSession = session
			this.updateCurrentPlan()
		},
		
		// 显示创建计划模态框
		showCreatePlanModal() {
			this.planNote = ''
			this.overwriteExisting = false
			this.$refs.createPlanPopup.open()
		},
		
		// 隐藏创建计划模态框
		hideCreatePlanModal() {
			this.$refs.createPlanPopup.close()
		},
		
		// 覆盖选项变化
		onOverwriteChange(e) {
			this.overwriteExisting = e.detail.value.length > 0
		},
		
		// 创建计划
		async createPlan() {
			if (!this.currentFamily) {
				uni.showToast({
					title: '请先选择家庭',
					icon: 'none'
				})
				return
			}
			
			try {
				uni.showLoading({ title: '创建中...' })
				
				const planData = {
					family_id: this.currentFamily.id,
					date: this.selectedDate,
					meal_session: this.currentSession,
					note: this.planNote,
					confirmed_items: []
				}
				
				await orderingManager.createDailyMealPlan(planData)
				
				uni.hideLoading()
				uni.showToast({
					title: '创建成功',
					icon: 'success'
				})
				
				this.hideCreatePlanModal()
				this.loadDailyPlans()
			} catch (error) {
				uni.hideLoading()
				console.error('创建用餐计划失败:', error)
				uni.showToast({
					title: '创建失败: ' + (error.message || '未知错误'),
					icon: 'none'
				})
			}
		},
		
		// 编辑计划
		editPlan() {
			if (!this.currentPlan) return
			
			uni.navigateTo({
				url: `/pages/ordering/edit-meal-plan?id=${this.currentPlan.id}`
			})
		},
		
		// 查看待处理点餐请求
		viewPendingRequests() {
			uni.navigateTo({
				url: '/pages/ordering/pending-requests'
			})
		},
		
		// 显示点餐请求模态框
		showRequestMealModal() {
			uni.navigateTo({
				url: '/pages/ordering/index'
			})
		},
		
		// 从已确认的请求生成计划
		async generatePlanFromRequests() {
			if (!this.currentFamily) {
				uni.showToast({
					title: '请先选择家庭',
					icon: 'none'
				})
				return
			}
			
			try {
				uni.showLoading({ title: '生成中...' })
				
				const data = {
					family_id: this.currentFamily.id,
					date: this.selectedDate,
					meal_session: this.currentSession,
					overwrite: this.overwriteExisting
				}
				
				await orderingManager.generateDailyMealPlan(data)
				
				uni.hideLoading()
				uni.showToast({
					title: '生成成功',
					icon: 'success'
				})
				
				this.loadDailyPlans()
			} catch (error) {
				uni.hideLoading()
				console.error('生成用餐计划失败:', error)
				uni.showToast({
					title: '生成失败: ' + (error.message || '未知错误'),
					icon: 'none'
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
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
	
	.page-title {
		font-size: 36rpx;
		font-weight: bold;
	}
	
	.header-actions {
		.action-btn {
			display: flex;
			align-items: center;
			background-color: #f5f5f5;
			padding: 10rpx 20rpx;
			border-radius: 30rpx;
			border: none;
			
			.calendar-icon {
				margin-right: 10rpx;
			}
		}
	}
}

.meal-session-tabs {
	display: flex;
	background-color: #fff;
	border-radius: 12rpx;
	box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
	margin-bottom: 30rpx;
	
	.meal-session-tab {
		flex: 1;
		text-align: center;
		padding: 20rpx 0;
		
		&.active {
			color: #FF6B95;
			position: relative;
			
			&:after {
				content: '';
				position: absolute;
				bottom: 0;
				left: 20%;
				width: 60%;
				height: 4rpx;
				background-color: #FF6B95;
				border-radius: 2rpx;
			}
		}
		
		.session-icon {
			display: block;
			font-size: 40rpx;
			margin-bottom: 6rpx;
		}
		
		.session-label {
			font-size: 26rpx;
		}
	}
}

.no-plan {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 100rpx 0;
	background-color: #fff;
	border-radius: 12rpx;
	box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
	
	.no-plan-content {
		text-align: center;
		
		.no-plan-icon {
			font-size: 80rpx;
			margin-bottom: 20rpx;
			display: block;
		}
		
		.no-plan-text {
			color: #999;
			margin-bottom: 40rpx;
			display: block;
		}
		
		.create-plan-btn {
			background-color: #FF6B95;
			color: #fff;
			border-radius: 40rpx;
			font-size: 28rpx;
			padding: 15rpx 40rpx;
		}
	}
}

.meal-plan {
	background-color: #fff;
	border-radius: 12rpx;
	box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
	padding: 30rpx;
	
	.plan-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30rpx;
		padding-bottom: 20rpx;
		border-bottom: 1px solid #f0f0f0;
		
		.plan-info {
			.plan-title {
				font-size: 32rpx;
				font-weight: bold;
				margin-bottom: 10rpx;
				display: block;
			}
			
			.plan-coordinator {
				color: #666;
				font-size: 26rpx;
			}
		}
		
		.plan-actions {
			.edit-plan-btn {
				background-color: transparent;
				color: #FF6B95;
				border: 1px solid #FF6B95;
				border-radius: 30rpx;
				padding: 10rpx 30rpx;
				font-size: 26rpx;
			}
		}
	}
	
	.plan-items {
		margin-bottom: 30rpx;
		
		.plan-item {
			display: flex;
			justify-content: space-between;
			padding: 20rpx 0;
			border-bottom: 1px solid #f8f8f8;
			
			&:last-child {
				border-bottom: none;
			}
			
			.item-info {
				display: flex;
				align-items: center;
				
				.item-name {
					font-size: 28rpx;
					margin-right: 20rpx;
				}
				
				.item-quantity {
					color: #666;
					background-color: #f5f5f5;
					padding: 4rpx 16rpx;
					border-radius: 20rpx;
					font-size: 24rpx;
				}
			}
		}
	}
	
	.plan-note {
		background-color: #f8f8f8;
		padding: 20rpx;
		border-radius: 8rpx;
		
		.note-label {
			color: #666;
			font-size: 26rpx;
			margin-right: 10rpx;
		}
		
		.note-content {
			font-size: 26rpx;
		}
	}
}

.bottom-toolbar {
	position: fixed;
	left: 0;
	right: 0;
	bottom: 0;
	display: flex;
	padding: 20rpx;
	background-color: #fff;
	box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
	
	.toolbar-btn {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 20rpx 0;
		border-radius: 40rpx;
		margin: 0 10rpx;
		background-color: #f5f5f5;
		border: none;
		position: relative;
		
		&.primary {
			background-color: #FF6B95;
			color: #fff;
		}
		
		.btn-icon {
			margin-right: 10rpx;
		}
		
		.btn-badge {
			position: absolute;
			top: -10rpx;
			right: 10rpx;
			background-color: #ff3b30;
			color: #fff;
			font-size: 20rpx;
			min-width: 32rpx;
			height: 32rpx;
			border-radius: 16rpx;
			display: flex;
			align-items: center;
			justify-content: center;
			padding: 0 6rpx;
		}
	}
}

.popup-content {
	background-color: #fff;
	width: 80vw;
	border-radius: 12rpx;
	overflow: hidden;
	
	.popup-header {
		padding: 30rpx;
		display: flex;
		justify-content: space-between;
		align-items: center;
		border-bottom: 1px solid #f0f0f0;
		
		.popup-title {
			font-size: 32rpx;
			font-weight: bold;
		}
		
		.close-icon {
			font-size: 40rpx;
			color: #999;
		}
	}
	
	.popup-body {
		padding: 30rpx;
		
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
			
			.form-value {
				font-size: 30rpx;
			}
			
			.form-textarea {
				width: 100%;
				height: 200rpx;
				padding: 20rpx;
				border: 1px solid #e0e0e0;
				border-radius: 8rpx;
			}
			
			.checkbox-label {
				display: flex;
				align-items: center;
				font-size: 28rpx;
			}
		}
	}
	
	.popup-footer {
		padding: 20rpx;
		display: flex;
		border-top: 1px solid #f0f0f0;
		
		.popup-btn {
			flex: 1;
			text-align: center;
			padding: 20rpx 0;
			font-size: 30rpx;
			
			&.primary {
				color: #FF6B95;
				font-weight: bold;
			}
		}
	}
}
</style>
