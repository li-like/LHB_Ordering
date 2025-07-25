<template>
	<view class="container">
		<!-- 表单内容 -->
		<scroll-view class="form-scroll" scroll-y="true">
			<!-- 菜品图片上传 -->
			<view class="form-section">
				<view class="section-title">
					<text class="title-text">菜品图片</text>
					<text class="required">*</text>
				</view>
				<view class="image-upload-area" @click="selectImage">
					<image 
						v-if="formData.image" 
						class="uploaded-image" 
						:src="formData.image" 
						mode="aspectFill"
					></image>
					<view v-else class="upload-placeholder">
						<view class="upload-icon">📷</view>
						<text class="upload-text">点击上传菜品图片</text>
					</view>
				</view>
			</view>
			
			<!-- 菜品名称 -->
			<view class="form-section">
				<view class="section-title">
					<text class="title-text">菜品名称</text>
					<text class="required">*</text>
				</view>
				<input 
					class="form-input"
					v-model="formData.name"
					placeholder="请输入菜品名称"
					@blur="checkNameUnique"
				/>
				<view v-if="nameError" class="error-text">{{ nameError }}</view>
			</view>
			
			<!-- 菜品简介 -->
			<view class="form-section">
				<view class="section-title">
					<text class="title-text">菜品简介</text>
				</view>
				<textarea 
					class="form-textarea"
					v-model="formData.description"
					placeholder="请输入菜品简介（可选）"
					maxlength="200"
				></textarea>
			</view>
			
			<!-- 详细介绍 -->
			<view class="form-section">
				<view class="section-title">
					<text class="title-text">详细介绍</text>
				</view>
				<textarea 
					class="form-textarea large"
					v-model="formData.detailedDescription"
					placeholder="请输入详细介绍（可选）"
					maxlength="500"
				></textarea>
			</view>
			
			<!-- 标签管理 -->
			<view class="form-section">
				<view class="section-title">
					<text class="title-text">特色标签</text>
				</view>
				<view class="tags-container">
					<!-- 已选标签 -->
					<view class="selected-tags" v-if="formData.tags.length > 0">
						<view 
							class="tag-item selected" 
							v-for="(tag, index) in formData.tags" 
							:key="index"
							@click="removeTag(index)"
						>
							{{ tag }}
							<text class="remove-icon">×</text>
						</view>
					</view>
					
					<!-- 预设标签 -->
					<view class="preset-tags">
						<view 
							class="tag-item preset" 
							v-for="tag in availableTags" 
							:key="tag"
							@click="addTag(tag)"
							:class="{ disabled: formData.tags.includes(tag) }"
						>
							{{ tag }}
						</view>
					</view>
					
					<!-- 自定义标签输入 -->
					<view class="custom-tag-input">
						<input 
							class="tag-input"
							v-model="customTag"
							placeholder="自定义标签"
							@confirm="addCustomTag"
						/>
						<view class="add-tag-btn" @click="addCustomTag">
							<text class="add-icon">+</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 制作时间 -->
			<view class="form-section">
				<view class="section-title">
					<text class="title-text">制作时间</text>
				</view>
				<view class="time-selector">
					<slider 
						class="time-slider"
						:value="formData.cookTime"
						:min="5"
						:max="120"
						:step="5"
						@change="onTimeChange"
						activeColor="#FF6B95"
					/>
					<text class="time-display">{{ formData.cookTime }}分钟</text>
				</view>
			</view>
			
			<!-- 难度等级 -->
			<view class="form-section">
				<view class="section-title">
					<text class="title-text">难度等级</text>
				</view>
				<view class="difficulty-selector">
					<view 
						class="difficulty-item" 
						v-for="level in difficultyLevels" 
						:key="level.value"
						@click="selectDifficulty(level.value)"
						:class="{ active: formData.difficulty === level.value }"
					>
						<view class="difficulty-icon">{{ level.icon }}</view>
						<text class="difficulty-text">{{ level.label }}</text>
					</view>
				</view>
			</view>
			
			<!-- 营养信息（可选） -->
			<view class="form-section">
				<view class="section-title">
					<text class="title-text">营养信息</text>
					<text class="optional">（可选）</text>
				</view>
				<view class="nutrition-inputs">
					<view class="nutrition-item">
						<text class="nutrition-label">热量</text>
						<input 
							class="nutrition-input"
							v-model="formData.nutrition.calories"
							placeholder="千卡"
							type="number"
						/>
					</view>
					<view class="nutrition-item">
						<text class="nutrition-label">蛋白质</text>
						<input 
							class="nutrition-input"
							v-model="formData.nutrition.protein"
							placeholder="克"
						/>
					</view>
					<view class="nutrition-item">
						<text class="nutrition-label">脂肪</text>
						<input 
							class="nutrition-input"
							v-model="formData.nutrition.fat"
							placeholder="克"
						/>
					</view>
					<view class="nutrition-item">
						<text class="nutrition-label">碳水</text>
						<input 
							class="nutrition-input"
							v-model="formData.nutrition.carbs"
							placeholder="克"
						/>
					</view>
				</view>
			</view>
		</scroll-view>
		
		<!-- 底部操作栏 -->
		<view class="action-bar">
			<view class="action-btn secondary" @click="goBack">
				<text class="action-text">取消</text>
			</view>
			<view class="action-btn primary" @click="saveFoodItem">
				<text class="action-text">{{ isEditMode ? '保存' : '添加' }}</text>
			</view>
		</view>
	</view>
</template>

<script>
import orderingManager from '../../utils/orderingManager.js'

export default {
	data() {
		return {
			isEditMode: false,
			categoryId: null,
			editingId: null,
			nameError: '',
			customTag: '',
			formData: {
				name: '',
				description: '',
				detailedDescription: '',
				image: '',
				tags: [],
				cookTime: 30,
				difficulty: 1,
				nutrition: {
					calories: '',
					protein: '',
					fat: '',
					carbs: ''
				}
			},
			availableTags: [
				'经典', '家常', '下饭', '清淡', '营养', '快手',
				'健康', '酸甜', '麻辣', '蒜香', '香甜', '滋补',
				'开胃', '节日', '传统', '创新', '精致', '简单'
			],
			difficultyLevels: [
				{ value: 1, label: '简单', icon: '😊' },
				{ value: 2, label: '中等', icon: '🤔' },
				{ value: 3, label: '困难', icon: '😰' }
			],
			existingNames: [] // 用于检查名称唯一性
		}
	},
	
	onLoad(options) {
		this.categoryId = options.categoryId;
		this.isEditMode = options.mode === 'edit';
		this.editingId = options.id;
		
		if (this.isEditMode && options.id) {
			this.loadFoodData(options.id);
		}
		
		// 设置页面标题
		uni.setNavigationBarTitle({
			title: this.isEditMode ? '编辑菜品' : '添加菜品'
		});
		
		// 模拟获取已存在的菜品名称
		this.loadExistingNames();
	},
	
	methods: {
		// 加载要编辑的菜品数据
		async loadFoodData(id) {
			try {
				uni.showLoading({
					title: '加载中...'
				});
				
				// 从后端获取菜品信息
				const mealData = await orderingManager.getMealDetail(id);
				
				// 填充表单数据，从后端数据映射到前端格式
				this.formData = {
					id: mealData.id,
					name: mealData.name || '',
					description: mealData.description || '',
					detailedDescription: mealData.detailed_description || '',
					image: mealData.image || '',
					tags: mealData.tags || [],
					cookTime: mealData.prep_time || 30,
					difficulty: this.mapDifficultyToNumber(mealData.difficulty),
					nutrition: this.parseNutritionInfo(mealData.nutrition_info)
				};
				
				// 保存原始名称用于重复性检查
				this.originalName = this.formData.name;
				
				uni.hideLoading();
			} catch (error) {
				console.error('加载菜品数据失败:', error);
				uni.hideLoading();
				uni.showToast({
					title: '加载失败',
					icon: 'error'
				});
			}
		},
		
		// 将后端difficulty字符串映射为前端数字
		mapDifficultyToNumber(difficulty) {
			const difficultyMap = {
				'easy': 1,
				'medium': 2,
				'hard': 3
			};
			return difficultyMap[difficulty] || 2;
		},
		
		// 解析营养信息JSON字符串
		parseNutritionInfo(nutritionStr) {
			try {
				if (nutritionStr) {
					return JSON.parse(nutritionStr);
				}
			} catch (error) {
				console.error('解析营养信息失败:', error);
			}
			return {
				calories: '',
				protein: '',
				fat: '',
				carbs: ''
			};
		},
		
		// 加载已存在的菜品名称
		async loadExistingNames() {
			try {
				// 从后端获取当前分类下的所有菜品名称
				const response = await orderingManager.getMeals(this.categoryId);
				const meals = response.results || response || [];
				this.existingNames = meals.map(meal => meal.name);
			} catch (error) {
				console.error('加载菜品列表失败:', error);
				this.existingNames = [];
			}
		},
		
		// 选择图片
		async selectImage() {
			uni.chooseImage({
				count: 1,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: async (res) => {
					try {
						console.log('选择的图片路径:', res.tempFilePaths[0]);
						
						uni.showLoading({
							title: '上传中...'
						});
						
						// 上传图片到服务器
						const uploadResult = await orderingManager.uploadImage(res.tempFilePaths[0]);
						console.log('图片上传成功，返回URL:', uploadResult);
						
						// 确保uploadResult是一个有效的URL字符串
						if (uploadResult && typeof uploadResult === 'string') {
							this.formData.image = uploadResult;
							console.log('设置formData.image为:', this.formData.image);
							
							// 测试图片URL是否可访问
							uni.getImageInfo({
								src: uploadResult,
								success: (info) => {
									console.log('图片信息获取成功:', info);
								},
								fail: (err) => {
									console.error('图片信息获取失败:', err);
								}
							});
						} else {
							console.error('上传返回值不是有效URL:', uploadResult);
							throw new Error('上传返回值不是有效URL');
						}
						
						uni.hideLoading();
						uni.showToast({
							title: '上传成功',
							icon: 'success'
						});
					} catch (error) {
						uni.hideLoading();
						console.error('上传图片失败:', error);
						uni.showToast({
							title: '上传失败: ' + (error.message || '未知错误'),
							icon: 'error',
							duration: 3000
						});
					}
				},
				fail: (error) => {
					console.error('选择图片失败:', error);
				}
			});
		},
		
		// 检查名称唯一性
		checkNameUnique() {
			if (!this.formData.name.trim()) {
				this.nameError = '菜品名称不能为空';
				return;
			}
			
			const trimmedName = this.formData.name.trim();
			if (this.existingNames.includes(trimmedName) && 
				(!this.isEditMode || trimmedName !== this.originalName)) {
				this.nameError = '菜品名称已存在，请使用其他名称';
			} else {
				this.nameError = '';
			}
		},
		
		// 添加标签
		addTag(tag) {
			if (!this.formData.tags.includes(tag) && this.formData.tags.length < 6) {
				this.formData.tags.push(tag);
			}
		},
		
		// 移除标签
		removeTag(index) {
			this.formData.tags.splice(index, 1);
		},
		
		// 添加自定义标签
		addCustomTag() {
			const tag = this.customTag.trim();
			if (tag && !this.formData.tags.includes(tag) && this.formData.tags.length < 6) {
				this.formData.tags.push(tag);
				this.customTag = '';
			}
		},
		
		// 时间改变
		onTimeChange(e) {
			this.formData.cookTime = e.detail.value;
		},
		
		// 选择难度
		selectDifficulty(level) {
			this.formData.difficulty = level;
		},
		
		// 将前端难度数字转换为后端字符串
		getDifficultyString(difficulty) {
			const difficultyMap = {
				1: 'easy',
				2: 'medium', 
				3: 'hard'
			};
			return difficultyMap[difficulty] || 'easy';
		},
		
		// 验证表单
		validateForm() {
			if (!this.formData.image) {
				uni.showToast({
					title: '请上传菜品图片',
					icon: 'none'
				});
				return false;
			}
			
			if (!this.formData.name.trim()) {
				uni.showToast({
					title: '请输入菜品名称',
					icon: 'none'
				});
				return false;
			}
			
			if (this.nameError) {
				uni.showToast({
					title: this.nameError,
					icon: 'none'
				});
				return false;
			}
			
			if (!this.categoryId) {
				uni.showToast({
					title: '缺少分类信息',
					icon: 'none'
				});
				return false;
			}
			
			return true;
		},
		
		// 保存菜品
		async saveFoodItem() {
			if (!this.validateForm()) return;
			
			uni.showLoading({
				title: '保存中...'
			});
			
			try {
				// 准备要保存的数据
				const mealData = {
					name: this.formData.name,
					description: this.formData.description,
					category: this.categoryId,
					image: this.formData.image || '',
					prep_time: this.formData.cookTime,
					difficulty: this.getDifficultyString(this.formData.difficulty),
					tags: this.formData.tags,
					is_available: true,
					// 移除了 nutrition_info 字段，因为后端模型没有这个字段
					// 如果需要，可以添加 ingredients 和 cooking_steps
					ingredients: [],
					cooking_steps: []
				};
				
				// 添加调试日志
				console.log('准备保存的菜品数据:', mealData);
				console.log('是否编辑模式:', this.isEditMode);
				console.log('编辑ID:', this.editingId);
				console.log('分类ID:', this.categoryId);
				
				let savedMeal;
				if (this.isEditMode) {
					// 更新菜品
					console.log('调用updateMeal，ID:', this.editingId);
					savedMeal = await orderingManager.updateMeal(this.editingId, mealData);
				} else {
					// 创建菜品
					console.log('调用createMeal');
					savedMeal = await orderingManager.createMeal(mealData);
				}
				
				console.log('保存成功，返回数据:', savedMeal);
				
				uni.hideLoading();
				
				// 返回数据给首页
				const pages = getCurrentPages();
				const prevPage = pages[pages.length - 2];
				
				if (prevPage && prevPage.handleFoodUpdate) {
					const foodData = {
						id: savedMeal.id,
						name: savedMeal.name,
						description: savedMeal.description,
						image: savedMeal.image,
						tags: savedMeal.tags || [],
						cookTime: savedMeal.prep_time,
						difficulty: this.formData.difficulty,
						categoryId: this.categoryId
					};
					
					prevPage.handleFoodUpdate({
						mode: this.isEditMode ? 'edit' : 'add',
						categoryId: this.categoryId,
						data: foodData
					});
				}
				
				uni.navigateBack();
				uni.showToast({
					title: this.isEditMode ? '修改成功' : '添加成功',
					icon: 'success'
				});
				
			} catch (error) {
				uni.hideLoading();
				console.error('保存菜品失败:', error);
				uni.showToast({
					title: '保存失败',
					icon: 'error'
				});
			}
		},
		
		// 删除菜品
		async deleteFood() {
			uni.showModal({
				title: '确认删除',
				content: `确定要删除"${this.formData.name}"吗？此操作不可撤销。`,
				confirmText: '删除',
				cancelText: '取消',
				confirmColor: '#FF6B95',
				success: async (res) => {
					if (res.confirm) {
						uni.showLoading({
							title: '删除中...'
						});
						
						try {
							// 调用后端API删除菜品
							await orderingManager.deleteMeal(this.editingId);
							
							uni.hideLoading();
							
							// 返回删除结果给上一页
							const pages = getCurrentPages();
							const prevPage = pages[pages.length - 2];
							
							if (prevPage && prevPage.handleFoodUpdate) {
								prevPage.handleFoodUpdate({
									mode: 'delete',
									categoryId: this.categoryId,
									foodId: this.editingId
								});
							}
							
							uni.navigateBack();
							uni.showToast({
								title: '删除成功',
								icon: 'success'
							});
							
						} catch (error) {
							uni.hideLoading();
							console.error('删除菜品失败:', error);
							uni.showToast({
								title: '删除失败',
								icon: 'error'
							});
						}
					}
				}
			});
		},
		
		// 返回
		goBack() {
			uni.showModal({
				title: '确认',
				content: '确定要放弃编辑吗？',
				success: (res) => {
					if (res.confirm) {
						uni.navigateBack();
					}
				}
			});
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

.form-scroll {
	height: calc(100vh - 120rpx);
	padding: 30rpx;
}

/* 表单区块 */
.form-section {
	background: white;
	border-radius: 20rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.section-title {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.title-text {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
}

.required {
	color: #FF6B95;
	margin-left: 8rpx;
	font-size: 24rpx;
}

.optional {
	color: #999;
	margin-left: 8rpx;
	font-size: 22rpx;
}

/* 图片上传 */
.image-upload-area {
	width: 100%;
	height: 300rpx;
	border: 2rpx dashed #DDD;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
}

.uploaded-image {
	width: 100%;
	height: 100%;
}

.upload-placeholder {
	text-align: center;
	color: #999;
}

.upload-icon {
	font-size: 48rpx;
	margin-bottom: 16rpx;
}

.upload-text {
	font-size: 24rpx;
}

/* 表单输入 */
.form-input,
.form-textarea {
	width: 100%;
	padding: 24rpx;
	border: 1rpx solid #E9ECEF;
	border-radius: 12rpx;
	font-size: 26rpx;
	background: #F8F9FA;
}

.form-textarea {
	height: 120rpx;
	resize: none;
}

.form-textarea.large {
	height: 200rpx;
}

.error-text {
	color: #FF6B95;
	font-size: 22rpx;
	margin-top: 12rpx;
}

/* 标签管理 */
.tags-container {
	background: #F8F9FA;
	border-radius: 16rpx;
	padding: 20rpx;
}

.selected-tags {
	margin-bottom: 20rpx;
}

.preset-tags {
	margin-bottom: 20rpx;
}

.tag-item {
	display: inline-block;
	padding: 8rpx 16rpx;
	margin: 8rpx 8rpx 8rpx 0;
	border-radius: 20rpx;
	font-size: 22rpx;
	cursor: pointer;
}

.tag-item.selected {
	background: linear-gradient(135deg, #FF6B95, #FF8C94);
	color: white;
	position: relative;
}

.tag-item.preset {
	background: #E9ECEF;
	color: #666;
	border: 1rpx solid #DDD;
}

.tag-item.preset.disabled {
	opacity: 0.5;
	pointer-events: none;
}

.remove-icon {
	margin-left: 8rpx;
	font-weight: bold;
}

.custom-tag-input {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.tag-input {
	flex: 1;
	padding: 16rpx;
	border: 1rpx solid #DDD;
	border-radius: 8rpx;
	font-size: 22rpx;
}

.add-tag-btn {
	width: 60rpx;
	height: 60rpx;
	background: #FF6B95;
	color: white;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24rpx;
	font-weight: bold;
}

/* 时间选择器 */
.time-selector {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.time-slider {
	flex: 1;
}

.time-display {
	min-width: 120rpx;
	text-align: center;
	font-size: 26rpx;
	font-weight: 500;
	color: #FF6B95;
}

/* 难度选择器 */
.difficulty-selector {
	display: flex;
	gap: 20rpx;
}

.difficulty-item {
	flex: 1;
	text-align: center;
	padding: 20rpx;
	border: 2rpx solid #E9ECEF;
	border-radius: 16rpx;
	background: #F8F9FA;
	transition: all 0.3s;
}

.difficulty-item.active {
	border-color: #FF6B95;
	background: rgba(255, 107, 149, 0.1);
}

.difficulty-icon {
	font-size: 32rpx;
	margin-bottom: 8rpx;
}

.difficulty-text {
	font-size: 22rpx;
	color: #666;
}

.difficulty-item.active .difficulty-text {
	color: #FF6B95;
	font-weight: 500;
}

/* 营养信息 */
.nutrition-inputs {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 16rpx;
}

.nutrition-item {
	background: #F8F9FA;
	padding: 20rpx;
	border-radius: 12rpx;
}

.nutrition-label {
	display: block;
	font-size: 22rpx;
	color: #666;
	margin-bottom: 12rpx;
}

.nutrition-input {
	width: 100%;
	padding: 12rpx;
	border: 1rpx solid #DDD;
	border-radius: 8rpx;
	font-size: 24rpx;
	text-align: center;
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
