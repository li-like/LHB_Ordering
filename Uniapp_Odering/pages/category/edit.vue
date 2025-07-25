<template>
	<view class="container">
		<!-- 标题 -->
		<view class="page-title">
			<text class="title-text">{{ isEditMode ? '编辑分类' : '添加分类' }}</text>
		</view>
		
		<!-- 表单内容 -->
		<view class="form-container">
			<!-- 分类名称 -->
			<view class="form-item">
				<view class="form-label">
					<text class="label-text">分类名称</text>
					<text class="required-mark">*</text>
				</view>
				<input 
					class="form-input" 
					v-model="formData.name" 
					placeholder="请输入分类名称" 
					maxlength="10"
					@input="validateName"
				/>
				<view v-if="nameError" class="error-tip">{{ nameError }}</view>
			</view>
			
			<!-- 图标选择 -->
			<view class="form-item">
				<view class="form-label">
					<text class="label-text">分类图标</text>
				</view>
				<view class="icon-selection">
					<!-- 当前选中的图标/图片 -->
					<view class="current-icon-preview">
						<view v-if="formData.iconType === 'emoji'" class="current-emoji">
							{{ formData.emoji }}
						</view>
						<image v-else-if="formData.iconType === 'image'" class="current-image" :src="formData.image" mode="aspectFill"></image>
						<view v-else class="no-icon">
							<text class="no-icon-text">未选择</text>
						</view>
					</view>
					
					<!-- 选择按钮 -->
					<view class="icon-actions">
						<view class="primary-action-btn" @click="showEmojiPicker">
							<text class="icon-select-text">选择图标</text>
						</view>
						<view class="secondary-action-btn" @click="selectImage">
							<text class="icon-select-text">上传图片</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 预览效果 -->
			<view class="form-item">
				<view class="form-label">
					<text class="label-text">预览效果</text>
				</view>
				<view class="category-preview">
					<view class="preview-tab">
						<text class="preview-icon">{{ formData.emoji || '🍽️' }}</text>
						<text class="preview-name">{{ formData.name || '分类名称' }}</text>
						<text class="preview-count">(0)</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 底部操作栏 -->
		<view class="bottom-actions">
			<!-- 删除按钮（仅编辑模式显示） -->
			<view v-if="isEditMode" class="delete-btn" @click="deleteCategory">
				<text class="delete-text">删除分类</text>
			</view>
			
			<!-- 返回和保存按钮 -->
			<view class="action-buttons">
				<view class="action-btn cancel-btn" @click="goBack">
					<text class="btn-text">取消</text>
				</view>
				<view class="action-btn save-btn" @click="saveCategory">
					<text class="btn-text">保存</text>
				</view>
			</view>
		</view>
		
		<!-- 图标选择弹窗 -->
		<view v-if="showEmojiModal" class="emoji-modal-overlay" @click="hideEmojiPicker">
			<view class="emoji-container" @click.stop>
				<view class="emoji-header">
					<text class="emoji-title">选择分类图标</text>
					<view class="emoji-close-btn" @click="hideEmojiPicker">
						<text class="emoji-close-icon">×</text>
					</view>
				</view>
				<view class="emoji-grid-wrapper">
					<scroll-view class="emoji-grid" scroll-y="true" show-scrollbar="false">
						<view class="emoji-rows">
							<view 
								class="emoji-item" 
								:class="{ 'selected': emoji === tempSelectedEmoji }"
								v-for="emoji in emojiList" 
								:key="emoji"
								@click="selectEmoji(emoji)"
								hover-class="emoji-item-hover"
							>
								<text class="emoji-text">{{ emoji }}</text>
							</view>
						</view>
					</scroll-view>
				</view>
				<view class="emoji-footer">
					<view class="emoji-cancel-btn" @click="hideEmojiPicker">
						<text>取消</text>
					</view>
					<view class="emoji-confirm-btn" @click="confirmEmojiSelection">
						<text>确定</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import orderingManager from '../../utils/orderingManager.js'

// 确保引入了uni-popup组件
// 如果项目中没有安装uni-popup组件，需要从插件市场安装
export default {
	data() {
		return {
			isEditMode: false,
			originalCategory: null,
			showEmojiModal: false, // 控制图标选择弹窗显示
			formData: {
				name: '',
				emoji: '🍽️',
				image: '',
				iconType: 'emoji' // 'emoji' 或 'image'
			},
			nameError: '',
			tempSelectedEmoji: '', // 添加临时选中的emoji
			// 内置图标库
			emojiList: [
				'🍽️', '🥩', '🥬', '🍲', '🍚', '🥟', '🍰', '🍜', '🍕', '🍔',
				'🌮', '🥙', '🥗', '🍖', '🍗', '🥓', '🍳', '🥞', '🧀', '🥨',
				'🥯', '🍞', '🥖', '🥐', '🫓', '🥪', '🌭', '🍟', '🍿', '🧈',
				'🥛', '☕', '🍵', '🧃', '🥤', '🧋', '🍶', '🍺', '🍷', '🥂',
				'🍸', '🍹', '🧊', '🥄', '🍴', '🥢', '🔥', '❄️', '🌶️', '🧂'
			]
		}
	},
	
	onLoad(options) {
		if (options.mode === 'edit') {
			this.isEditMode = true;
			if (options.categoryData) {
				// 兼容旧的传递数据方式
				this.originalCategory = JSON.parse(decodeURIComponent(options.categoryData));
				this.formData = { ...this.originalCategory };
			} else if (options.id) {
				// 新的方式：通过ID从后端获取数据
				this.loadCategoryData(options.id);
			}
			this.tempSelectedEmoji = this.formData.emoji; // 初始化临时选中的emoji
		} else {
			// 新建模式，初始化临时选中的emoji为默认值
			this.tempSelectedEmoji = this.formData.emoji;
		}
		
		// 确保弹窗初始状态为关闭
		this.showEmojiModal = false;
	},
	
	methods: {
		// 从后端加载分类数据
		async loadCategoryData(categoryId) {
			try {
				uni.showLoading({
					title: '加载中...'
				});
				
				const category = await orderingManager.getCategory(categoryId);
				
				this.originalCategory = {
					id: category.id,
					name: category.name || '',
					emoji: category.icon || '🍽️',
					iconType: 'emoji',
					image: category.image || ''
				};
				
				this.formData = { ...this.originalCategory };
				this.tempSelectedEmoji = this.formData.emoji;
				
				uni.hideLoading();
			} catch (error) {
				console.error('加载分类数据失败:', error);
				uni.hideLoading();
				uni.showToast({
					title: '加载失败',
					icon: 'error'
				});
			}
		},
		
		// 返回上一页
		goBack() {
			if (this.hasChanges()) {
				uni.showModal({
					title: '提示',
					content: '当前有未保存的更改，确定要离开吗？',
					success: (res) => {
						if (res.confirm) {
							uni.navigateBack();
						}
					}
				});
			} else {
				uni.navigateBack();
			}
		},
		
		// 检查是否有变更
		hasChanges() {
			if (!this.isEditMode) {
				return this.formData.name.trim() !== '' || this.formData.emoji !== '🍽️';
			}
			return JSON.stringify(this.formData) !== JSON.stringify(this.originalCategory);
		},
		
		// 验证分类名称
		validateName() {
			this.nameError = '';
			if (!this.formData.name.trim()) {
				this.nameError = '分类名称不能为空';
				return false;
			}
			if (this.formData.name.trim().length > 10) {
				this.nameError = '分类名称不能超过10个字符';
				return false;
			}
			// 这里可以添加重名检查逻辑
			return true;
		},
		
		// 显示图标选择器
		showEmojiPicker() {
			// 确保有临时选中的emoji
			if (!this.tempSelectedEmoji) {
				this.tempSelectedEmoji = this.formData.emoji || '🍽️';
			}
			
			this.showEmojiModal = true;
		},
		
		// 隐藏图标选择器
		hideEmojiPicker() {
			this.showEmojiModal = false;
		},
		
		// 选择图标
		selectEmoji(emoji) {
			this.tempSelectedEmoji = emoji; // 设置临时选中的emoji
		},
		
		// 确认选择的图标
		confirmEmojiSelection() {
			if (this.tempSelectedEmoji) {
				this.formData.emoji = this.tempSelectedEmoji;
				this.formData.iconType = 'emoji';
				this.formData.image = '';
			}
			this.hideEmojiPicker();
			
			uni.showToast({
				title: '已选择图标',
				icon: 'none',
				duration: 1000
			});
		},
		
		// 选择图片
		selectImage() {
			uni.chooseImage({
				count: 1,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					const tempFilePath = res.tempFilePaths[0];
					this.formData.image = tempFilePath;
					this.formData.iconType = 'image';
					this.formData.emoji = '';
				},
				fail: (err) => {
					console.error('选择图片失败:', err);
					uni.showToast({
						title: '选择图片失败',
						icon: 'none'
					});
				}
			});
		},
		
		// 保存分类
		async saveCategory() {
			if (!this.validateForm()) {
				return;
			}
			
			uni.showLoading({
				title: '保存中...'
			});
			
			try {
				// 准备要保存的数据
				const categoryData = {
					name: this.formData.name,
					icon: this.formData.emoji || '',
					description: this.formData.description || '',
					family_id: 1 // 临时硬编码，后续需要从用户信息获取
				};
				
				let savedCategory;
				if (this.isEditMode) {
					// 更新分类
					savedCategory = await orderingManager.updateCategory(this.originalCategory.id, categoryData);
				} else {
					// 创建分类
					savedCategory = await orderingManager.createCategory(categoryData);
				}
				
				uni.hideLoading();
				
				// 返回数据给上一页
				const pages = getCurrentPages();
				const prevPage = pages[pages.length - 2];
				
				if (prevPage) {
					const eventData = {
						mode: this.isEditMode ? 'edit' : 'add',
						data: {
							...this.formData,
							id: savedCategory.id // 使用后端返回的ID
						}
					};
					
					if (this.isEditMode) {
						eventData.originalId = this.originalCategory.id;
					}
					
					// 触发上一页的事件处理
					if (prevPage.handleCategoryUpdate) {
						prevPage.handleCategoryUpdate(eventData);
					}
				}
				
				uni.navigateBack();
				uni.showToast({
					title: this.isEditMode ? '修改成功' : '添加成功',
					icon: 'success'
				});
				
			} catch (error) {
				uni.hideLoading();
				console.error('保存分类失败:', error);
				uni.showToast({
					title: '保存失败',
					icon: 'error'
				});
			}
		},
		
		// 验证表单
		validateForm() {
			if (!this.validateName()) {
				return false;
			}
			return true;
		},
		
		// 删除分类
		deleteCategory() {
			uni.showModal({
				title: '确认删除',
				content: `确定要删除"${this.formData.name}"分类吗？此操作不可恢复。`,
				confirmText: '删除',
				cancelText: '取消',
				confirmColor: '#FF6B95',
				success: (res) => {
					if (res.confirm) {
						this.performDelete();
					}
				}
			});
		},
		
		// 执行删除
		async performDelete() {
			uni.showLoading({
				title: '删除中...'
			});
			
			try {
				// 调用后端API删除分类
				await orderingManager.deleteCategory(this.originalCategory.id);
				
				uni.hideLoading();
				
				// 返回删除结果给上一页
				const pages = getCurrentPages();
				const prevPage = pages[pages.length - 2];
				
				if (prevPage && prevPage.handleCategoryUpdate) {
					prevPage.handleCategoryUpdate({
						mode: 'delete',
						originalId: this.originalCategory.id
					});
				}
				
				uni.navigateBack();
				uni.showToast({
					title: '删除成功',
					icon: 'success'
				});
				
			} catch (error) {
				uni.hideLoading();
				console.error('删除分类失败:', error);
				uni.showToast({
					title: '删除失败',
					icon: 'error'
				});
			}
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #F8F9FA;
}

.page-title {
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 40rpx 0;
	background: #FFFFFF;
	border-bottom: 2rpx solid #F0F0F0;
}

.title-text {
	font-size: 36rpx;
	font-weight: bold;
	color: #333333;
}

.bottom-actions {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.05);
	z-index: 10;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.action-buttons {
	display: flex;
	gap: 20rpx;
}

.action-btn {
	flex: 1;
	height: 76rpx;
	border-radius: 38rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.2s;
}

.action-btn:active {
	transform: scale(0.97);
	opacity: 0.9;
}

.cancel-btn {
	background: #F5F5F5;
	border: 1rpx solid #E0E0E0;
}

.save-btn {
	background: linear-gradient(135deg, #FF6B95, #FF8C94);
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 149, 0.2);
}

.btn-text {
	font-size: 26rpx;
	font-weight: 500;
}

.save-btn .btn-text {
	color: white;
}

.form-container {
	padding: 40rpx 30rpx 180rpx;
}

.form-item {
	margin-bottom: 40rpx;
	animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
	from {
		opacity: 0;
		transform: translateY(10rpx);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.form-label {
	display: flex;
	align-items: center;
	margin-bottom: 16rpx;
}

.label-text {
	font-size: 28rpx;
	font-weight: 500;
	color: #333333;
}

.required-mark {
	color: #FF6B95;
	margin-left: 8rpx;
}

.form-input {
	background: #FFFFFF;
	border: 2rpx solid #E9ECEF;
	border-radius: 16rpx;
	padding: 24rpx 20rpx;
	font-size: 28rpx;
	color: #333333;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.02);
	transition: all 0.3s;
}

.form-input:focus {
	border-color: #FF6B95;
	box-shadow: 0 4rpx 16rpx rgba(255, 107, 149, 0.1);
}

.error-tip {
	margin-top: 12rpx;
	font-size: 24rpx;
	color: #FF6B95;
	animation: shake 0.5s;
}

@keyframes shake {
	0%, 100% {transform: translateX(0);}
	10%, 30%, 50%, 70%, 90% {transform: translateX(-4rpx);}
	20%, 40%, 60%, 80% {transform: translateX(4rpx);}
}

.icon-selection {
	display: flex;
	align-items: center;
	padding: 10rpx 0;
}

.current-icon-preview {
	width: 120rpx;
	height: 120rpx;
	border-radius: 20rpx;
	border: 2rpx solid #E9ECEF;
	display: flex;
	align-items: center;
	justify-content: center;
	background: #FFFFFF;
	box-shadow: 0 6rpx 16rpx rgba(0, 0, 0, 0.05);
	transition: all 0.3s;
	margin-right: 20rpx;
	position: relative;
	overflow: hidden;
}

.current-emoji {
	font-size: 56rpx;
	text-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.1);
	transform-origin: center;
	animation: pulseScale 2s ease-in-out infinite;
}

@keyframes pulseScale {
	0%, 100% { transform: scale(1); }
	50% { transform: scale(1.05); }
}

.current-image {
	width: 100%;
	height: 100%;
	border-radius: 18rpx;
	object-fit: cover;
}

.no-icon {
	color: #999999;
	font-size: 24rpx;
	background: #F8F8F8;
	padding: 12rpx 20rpx;
	border-radius: 10rpx;
}

.icon-actions {
	flex: 1;
	display: flex;
	gap: 16rpx;
}

.icon-actions .primary-action-btn {
	flex: 1;
	height: auto;
	background: linear-gradient(135deg, #FF6B95, #FF8C94);
	color: white;
	padding: 16rpx 0;
	border-radius: 30rpx;
	text-align: center;
	box-shadow: 0 4rpx 10rpx rgba(255, 107, 149, 0.2);
	transition: all 0.2s;
	display: flex;
	align-items: center;
	justify-content: center;
}

.icon-actions .secondary-action-btn {
	flex: 1;
	height: auto;
	background: #F8F8F8;
	border: 1rpx solid #E0E0E0;
	color: #666;
	padding: 16rpx 0;
	border-radius: 30rpx;
	text-align: center;
	transition: all 0.2s;
	display: flex;
	align-items: center;
	justify-content: center;
}

.icon-actions .primary-action-btn:active,
.icon-actions .secondary-action-btn:active {
	transform: scale(0.97);
	opacity: 0.9;
}

.icon-select-text {
	font-size: 26rpx;
	font-weight: 500;
}

.action-text {
	font-size: 26rpx;
	color: white;
}

.icon-select-text {
	color: inherit;
}

.category-preview {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	border: 2rpx solid #E9ECEF;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.03);
}

.preview-tab {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 30rpx 20rpx;
	background: rgba(255, 107, 149, 0.05);
	border-radius: 16rpx;
	border-left: 6rpx solid #FF6B95;
	position: relative;
	transition: all 0.3s;
}

.preview-tab::after {
	content: "";
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	border-radius: 16rpx;
	box-shadow: 0 6rpx 16rpx rgba(255, 107, 149, 0.08);
	opacity: 0;
	transition: all 0.3s;
	pointer-events: none;
}

.preview-tab:hover::after {
	opacity: 1;
}

.preview-icon {
	display: block;
	font-size: 36rpx;
	margin-bottom: 12rpx;
	text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.1);
}

.preview-name {
	display: block;
	font-size: 26rpx;
	font-weight: 500;
	margin-bottom: 8rpx;
	color: #333333;
}

.preview-count {
	font-size: 22rpx;
	color: #999999;
	background: #F0F0F0;
	padding: 4rpx 12rpx;
	border-radius: 10rpx;
}

.delete-btn {
	width: 100%;
	background: rgba(255, 71, 87, 0.08);
	border: 1rpx solid rgba(255, 71, 87, 0.3);
	color: #FF4757;
	padding: 20rpx;
	border-radius: 38rpx;
	text-align: center;
	margin-bottom: 16rpx;
	transition: all 0.2s;
}

.delete-btn:active {
	background: rgba(255, 71, 87, 0.15);
	transform: scale(0.98);
}

.delete-text {
	font-size: 26rpx;
	color: #FF4757;
	font-weight: 500;
}

/* 图标选择弹窗覆盖层 */
.emoji-modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.6);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
	padding: 40rpx;
}

/* 图标选择弹窗 */
.emoji-container {
	background: #FFFFFF;
	border-radius: 28rpx;
	width: 100%;
	max-width: 650rpx;
	max-height: 750rpx;
	display: flex;
	flex-direction: column;
	box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.25);
	overflow: hidden;
	animation: popIn 0.35s cubic-bezier(0.18, 0.89, 0.32, 1.28);
	position: relative;
}

@keyframes popIn {
	0% {
		opacity: 0;
		transform: scale(0.85);
	}
	70% {
		opacity: 1;
		transform: scale(1.03);
	}
	100% {
		opacity: 1;
		transform: scale(1);
	}
}

.emoji-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 26rpx 30rpx;
	border-bottom: 1rpx solid #F0F0F0;
	background: linear-gradient(to bottom, #FFFFFF, #FAFAFA);
}

.emoji-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	text-align: center;
	flex: 1;
	margin: 0 40rpx; /* 为关闭按钮留出空间 */
}

.emoji-close-btn {
	width: 44rpx;
	height: 44rpx;
	border-radius: 22rpx;
	background: #F2F2F2;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.2s;
	border: 1rpx solid #E5E5E5;
	position: absolute;
	right: 20rpx;
	top: 20rpx;
}

.emoji-close-btn:active {
	background: #EBEBEB;
	transform: scale(0.92);
}

.emoji-close-icon {
	font-size: 28rpx;
	color: #999999;
	line-height: 1;
	margin-top: -2rpx; /* 微调居中 */
}

.emoji-grid-wrapper {
	flex: 1;
	position: relative;
	overflow: hidden;
	max-height: 480rpx;
	padding: 0 10rpx;
}

.emoji-grid {
	height: 100%;
	padding: 15rpx 5rpx;
}

.emoji-rows {
	display: flex;
	flex-wrap: wrap;
	justify-content: space-between;
	padding: 5rpx;
}

.emoji-item {
	width: 96rpx;
	height: 96rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 18rpx;
	margin: 8rpx;
	border: 2rpx solid transparent;
	background-color: #F8F8F8;
	transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1);
	position: relative;
	box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.05);
}

.emoji-item::before {
	content: "";
	position: absolute;
	top: -2rpx;
	left: -2rpx;
	right: -2rpx;
	bottom: -2rpx;
	border-radius: 20rpx;
	border: 2rpx solid transparent;
	opacity: 0;
	transition: all 0.2s;
}

.emoji-item::after {
	content: "";
	position: absolute;
	top: -6rpx;
	left: -6rpx;
	right: -6rpx;
	bottom: -6rpx;
	border-radius: 24rpx;
	border: 2rpx solid transparent;
	opacity: 0;
	transition: all 0.2s;
}

.emoji-item.selected {
	border-color: #FF6B95;
	background: rgba(255, 107, 149, 0.08);
	transform: translateY(-2rpx);
	box-shadow: 0 4rpx 10rpx rgba(255, 107, 149, 0.2);
}

.emoji-item.selected::before {
	border-color: rgba(255, 107, 149, 0.3);
	opacity: 1;
}

.emoji-item.selected::after {
	border-color: rgba(255, 107, 149, 0.15);
	opacity: 1;
}

.emoji-item-hover {
	transform: scale(1.08);
	background: #F0F0F0;
	box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.1);
}

.emoji-text {
	font-size: 40rpx;
	transition: all 0.2s;
}

.emoji-item.selected .emoji-text {
	transform: scale(1.1);
}

.emoji-footer {
	display: flex;
	padding: 20rpx 30rpx;
	border-top: 1rpx solid #F0F0F0;
	justify-content: space-between;
	background: linear-gradient(to top, #FFFFFF, #FAFAFA);
}

.emoji-cancel-btn,
.emoji-confirm-btn {
	padding: 14rpx 0;
	border-radius: 40rpx;
	font-size: 28rpx;
	transition: all 0.25s;
	font-weight: 500;
	text-align: center;
	flex: 1;
}

.emoji-cancel-btn {
	background: #F5F5F5;
	color: #666666;
	margin-right: 16rpx;
	border: 1rpx solid #E0E0E0;
}

.emoji-confirm-btn {
	background: linear-gradient(135deg, #FF6B95, #FF8C94);
	color: white;
	margin-left: 16rpx;
	box-shadow: 0 4rpx 12rpx rgba(255, 107, 149, 0.25);
}

.emoji-cancel-btn:active,
.emoji-confirm-btn:active {
	transform: scale(0.96);
	opacity: 0.9;
}
</style>
