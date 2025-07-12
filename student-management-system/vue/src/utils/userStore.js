import { reactive } from 'vue'

// 简单的响应式用户状态管理
const state = reactive({
  user: null,
  token: null,
  isLoggedIn: false
})

// 存储类型配置
const STORAGE_TYPE = {
  SESSION: 'session',  // 会话存储（关闭浏览器清除）
  LOCAL: 'local'       // 本地存储（永久保存）
}

// 获取存储对象
const getStorage = (type = STORAGE_TYPE.SESSION) => {
  return type === STORAGE_TYPE.LOCAL ? localStorage : sessionStorage
}

// 检查token是否过期
const isTokenExpired = (token) => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const currentTime = Date.now() / 1000
    return payload.exp < currentTime
  } catch (error) {
    console.error('Token解析失败:', error)
    return true
  }
}

// 从存储恢复状态
const initializeStore = () => {
  console.log('🔄 初始化用户状态...')
  
  // 🔥 关键修复：只从 sessionStorage 恢复
  let token = sessionStorage.getItem('token')
  let user = sessionStorage.getItem('user')
  
  // 🔥 只有在明确标记"记住登录"时才从 localStorage 恢复
  const shouldRememberLogin = localStorage.getItem('shouldRememberLogin') === 'true'
  
  if ((!token || !user) && shouldRememberLogin) {
    console.log('📖 从localStorage恢复登录状态（用户选择了记住登录）')
    token = localStorage.getItem('token')
    user = localStorage.getItem('user')
    
    // 同步到sessionStorage
    if (token && user) {
      sessionStorage.setItem('token', token)
      sessionStorage.setItem('user', user)
    }
  }
  
  if (token && user) {
    try {
      // 检查token是否过期
      if (isTokenExpired(token)) {
        console.log('⏰ Token已过期，清除登录状态')
        clearAllStorage()
        return
      }
      
      state.token = token
      state.user = JSON.parse(user)
      state.isLoggedIn = true
      
      console.log('✅ 成功恢复登录状态:', state.user.username)
    } catch (error) {
      console.error('❌ 恢复用户状态失败:', error)
      clearAllStorage()
    }
  } else {
    console.log('🚫 没有找到有效的登录状态')
  }
}

// 设置用户信息
const setUser = (user, rememberMe = false) => {
  state.user = user
  state.isLoggedIn = true
  
  // 总是存储到 sessionStorage
  sessionStorage.setItem('user', JSON.stringify(user))
  
  // 根据用户选择决定是否存储到 localStorage
  if (rememberMe) {
    localStorage.setItem('user', JSON.stringify(user))
    localStorage.setItem('shouldRememberLogin', 'true')
    console.log('💾 已保存到localStorage（记住登录）')
  } else {
    // 清除localStorage中的登录状态标记
    localStorage.removeItem('shouldRememberLogin')
    console.log('🗑️ 不记住登录状态')
  }
}

// 设置token
const setToken = (token, rememberMe = false) => {
  state.token = token
  
  // 总是存储到 sessionStorage
  sessionStorage.setItem('token', token)
  
  // 根据用户选择决定是否存储到 localStorage
  if (rememberMe) {
    localStorage.setItem('token', token)
  }
}

// 清除所有存储
const clearAllStorage = () => {
  state.user = null
  state.token = null
  state.isLoggedIn = false
  
  // 清除所有存储
  sessionStorage.removeItem('user')
  sessionStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  localStorage.removeItem('shouldRememberLogin')
  
  console.log('🧹 已清除所有登录状态')
}

// 登出
const logout = () => {
  console.log('👋 用户退出登录')
  clearAllStorage()
}

// 检查登录状态
const checkLoginStatus = () => {
  if (state.token && isTokenExpired(state.token)) {
    console.log('⏰ Token已过期，自动退出')
    clearAllStorage()
    return false
  }
  return state.isLoggedIn
}

// 导出store
export const useUserStore = () => {
  return {
    state,
    setUser,
    setToken,
    logout,
    clearAllStorage,
    checkLoginStatus
  }
}

// 初始化store
initializeStore() 