import request from './request'

export const gradeAPI = {
  // 获取科目列表
  getSubjects() {
    return request({
      url: '/student_data/subjects/',
      method: 'get'
    })
  },

  // 创建科目
  createSubject(data) {
    return request({
      url: '/student_data/subjects/',
      method: 'post',
      data
    })
  },

  // 获取考试列表
  getExams(params = {}) {
    const cleanParams = {}
    Object.keys(params).forEach(key => {
      if (params[key] !== '' && params[key] !== null && params[key] !== undefined) {
        cleanParams[key] = params[key]
      }
    })
    
    return request({
      url: '/student_data/exams/',
      method: 'get',
      params: cleanParams
    })
  },

  // 创建考试
  createExam(data) {
    return request({
      url: '/student_data/exams/',
      method: 'post',
      data
    })
  },

  // 获取成绩列表
  getGrades(params = {}) {
    return request({
      url: '/student_data/grades/',
      method: 'get',
      params
    })
  },

  // 创建成绩记录
  createGrade(data) {
    return request({
      url: '/student_data/grades/create/',
      method: 'post',
      data
    })
  },

  // 获取成绩分析
  getGradeAnalysis(params = {}) {
    return request({
      url: '/student_data/grades/analysis/',
      method: 'get',
      params
    })
  },

  // ======== 以下是新的横向格式API（保留） ========

  // 横向成绩查询
  getGradeMatrix(params = {}) {
    return request({
      url: '/student_data/grades/matrix/',
      method: 'get',
      params
    })
  },

  // 横向成绩导入
  importMatrixGrades(formData) {
    return request({
      url: '/student_data/grades/matrix/import/',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 导出横向成绩
  exportGradeMatrix(params = {}) {
    return request({
      url: '/student_data/grades/matrix/export/',
      method: 'get',
      params,
      responseType: 'blob'
    })
  },

  // 下载横向模板
  downloadMatrixTemplate() {
    return request({
      url: '/student_data/grades/matrix/template/',
      method: 'get',
      responseType: 'blob'
    })
  }
}

export default gradeAPI

