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
            <img src="/logo_login.png" alt="Logo" class="logo-image">
          </div>
          <div class="logo-glow"></div>
        </div>
        <h1 class="system-title">Jnua学籍管理系统</h1>
        <!-- 删除了 welcome-text -->
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
            <label class="input-label">
              <el-icon class="label-icon"><User /></el-icon>
              用户名
            </label>
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="default"
              clearable
              class="custom-input"
            />
          </div>
        </el-form-item>
        
        <el-form-item prop="password" class="form-item-custom">
          <div class="input-container">
            <label class="input-label">
              <el-icon class="label-icon"><Lock /></el-icon>
              密码
            </label>
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="default"
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
            size="default" 
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
import { User, Lock } from '@element-plus/icons-vue'
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
  width: 60px; /* 缩小 */
  height: 60px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 45px; /* 缩小 */
  height: 45px;
  top: 60%;
  left: 80%;
  animation-delay: 2s;
}

.shape-3 {
  width: 90px; /* 缩小 */
  height: 90px;
  top: 80%;
  left: 20%;
  animation-delay: 4s;
}

.shape-4 {
  width: 30px; /* 缩小 */
  height: 30px;
  top: 10%;
  left: 70%;
  animation-delay: 1s;
}

.shape-5 {
  width: 75px; /* 缩小 */
  height: 75px;
  top: 40%;
  left: 5%;
  animation-delay: 3s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(180deg); } /* 减少浮动距离 */
}

/* 登录卡片 - 调整为更紧凑的尺寸 */
.login-card {
  width: 100%;
  max-width: 420px; /* 减小宽度 */
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px; /* 减小圆角 */
  padding: 35px 35px; /* 减少内边距 */
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.12), /* 减小阴影 */
    0 0 0 1px rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 2;
  animation: cardSlideIn 0.8s ease-out;
}

@keyframes cardSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px); /* 减少移动距离 */
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 标题区域 - 更紧凑 */
.login-header {
  text-align: center;
  margin-bottom: 25px; /* 减少间距 */
}

.logo-container {
  position: relative;
  display: inline-block;
  margin-bottom: 15px; /* 减少间距 */
}

.logo-circle {
  width: 65px; /* 缩小Logo */
  height: 65px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3); /* 减小阴影 */
  animation: logoFloat 3s ease-in-out infinite;
  overflow: hidden; /* 确保图片不会溢出圆形容器 */
}

/* 🎨 新增：Logo图片样式 */
.logo-image {
  width: 45px; /* 调整图片大小 */
  height: 45px;
  object-fit: contain; /* 保持图片比例 */
  filter: brightness(0) invert(1); /* 将图片转为白色 */
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-3px); } /* 减少浮动距离 */
}

.logo-glow {
  position: absolute;
  top: -3px; /* 减小发光效果 */
  left: -3px;
  right: -3px;
  bottom: -3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  opacity: 0.3;
  z-index: -1;
  animation: glowPulse 2s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(1.03); } /* 减小缩放 */
}

.system-title {
  font-size: 22px; /* 缩小字体 */
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 12px; /* 减少间距 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-underline {
  width: 40px; /* 缩小下划线 */
  height: 2px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 0 auto;
  border-radius: 2px;
}

/* 表单样式 */
.login-form {
  margin-bottom: 25px; /* 减少间距 */
}

.form-item-custom {
  margin-bottom: 20px; /* 减少间距 */
}

.input-container {
  position: relative;
  width: 100%;
}

/* 输入框标签样式 - 更小 */
.input-label {
  display: flex;
  align-items: center;
  margin-bottom: 8px; /* 减少间距 */
  font-size: 13px; /* 缩小字体 */
  font-weight: 600;
  color: #4a5568;
  gap: 5px; /* 减少间距 */
}

.label-icon {
  color: #667eea;
  font-size: 14px; /* 缩小图标 */
}

/* 🎨 优化后的输入框样式 - 更紧凑 */
.custom-input {
  width: 100%;
}

.custom-input :deep(.el-input__wrapper) {
  width: 100%;
  background: rgba(248, 250, 252, 0.8);
  border: 1px solid rgba(226, 232, 240, 0.6);
  border-radius: 10px; /* 缩小圆角 */
  padding: 12px 16px; /* 减少内边距 */
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  min-height: 40px; /* 减少最小高度 */
}

.custom-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.3);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08); /* 减小阴影 */
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.08); /* 减小聚焦阴影 */
  background: rgba(255, 255, 255, 0.95);
}

.custom-input :deep(.el-input__inner) {
  color: #2d3748;
  font-weight: 500;
  font-size: 14px; /* 缩小字体 */
  width: 100%;
}

.custom-input :deep(.el-input__inner::placeholder) {
  color: #a0aec0;
  font-weight: 400;
}

/* 复选框样式 - 改为一行显示 */
.checkbox-container {
  margin-bottom: 25px; /* 减少间距 */
}

.checkbox-group {
  display: flex;
  flex-direction: row; /* 🎨 改为横向排列 */
  justify-content: space-between; /* 🎨 两端对齐 */
  align-items: center;
  gap: 15px; /* 🎨 设置合适的间距 */
}

.custom-checkbox {
  flex: 1; /* 🎨 让两个复选框平均分配空间 */
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
  font-size: 13px; /* 缩小字体 */
  font-weight: 500;
}

/* 登录按钮 - 更紧凑 */
.login-button {
  width: 100%;
  height: 42px; /* 减少高度 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px; /* 缩小圆角 */
  font-size: 14px; /* 缩小字体 */
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
  transform: translateY(-1px); /* 减少位移 */
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3); /* 减小阴影 */
}

.login-button:active {
  transform: translateY(0);
}

/* 底部区域 */
.login-footer {
  text-align: center;
  position: relative;
  padding-top: 20px; /* 减少间距 */
}

.footer-decoration {
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
  margin-bottom: 15px; /* 减少间距 */
}

.version-info {
  color: #7f8c8d;
  font-size: 12px; /* 缩小字体 */
  margin-bottom: 4px; /* 减少间距 */
  font-weight: 500;
}

.copyright {
  color: #bdc3c7;
  font-size: 11px; /* 缩小字体 */
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    max-width: 340px; /* 调整移动端宽度 */
    padding: 30px 30px; /* 减少内边距 */
    margin: 0 15px;
  }
  
  .system-title {
    font-size: 20px; /* 缩小字体 */
  }
  
  .logo-circle {
    width: 55px; /* 缩小Logo */
    height: 55px;
  }
  
  .logo-image {
    width: 35px; /* 移动端缩小图片 */
    height: 35px;
  }
  
  /* 🎨 移动端复选框调整 */
  .checkbox-group {
    flex-direction: column; /* 移动端改为垂直排列 */
    align-items: flex-start;
    gap: 10px;
  }
  
  .custom-checkbox {
    flex: none; /* 移动端取消flex */
  }
}

@media (max-width: 480px) {
  .login-card {
    max-width: 300px;
    padding: 25px 20px; /* 减少内边距 */
  }
  
  .system-title {
    font-size: 18px; /* 缩小字体 */
  }
  
  .logo-image {
    width: 30px; /* 小屏幕进一步缩小 */
    height: 30px;
  }
}
</style> 