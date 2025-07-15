import request from './request'

// 获取用户列表
export const getUserList = () => {
  return request({
    url: '/student_data/users/',
    method: 'get'
  })
}

// 创建用户
export const createUser = (data) => {
  return request({
    url: '/student_data/users/',
    method: 'post',
    data
  })
}

// 获取用户详情
export const getUserDetail = (userId) => {
  return request({
    url: `/student_data/users/${userId}/`,
    method: 'get'
  })
}

// 更新用户信息
export const updateUser = (userId, data) => {
  return request({
    url: `/student_data/users/${userId}/`,
    method: 'put',
    data
  })
}

// 切换用户状态（启用/禁用）
export const toggleUserStatus = (userId) => {
  return request({
    url: `/student_data/users/${userId}/toggle-status/`,
    method: 'post'
  })
} 