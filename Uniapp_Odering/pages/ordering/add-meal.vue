<template>
	<view class="container">
		<form @submit="submitForm">
			<!-- 餐品图片 -->
			<view class="form-section">
				<text class="section-title">餐品图片</text>
				<view class="image-upload">
					<view class="image-list">
						<view v-for="(image, index) in mealForm.images" :key="index" class="image-item">
							<image :src="image" mode="aspectFill" class="uploaded-image"></image>
							<view class="image-remove" @click="removeImage(index)">×</view>
						</view>
						<view class="image-add" @click="chooseImage" v-if="mealForm.images.length < 5">
							<text class="add-icon">+</text>
							<text class="add-text">添加图片</text>
						</view>
					</view>
					<text class="image-tip">最多上传5张图片，建议尺寸 1:1</text>
				</view>
			</view>

			<!-- 基本信息 -->
			<view class="form-section">
				<text class="section-title">基本信息</text>
				
				<view class="form-item">
					<text class="form-label">餐品名称 *</text>
					<input 
						v-model="mealForm.name" 
						class="form-input" 
						placeholder="请输入餐品名称"
						maxlength="50"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">餐品分类 *</text>
					<picker :value="categoryIndex" :range="categoryList" range-key="name" @change="onCategoryChange">
						<view class="picker-view">
							<text class="picker-text" :class="{ placeholder: !mealForm.category }">
								{{ mealForm.category_name || '请选择餐品分类' }}
							</text>
							<text class="picker-arrow">▼</text>
						</view>
					</picker>
				</view>
				
				<view class="form-item">
					<text class="form-label">餐品描述</text>
					<textarea 
						v-model="mealForm.description" 
						class="form-textarea" 
						placeholder="请描述餐品的特色、口味等..."
						maxlength="200"
					></textarea>
				</view>
				
				<view class="form-item">
					<text class="form-label">参考价格</text>
					<input 
						v-model="mealForm.price" 
						class="form-input" 
						placeholder="0.00"
						type="digit"
					/>
				</view>
			</view>

			<!-- 营养信息 -->
			<view class="form-section">
				<view class="section-header">
					<text class="section-title">营养信息</text>
					<switch :checked="showNutrition" @change="toggleNutrition" color="#FF6B95"></switch>
				</view>
				
				<view v-if="showNutrition" class="nutrition-form">
					<view class="nutrition-grid">
						<view class="nutrition-item">
							<text class="nutrition-label">热量 (kcal)</text>
							<input v-model="nutritionForm.calories" type="number" class="nutrition-input" placeholder="0" />
						</view>
						<view class="nutrition-item">
							<text class="nutrition-label">蛋白质 (g)</text>
							<input v-model="nutritionForm.protein" type="digit" class="nutrition-input" placeholder="0" />
						</view>
						<view class="nutrition-item">
							<text class="nutrition-label">碳水 (g)</text>
							<input v-model="nutritionForm.carbs" type="digit" class="nutrition-input" placeholder="0" />
						</view>
						<view class="nutrition-item">
							<text class="nutrition-label">脂肪 (g)</text>
							<input v-model="nutritionForm.fat" type="digit" class="nutrition-input" placeholder="0" />
						</view>
						<view class="nutrition-item">
							<text class="nutrition-label">纤维 (g)</text>
							<input v-model="nutritionForm.fiber" type="digit" class="nutrition-input" placeholder="0" />
						</view>
						<view class="nutrition-item">
							<text class="nutrition-label">钠 (mg)</text>
							<input v-model="nutritionForm.sodium" type="number" class="nutrition-input" placeholder="0" />
						</view>
					</view>
				</view>
			</view>

			<!-- 标签 -->
			<view class="form-section">
				<text class="section-title">餐品标签</text>
				<view class="tags-input">
					<view class="current-tags">
						<view v-for="(tag, index) in mealForm.tags" :key="index" class="tag-item">
							<text class="tag-text"># {{ tag }}</text>
							<text class="tag-remove" @click="removeTag(index)">×</text>
						</view>
					</view>
					<view class="add-tag">
						<input 
							v-model="newTag" 
							class="tag-input" 
							placeholder="添加标签后按回车" 
							maxlength="10"
							@confirm="addTag"
						/>
					</view>
				</view>
				<view class="popular-tags">
					<text class="popular-title">常用标签:</text>
					<view class="popular-list">
						<text 
							v-for="tag in popularTags" 
							:key="tag" 
							class="popular-tag"
							:class="{ selected: mealForm.tags.includes(tag) }"
							@click="togglePopularTag(tag)"
						>
							{{ tag }}
						</text>
					</view>
				</view>
			</view>

			<!-- 可用性设置 -->
			<view class="form-section">
				<text class="section-title">设置</text>
				
				<view class="form-item">
					<text class="form-label">是否可用</text>
					<switch :checked="mealForm.is_available" @change="onAvailableChange" color="#FF6B95"></switch>
				</view>
				
				<view class="form-item">
					<text class="form-label">每日限量</text>
					<view class="limit-input">
						<switch :checked="hasLimit" @change="toggleLimit" color="#FF6B95"></switch>
						<input 
							v-if="hasLimit"
							v-model="mealForm.daily_limit" 
							type="number" 
							class="form-input limit-number" 
							placeholder="份数"
						/>
					</view>
				</view>
			</view>

			<!-- 底部按钮 -->
			<view class="form-actions">
				<button v-if="isEdit" class="delete-btn" @click="deleteMeal" type="button">删除餐品</button>
				<button class="save-btn" :loading="saving" form-type="submit">
					{{ isEdit ? '保存修改' : '添加餐品' }}
				</button>
			</view>
		</form>
	</view>
</template>

<script>
import orderingManager from '@/utils/orderingManager.js'

export default {
	data() {
		return {
			isEdit: false,
			mealId: null,
			saving: false,
			showNutrition: false,
			hasLimit: false,
			newTag: '',
			categoryIndex: 0,
			categoryList: [],
			popularTags: ['辣', '清淡', '下饭', '汤品', '素食', '荤菜', '凉菜', '热菜', '主食', '甜品'],
			mealForm: {
				name: '',
				category: '',
				category_name: '',
				description: '',
				price: '',
				images: [],
				tags: [],
				is_available: true,
				daily_limit: null
			},
			nutritionForm: {
				calories: '',
				protein: '',
				carbs: '',
				fat: '',
				fiber: '',
				sodium: ''
			}
		}
	},
	
	onLoad(options) {
		if (options.id) {
			this.isEdit = true
			this.mealId = options.id
			this.loadMealData()
		}
		this.loadCategories()
	},
	
	methods: {
		async loadCategories() {
			try {
				const response = await orderingManager.getMealCategories()
				this.categoryList = response.results || []
			} catch (error) {
				console.error('加载分类失败:', error)
			}
		},
		
		async loadMealData() {
			try {
				uni.showLoading({ title: '加载中...' })
				const meal = await orderingManager.getMealItem(this.mealId)
				
				this.mealForm = {
					name: meal.name || '',
					category: meal.category || '',
					category_name: meal.category_name || '',
					description: meal.description || '',
					price: meal.price ? meal.price.toString() : '',
					images: meal.images || [meal.image].filter(Boolean),
					tags: meal.tags || [],
					is_available: meal.is_available !== false,
					daily_limit: meal.daily_limit
				}
				
				// 设置分类索引
				this.categoryIndex = this.categoryList.findIndex(cat => cat.id === meal.category)
				if (this.categoryIndex === -1) this.categoryIndex = 0
				
				// 加载营养信息
				if (meal.nutritional_info) {
					try {
						this.nutritionForm = JSON.parse(meal.nutritional_info)
						this.showNutrition = true
					} catch (error) {
						console.error('解析营养信息失败:', error)
					}
				}
				
				// 检查是否有每日限量
				this.hasLimit = !!meal.daily_limit
			} catch (error) {
				console.error('加载餐品数据失败:', error)
				uni.showToast({
					title: '加载失败',
					icon: 'none'
				})
			} finally {
				uni.hideLoading()
			}
		},
		
		chooseImage() {
			const maxCount = 5 - this.mealForm.images.length
			uni.chooseImage({
				count: maxCount,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					this.uploadImages(res.tempFilePaths)
				}
			})
		},
		
		async uploadImages(imagePaths) {
			try {
				uni.showLoading({ title: '上传中...' })
				
				for (const imagePath of imagePaths) {
					// 这里应该调用实际的图片上传API
					// const uploadedUrl = await orderingManager.uploadImage(imagePath)
					// this.mealForm.images.push(uploadedUrl)
					
					// 临时使用本地路径
					this.mealForm.images.push(imagePath)
				}
			} catch (error) {
				console.error('上传图片失败:', error)
				uni.showToast({
					title: '上传失败',
					icon: 'none'
				})
			} finally {
				uni.hideLoading()
			}
		},
		
		removeImage(index) {
			this.mealForm.images.splice(index, 1)
		},
		
		onCategoryChange(e) {
			this.categoryIndex = e.detail.value
			const category = this.categoryList[this.categoryIndex]
			if (category) {
				this.mealForm.category = category.id
				this.mealForm.category_name = category.name
			}
		},
		
		toggleNutrition(e) {
			this.showNutrition = e.detail.value
		},
		
		onAvailableChange(e) {
			this.mealForm.is_available = e.detail.value
		},
		
		toggleLimit(e) {
			this.hasLimit = e.detail.value
			if (!this.hasLimit) {
				this.mealForm.daily_limit = null
			}
		},
		
		addTag() {
			const tag = this.newTag.trim()
			if (tag && !this.mealForm.tags.includes(tag)) {
				this.mealForm.tags.push(tag)
				this.newTag = ''
			}
		},
		
		removeTag(index) {
			this.mealForm.tags.splice(index, 1)
		},
		
		togglePopularTag(tag) {
			const index = this.mealForm.tags.indexOf(tag)
			if (index > -1) {
				this.mealForm.tags.splice(index, 1)
			} else {
				this.mealForm.tags.push(tag)
			}
		},
		
		validateForm() {
			if (!this.mealForm.name.trim()) {
				uni.showToast({
					title: '请输入餐品名称',
					icon: 'none'
				})
				return false
			}
			
			if (!this.mealForm.category) {
				uni.showToast({
					title: '请选择餐品分类',
					icon: 'none'
				})
				return false
			}
			
			if (this.mealForm.images.length === 0) {
				uni.showToast({
					title: '请至少上传一张图片',
					icon: 'none'
				})
				return false
			}
			
			return true
		},
		
		async submitForm() {
			if (!this.validateForm()) return
			
			try {
				this.saving = true
				
				const formData = {
					...this.mealForm,
					price: this.mealForm.price ? parseFloat(this.mealForm.price) : null,
					daily_limit: this.hasLimit ? parseInt(this.mealForm.daily_limit) : null,
					image: this.mealForm.images[0] // 主图片
				}
				
				// 添加营养信息
				if (this.showNutrition) {
					const nutritionData = {}
					Object.keys(this.nutritionForm).forEach(key => {
						const value = this.nutritionForm[key]
						if (value !== '' && value !== null) {
							nutritionData[key] = parseFloat(value) || 0
						}
					})
					formData.nutritional_info = JSON.stringify(nutritionData)
				}
				
				if (this.isEdit) {
					await orderingManager.updateMealItem(this.mealId, formData)
					uni.showToast({
						title: '保存成功',
						icon: 'success'
					})
				} else {
					await orderingManager.createMealItem(formData)
					uni.showToast({
						title: '添加成功',
						icon: 'success'
					})
				}
				
				setTimeout(() => {
					uni.navigateBack()
				}, 1500)
			} catch (error) {
				console.error('保存失败:', error)
				uni.showToast({
					title: '保存失败',
					icon: 'none'
				})
			} finally {
				this.saving = false
			}
		},
		
		async deleteMeal() {
			try {
				const res = await uni.showModal({
					title: '确认删除',
					content: '删除后无法恢复，确定要删除这个餐品吗？',
					showCancel: true,
					confirmColor: '#f44336'
				})
				
				if (!res.confirm) return
				
				uni.showLoading({ title: '删除中...' })
				await orderingManager.deleteMealItem(this.mealId)
				
				uni.showToast({
					title: '删除成功',
					icon: 'success'
				})
				
				setTimeout(() => {
					uni.navigateBack()
				}, 1500)
			} catch (error) {
				console.error('删除失败:', error)
				uni.showToast({
					title: '删除失败',
					icon: 'none'
				})
			} finally {
				uni.hideLoading()
			}
		}
	}
}
</script>

<style scoped>
.container {
	background-color: #f5f5f5;
	min-height: 100vh;
	padding-bottom: 100rpx;
}

/* 表单区块 */
.form-section {
	background: white;
	margin-bottom: 20rpx;
	padding: 30rpx;
}

.section-title {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 30rpx;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
}

/* 图片上传 */
.image-upload {
	width: 100%;
}

.image-list {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20rpx;
	margin-bottom: 20rpx;
}

.image-item {
	position: relative;
	aspect-ratio: 1;
}

.uploaded-image {
	width: 100%;
	height: 100%;
	border-radius: 15rpx;
}

.image-remove {
	position: absolute;
	top: -10rpx;
	right: -10rpx;
	width: 40rpx;
	height: 40rpx;
	background: #f44336;
	color: white;
	border-radius: 50%;
	text-align: center;
	line-height: 40rpx;
	font-size: 24rpx;
	font-weight: bold;
}

.image-add {
	aspect-ratio: 1;
	border: 2rpx dashed #ddd;
	border-radius: 15rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	background: #f8f8f8;
}

.add-icon {
	font-size: 48rpx;
	color: #999;
	margin-bottom: 10rpx;
}

.add-text {
	font-size: 24rpx;
	color: #999;
}

.image-tip {
	font-size: 24rpx;
	color: #666;
	text-align: center;
}

/* 表单项 */
.form-item {
	margin-bottom: 30rpx;
}

.form-label {
	display: block;
	font-size: 28rpx;
	color: #333;
	margin-bottom: 15rpx;
}

.form-input, .form-textarea {
	width: 100%;
	padding: 25rpx;
	border: 2rpx solid #eee;
	border-radius: 15rpx;
	font-size: 28rpx;
	background: #f8f8f8;
}

.form-textarea {
	min-height: 150rpx;
	resize: none;
}

.picker-view {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 25rpx;
	border: 2rpx solid #eee;
	border-radius: 15rpx;
	background: #f8f8f8;
}

.picker-text {
	font-size: 28rpx;
	color: #333;
}

.picker-text.placeholder {
	color: #999;
}

.picker-arrow {
	font-size: 20rpx;
	color: #666;
}

.limit-input {
	display: flex;
	align-items: center;
	gap: 30rpx;
}

.limit-number {
	flex: 1;
	max-width: 200rpx;
}

/* 营养信息表单 */
.nutrition-form {
	margin-top: 30rpx;
}

.nutrition-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 30rpx;
}

.nutrition-item {
	display: flex;
	flex-direction: column;
	gap: 15rpx;
}

.nutrition-label {
	font-size: 24rpx;
	color: #666;
}

.nutrition-input {
	padding: 20rpx;
	border: 2rpx solid #eee;
	border-radius: 10rpx;
	font-size: 28rpx;
	background: #f8f8f8;
}

/* 标签输入 */
.tags-input {
	margin-bottom: 20rpx;
}

.current-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
	margin-bottom: 20rpx;
}

.tag-item {
	display: flex;
	align-items: center;
	background: #fff5f8;
	border: 2rpx solid #FF6B95;
	border-radius: 25rpx;
	padding: 10rpx 20rpx;
	gap: 10rpx;
}

.tag-text {
	font-size: 24rpx;
	color: #FF6B95;
}

.tag-remove {
	font-size: 24rpx;
	color: #FF6B95;
	font-weight: bold;
}

.add-tag {
	margin-bottom: 20rpx;
}

.tag-input {
	width: 100%;
	padding: 20rpx;
	border: 2rpx solid #eee;
	border-radius: 25rpx;
	font-size: 28rpx;
	background: #f8f8f8;
}

.popular-tags {
	margin-top: 30rpx;
}

.popular-title {
	font-size: 28rpx;
	color: #666;
	margin-bottom: 20rpx;
	display: block;
}

.popular-list {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
}

.popular-tag {
	font-size: 24rpx;
	color: #666;
	background: #f0f0f0;
	border: 2rpx solid transparent;
	border-radius: 25rpx;
	padding: 10rpx 20rpx;
}

.popular-tag.selected {
	color: #FF6B95;
	background: #fff5f8;
	border-color: #FF6B95;
}

/* 底部按钮 */
.form-actions {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background: white;
	padding: 20rpx 30rpx;
	border-top: 1rpx solid #eee;
	display: flex;
	gap: 20rpx;
	box-shadow: 0 -2rpx 20rpx rgba(0,0,0,0.1);
}

.delete-btn {
	flex: 1;
	background: #f44336;
	color: white;
	border-radius: 40rpx;
	padding: 25rpx;
	border: none;
	font-size: 28rpx;
	font-weight: bold;
}

.save-btn {
	flex: 2;
	background: linear-gradient(45deg, #FF6B95, #FF8C94);
	color: white;
	border-radius: 40rpx;
	padding: 25rpx;
	border: none;
	font-size: 32rpx;
	font-weight: bold;
}
</style>
