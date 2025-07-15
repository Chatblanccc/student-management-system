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
        <el-table :data="users" v-loading="loading">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="first_name" label="姓名" />
          <el-table-column label="角色">
            <template #default="scope">
              <el-tag :type="scope.row.is_superuser ? 'danger' : scope.row.is_staff ? 'warning' : 'info'">
                {{ getUserRole(scope.row) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                {{ scope.row.is_active ? '活跃' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="toggleUserStatus(scope.row)">
                {{ scope.row.is_active ? '禁用' : '启用' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      
      <!-- 创建/编辑用户对话框 -->
      <el-dialog v-model="showCreateDialog" title="创建用户" width="500px">
        <el-form :model="userForm" label-width="100px">
          <el-form-item label="用户名" required>
            <el-input v-model="userForm.username" />
          </el-form-item>
          <el-form-item label="密码" required>
            <el-input v-model="userForm.password" type="password" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="userForm.email" />
          </el-form-item>
          <el-form-item label="姓名">
            <el-input v-model="userForm.first_name" />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="userForm.role" style="width: 100%">
              <el-option label="普通用户" value="user" />
              <el-option label="管理员" value="admin" />
              <el-option label="超级管理员" value="superuser" />
            </el-select>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createUser" :loading="creating">创建</el-button>
        </template>
      </el-dialog>
    </div>
  </PermissionWrapper>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import PermissionWrapper from '@/components/PermissionWrapper.vue'

const users = ref([])
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)

const userForm = ref({
  username: '',
  password: '',
  email: '',
  first_name: '',
  role: 'user'
})

const getUserRole = (user) => {
  if (user.is_superuser) return '超级管理员'
  if (user.is_staff) return '管理员'
  return '普通用户'
}

// 这里需要实现相应的API调用
const loadUsers = async () => {
  // 实现用户列表加载
}

const createUser = async () => {
  // 实现用户创建
}

const editUser = (user) => {
  // 实现用户编辑
}

const toggleUserStatus = async (user) => {
  // 实现用户状态切换
}

onMounted(() => {
  loadUsers()
})
</script>