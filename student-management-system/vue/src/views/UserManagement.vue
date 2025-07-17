<template>
  <PermissionWrapper admin-only show-fallback fallback-message="仅管理员可访问用户管理">
    <div class="user-management">
      <!-- 美化后的页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="header-left">
            <div class="title-section">
              <div class="icon-wrapper">
                <el-icon class="page-icon"><UserFilled /></el-icon>
              </div>
              <div class="title-content">
                <h1 class="page-title">用户管理</h1>
                <p class="page-subtitle">管理系统用户账户和权限</p>
              </div>
            </div>
          </div>
          <div class="header-right">
            <el-button type="primary" size="large" class="create-btn" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon>
              创建用户
            </el-button>
          </div>
        </div>
      </div>

      <!-- 美化后的统计卡片 -->
      <div class="stats-section">
        <el-row :gutter="24">
          <el-col :span="6">
            <div class="stat-card total-users">
              <div class="card-content">
                <div class="stat-icon">
                  <el-icon><User /></el-icon>
                </div>
                <div class="stat-details">
                  <div class="stat-number">{{ users.length }}</div>
                  <div class="stat-label">总用户数</div>
                </div>
                <div class="card-bg-pattern"></div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card admin-users">
              <div class="card-content">
                <div class="stat-icon">
                  <el-icon><Star /></el-icon>
                </div>
                <div class="stat-details">
                  <div class="stat-number">{{ adminCount }}</div>
                  <div class="stat-label">管理员</div>
                </div>
                <div class="card-bg-pattern"></div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card active-users">
              <div class="card-content">
                <div class="stat-icon">
                  <el-icon><CircleCheck /></el-icon>
                </div>
                <div class="stat-details">
                  <div class="stat-number">{{ activeCount }}</div>
                  <div class="stat-label">活跃用户</div>
                </div>
                <div class="card-bg-pattern"></div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card inactive-users">
              <div class="card-content">
                <div class="stat-icon">
                  <el-icon><CircleClose /></el-icon>
                </div>
                <div class="stat-details">
                  <div class="stat-number">{{ inactiveCount }}</div>
                  <div class="stat-label">禁用用户</div>
                </div>
                <div class="card-bg-pattern"></div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 美化后的用户表格 -->
      <div class="table-section">
        <div class="table-card">
          <div class="table-header">
            <div class="table-title">
              <h3>用户列表</h3>
              <span class="user-count">共 {{ filteredUsers.length }} 个用户</span>
            </div>
            <div class="table-controls">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索用户名或邮箱"
                class="search-input"
                clearable>
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button class="refresh-btn" @click="loadUsers">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </div>
          
          <!-- 表格容器 -->
          <div class="table-container" v-loading="loading">
            <el-table 
              :data="filteredUsers" 
              stripe
              class="modern-table"
              :header-cell-style="{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
                color: 'white', 
                fontWeight: '600',
                border: 'none'
              }"
              :row-style="{ height: '70px' }">
              
              <!-- 用户信息列 -->
              <el-table-column label="用户" width="280" fixed="left">
                <template #default="scope">
                  <div class="user-cell">
                    <div class="user-avatar-wrapper">
                      <el-avatar 
                        :size="50" 
                        :src="scope.row.avatar" 
                        class="user-avatar">
                        <el-icon><User /></el-icon>
                      </el-avatar>
                      <div class="online-indicator" v-if="scope.row.is_active"></div>
                    </div>
                    <div class="user-info">
                      <div class="user-name">{{ scope.row.username }}</div>
                      <div class="user-email">{{ scope.row.email || '未设置邮箱' }}</div>
                    </div>
                  </div>
                </template>
              </el-table-column>
              
              <!-- 真实姓名列 -->
              <el-table-column label="真实姓名" width="150">
                <template #default="scope">
                  <div class="real-name-cell">
                    {{ (scope.row.first_name || '') + ' ' + (scope.row.last_name || '') || '未设置' }}
                  </div>
                </template>
              </el-table-column>
              
              <!-- 角色列 -->
              <el-table-column label="角色" width="140" align="center">
                <template #default="scope">
                  <el-tag 
                    :class="['role-tag', getRoleClass(scope.row)]"
                    effect="dark">
                    <el-icon class="role-icon">
                      <component :is="getRoleIcon(scope.row)" />
                    </el-icon>
                    {{ getUserRole(scope.row) }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <!-- 状态列 -->
              <el-table-column label="状态" width="120" align="center">
                <template #default="scope">
                  <div class="status-cell">
                    <div :class="['status-indicator', scope.row.is_active ? 'active' : 'inactive']">
                      <el-icon>
                        <component :is="scope.row.is_active ? 'CircleCheck' : 'CircleClose'" />
                      </el-icon>
                      {{ scope.row.is_active ? '活跃' : '禁用' }}
                    </div>
                  </div>
                </template>
              </el-table-column>
              
              <!-- 注册时间列 -->
              <el-table-column label="注册时间" width="180" align="center">
                <template #default="scope">
                  <div class="date-cell">
                    <el-icon class="date-icon"><Calendar /></el-icon>
                    <span>{{ formatDate(scope.row.date_joined) }}</span>
                  </div>
                </template>
              </el-table-column>
              
              <!-- 最后登录列 -->
              <el-table-column label="最后登录" width="180" align="center">
                <template #default="scope">
                  <div class="date-cell" v-if="scope.row.last_login">
                    <el-icon class="date-icon"><Clock /></el-icon>
                    <span>{{ formatDate(scope.row.last_login) }}</span>
                  </div>
                  <el-tag v-else type="info" size="small" class="never-login">从未登录</el-tag>
                </template>
              </el-table-column>
              
              <!-- 操作列 -->
              <el-table-column label="操作" width="200" fixed="right" align="center">
                <template #default="scope">
                  <div class="action-buttons">
                    <el-button 
                      type="primary" 
                      size="small" 
                      class="action-btn edit-btn"
                      @click="editUser(scope.row)">
                      <el-icon><Edit /></el-icon>
                      编辑
                    </el-button>
                    <el-button 
                      :type="scope.row.is_active ? 'danger' : 'success'"
                      size="small" 
                      class="action-btn toggle-btn"
                      @click="toggleUserStatus(scope.row)"
                      :disabled="scope.row.id === currentUserId">
                      <el-icon>
                        <component :is="scope.row.is_active ? 'Lock' : 'Unlock'" />
                      </el-icon>
                      {{ scope.row.is_active ? '禁用' : '启用' }}
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
      
      <!-- 创建/编辑用户对话框 -->
      <el-dialog 
        v-model="showCreateDialog" 
        :title="isEditing ? '编辑用户' : '创建用户'" 
        width="650px"
        class="modern-dialog"
        @closed="resetForm">
        
        <el-form 
          :model="userForm" 
          :rules="formRules" 
          ref="formRef" 
          label-width="120px"
          class="modern-form">
          
          <div class="form-section">
            <h4 class="section-title">账户信息</h4>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input 
                    v-model="userForm.username" 
                    :disabled="isEditing"
                    placeholder="请输入用户名">
                    <template #prefix>
                      <el-icon><User /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="密码" prop="password">
                  <el-input 
                    v-model="userForm.password" 
                    type="password" 
                    show-password
                    :placeholder="isEditing ? '留空则不修改密码' : '请输入密码'">
                    <template #prefix>
                      <el-icon><Lock /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          
          <div class="form-section">
            <h4 class="section-title">个人信息</h4>
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="邮箱" prop="email">
                  <el-input 
                    v-model="userForm.email"
                    placeholder="请输入邮箱地址">
                    <template #prefix>
                      <el-icon><Message /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="姓" prop="first_name">
                  <el-input v-model="userForm.first_name" placeholder="请输入姓" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="名" prop="last_name">
                  <el-input v-model="userForm.last_name" placeholder="请输入名" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          
          <div class="form-section">
            <h4 class="section-title">权限设置</h4>
            <el-form-item label="用户角色" prop="role">
              <el-select v-model="userForm.role" style="width: 100%" size="large">
                <el-option label="普通用户" value="user">
                  <div class="role-option">
                    <el-icon><User /></el-icon>
                    <span>普通用户</span>
                    <small>只能查看和导出数据</small>
                  </div>
                </el-option>
                <el-option label="管理员" value="admin">
                  <div class="role-option">
                    <el-icon><UserFilled /></el-icon>
                    <span>管理员</span>
                    <small>可以管理学生数据和成绩</small>
                  </div>
                </el-option>
                <el-option label="超级管理员" value="superuser">
                  <div class="role-option">
                    <el-icon><Avatar /></el-icon>
                    <span>超级管理员</span>
                    <small>拥有所有权限，包括用户管理</small>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </div>
        </el-form>
        
        <template #footer>
          <div class="dialog-footer">
            <el-button size="large" @click="showCreateDialog = false">取消</el-button>
            <el-button 
              type="primary" 
              size="large"
              @click="submitForm" 
              :loading="creating">
              <el-icon v-if="!creating">
                <component :is="isEditing ? 'Check' : 'Plus'" />
              </el-icon>
              {{ isEditing ? '更新用户' : '创建用户' }}
            </el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </PermissionWrapper>
</template>

<script setup>
import { ref, reactive, onMounted, computed, h } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  User, 
  UserFilled,
  Star,  // 替换 Crown 为 Star
  Edit, 
  Lock, 
  Unlock,
  CircleCheck,
  CircleClose,
  Calendar,
  Clock,
  Search,
  Message,
  Check,
  Avatar,  // 替换 Crown
  Key,     // 用于超级管理员
  Tools,    // 用于普通管理员
  Refresh
} from '@element-plus/icons-vue'
import PermissionWrapper from '@/components/PermissionWrapper.vue'
import { getUserList, createUser, updateUser, toggleUserStatus as toggleStatus } from '@/api/user'
import { useUserStore } from '@/utils/userStore'
import axios from 'axios' // 引入axios

const userStore = useUserStore()
const currentUserId = computed(() => userStore.state.user?.id)

const users = ref([])
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const isEditing = ref(false)
const editingUserId = ref(null)
const formRef = ref()
const searchKeyword = ref('')

// 过滤用户列表
const filteredUsers = computed(() => {
  if (!searchKeyword.value) return users.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(keyword) ||
    (user.email && user.email.toLowerCase().includes(keyword))
  )
})

// 统计数据
const adminCount = computed(() => 
  users.value.filter(user => user.is_staff || user.is_superuser).length
)
const activeCount = computed(() => 
  users.value.filter(user => user.is_active).length
)
const inactiveCount = computed(() => 
  users.value.filter(user => !user.is_active).length
)

const userForm = reactive({
  username: '',
  password: '',
  email: '',
  first_name: '',
  last_name: '',
  role: 'user'
})

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { 
      validator: (rule, value, callback) => {
        if (!isEditing.value && !value) {
          callback(new Error('请输入密码'))
        } else if (value && value.length < 6) {
          callback(new Error('密码长度不能少于 6 个字符'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 修复角色图标函数
const getRoleIcon = (user) => {
  if (user.is_superuser) {
    return Key  // 超级管理员用钥匙图标
  } else if (user.is_staff) {
    return Tools  // 管理员用工具图标
  } else {
    return User  // 普通用户
  }
}

// 修复角色标签类型
const getRoleTagType = (user) => {
  if (user.is_superuser) {
    return 'danger'
  } else if (user.is_staff) {
    return 'warning'
  } else {
    return 'primary'
  }
}

// 修复用户角色显示
const getUserRole = (user) => {
  if (user.is_superuser) {
    return '超级管理员'
  } else if (user.is_staff) {
    return '管理员'
  } else {
    return '普通用户'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) {
    return '今天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diffDays <= 7) {
    return `${diffDays}天前`
  } else {
    return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
}

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const response = await getUserList()
    users.value = response.data || []
    console.log('用户列表加载成功:', users.value.length, '个用户')
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 创建用户
const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    creating.value = true
    
    if (isEditing.value) {
      // 编辑用户
      const updateData = { ...userForm }
      if (!updateData.password) {
        delete updateData.password
      }
      
      const response = await updateUser(editingUserId.value, updateData)
      ElMessage.success(response.message || '用户更新成功')
    } else {
      // 创建用户
      const response = await createUser(userForm)
      ElMessage.success(response.message || '用户创建成功')
    }
    
    showCreateDialog.value = false
    await loadUsers()
    
  } catch (error) {
    console.error('操作失败:', error)
    const errorMsg = error.response?.data?.error || error.message || '操作失败'
    ElMessage.error(errorMsg)
  } finally {
    creating.value = false
  }
}

// 编辑用户
const editUser = (user) => {
  isEditing.value = true
  editingUserId.value = user.id
  
  // 填充表单
  Object.assign(userForm, {
    username: user.username,
    password: '',
    email: user.email || '',
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    role: user.is_superuser ? 'superuser' : (user.is_staff ? 'admin' : 'user')
  })
  
  showCreateDialog.value = true
}

// 切换用户状态
const toggleUserStatus = async (user) => {
  try {
    const action = user.is_active ? '禁用' : '启用'
    await ElMessageBox.confirm(
      `确定要${action}用户"${user.username}"吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await toggleStatus(user.id)
    ElMessage.success(response.message || '操作成功')
    await loadUsers()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换用户状态失败:', error)
      const errorMsg = error.response?.data?.error || error.message || '操作失败'
      ElMessage.error(errorMsg)
    }
  }
}

// 重置表单
const resetForm = () => {
  isEditing.value = false
  editingUserId.value = null
  Object.assign(userForm, {
    username: '',
    password: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'user'
  })
  
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 表格列配置
const tableColumns = ref([
  {
    key: 'user_info',
    title: '用户',
    width: 200,
    fixed: 'left',
    cellRenderer: ({ rowData }) => {
      return h('div', { class: 'user-info' }, [
        h('el-avatar', {
          size: 40,
          src: rowData.avatar || '', // 添加默认值
          class: 'user-avatar'
        }, rowData.avatar ? null : h('el-icon', null, h(User))),
        h('div', { class: 'user-details' }, [
          h('div', { class: 'user-name' }, rowData.username || '未知用户'),
          h('div', { class: 'user-email' }, rowData.email || '未设置邮箱')
        ])
      ])
    }
  },
  {
    key: 'real_name',
    title: '真实姓名',
    dataKey: 'first_name',
    width: 120,
    cellRenderer: ({ rowData }) => {
      const realName = (rowData.first_name || '') + ' ' + (rowData.last_name || '') || '未设置'
      return h('span', { class: 'real-name' }, realName)
    }
  },
  {
    key: 'role',
    title: '角色',
    dataKey: 'is_superuser',
    width: 120,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('el-tag', {
        type: getRoleTagType(rowData),
        effect: 'dark',
        class: 'role-tag'
      }, {
        default: () => [
          h('el-icon', { class: 'role-icon' }, {
            default: () => h(getRoleIcon(rowData))
          }),
          getUserRole(rowData)
        ]
      })
    }
  },
  {
    key: 'status',
    title: '状态',
    dataKey: 'is_active',
    width: 100,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('el-tag', {
        type: rowData.is_active ? 'success' : 'danger',
        effect: 'dark',
        class: 'status-tag'
      }, {
        default: () => [
          h('el-icon', {}, {
            default: () => h(rowData.is_active ? CircleCheck : CircleClose)
          }),
          rowData.is_active ? '活跃' : '禁用'
        ]
      })
    }
  },
  {
    key: 'date_joined',
    title: '注册时间',
    dataKey: 'date_joined',
    width: 160,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('div', { class: 'date-info' }, [
        h('el-icon', { class: 'date-icon' }, { default: () => h(Calendar) }),
        h('span', {}, formatDate(rowData.date_joined))
      ])
    }
  },
  {
    key: 'last_login',
    title: '最后登录',
    dataKey: 'last_login',
    width: 160,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      if (rowData.last_login) {
        return h('div', { class: 'date-info' }, [
          h('el-icon', { class: 'date-icon' }, { default: () => h(Clock) }),
          h('span', {}, formatDate(rowData.last_login))
        ])
      } else {
        return h('el-tag', { type: 'info', size: 'small' }, '从未登录')
      }
    }
  },
  {
    key: 'actions',
    title: '操作',
    width: 180,
    fixed: 'right',
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('div', { class: 'action-buttons' }, [
        h('el-button', {
          type: 'primary',
          size: 'small',
          plain: true,
          onClick: () => editUser(rowData)
        }, {
          default: () => [
            h('el-icon', {}, { default: () => h(Edit) }),
            '编辑'
          ]
        }),
        h('el-button', {
          type: rowData.is_active ? 'danger' : 'success',
          size: 'small',
          plain: true,
          disabled: rowData.id === currentUserId.value,
          onClick: () => toggleUserStatus(rowData)
        }, {
          default: () => [
            h('el-icon', {}, {
              default: () => h(rowData.is_active ? Lock : Unlock)
            }),
            rowData.is_active ? '禁用' : '启用'
          ]
        })
      ])
    }
  }
])

// 处理行点击事件
const handleRowClick = (rowData) => {
  console.log('点击行:', rowData)
  // 可以添加行点击逻辑
}

onMounted(() => {
  loadUsers()
})

// 添加角色样式类方法
const getRoleClass = (user) => {
  if (user.is_superuser) return 'super-admin'
  if (user.is_staff) return 'admin'
  return 'user'
}
</script>

<style scoped>
/* 调整整体布局尺寸 */
.user-management {
  padding: 16px;
  background: #f8fafc;
}

/* 压缩头部区域 */
.header-content {
  padding: 20px 24px;
}
.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
}
.page-title {
  font-size: 24px;
}
.page-subtitle {
  font-size: 14px;
}

/* 缩小统计卡片 */
.stat-card {
  height: 120px;
  border-radius: 12px;
}
.stat-icon {
  width: 50px;
  height: 50px;
  font-size: 24px;
}
.stat-number {
  font-size: 28px;
}
.stat-label {
  font-size: 13px;
}

/* 紧凑表格样式 */
.table-header {
  padding: 16px 24px;
}
.table-title h3 {
  font-size: 18px;
}

/* 调整表格列宽 */
.modern-table {
  width: 100% !important;
}
:deep(.el-table__row) {
  height: 56px;
}
:deep(.el-table__cell) {
  padding: 8px 0;
}

/* 压缩用户信息列 */
.user-cell {
  gap: 12px;
}
.user-avatar {
  width: 40px;
  height: 40px;
}
.user-name {
  font-size: 14px;
}
.user-email {
  font-size: 12px;
}

/* 调整操作按钮尺寸 */
.action-btn {
  padding: 6px 12px;
  font-size: 12px;
}

/* 紧凑对话框样式 */
.modern-dialog {
  --el-dialog-padding-primary: 20px;
}
.modern-form {
  padding: 0 20px;
}
.form-section {
  margin-bottom: 16px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .header-content {
    padding: 16px;
  }
  .stat-card {
    height: 100px;
    margin-bottom: 8px;
  }
  .stat-icon {
    width: 40px;
    height: 40px;
  }
  .stat-number {
    font-size: 24px;
  }
}
</style>