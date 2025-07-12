<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <el-icon size="40" color="#409EFF">
            <School />
          </el-icon>
        </div>
        <h2>Jnua学籍管理系统</h2>
        <p>欢迎使用Jnua学籍管理系统</p>
      </div>
      
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <el-checkbox v-model="loginForm.rememberUsername">
              记住用户名
            </el-checkbox>
            <el-checkbox v-model="loginForm.rememberLogin">
              保持登录状态
            </el-checkbox>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            style="width: 100%"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>学生学籍管理系统 v1.0</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { School, User, Lock } from '@element-plus/icons-vue'
import { login } from '@/api/auth'
import { useUserStore } from '@/utils/userStore'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref()
const loading = ref(false)

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
  rememberUsername: false,  // 记住用户名
  rememberLogin: false      // 保持登录状态
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    
    const response = await login({
      username: loginForm.username,
      password: loginForm.password
    })
    
    console.log('登录响应:', response)
    
    // 🔥 关键修复：正确传递 rememberMe 参数
    userStore.setUser(response.user, loginForm.rememberLogin)
    userStore.setToken(response.token, loginForm.rememberLogin)
    
    // 记住用户名功能
    if (loginForm.rememberUsername) {
      localStorage.setItem('rememberedUsername', loginForm.username)
    } else {
      localStorage.removeItem('rememberedUsername')
    }
    
    // 根据用户选择显示不同的成功消息
    if (loginForm.rememberLogin) {
      ElMessage.success('登录成功！已保持登录状态')
    } else {
      ElMessage.success('登录成功！')
    }
    
    router.push('/manage/home')
    
  } catch (error) {
    console.error('登录失败:', error)
    const errorMsg = error.response?.data?.error || 
                     error.response?.data?.message || 
                     error.message ||
                     '登录失败，请检查用户名和密码'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 页面加载时恢复记住的用户名
onMounted(() => {
  const rememberedUsername = localStorage.getItem('rememberedUsername')
  if (rememberedUsername) {
    loginForm.username = rememberedUsername
    loginForm.rememberUsername = true
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  margin-bottom: 20px;
}

.login-header h2 {
  color: #303133;
  margin-bottom: 10px;
  font-weight: 600;
}

.login-header p {
  color: #909399;
  font-size: 14px;
}

.login-form {
  margin-bottom: 20px;
}

.login-form .el-form-item {
  margin-bottom: 24px;
}

.login-footer {
  text-align: center;
  color: #909399;
  font-size: 12px;
  border-top: 1px solid #f0f0f0;
  padding-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    margin: 0 20px;
    padding: 30px 20px;
  }
}
</style> 