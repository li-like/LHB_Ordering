<template>
	<view class="page-container">
		<view class="container">
			<!-- 家庭信息卡片 -->
			<view class="family-card">
				<view class="family-header">
					<view class="family-avatar">
						<text class="family-icon">🏠</text>
					</view>
					<view class="family-info">
						<text class="family-name">{{ familyData.familyName || '我的家庭' }}</text>
						<text class="create-time">创建于 {{ formatDate(familyData.createTime) }}</text>
					</view>
					<view class="edit-btn" @click="editFamilyName">
						<text class="edit-icon">✏️</text>
					</view>
				</view>
				
				<view class="family-stats">
					<view class="stat-item" @click="navigateToCooking">
						<text class="stat-number">{{ familyData.members?.length || 0 }}</text>
						<text class="stat-label">家庭成员</text>
					</view>
					<view class="stat-item" @click="navigateToCooking">
						<text class="stat-number">{{ getTotalMeals() }}</text>
						<text class="stat-label">共同用餐</text>
					</view>
					<view class="stat-item" @click="navigateToFavorite">
						<text class="stat-number">{{ getFavoriteDishes() }}</text>
						<text class="stat-label">喜爱菜品</text>
					</view>
				</view>
			</view>
			
			<!-- 成员列表 -->
			<view class="members-section">
				<view class="section-header">
					<text class="section-title">家庭成员</text>
					<view class="add-member-btn" @click="showAddMember">
						<text class="add-icon">+</text>
						<text class="add-text">添加成员</text>
					</view>
				</view>
				
				<view class="members-list">
					<view class="member-item" v-for="member in familyData.members" :key="member.id" @click="showMemberDetail(member)">
						<image class="member-avatar" :src="member.avatar || '/static/default-avatar.png'" mode="aspectFill"></image>
						<view class="member-info">
							<view class="member-main">
								<text class="member-name">{{ member.name }}</text>
								<view class="member-role" v-if="member.role === 'admin'">
									<text class="role-text">管理员</text>
								</view>
							</view>
							<text class="join-time">{{ formatDate(member.joinTime) }} 加入</text>
							<view class="member-tags" v-if="member.preferences && (member.preferences.taste.length > 0 || member.preferences.allergies.length > 0)">
								<text class="tag preference-tag" v-for="taste in member.preferences.taste.slice(0, 2)" :key="taste">{{ taste }}</text>
								<text class="tag allergy-tag" v-for="allergy in member.preferences.allergies.slice(0, 1)" :key="allergy">忌{{ allergy }}</text>
							</view>
						</view>
						<view class="member-actions">
							<text class="action-icon">></text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 快速设置 -->
			<view class="quick-settings">
				<view class="section-header">
					<text class="section-title">快速设置</text>
				</view>
				
				<view class="settings-list">
					<view class="setting-item" @click="navigateToCooking">
						<view class="setting-icon">
							<text class="icon-text">📝</text>
						</view>
						<view class="setting-info">
							<text class="setting-name">用餐记录</text>
							<text class="setting-desc">查看和管理家庭用餐记录</text>
						</view>
						<view class="setting-arrow">
							<text class="arrow-icon">></text>
						</view>
					</view>
					
					<view class="setting-item" @click="navigateToFavorite">
						<view class="setting-icon">
							<text class="icon-text">❤️</text>
						</view>
						<view class="setting-info">
							<text class="setting-name">喜爱菜品</text>
							<text class="setting-desc">管理家庭喜爱的菜品</text>
						</view>
						<view class="setting-arrow">
							<text class="arrow-icon">></text>
						</view>
					</view>
					
					<view class="setting-item" @click="setFamilyPreferences">
						<view class="setting-icon">
							<text class="icon-text">🍽️</text>
						</view>
						<view class="setting-info">
							<text class="setting-name">家庭饮食偏好</text>
							<text class="setting-desc">设置共同的口味偏好</text>
						</view>
						<view class="setting-arrow">
							<text class="arrow-icon">></text>
						</view>
					</view>
					
					<view class="setting-item" @click="setMealTimes">
						<view class="setting-icon">
							<text class="icon-text">⏰</text>
						</view>
						<view class="setting-info">
							<text class="setting-name">用餐时间</text>
							<text class="setting-desc">设置家庭用餐时间</text>
						</view>
						<view class="setting-arrow">
							<text class="arrow-icon">></text>
						</view>
					</view>
					
					<view class="setting-item" @click="manageFamilyCode">
						<view class="setting-icon">
							<text class="icon-text">🔗</text>
						</view>
						<view class="setting-info">
							<text class="setting-name">邀请码管理</text>
							<text class="setting-desc">生成邀请码让家人加入</text>
						</view>
						<view class="setting-arrow">
							<text class="arrow-icon">></text>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 添加成员弹窗 -->
		<view class="modal-mask" v-if="showAddMemberModal" @tap="closeModal">
			<view class="modal-content" @tap.stop>
				<view class="popup-header">
					<text class="popup-title">添加家庭成员</text>
				</view>
				<view class="popup-body">
					<view class="input-group">
						<text class="input-label">成员姓名</text>
						<input class="input-field" v-model="newMember.name" placeholder="请输入成员姓名" />
					</view>
					<view class="input-group">
						<text class="input-label">关系</text>
						<picker mode="selector" :range="relationOptions" @change="onRelationChange">
							<view class="picker-input">
								<text>{{ newMember.relation || '请选择关系' }}</text>
								<text class="picker-arrow">></text>
							</view>
						</picker>
					</view>
				</view>
				<view class="popup-actions">
					<button class="cancel-btn" @click="cancelAddMember">取消</button>
					<button class="confirm-btn" @click="confirmAddMember">确定</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import userManager from '../../utils/userManager.js'
import familyManager from '../../utils/familyManager.js'
import { FamilyAPI } from '../../utils/api.js'

export default {
	data() {
		return {
			familyData: {
				familyName: '',
				createTime: null,
				members: []
			},
			userInfo: {},
			currentFamilyId: null,
			familyList: [],
			showAddMemberModal: false,
			newMember: {
				name: '',
				relation: ''
			},
			relationOptions: ['父亲', '母亲', '配偶', '儿子', '女儿', '兄弟', '姐妹', '其他'],
			loading: false,
			familyManager: familyManager
		}
	},
	
	onLoad() {
		this.checkLogin();
		this.initializeFamilyManager();
		// 注册用户信息更新监听
		this.userInfoUpdateHandler = (updatedUserInfo) => {
			console.log('family页面收到用户信息更新通知:', updatedUserInfo);
			this.userInfo = updatedUserInfo;
			// 同时更新家庭数据中的当前用户信息
			this.updateCurrentUserInFamily(updatedUserInfo);
		};
		userManager.onUserInfoUpdated(this.userInfoUpdateHandler);
	},
	
	onShow() {
		this.checkLogin();
		this.refreshFamilyData();
	},
	
	onUnload() {
		// 移除用户信息更新监听
		if (this.userInfoUpdateHandler) {
			userManager.offUserInfoUpdated(this.userInfoUpdateHandler);
		}
		// 移除家庭管理器监听
		if (this.familyUpdateHandler) {
			familyManager.off('familyUpdated', this.familyUpdateHandler);
		}
		if (this.membersUpdateHandler) {
			familyManager.off('membersUpdated', this.membersUpdateHandler);
		}
	},
	
	methods: {
		// 检查登录状态
		async checkLogin() {
			if (!userManager.isLoggedIn()) {
				uni.redirectTo({
					url: '/pages/login/login'
				});
				return;
			}
			
			// #ifdef MP-WEIXIN
			try {
				const sessionValid = await userManager.checkWechatSession();
				if (!sessionValid) {
					uni.redirectTo({
						url: '/pages/login/login'
					});
					return;
				}
			} catch (error) {
				console.error('检查微信session失败:', error);
				uni.redirectTo({
					url: '/pages/login/login'
				});
				return;
			}
			// #endif
		},
		
		// 初始化家庭管理器
		async initializeFamilyManager() {
			try {
				// 注册家庭数据更新监听
				this.familyUpdateHandler = (event) => {
					console.log('家庭数据更新:', event);
					this.updateFamilyDataFromManager();
				};
				familyManager.on('familyUpdated', this.familyUpdateHandler);
				
				// 注册成员数据更新监听
				this.membersUpdateHandler = (event) => {
					console.log('成员数据更新:', event);
					this.updateMembersDataFromManager();
				};
				familyManager.on('membersUpdated', this.membersUpdateHandler);
				
				// 初始化家庭管理器
				await familyManager.initialize();
				
				// 更新页面数据
				this.updateFamilyDataFromManager();
				this.updateMembersDataFromManager();
				
			} catch (error) {
				console.error('初始化家庭管理器失败:', error);
				// 回退到原有的加载方式
				await this.loadFamilyData();
			}
		},
		
		// 从家庭管理器更新家庭数据
		updateFamilyDataFromManager() {
			const currentFamily = familyManager.getCurrentFamily();
			if (currentFamily) {
				this.currentFamilyId = currentFamily.id;
				this.familyData = {
					familyName: currentFamily.name,
					createTime: new Date(currentFamily.created_at).getTime(),
					members: [],
					familyId: currentFamily.id,
					inviteCode: currentFamily.invite_code,
					maxMembers: currentFamily.max_members,
					currentUserPermission: currentFamily.current_user_permission
				};
			} else {
				this.familyData = {
					familyName: '还没有家庭',
					createTime: null,
					members: []
				};
			}
		},
		
		// 从家庭管理器更新成员数据
		updateMembersDataFromManager() {
			const members = familyManager.getFamilyMembers();
			if (Array.isArray(members)) {
				this.familyData.members = members.map(member => ({
					id: member.user_info.openid,
					name: member.user_info.nickname,
					avatar: member.user_info.avatar,
					role: member.permission_level,
					joinTime: new Date(member.joined_at).getTime(),
					displayName: member.display_name,
					preferences: {
						taste: [],
						allergies: [],
						dislikes: []
					}
				}));
			}
		},
		
		// 刷新家庭数据
		async refreshFamilyData() {
			if (this.loading) return;
			this.loading = true;
			
			try {
				// 优先从后端获取用户信息
				if (userManager.isLoggedIn()) {
					const backendUserInfo = await userManager.fetchUserCompleteData();
					this.userInfo = backendUserInfo;
				} else {
					this.userInfo = userManager.getUserInfo() || {};
				}
				
				// 刷新家庭管理器数据
				if (familyManager.getCurrentFamily()) {
					await familyManager.refreshCurrentFamily();
				} else {
					await familyManager.getFamilyList();
				}
				
			} catch (error) {
				console.error('刷新家庭数据失败:', error);
				// 回退到本地数据
				this.userInfo = userManager.getUserInfo() || {};
				
				uni.showToast({
					title: '加载失败，使用本地数据',
					icon: 'none'
				});
			} finally {
				this.loading = false;
			}
		},
		
		// 更新家庭数据中的当前用户信息
		updateCurrentUserInFamily(updatedUserInfo) {
			if (this.familyData && this.familyData.members && updatedUserInfo.openid) {
				const memberIndex = this.familyData.members.findIndex(member => member.id === updatedUserInfo.openid);
				if (memberIndex !== -1) {
					// 更新家庭成员中当前用户的信息
					this.familyData.members[memberIndex] = {
						...this.familyData.members[memberIndex],
						name: updatedUserInfo.nickName,
						avatar: updatedUserInfo.avatarUrl
					};
					// 保存更新后的家庭数据
					userManager.saveFamilyData(this.familyData);
				}
			}
		},
		
		// 格式化日期
		formatDate(timestamp) {
			if (!timestamp) return '';
			const date = new Date(timestamp);
			return `${date.getFullYear()}.${(date.getMonth() + 1).toString().padStart(2, '0')}.${date.getDate().toString().padStart(2, '0')}`;
		},
		
		// 获取总用餐次数
		getTotalMeals() {
			const stats = this.familyManager?.getStatistics() || {}
			return stats.totalMeals || 0
		},
		
		// 获取喜爱菜品数量
		getFavoriteDishes() {
			const stats = this.familyManager?.getStatistics() || {}
			return stats.favoriteMealsCount || 0
		},
		
		// 导航到用餐记录页面
		navigateToCooking() {
			uni.navigateTo({
				url: '/pages/cooking/cooking'
			})
		},
		
		// 导航到喜爱菜品页面
		navigateToFavorite() {
			uni.navigateTo({
				url: '/pages/favorite/favorite'
			})
		},
		
		// 编辑家庭名称
		async editFamilyName() {
			// 检查权限
			if (this.familyData.currentUserPermission !== 'admin') {
				uni.showToast({
					title: '只有管理员可以修改家庭名称',
					icon: 'none'
				});
				return;
			}
			
			uni.showModal({
				title: '修改家庭名称',
				editable: true,
				placeholderText: this.familyData.familyName,
				success: async (res) => {
					if (res.confirm && res.content) {
						const newName = res.content.trim();
						if (newName === this.familyData.familyName) {
							return;
						}
						
						uni.showLoading({
							title: '修改中...'
						});
						
						try {
							await FamilyAPI.updateFamilySettings(this.currentFamilyId, {
								name: newName
							});
							
							this.familyData.familyName = newName;
							uni.hideLoading();
							uni.showToast({
								title: '修改成功',
								icon: 'success'
							});
							
						} catch (error) {
							uni.hideLoading();
							console.error('修改家庭名称失败:', error);
							uni.showToast({
								title: error.message || '修改失败',
								icon: 'none'
							});
						}
					}
				}
			});
		},
		
		// 显示添加成员弹窗
		showAddMember() {
			// 检查是否有权限邀请成员（管理员权限）
			if (this.familyData.currentUserPermission !== 'admin') {
				uni.showModal({
					title: '没有权限',
					content: '只有管理员才能邀请新成员加入家庭',
					showCancel: false
				});
				return;
			}
			
			// 显示邀请码而不是手动添加
			this.showInviteCode();
		},
		
		// 显示邀请码
		showInviteCode() {
			const inviteCode = this.familyData.inviteCode;
			if (!inviteCode) {
				uni.showToast({
					title: '邀请码获取失败',
					icon: 'none'
				});
				return;
			}
			
			uni.showModal({
				title: '邀请家庭成员',
				content: `邀请码：${inviteCode}\n\n请将此邀请码分享给家人，他们可以在"加入家庭"页面输入邀请码加入您的家庭。`,
				confirmText: '复制邀请码',
				success: (res) => {
					if (res.confirm) {
						uni.setClipboardData({
							data: inviteCode,
							success: () => {
								uni.showToast({
									title: '邀请码已复制',
									icon: 'success'
								});
							}
						});
					}
				}
			});
		},
		
		// 加入家庭功能（通过邀请码）
		async joinFamilyByCode() {
			uni.showModal({
				title: '加入家庭',
				editable: true,
				placeholderText: '请输入6位邀请码',
				success: async (res) => {
					if (res.confirm && res.content) {
						const inviteCode = res.content.trim();
						if (inviteCode.length !== 6) {
							uni.showToast({
								title: '邀请码格式错误',
								icon: 'none'
							});
							return;
						}
						
						// 询问在家庭中的称呼
						uni.showModal({
							title: '设置称呼',
							editable: true,
							placeholderText: '请输入您在家庭中的称呼（如：爸爸、妈妈等）',
							success: async (res2) => {
								if (res2.confirm && res2.content) {
									const displayName = res2.content.trim();
									await this.performJoinFamily(inviteCode, displayName);
								}
							}
						});
					}
				}
			});
		},
		
		// 执行加入家庭
		async performJoinFamily(inviteCode, displayName) {
			uni.showLoading({
				title: '加入中...'
			});
			
			try {
				await familyManager.joinFamily(inviteCode, displayName);
				uni.hideLoading();
				
				uni.showToast({
					title: '加入家庭成功',
					icon: 'success'
				});
				
			} catch (error) {
				uni.hideLoading();
				console.error('加入家庭失败:', error);
				uni.showToast({
					title: error.message || '加入失败',
					icon: 'none'
				});
			}
		},
		
		// 创建新家庭
		async createNewFamily() {
			uni.showModal({
				title: '创建家庭',
				editable: true,
				placeholderText: '请输入家庭名称',
				success: async (res) => {
					if (res.confirm && res.content) {
						const familyName = res.content.trim();
						
						// 询问创建者的称呼
						uni.showModal({
							title: '设置称呼',
							editable: true,
							placeholderText: '请输入您在家庭中的称呼（如：爸爸、妈妈等）',
							success: async (res2) => {
								if (res2.confirm && res2.content) {
									const displayName = res2.content.trim();
									await this.performCreateFamily(familyName, displayName);
								}
							}
						});
					}
				}
			});
		},
		
		// 执行创建家庭
		async performCreateFamily(familyName, displayName) {
			uni.showLoading({
				title: '创建中...'
			});
			
			try {
				await familyManager.createFamily(familyName, displayName);
				uni.hideLoading();
				
				uni.showToast({
					title: '创建家庭成功',
					icon: 'success'
				});
				
			} catch (error) {
				uni.hideLoading();
				console.error('创建家庭失败:', error);
				uni.showToast({
					title: error.message || '创建失败',
					icon: 'none'
				});
			}
		},
		
		// 关系选择器变化（已弃用）
		onRelationChange(e) {
			this.newMember.relation = this.relationOptions[e.detail.value];
		},
		
		// 关闭弹窗（已弃用）
		closeModal() {
			this.showAddMemberModal = false;
		},
		
		// 取消添加成员（已弃用）
		cancelAddMember() {
			this.showAddMemberModal = false;
		},
		
		// 确认添加成员（已弃用 - 现在使用邀请码）
		confirmAddMember() {
			uni.showToast({
				title: '请使用邀请码邀请成员',
				icon: 'none'
			});
			this.showAddMemberModal = false;
		},
		
		// 显示成员详情
		showMemberDetail(member) {
			const isCurrentUser = member.id === this.userInfo.openid;
			const isAdmin = this.familyData.currentUserPermission === 'admin';
			
			let actions = ['查看饮食偏好'];
			
			if (isCurrentUser) {
				actions.push('编辑我的偏好');
			} else if (isAdmin) {
				if (member.role !== 'admin') {
					actions.push('设为管理员');
				}
				actions.push('移除成员');
			}
			
			if (isCurrentUser && !isAdmin) {
				actions.push('退出家庭');
			}
			
			actions.push('取消');
			
			uni.showActionSheet({
				itemList: actions,
				success: async (res) => {
					const action = actions[res.tapIndex];
					
					switch (action) {
						case '查看饮食偏好':
							this.showMemberPreferences(member);
							break;
						case '编辑我的偏好':
							this.editMemberPreferences(member);
							break;
						case '设为管理员':
							await this.transferAdminToMember(member);
							break;
						case '移除成员':
							await this.removeMember(member);
							break;
						case '退出家庭':
							await this.leaveFamily();
							break;
					}
				}
			});
		},
		
		// 转让管理员权限
		async transferAdminToMember(member) {
			uni.showModal({
				title: '转让管理员权限',
				content: `确定要将管理员权限转让给"${member.name}"吗？转让后您将变为普通成员。`,
				success: async (res) => {
					if (res.confirm) {
						uni.showLoading({
							title: '转让中...'
						});
						
						try {
							await FamilyAPI.transferAdmin(this.currentFamilyId, member.id);
							uni.hideLoading();
							
							uni.showToast({
								title: '权限转让成功',
								icon: 'success'
							});
							
							// 重新加载数据
							await this.loadFamilyData();
							
						} catch (error) {
							uni.hideLoading();
							console.error('转让管理员权限失败:', error);
							uni.showToast({
								title: error.message || '转让失败',
								icon: 'none'
							});
						}
					}
				}
			});
		},
		
		// 移除成员
		async removeMember(member) {
			uni.showModal({
				title: '移除成员',
				content: `确定要移除成员"${member.name}"吗？此操作不可撤销。`,
				success: async (res) => {
					if (res.confirm) {
						uni.showLoading({
							title: '移除中...'
						});
						
						try {
							await FamilyAPI.removeFamilyMember(this.currentFamilyId, member.id);
							uni.hideLoading();
							
							uni.showToast({
								title: '移除成员成功',
								icon: 'success'
							});
							
							// 重新加载数据
							await this.loadFamilyData();
							
						} catch (error) {
							uni.hideLoading();
							console.error('移除成员失败:', error);
							uni.showToast({
								title: error.message || '移除失败',
								icon: 'none'
							});
						}
					}
				}
			});
		},
		
		// 退出家庭
		async leaveFamily() {
			uni.showModal({
				title: '退出家庭',
				content: '确定要退出这个家庭吗？退出后您将无法查看家庭信息。',
				success: async (res) => {
					if (res.confirm) {
						uni.showLoading({
							title: '退出中...'
						});
						
						try {
							await FamilyAPI.leaveFamily(this.currentFamilyId);
							uni.hideLoading();
							
							uni.showToast({
								title: '已退出家庭',
								icon: 'success'
							});
							
							// 重新加载数据
							await this.loadFamilyData();
							
						} catch (error) {
							uni.hideLoading();
							console.error('退出家庭失败:', error);
							uni.showToast({
								title: error.message || '退出失败',
								icon: 'none'
							});
						}
					}
				}
			});
		},
		
		// 显示成员偏好
		showMemberPreferences(member) {
			const prefs = member.preferences || {};
			let content = '';
			
			if (prefs.taste && prefs.taste.length > 0) {
				content += `口味偏好：${prefs.taste.join('、')}\n`;
			}
			if (prefs.allergies && prefs.allergies.length > 0) {
				content += `过敏信息：${prefs.allergies.join('、')}\n`;
			}
			if (prefs.dislikes && prefs.dislikes.length > 0) {
				content += `不喜欢：${prefs.dislikes.join('、')}\n`;
			}
			
			if (!content) {
				content = '暂无饮食偏好设置';
			}
			
			uni.showModal({
				title: member.name + ' 的饮食偏好',
				content: content,
				showCancel: false
			});
		},
		
		// 编辑成员偏好
		editMemberPreferences(member) {
			uni.showModal({
				title: '编辑偏好',
				content: '偏好设置功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 移除成员
		removeMember(member) {
			uni.showModal({
				title: '确认移除',
				content: `确定要移除成员"${member.name}"吗？`,
				success: (res) => {
					if (res.confirm) {
						const index = this.familyData.members.findIndex(m => m.id === member.id);
						if (index > -1) {
							this.familyData.members.splice(index, 1);
							uni.setStorageSync('familyData', this.familyData);
							uni.showToast({
								title: '移除成功',
								icon: 'success'
							});
						}
					}
				}
			});
		},
		
		// 设置家庭偏好
		setFamilyPreferences() {
			uni.showModal({
				title: '家庭饮食偏好',
				content: '功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 设置用餐时间
		setMealTimes() {
			uni.showModal({
				title: '用餐时间',
				content: '功能开发中，敬请期待！',
				showCancel: false
			});
		},
		
		// 管理邀请码
		manageFamilyCode() {
			if (!this.currentFamilyId) {
				// 没有家庭，显示创建和加入选项
				uni.showActionSheet({
					itemList: ['创建新家庭', '加入家庭', '取消'],
					success: (res) => {
						if (res.tapIndex === 0) {
							this.createNewFamily();
						} else if (res.tapIndex === 1) {
							this.joinFamilyByCode();
						}
					}
				});
				return;
			}
			
			const familyCode = this.familyData.inviteCode;
			if (!familyCode) {
				uni.showToast({
					title: '邀请码获取失败',
					icon: 'none'
				});
				return;
			}
			
			uni.showModal({
				title: '家庭邀请码',
				content: `邀请码：${familyCode}\n\n分享此邀请码给家人，他们可以通过邀请码加入您的家庭。`,
				confirmText: '复制',
				success: (res) => {
					if (res.confirm) {
						uni.setClipboardData({
							data: familyCode,
							success: () => {
								uni.showToast({
									title: '已复制到剪贴板',
									icon: 'success'
								});
							}
						});
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
	background: #FFF5F8;
	padding-bottom: 40rpx;
}

.family-card {
	background: linear-gradient(135deg, #FF6B95, #FFB6C1);
	margin: 30rpx;
	border-radius: 24rpx;
	padding: 40rpx;
	color: white;
}

.family-header {
	display: flex;
	align-items: center;
	margin-bottom: 30rpx;
}

.family-avatar {
	width: 80rpx;
	height: 80rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 20rpx;
}

.family-icon {
	font-size: 36rpx;
}

.family-info {
	flex: 1;
}

.family-name {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	margin-bottom: 8rpx;
}

.create-time {
	font-size: 24rpx;
	opacity: 0.8;
}

.edit-btn {
	width: 60rpx;
	height: 60rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.edit-icon {
	font-size: 24rpx;
}

.family-stats {
	display: flex;
	justify-content: space-around;
}

.stat-item {
	text-align: center;
}

.stat-number {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	margin-bottom: 8rpx;
}

.stat-label {
	font-size: 24rpx;
	opacity: 0.8;
}

.members-section,
.quick-settings {
	margin: 30rpx;
}

.section-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 20rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.add-member-btn {
	display: flex;
	align-items: center;
	background: #FF6B95;
	color: white;
	padding: 12rpx 20rpx;
	border-radius: 20rpx;
	font-size: 24rpx;
}

.add-icon {
	margin-right: 8rpx;
	font-size: 20rpx;
}

.add-text {
	font-size: 24rpx;
}

.members-list {
	background: white;
	border-radius: 20rpx;
	overflow: hidden;
}

.member-item {
	display: flex;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #F5F5F5;
}

.member-item:last-child {
	border-bottom: none;
}

.member-avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	margin-right: 20rpx;
}

.member-info {
	flex: 1;
}

.member-main {
	display: flex;
	align-items: center;
	margin-bottom: 8rpx;
}

.member-name {
	font-size: 28rpx;
	font-weight: 500;
	color: #333333;
	margin-right: 12rpx;
}

.member-role {
	background: #FF6B95;
	color: white;
	padding: 4rpx 12rpx;
	border-radius: 10rpx;
	font-size: 20rpx;
}

.role-text {
	font-size: 20rpx;
}

.join-time {
	font-size: 22rpx;
	color: #999999;
	margin-bottom: 12rpx;
}

.member-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 8rpx;
}

.tag {
	font-size: 20rpx;
	padding: 4rpx 8rpx;
	border-radius: 8rpx;
}

.preference-tag {
	background: #E3F2FD;
	color: #1976D2;
}

.allergy-tag {
	background: #FFEBEE;
	color: #D32F2F;
}

.member-actions {
	color: #C0C4CC;
}

.action-icon {
	font-size: 24rpx;
}

.settings-list {
	background: white;
	border-radius: 20rpx;
	overflow: hidden;
}

.setting-item {
	display: flex;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #F5F5F5;
}

.setting-item:last-child {
	border-bottom: none;
}

.setting-icon {
	width: 60rpx;
	height: 60rpx;
	background: #FFF0F5;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 20rpx;
}

.icon-text {
	font-size: 28rpx;
}

.setting-info {
	flex: 1;
}

.setting-arrow {
	margin-left: 20rpx;
}

.arrow-icon {
	font-size: 28rpx;
	color: #C0C4CC;
}

.setting-name {
	display: block;
	font-size: 28rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 8rpx;
}

.setting-desc {
	font-size: 22rpx;
	color: #999999;
}

/* 弹窗样式 */
.modal-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.modal-content {
	width: 600rpx;
	background: white;
	border-radius: 20rpx;
	overflow: hidden;
	animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
	from {
		opacity: 0;
		transform: scale(0.8);
	}
	to {
		opacity: 1;
		transform: scale(1);
	}
}

.popup-content {
	width: 600rpx;
	background: white;
	border-radius: 20rpx;
	overflow: hidden;
}

.popup-header {
	padding: 40rpx 30rpx 20rpx;
	text-align: center;
	border-bottom: 1rpx solid #F5F5F5;
}

.popup-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.popup-body {
	padding: 30rpx;
}

.input-group {
	margin-bottom: 30rpx;
}

.input-label {
	display: block;
	font-size: 26rpx;
	color: #333333;
	margin-bottom: 12rpx;
}

.input-field {
	width: 100%;
	height: 80rpx;
	border: 1rpx solid #E5E5E5;
	border-radius: 12rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	box-sizing: border-box;
}

.picker-input {
	width: 100%;
	height: 80rpx;
	border: 1rpx solid #E5E5E5;
	border-radius: 12rpx;
	padding: 0 20rpx;
	display: flex;
	align-items: center;
	justify-content: space-between;
	font-size: 28rpx;
	color: #333333;
	box-sizing: border-box;
}

.picker-arrow {
	color: #C0C4CC;
}

.popup-actions {
	display: flex;
	border-top: 1rpx solid #F5F5F5;
}

.cancel-btn,
.confirm-btn {
	flex: 1;
	height: 88rpx;
	border: none;
	font-size: 28rpx;
	line-height: 88rpx;
}

.cancel-btn {
	background: #F5F5F5;
	color: #666666;
}

.confirm-btn {
	background: #FF6B95;
	color: white;
}
</style>
