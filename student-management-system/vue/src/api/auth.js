import request from './request'
import { encryptPassword } from '@/utils/crypto'

// 获取CSRF Token
export const getCSRFToken = () => {
  return request({
    url: '/student_data/csrf-token/',
    method: 'get'
  })
}

// 登录API - 使用加密密码
export const login = (data) => {
  // 加密密码
  const encryptedData = encryptPassword(data.password)
  
  console.log('🔐 密码已加密，Network面板中不会显示明文密码')
  
  return request({
    url: '/student_data/auth/login/',
    method: 'post',
    data: {
      username: data.username,
      // 发送加密后的密码数据
      encryptedPassword: encryptedData.encryptedPassword,
      iv: encryptedData.iv,
      timestamp: encryptedData.timestamp,
      // 标识这是加密请求
      isEncrypted: true
    }
  })
}

// 登出API
export const logout = () => {
  return request({
    url: '/student_data/auth/logout/',
    method: 'post'
  })
}

// 获取用户信息API
export const getUserInfo = () => {
  return request({
    url: '/student_data/auth/user/',
    method: 'get'
  })
}

// 刷新token API
export const refreshToken = (refreshToken) => {
  return request({
    url: '/auth/refresh/',
    method: 'post',
    data: { refresh: refreshToken }
  })
} 