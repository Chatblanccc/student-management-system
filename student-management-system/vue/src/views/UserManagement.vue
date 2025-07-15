<template>
  <PermissionWrapper admin-only show-fallback fallback-message="仅管理员可访问用户管理">
    <div class="user-management">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>用户管理</span>
            <el-button type="primary" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon>
              创建用户
            </el-button>
          </div>
        </template>
        
        <!-- 用户列表 -->
        <el-table :data="users" v-loading="loading" stripe>
          <el-table-column prop="username" label="用户名" width="150" />
          <el-table-column prop="email" label="邮箱" width="200" />
          <el-table-column label="姓名" width="150">
            <template #default="scope">
              {{ (scope.row.first_name || '') + ' ' + (scope.row.last_name || '') || '未设置' }}
            </template>
          </el-table-column>
          <el-table-column label="角色" width="120">
            <template #default="scope">
              <el-tag :type="scope.row.is_superuser ? 'danger' : scope.row.is_staff ? 'warning' : 'info'">
                {{ getUserRole(scope.row) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                {{ scope.row.is_active ? '活跃' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="注册时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.date_joined) }}
            </template>
          </el-table-column>
          <el-table-column label="最后登录" width="180">
            <template #default="scope">
              {{ scope.row.last_login ? formatDate(scope.row.last_login) : '从未登录' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
              <el-button 
                size="small" 
                :type="scope.row.is_active ? 'danger' : 'success'"
                @click="toggleUserStatus(scope.row)"
                :disabled="scope.row.id === currentUserId">
                {{ scope.row.is_active ? '禁用' : '启用' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      
      <!-- 创建/编辑用户对话框 -->
      <el-dialog 
        v-model="showCreateDialog" 
        :title="isEditing ? '编辑用户' : '创建用户'" 
        width="500px"
        @closed="resetForm">
        <el-form :model="userForm" :rules="formRules" ref="formRef" label-width="100px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="userForm.username" :disabled="isEditing" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="userForm.password" 
              type="password" 
              show-password
              :placeholder="isEditing ? '留空则不修改密码' : '请输入密码'" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="userForm.email" />
          </el-form-item>
          <el-form-item label="姓" prop="first_name">
            <el-input v-model="userForm.first_name" />
          </el-form-item>
          <el-form-item label="名" prop="last_name">
            <el-input v-model="userForm.last_name" />
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="userForm.role" style="width: 100%">
              <el-option label="普通用户" value="user" />
              <el-option label="管理员" value="admin" />
              <el-option label="超级管理员" value="superuser" />
            </el-select>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitForm" 
            :loading="creating">
            {{ isEditing ? '更新' : '创建' }}
          </el-button>
        </template>
      </el-dialog>
    </div>
  </PermissionWrapper>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import PermissionWrapper from '@/components/PermissionWrapper.vue'
import { getUserList, createUser, updateUser, toggleUserStatus as toggleStatus } from '@/api/user'
import { useUserStore } from '@/utils/userStore'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.state.user?.id)

const users = ref([])
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const isEditing = ref(false)
const editingUserId = ref(null)
const formRef = ref()

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

const getUserRole = (user) => {
  if (user.is_superuser) return '超级管理员'
  if (user.is_staff) return '管理员'
  return '普通用户'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
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

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
</style>