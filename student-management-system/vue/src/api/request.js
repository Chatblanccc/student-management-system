import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/utils/userStore'

// 根据环境确定API基础URL
const getBaseURL = () => {
  // 生产环境使用相对路径（nginx会代理到后端）
  if (import.meta.env.PROD) {
    return '/api'
  }
  // 开发环境使用完整URL
  return 'http://localhost:8000/api'
}

// CSRF token缓存
let csrfToken = null

// 获取CSRF token的函数
const getCSRFToken = async () => {
  if (csrfToken) {
    return csrfToken
  }
  
  try {
    const response = await axios.get(`${getBaseURL()}/student_data/csrf-token/`, {
      withCredentials: true
    })
    csrfToken = response.data.csrfToken
    console.log('获取到CSRF Token:', csrfToken)
    return csrfToken
  } catch (error) {
    console.error('获取CSRF Token失败:', error)
    return null
  }
}

// 创建axios实例
const request = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
  withCredentials: true, // 重要：支持cookies
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器
request.interceptors.request.use(
  async config => {
    // 添加token认证
    const userStore = useUserStore()
    const token = userStore.state.token
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 为POST、PUT、PATCH、DELETE请求添加CSRF token
    if (['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())) {
      const token = await getCSRFToken()
      if (token) {
        config.headers['X-CSRFToken'] = token
        console.log('添加CSRF Token到请求头:', token)
      }
    }
    
    console.log('请求配置:', config)
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 统一处理响应数据
    return response.data
  },
  error => {
    console.error('响应错误:', error)
    
    // 如果是CSRF错误，清除缓存的token并重试
    if (error.response?.status === 403 && 
        error.response?.data?.detail?.includes('CSRF')) {
      console.log('CSRF Token失效，清除缓存')
      csrfToken = null
      // 可以选择自动重试请求
      // return request(error.config)
    }
    
    // 统一错误处理
    let errorMessage = '请求失败'
    
    if (error.response) {
      // 服务器返回了错误状态码
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          errorMessage = data.error || data.message || '请求参数错误'
          break
        case 401:
          errorMessage = '登录已过期，请重新登录'
          // 清除用户状态并跳转到登录页
          const userStore = useUserStore()
          userStore.logout()
          // 如果当前不在登录页，则跳转
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          break
        case 403:
          if (data.detail && data.detail.includes('CSRF')) {
            errorMessage = 'CSRF验证失败，请刷新页面重试'
          } else {
            errorMessage = '没有权限访问该资源'
          }
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        default:
          errorMessage = data.error || data.message || `请求失败 (${status})`
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '网络连接失败，请检查网络设置'
    } else {
      // 其他错误
      errorMessage = error.message || '未知错误'
    }
    
    // 只在非401错误时显示错误消息（401已经在上面处理了）
    if (error.response?.status !== 401) {
      ElMessage.error(errorMessage)
    }
    
    return Promise.reject(error)
  }
)

// 导出获取CSRF Token的函数，以便其他地方使用
export { getCSRFToken }
export default request 