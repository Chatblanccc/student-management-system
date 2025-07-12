import axios from 'axios'
import request from './request'

// 根据环境确定API基础URL（与request.js保持一致）
const getBaseURL = () => {
  // 生产环境使用相对路径（nginx会代理到后端）
  if (import.meta.env.PROD) {
    return '/api'
  }
  // 开发环境使用完整URL
  return 'http://localhost:8000/api'
}

// 创建axios实例
const api = axios.create({
  baseURL: `${getBaseURL()}/student`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 学生数据相关API
export const studentAPI = {
  // 导入数据 - 使用原有的直接axios方式（因为需要multipart/form-data）
  importData(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    return axios({
      method: 'post',
      url: `${getBaseURL()}/student_data/import/`,
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 30000, // 导入可能需要更长时间
    })
  },

  // 获取学生数据列表
  getStudentList(params = {}) {
    return request({
      url: '/student_data/list/',
      method: 'get',
      params
    })
  },

  // 获取导入日志
  getImportLogs() {
    return request({
      url: '/student_data/logs/',
      method: 'get'
    })
  },

  // 批量删除数据
  deleteStudents(ids) {
    return request({
      url: '/student_data/delete/',
      method: 'delete',
      data: { ids }
    })
  },

  // 获取单个学生详细信息
  getStudentDetail(id) {
    return request({
      url: `/student_data/detail/${id}/`,
      method: 'get'
    })
  },

  // 更新学生数据
  updateStudent(id, data) {
    return request({
      url: `/student_data/update/${id}/`,
      method: 'put',
      data
    })
  },

  // 转学相关API
  transferIn: (data) => {
    return request({
      url: '/student_data/transfer/in/',
      method: 'post',
      data
    })
  },
  
  // 新增转出API
  transferOut: (data) => {
    console.log('发送转出请求:', data)
    return request.post('/student_data/transfer/out/', data)
        .then(response => {
            console.log('转出API响应:', response)
            return response
        })
        .catch(error => {
            console.error('转出API错误:', error)
            throw error
        })
  },
  
  getTransferRecords: (params) => {
    return request({
      url: '/student_data/transfer/records/',
      method: 'get',
      params
    })
  },
  
  getTransferRecordDetail: (recordId) => {
    return request({
      url: `/student_data/transfer/records/${recordId}/`,
      method: 'get'
    })
  },

  // 更新转学记录
  updateTransferRecord: (recordId, data) => {
    console.log('更新转学记录:', recordId, data)
    return request({
      url: `/student_data/transfer/records/${recordId}/update/`,
      method: 'put',
      data
    })
  },

  // 获取仪表盘统计数据
  getDashboardStats(period = 'month') {
    return request({
      url: '/student_data/dashboard/stats/',
      method: 'get',
      params: { period }
    })
  },

  // 根据时间周期获取趋势数据
  getTrendData(period = 'month') {
    return request({
      url: '/student_data/dashboard/stats/',
      method: 'get',
      params: { period }
    })
  },

  // 休学申请 - 修正URL路径
  submitSuspend: (data) => {
    return request({
      url: '/student_data/student/suspend/',  // 修改这里，去掉 /api/ 前缀
      method: 'post',
      data
    })
  },

  // 复学申请 - 修正URL路径
  submitResume: (data) => {
    return request({
      url: '/student_data/student/resume/',   // 修改这里，去掉 /api/ 前缀
      method: 'post',
      data
    })
  },

  // 获取休学学生列表 - 修正URL路径
  getSuspendedStudents: (params) => {
    return request({
      url: '/student_data/student/suspended/', // 修改这里，去掉 /api/ 前缀
      method: 'get',
      params
    })
  }
}

// 兼容性导出（如果其他地方还在使用旧的导出方式）
export default studentAPI
