<template>
  <div class="login-container">
    <!-- 动态背景装饰 -->
    <div class="background-decoration">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
        <div class="shape shape-5"></div>
      </div>
    </div>
    
    <div class="login-card">
      <div class="login-header">
        <div class="logo-container">
          <div class="logo-circle">
            <el-icon size="50" color="#ffffff">
              <School />
            </el-icon>
          </div>
          <div class="logo-glow"></div>
        </div>
        <h1 class="system-title">Jnua学籍管理系统</h1>
        <p class="welcome-text">Welcome to Student Management System</p>
        <div class="title-underline"></div>
      </div>
      
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username" class="form-item-custom">
          <div class="input-container">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              size="large"
              clearable
              class="custom-input"
            />
          </div>
        </el-form-item>
        
        <el-form-item prop="password" class="form-item-custom">
          <div class="input-container">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              size="large"
              show-password
              class="custom-input"
              @keyup.enter="handleLogin"
            />
          </div>
        </el-form-item>
        
        <el-form-item class="checkbox-container">
          <div class="checkbox-group">
            <el-checkbox v-model="loginForm.rememberUsername" class="custom-checkbox">
              <span class="checkbox-text">记住用户名</span>
            </el-checkbox>
            <el-checkbox v-model="loginForm.rememberLogin" class="custom-checkbox">
              <span class="checkbox-text">保持登录状态</span>
            </el-checkbox>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            <span v-if="!loading">登录系统</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <div class="footer-decoration"></div>
        <p class="version-info">学生学籍管理系统 v1.0</p>
        <p class="copyright">© 2024 Jnua. All rights reserved.</p>
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
/* 主容器 */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 背景动画 */
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 浮动装饰形状 */
.background-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 60px;
  height: 60px;
  top: 60%;
  left: 80%;
  animation-delay: 2s;
}

.shape-3 {
  width: 120px;
  height: 120px;
  top: 80%;
  left: 20%;
  animation-delay: 4s;
}

.shape-4 {
  width: 40px;
  height: 40px;
  top: 10%;
  left: 70%;
  animation-delay: 1s;
}

.shape-5 {
  width: 100px;
  height: 100px;
  top: 40%;
  left: 5%;
  animation-delay: 3s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

/* 登录卡片 */
.login-card {
  width: 100%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 50px 40px;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 2;
  animation: cardSlideIn 0.8s ease-out;
}

@keyframes cardSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 标题区域 */
.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-container {
  position: relative;
  display: inline-block;
  margin-bottom: 25px;
}

.logo-circle {
  width: 90px;
  height: 90px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
}

.logo-glow {
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  opacity: 0.3;
  z-index: -1;
  animation: glowPulse 2s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.05); }
}

.system-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-text {
  color: #7f8c8d;
  font-size: 14px;
  margin-bottom: 20px;
  font-weight: 400;
}

.title-underline {
  width: 50px;
  height: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 0 auto;
  border-radius: 2px;
}

/* 表单样式 */
.login-form {
  margin-bottom: 30px;
}

.form-item-custom {
  margin-bottom: 25px;
}

.input-container {
  position: relative;
}

.custom-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.custom-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.4);
  background: rgba(255, 255, 255, 0.9);
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.95);
}

.custom-input :deep(.el-input__inner) {
  color: #2c3e50;
  font-weight: 500;
}

.custom-input :deep(.el-input__inner::placeholder) {
  color: #95a5a6;
}

/* 复选框样式 */
.checkbox-container {
  margin-bottom: 30px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.custom-checkbox :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #667eea;
  border-color: #667eea;
}

.custom-checkbox :deep(.el-checkbox__inner:hover) {
  border-color: #667eea;
}

.checkbox-text {
  color: #5a6c7d;
  font-size: 14px;
  font-weight: 500;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.login-button:hover::before {
  left: 100%;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

/* 底部区域 */
.login-footer {
  text-align: center;
  position: relative;
  padding-top: 25px;
}

.footer-decoration {
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
  margin-bottom: 20px;
}

.version-info {
  color: #7f8c8d;
  font-size: 13px;
  margin-bottom: 5px;
  font-weight: 500;
}

.copyright {
  color: #bdc3c7;
  font-size: 12px;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    max-width: 350px;
    padding: 40px 30px;
    margin: 0 15px;
  }
  
  .system-title {
    font-size: 24px;
  }
  
  .logo-circle {
    width: 70px;
    height: 70px;
  }
  
  .logo-circle .el-icon {
    font-size: 35px;
  }
}

@media (max-width: 480px) {
  .login-card {
    max-width: 300px;
    padding: 30px 20px;
  }
  
  .system-title {
    font-size: 22px;
  }
  
  .checkbox-group {
    gap: 8px;
  }
}
</style> 