<template>
	<view class="container">
		<!-- 加载状态 -->
		<view class="loading" v-if="loading">
			<text class="loading-text">加载中...</text>
		</view>
		
		<form @submit="handleSubmit" v-else>
			<!-- 基本信息 -->
			<view class="section">
				<view class="section-title">
					<text class="section-icon">📋</text>
					<text class="section-text">基本信息</text>
				</view>
				
				<view class="form-group">
					<text class="label">菜谱名称 *</text>
					<input 
						class="input" 
						v-model="form.name" 
						placeholder="请输入菜谱名称" 
						maxlength="50" 
						confirm-type="next"
						adjust-position="true"
						cursor-spacing="10"
						@blur="checkRecipeName"
					/>
					<view v-if="nameCheckResult.checked" class="name-check-result" :class="{ error: nameCheckResult.exists, success: !nameCheckResult.exists }">
						<text class="check-icon">{{ nameCheckResult.exists ? '❌' : '✅' }}</text>
						<text class="check-text">{{ nameCheckResult.message }}</text>
					</view>
				</view>
				
				<view class="form-group">
					<text class="label">菜谱描述</text>
					<textarea 
						class="textarea" 
						v-model="form.description" 
						placeholder="请简要描述这道菜..." 
						maxlength="200" 
						confirm-type="done"
						adjust-position="true"
						cursor-spacing="10"
						auto-height="true"
					></textarea>
				</view>
				
				<view class="form-group">
					<text class="label">封面图片</text>
					<view class="image-upload" @click="selectCoverImage">
						<image v-if="form.cover_image" class="cover-preview" :src="form.cover_image" mode="aspectFill"></image>
						<view v-else class="upload-placeholder">
							<text class="upload-icon">📷</text>
							<text class="upload-text">点击上传封面</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 分类和属性 -->
			<view class="section">
				<view class="section-title">
					<text class="section-icon">🏷️</text>
					<text class="section-text">分类属性</text>
				</view>
				
				<view class="form-group">
					<text class="label">菜谱分类 *</text>
					<picker :value="categoryIndex" :range="categoryOptions" range-key="label" @change="onCategoryChange">
						<view class="picker">
							<text class="picker-text">{{ categoryOptions[categoryIndex].label }}</text>
							<text class="picker-arrow">▼</text>
						</view>
					</picker>
				</view>
				
				<view class="form-row">
					<view class="form-group half">
						<text class="label">制作时间(分钟) *</text>
						<input 
							class="input" 
							v-model.number="form.cook_time" 
							type="number" 
							placeholder="30"
							confirm-type="next"
							adjust-position="true"
							cursor-spacing="10"
						/>
					</view>
					<view class="form-group half">
						<text class="label">用餐人数 *</text>
						<input 
							class="input" 
							v-model.number="form.servings" 
							type="number" 
							placeholder="2"
							confirm-type="done"
							adjust-position="true"
							cursor-spacing="10"
						/>
					</view>
				</view>
				
				<view class="form-group">
					<text class="label">难度等级 *</text>
					<view class="difficulty-selector">
						<view class="difficulty-item" 
							v-for="level in 5" 
							:key="level"
							:class="{ active: form.difficulty >= level }"
							@click="selectDifficulty(level)"
						>
							<text class="star">⭐</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 食材清单 -->
			<view class="section">
				<view class="section-title">
					<text class="section-icon">🥕</text>
					<text class="section-text">食材清单</text>
					<button class="add-btn" @click="addIngredient">添加食材</button>
				</view>
				
				<view class="ingredients-list">
					<view class="ingredient-item" v-for="(ingredient, index) in form.ingredients" :key="index">
						<input 
							class="ingredient-name" 
							v-model="ingredient.name" 
							placeholder="食材名称"
							confirm-type="next"
							adjust-position="true"
							cursor-spacing="10"
						/>
						<input 
							class="ingredient-amount" 
							v-model="ingredient.amount" 
							placeholder="用量"
							confirm-type="next"
							adjust-position="true"
							cursor-spacing="10"
						/>
						<input 
							class="ingredient-unit" 
							v-model="ingredient.unit" 
							placeholder="单位"
							confirm-type="done"
							adjust-position="true"
							cursor-spacing="10"
						/>
						<button class="remove-btn" @click="removeIngredient(index)">×</button>
					</view>
				</view>
			</view>
			
			<!-- 制作步骤 -->
			<view class="section">
				<view class="section-title">
					<text class="section-icon">📝</text>
					<text class="section-text">制作步骤</text>
					<button class="add-btn" @click="addStep">添加步骤</button>
				</view>
				
				<view class="steps-list">
					<view class="step-item" v-for="(step, index) in form.steps" :key="index">
						<view class="step-header">
							<view class="step-number">{{ index + 1 }}</view>
							<button class="remove-btn" @click="removeStep(index)">×</button>
						</view>
						
						<view class="step-content">
							<!-- 主要描述 -->
							<view class="step-field">
								<text class="step-label">操作步骤 *</text>
								<textarea 
									class="step-textarea" 
									v-model="step.description" 
									:placeholder="`请输入第${index + 1}步详细操作...`"
									confirm-type="done"
									adjust-position="true"
									cursor-spacing="10"
									auto-height="true"
								></textarea>
							</view>
							
							<!-- 可选字段 -->
							<view class="step-optional">
								<view class="step-row">
									<view class="step-field-small">
										<text class="step-label-small">步骤标题</text>
										<input 
											class="step-input" 
											v-model="step.title" 
											placeholder="如：炒制"
											confirm-type="next"
											adjust-position="true"
											cursor-spacing="10"
										/>
									</view>
									<view class="step-field-small">
										<text class="step-label-small">所需时间(分钟)</text>
										<input 
											class="step-input" 
											v-model.number="step.time_required" 
											type="number"
											placeholder="5"
											confirm-type="next"
											adjust-position="true"
											cursor-spacing="10"
										/>
									</view>
								</view>
								
								<view class="step-row">
									<view class="step-field-small">
										<text class="step-label-small">温度设置</text>
										<input 
											class="step-input" 
											v-model="step.temperature" 
											placeholder="如：大火、中火、180°C"
											confirm-type="next"
											adjust-position="true"
											cursor-spacing="10"
										/>
									</view>
								</view>
								
								<view class="step-field">
									<text class="step-label-small">小提示</text>
									<textarea 
										class="step-textarea-small" 
										v-model="step.tips" 
										placeholder="分享一些制作小技巧..."
										confirm-type="done"
										adjust-position="true"
										cursor-spacing="10"
										auto-height="true"
									></textarea>
								</view>
							</view>
							
							<!-- 图片上传 -->
							<view class="step-image-section">
								<text class="step-label-small">步骤图片</text>
								<view class="step-images-container">
									<!-- 已上传的图片 -->
									<view v-if="step.images && step.images.length > 0" class="step-images-list">
										<view v-for="(image, imgIndex) in step.images" :key="imgIndex" class="step-image-item">
											<image class="step-image-preview" :src="image" mode="aspectFill"></image>
											<view class="step-image-remove" @click="removeStepImage(index, imgIndex)">×</view>
										</view>
									</view>
									
									<!-- 上传按钮 -->
									<view v-if="!step.images || step.images.length < 3" class="step-image-upload" @click="selectStepImage(index)">
										<text class="upload-icon">📷</text>
										<text class="upload-text">{{ step.images && step.images.length > 0 ? '添加更多' : '添加图片' }}</text>
									</view>
								</view>
							</view>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 营养信息 -->
			<view class="section">
				<view class="section-title">
					<text class="section-icon">🍎</text>
					<text class="section-text">营养信息(可选)</text>
				</view>
				
				<view class="form-row">
					<view class="form-group quarter">
						<text class="label">卡路里</text>
						<input 
							class="input" 
							v-model.number="form.nutrition.calories" 
							type="number" 
							placeholder="0"
							confirm-type="next"
							adjust-position="true"
							cursor-spacing="10"
						/>
					</view>
					<view class="form-group quarter">
						<text class="label">蛋白质(g)</text>
						<input 
							class="input" 
							v-model.number="form.nutrition.protein" 
							type="number" 
							placeholder="0"
							confirm-type="next"
							adjust-position="true"
							cursor-spacing="10"
						/>
					</view>
					<view class="form-group quarter">
						<text class="label">碳水(g)</text>
						<input 
							class="input" 
							v-model.number="form.nutrition.carbs" 
							type="number" 
							placeholder="0"
							confirm-type="next"
							adjust-position="true"
							cursor-spacing="10"
						/>
					</view>
					<view class="form-group quarter">
						<text class="label">脂肪(g)</text>
						<input 
							class="input" 
							v-model.number="form.nutrition.fat" 
							type="number" 
							placeholder="0"
							confirm-type="done"
							adjust-position="true"
							cursor-spacing="10"
						/>
					</view>
				</view>
			</view>
			
			<!-- 标签 -->
			<view class="section">
				<view class="section-title">
					<text class="section-icon">🏷️</text>
					<text class="section-text">标签</text>
				</view>
				
				<view class="tags-input">
					<input 
						class="tag-input" 
						v-model="newTag" 
						placeholder="输入标签后按回车添加" 
						@confirm="addTag"
						confirm-type="done"
						adjust-position="true"
						cursor-spacing="10"
					/>
				</view>
				
				<view class="tags-list" v-if="form.tags.length > 0">
					<view class="tag" v-for="(tag, index) in form.tags" :key="index">
						<text class="tag-text">{{ tag }}</text>
						<text class="tag-remove" @click="removeTag(index)">×</text>
					</view>
				</view>
			</view>
			
			<!-- 提交按钮 -->
			<view class="submit-section">
				<button class="submit-btn" @click="handleSubmit" :disabled="submitting">
					{{ submitting ? '保存中...' : '保存修改' }}
				</button>
			</view>
		</form>
	</view>
</template>

<script>
import recipeManager from '../../utils/recipeManager.js'

export default {
	data() {
		return {
			recipeId: null,
			loading: true,
			form: {
				name: '',
				description: '',
				cover_image: '',
				category: 'meat',
				cook_time: '',
				servings: '',
				difficulty: 1,
				ingredients: [
					{ name: '', amount: '', unit: '' }
				],
				steps: [
					{ 
						title: '',
						description: '', 
						images: [],
						time_required: '',
						temperature: '',
						tips: ''
					}
				],
				nutrition: {
					calories: '',
					protein: '',
					carbs: '',
					fat: ''
				},
				tags: []
			},
			categoryIndex: 1,
			categoryOptions: [
				{ label: '全部', value: 'all' },
				{ label: '荤菜', value: 'meat' },
				{ label: '素菜', value: 'vegetable' },
				{ label: '汤品', value: 'soup' },
				{ label: '主食', value: 'staple' },
				{ label: '小食', value: 'snack' },
				{ label: '甜品', value: 'dessert' }
			],
			newTag: '',
			submitting: false,
			nameCheckResult: {
				checked: false,
				exists: false,
				message: ''
			},
			originalName: '' // 保存原始名称，用于名称检查
		}
	},
	
	onLoad(options) {
		this.recipeId = options.id
		if (!this.recipeId) {
			uni.showToast({
				title: '菜谱ID无效',
				icon: 'error'
			})
			setTimeout(() => {
				uni.navigateBack()
			}, 1500)
			return
		}
		this.loadRecipeData()
	},
	
	methods: {
		// 加载菜谱数据
		async loadRecipeData() {
			this.loading = true
			
			try {
				const result = await recipeManager.getRecipeDetail(this.recipeId)
				if (result.success) {
					this.fillFormData(result.data)
				} else {
					throw new Error(result.error || '加载失败')
				}
			} catch (error) {
				console.error('加载菜谱数据失败:', error)
				uni.showToast({
					title: '加载失败',
					icon: 'error'
				})
				setTimeout(() => {
					uni.navigateBack()
				}, 2000)
			} finally {
				this.loading = false
			}
		},
		
		// 填充表单数据
		fillFormData(recipe) {
			// 保存原始名称
			this.originalName = recipe.name || ''
			
			this.form = {
				name: recipe.name || '',
				description: recipe.description || '',
				cover_image: recipe.cover_image || '',
				category: recipe.category || 'meat',
				cook_time: recipe.cook_time || '',
				servings: recipe.servings || '',
				difficulty: recipe.difficulty || 1,
				ingredients: recipe.ingredients && recipe.ingredients.length > 0 
					? recipe.ingredients.map(ing => ({
						name: ing.name || '',
						amount: ing.amount || '',
						unit: ing.unit || '',
						category: ing.category || '',
						notes: ing.notes || ''
					}))
					: [{ name: '', amount: '', unit: '', category: '', notes: '' }],
				steps: recipe.steps && recipe.steps.length > 0
					? recipe.steps.map(step => ({
						title: step.title || '',
						description: step.description || '',
						images: step.images || [],
						time_required: step.time_required || '',
						temperature: step.temperature || '',
						tips: step.tips || ''
					}))
					: [{ 
						title: '',
						description: '', 
						images: [],
						time_required: '',
						temperature: '',
						tips: ''
					}],
				nutrition: {
					calories: recipe.nutrition?.calories || '',
					protein: recipe.nutrition?.protein || '',
					carbs: recipe.nutrition?.carbs || '',
					fat: recipe.nutrition?.fat || ''
				},
				tags: recipe.tags || []
			}
			
			// 设置分类索引
			const categoryIndex = this.categoryOptions.findIndex(option => option.value === this.form.category)
			this.categoryIndex = categoryIndex >= 0 ? categoryIndex : 1
		},
		
		// 选择分类
		onCategoryChange(e) {
			this.categoryIndex = e.detail.value
			this.form.category = this.categoryOptions[this.categoryIndex].value
		},
		
		// 选择难度
		selectDifficulty(level) {
			this.form.difficulty = level
		},
		
		// 检查菜谱名称
		async checkRecipeName() {
			if (!this.form.name.trim()) {
				this.nameCheckResult = {
					checked: false,
					exists: false,
					message: ''
				}
				return
			}
			
			// 如果名称没有改变，不需要检查
			if (this.form.name.trim() === this.originalName) {
				this.nameCheckResult = {
					checked: true,
					exists: false,
					message: '名称未修改'
				}
				return
			}
			
			try {
				const result = await recipeManager.checkRecipeName(this.form.name.trim())
				this.nameCheckResult = {
					checked: true,
					exists: result.exists,
					message: result.message
				}
			} catch (error) {
				console.error('检查菜谱名称失败:', error)
				this.nameCheckResult = {
					checked: true,
					exists: false,
					message: '无法检查名称重复性'
				}
			}
		},
		
		// 选择封面图片
		selectCoverImage() {
			uni.chooseImage({
				count: 1,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					this.form.cover_image = res.tempFilePaths[0]
				}
			})
		},
		
		// 选择步骤图片
		selectStepImage(index) {
			uni.chooseImage({
				count: 3, // 支持最多3张图片
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					// 如果已有图片，则追加；否则创建新数组
					if (!this.form.steps[index].images) {
						this.form.steps[index].images = []
					}
					
					// 合并新选择的图片，但限制总数不超过3张
					const currentImages = this.form.steps[index].images
					const newImages = res.tempFilePaths
					const totalImages = [...currentImages, ...newImages].slice(0, 3)
					
					this.form.steps[index].images = totalImages
				}
			})
		},
		
		// 移除步骤图片
		removeStepImage(stepIndex, imageIndex) {
			this.form.steps[stepIndex].images.splice(imageIndex, 1)
		},
		
		// 添加食材
		addIngredient() {
			this.form.ingredients.push({ name: '', amount: '', unit: '' })
		},
		
		// 删除食材
		removeIngredient(index) {
			if (this.form.ingredients.length > 1) {
				this.form.ingredients.splice(index, 1)
			}
		},
		
		// 添加步骤
		addStep() {
			this.form.steps.push({ 
				title: '',
				description: '', 
				images: [],
				time_required: '',
				temperature: '',
				tips: ''
			})
		},
		
		// 删除步骤
		removeStep(index) {
			if (this.form.steps.length > 1) {
				this.form.steps.splice(index, 1)
			}
		},
		
		// 添加标签
		addTag() {
			if (this.newTag.trim() && !this.form.tags.includes(this.newTag.trim())) {
				this.form.tags.push(this.newTag.trim())
				this.newTag = ''
			}
		},
		
		// 删除标签
		removeTag(index) {
			this.form.tags.splice(index, 1)
		},
		
		// 验证表单
		validateForm() {
			// 基本信息验证
			if (!this.form.name.trim()) {
				uni.showToast({ title: '请输入菜谱名称', icon: 'none' })
				return false
			}
			
			// 检查名称重复（如果名称有变化）
			if (this.form.name.trim() !== this.originalName && this.nameCheckResult.checked && this.nameCheckResult.exists) {
				uni.showToast({ title: '菜谱名称已存在，请修改', icon: 'none' })
				return false
			}
			
			if (!this.form.cook_time || this.form.cook_time <= 0) {
				uni.showToast({ title: '请输入正确的制作时间', icon: 'none' })
				return false
			}
			
			if (!this.form.servings || this.form.servings <= 0) {
				uni.showToast({ title: '请输入正确的用餐人数', icon: 'none' })
				return false
			}
			
			// 检查食材
			const validIngredients = this.form.ingredients.filter(ing => ing.name.trim())
			if (validIngredients.length === 0) {
				uni.showToast({ title: '请至少添加一个食材', icon: 'none' })
				return false
			}
			
			// 检查步骤
			const validSteps = this.form.steps.filter(step => step.description.trim())
			if (validSteps.length === 0) {
				uni.showToast({ title: '请至少添加一个制作步骤', icon: 'none' })
				return false
			}
			
			return true
		},
		
		// 提交表单
		async handleSubmit() {
			if (!this.validateForm() || this.submitting) return
			
			this.submitting = true
			
			try {
				// 准备提交的数据，确保与后端结构一致
				const formData = {
					name: this.form.name.trim(),
					description: this.form.description.trim(),
					cover_image: this.form.cover_image,
					category: this.form.category,
					cook_time: parseInt(this.form.cook_time),
					servings: parseInt(this.form.servings),
					difficulty: this.form.difficulty,
					tags: this.form.tags,
					is_public: false, // 默认为私有
					
					// 过滤并规范化食材数据
					ingredients: this.form.ingredients
						.filter(ing => ing.name.trim())
						.map((ing, index) => ({
							name: ing.name.trim(),
							amount: ing.amount.trim(),
							unit: ing.unit.trim(),
							category: ing.category || '',
							notes: ing.notes || '',
							order: index
						})),
					
					// 过滤并规范化步骤数据
					steps: this.form.steps
						.filter(step => step.description.trim())
						.map((step, index) => ({
							step_number: index + 1,
							title: step.title?.trim() || '',
							description: step.description.trim(),
							images: step.images || [],
							time_required: step.time_required ? parseInt(step.time_required) : null,
							temperature: step.temperature?.trim() || '',
							tips: step.tips?.trim() || ''
						}))
				}
				
				const result = await recipeManager.updateRecipe(this.recipeId, formData)
				
				if (result.success) {
					uni.showToast({
						title: '保存成功',
						icon: 'success'
					})
					
					// 延迟返回，确保toast显示完成
					setTimeout(() => {
						// 通过事件总线通知详情页刷新数据
						uni.$emit('recipeUpdated', this.recipeId)
						uni.navigateBack()
					}, 1500)
				} else {
					throw new Error(result.error || '保存失败')
				}
			} catch (error) {
				console.error('更新菜谱失败:', error)
				
				// 根据错误类型显示不同的提示
				let errorMessage = '保存失败'
				if (error.message.includes('名称') && error.message.includes('已存在')) {
					errorMessage = '菜谱名称已存在，请使用不同的名称'
				} else if (error.message.includes('食材')) {
					errorMessage = '请至少添加一个食材'
				} else if (error.message.includes('步骤')) {
					errorMessage = '请至少添加一个制作步骤'
				} else if (error.message.includes('登录')) {
					errorMessage = '请先登录'
				} else {
					errorMessage = error.message || '保存失败，请检查网络连接'
				}
				
				uni.showToast({
					title: errorMessage,
					icon: 'none',
					duration: 3000
				})
			} finally {
				this.submitting = false
			}
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #FFF5F8;
	padding-bottom: 40rpx;
	position: relative;
	overflow-x: hidden;
}

.loading {
	display: flex;
	justify-content: center;
	align-items: center;
	height: 400rpx;
}

.loading-text {
	font-size: 28rpx;
	color: #999999;
}

.section {
	background: #FFFFFF;
	margin: 20rpx 30rpx;
	border-radius: 20rpx;
	padding: 30rpx;
}

.section-title {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 20rpx;
}

.section-icon {
	font-size: 24rpx;
	margin-right: 8rpx;
}

.section-text {
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
	flex: 1;
}

.add-btn {
	background: #FF6B95;
	color: #FFFFFF;
	border: none;
	border-radius: 15rpx;
	padding: 8rpx 16rpx;
	font-size: 24rpx;
}

.form-group {
	margin-bottom: 30rpx;
}

.form-group.half {
	width: 48%;
	display: inline-block;
	margin-right: 4%;
}

.form-group.quarter {
	width: 23%;
	display: inline-block;
	margin-right: 2.5%;
}

.form-group.quarter:last-child {
	margin-right: 0;
}

.form-row {
	display: flex;
	justify-content: space-between;
}

.label {
	display: block;
	font-size: 26rpx;
	color: #333333;
	margin-bottom: 12rpx;
}

.input, .textarea {
	width: 100%;
	padding: 24rpx 20rpx;
	border: 2rpx solid #E0E0E0;
	border-radius: 12rpx;
	font-size: 30rpx;
	background: #FFFFFF;
	box-sizing: border-box;
	color: #333333;
	line-height: 1.5;
	outline: none;
	-webkit-appearance: none;
	appearance: none;
	min-height: 88rpx;
	height: 88rpx;
	display: flex;
	align-items: center;
	transition: border-color 0.3s ease;
}

.input:focus, .textarea:focus {
	border-color: #FF6B95;
	background: #FAFAFA;
}

.textarea {
	height: 140rpx;
	min-height: 140rpx;
	resize: none;
	align-items: flex-start;
	padding-top: 24rpx;
	line-height: 1.6;
}

.image-upload {
	width: 200rpx;
	height: 200rpx;
	border: 2rpx dashed #E0E0E0;
	border-radius: 15rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
}

.cover-preview {
	width: 100%;
	height: 100%;
}

.upload-placeholder {
	text-align: center;
}

.upload-icon {
	display: block;
	font-size: 40rpx;
	margin-bottom: 8rpx;
	color: #999999;
}

.upload-text {
	font-size: 22rpx;
	color: #999999;
}

.picker {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20rpx;
	border: 1rpx solid #E0E0E0;
	border-radius: 10rpx;
	background: #FFFFFF;
}

.picker-text {
	font-size: 28rpx;
	color: #333333;
}

.picker-arrow {
	font-size: 20rpx;
	color: #999999;
}

.difficulty-selector {
	display: flex;
	gap: 10rpx;
}

.difficulty-item {
	padding: 10rpx;
	border-radius: 8rpx;
	cursor: pointer;
	transition: all 0.3s ease;
}

.difficulty-item:hover {
	background-color: rgba(255, 107, 149, 0.1);
}

.difficulty-item.active .star {
	color: #FFD700;
	transform: scale(1.1);
}

.star {
	font-size: 32rpx;
	color: #E0E0E0;
	transition: all 0.3s ease;
}

.ingredients-list, .steps-list {
	margin-top: 20rpx;
}

.ingredient-item {
	display: flex;
	gap: 16rpx;
	margin-bottom: 20rpx;
	align-items: center;
	background: #F8F9FA;
	padding: 20rpx;
	border-radius: 12rpx;
	border: 1rpx solid #E9ECEF;
}

.ingredient-name {
	flex: 2.5;
	padding: 20rpx 16rpx;
	border: 2rpx solid #E0E0E0;
	border-radius: 10rpx;
	font-size: 28rpx;
	box-sizing: border-box;
	background: #FFFFFF;
	color: #333333;
	min-height: 76rpx;
	line-height: 1.4;
	transition: border-color 0.3s ease;
}

.ingredient-name:focus {
	border-color: #FF6B95;
	background: #FAFAFA;
}

.ingredient-amount {
	flex: 1.2;
	padding: 20rpx 16rpx;
	border: 2rpx solid #E0E0E0;
	border-radius: 10rpx;
	font-size: 28rpx;
	box-sizing: border-box;
	background: #FFFFFF;
	color: #333333;
	min-height: 76rpx;
	line-height: 1.4;
	transition: border-color 0.3s ease;
}

.ingredient-amount:focus {
	border-color: #FF6B95;
	background: #FAFAFA;
}

.ingredient-unit {
	flex: 1;
	padding: 20rpx 16rpx;
	border: 2rpx solid #E0E0E0;
	border-radius: 10rpx;
	font-size: 28rpx;
	box-sizing: border-box;
	background: #FFFFFF;
	color: #333333;
	min-height: 76rpx;
	line-height: 1.4;
	transition: border-color 0.3s ease;
}

.ingredient-unit:focus {
	border-color: #FF6B95;
	background: #FAFAFA;
}

.remove-btn {
	width: 56rpx;
	height: 56rpx;
	background: linear-gradient(135deg, #FF4757, #FF6B7A);
	color: #FFFFFF;
	border: none;
	border-radius: 50%;
	font-size: 24rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 2rpx 8rpx rgba(255, 71, 87, 0.3);
	transition: all 0.3s ease;
}

.remove-btn:active {
	transform: scale(0.95);
	box-shadow: 0 1rpx 4rpx rgba(255, 71, 87, 0.4);
}

.step-item {
	background: #FFFFFF;
	border: 2rpx solid #F0F2F5;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 20rpx;
	position: relative;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
	transition: all 0.3s ease;
}

.step-item:hover {
	border-color: #FF6B95;
	box-shadow: 0 4rpx 16rpx rgba(255, 107, 149, 0.15);
}

.step-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.step-number {
	width: 56rpx;
	height: 56rpx;
	background: linear-gradient(135deg, #FF6B95, #FF8FA3);
	color: #FFFFFF;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24rpx;
	font-weight: bold;
	flex-shrink: 0;
	box-shadow: 0 2rpx 8rpx rgba(255, 107, 149, 0.3);
}

.step-content {
	width: 100%;
}

.step-field {
	margin-bottom: 16rpx;
}

.step-label {
	font-size: 26rpx;
	color: #333333;
	margin-bottom: 10rpx;
	display: block;
	font-weight: 500;
}

.step-label-small {
	font-size: 24rpx;
	color: #666666;
	margin-bottom: 8rpx;
	display: block;
	font-weight: 400;
}

.step-textarea {
	width: 100%;
	min-height: 120rpx;
	padding: 16rpx 20rpx;
	border: 2rpx solid #E9ECEF;
	border-radius: 12rpx;
	font-size: 28rpx;
	background: #FFFFFF;
	color: #333333;
	line-height: 1.6;
	resize: none;
	box-sizing: border-box;
	transition: all 0.3s ease;
}

.step-textarea:focus {
	border-color: #FF6B95;
	background: #FAFAFA;
	outline: none;
}

.step-textarea-small {
	width: 100%;
	min-height: 80rpx;
	padding: 12rpx 16rpx;
	border: 2rpx solid #E9ECEF;
	border-radius: 10rpx;
	font-size: 26rpx;
	background: #FFFFFF;
	color: #333333;
	line-height: 1.5;
	resize: none;
	box-sizing: border-box;
	transition: all 0.3s ease;
}

.step-textarea-small:focus {
	border-color: #FF6B95;
	background: #FAFAFA;
	outline: none;
}

.step-optional {
	background: linear-gradient(135deg, #F8F9FA, #F1F3F4);
	padding: 20rpx;
	border-radius: 12rpx;
	margin: 16rpx 0;
	border: 1rpx solid #E9ECEF;
	position: relative;
}

.step-optional::before {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	width: 4rpx;
	height: 100%;
	background: linear-gradient(180deg, #FF6B95, #FF8FA3);
	border-radius: 2rpx 0 0 2rpx;
}

.step-row {
	display: flex;
	gap: 16rpx;
	margin-bottom: 12rpx;
}

.step-row:last-child {
	margin-bottom: 0;
}

.step-field-small {
	flex: 1;
}

.step-input {
	width: 100%;
	padding: 12rpx 16rpx;
	border: 2rpx solid #E0E0E0;
	border-radius: 8rpx;
	font-size: 26rpx;
	background: #FFFFFF;
	color: #333333;
	box-sizing: border-box;
	transition: all 0.3s ease;
	line-height: 1.4;
}

.step-input:focus {
	border-color: #FF6B95;
	background: #FAFAFA;
	outline: none;
}

.step-image-section {
	margin-top: 20rpx;
	padding-top: 16rpx;
	border-top: 1rpx solid #F0F2F5;
}

.step-images-container {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.step-images-list {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
}

.step-image-item {
	position: relative;
	width: 140rpx;
	height: 140rpx;
	border-radius: 12rpx;
	overflow: hidden;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.step-image-preview {
	width: 100%;
	height: 100%;
	border-radius: 12rpx;
	object-fit: cover;
}

.step-image-remove {
	position: absolute;
	top: -6rpx;
	right: -6rpx;
	width: 28rpx;
	height: 28rpx;
	background: linear-gradient(135deg, #FF4757, #FF6B7A);
	color: #FFFFFF;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 18rpx;
	font-weight: bold;
	box-shadow: 0 2rpx 6rpx rgba(255, 71, 87, 0.4);
	border: 2rpx solid #FFFFFF;
}

.step-image-upload {
	width: 140rpx;
	height: 140rpx;
	border: 2rpx dashed #D1D5DB;
	border-radius: 12rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	background: linear-gradient(135deg, #FAFBFC, #F3F4F6);
	transition: all 0.3s ease;
}

.step-image-upload:active {
	background: linear-gradient(135deg, #F1F3F4, #E5E7EB);
	border-color: #FF6B95;
}

.step-image-upload .upload-icon {
	font-size: 36rpx;
	color: #9CA3AF;
	margin-bottom: 6rpx;
	transition: color 0.3s ease;
}

.step-image-upload:active .upload-icon {
	color: #FF6B95;
}

.step-image-upload .upload-text {
	font-size: 22rpx;
	color: #6B7280;
	text-align: center;
	line-height: 1.3;
	font-weight: 400;
}

.step-image-upload:active .upload-text {
	color: #FF6B95;
}

/* 提交按钮样式优化 */
.submit-section {
	padding: 30rpx;
	background: transparent;
}

.submit-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #FF6B95, #FF8FA3);
	color: #FFFFFF;
	border: none;
	border-radius: 44rpx;
	font-size: 32rpx;
	font-weight: 600;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 4rpx 16rpx rgba(255, 107, 149, 0.4);
	transition: all 0.3s ease;
}

.submit-btn:disabled {
	background: linear-gradient(135deg, #D1D5DB, #9CA3AF);
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
	color: #6B7280;
}

.submit-btn:active:not(:disabled) {
	transform: translateY(2rpx);
	box-shadow: 0 2rpx 8rpx rgba(255, 107, 149, 0.3);
}

/* 标签相关样式 */
.tags-input {
	margin-bottom: 20rpx;
}

.tag-input {
	width: 100%;
	padding: 24rpx 20rpx;
	border: 2rpx solid #E0E0E0;
	border-radius: 12rpx;
	font-size: 14rpx;
	background: #FFFFFF;
	box-sizing: border-box;
	transition: border-color 0.3s ease;
}

.tag-input:focus {
	border-color: #FF6B95;
	background: #FAFAFA;
	outline: none;
}

.tags-list {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
	margin-top: 16rpx;
}

.tag {
	display: flex;
	align-items: center;
	background: linear-gradient(135deg, #FF6B95, #FF8FA3);
	color: #FFFFFF;
	padding: 8rpx 16rpx;
	border-radius: 20rpx;
	font-size: 24rpx;
	box-shadow: 0 2rpx 6rpx rgba(255, 107, 149, 0.3);
}

.tag-text {
	margin-right: 8rpx;
}

.tag-remove {
	width: 20rpx;
	height: 20rpx;
	background: rgba(255, 255, 255, 0.3);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 16rpx;
	font-weight: bold;
	cursor: pointer;
}

.tag-remove:active {
	background: rgba(255, 255, 255, 0.5);
}

/* 名称检查结果样式 */
.name-check-result {
	display: flex;
	align-items: center;
	margin-top: 8rpx;
	padding: 8rpx 12rpx;
	border-radius: 6rpx;
	font-size: 24rpx;
}

.name-check-result.success {
	background: #E8F5E8;
	color: #2E8B2E;
}

.name-check-result.error {
	background: #FFE8E8;
	color: #D32F2F;
}

.check-icon {
	margin-right: 6rpx;
	font-size: 20rpx;
}

.check-text {
	flex: 1;
}
</style>
