// 数据处理工具
export class DataProcessor {
  // 批量处理数据，添加计算属性
  static processTableData(rawData) {
    return rawData.map(item => Object.freeze({
      ...item,
      // 预计算显示相关的属性
      displayName: item.name || '未知',
      displayAge: `${item.age}岁`,
      displayGrade: item.grade || '未分配',
      displayClass: item.class_name || '未分班',
      statusConfig: this.getStatusConfig(item.current_status),
      // 完整度计算
      completeness: this.calculateCompleteness(item),
      // 搜索关键字（用于前端筛选）
      searchKeywords: [
        item.name,
        item.school_id,
        item.id_card,
        item.gz_student_id,
        item.national_student_id
      ].filter(Boolean).join(' ').toLowerCase()
    }))
  }
  
  // 状态配置
  static getStatusConfig(status) {
    const configs = {
      'active': { type: 'success', effect: 'light', text: '在校', color: '#67c23a' },
      'suspended': { type: 'warning', effect: 'dark', text: '休学', color: '#e6a23c' },
      'transferred_out': { type: 'info', effect: 'light', text: '已转出', color: '#909399' },
      'transferred_in': { type: 'primary', effect: 'light', text: '转入', color: '#409eff' }
    }
    return configs[status] || configs['active']
  }
  
  // 计算数据完整度
  static calculateCompleteness(student) {
    const requiredFields = ['name', 'school_id', 'id_card', 'age', 'grade', 'class_name', 'gz_student_id']
    const optionalFields = [
      'national_student_id', 'household_address', 'living_address',
      'guardian_father', 'guardian_mother', 'guardian_father_phone', 'guardian_mother_phone'
    ]
    
    const requiredFilled = requiredFields.filter(field => 
      student[field] && student[field].toString().trim() !== ''
    )
    
    const optionalFilled = optionalFields.filter(field => 
      student[field] && student[field].toString().trim() !== ''
    )
    
    const requiredRate = (requiredFilled.length / requiredFields.length) * 0.8
    const optionalRate = (optionalFilled.length / optionalFields.length) * 0.2
    
    return Math.round((requiredRate + optionalRate) * 100)
  }
  
  // 前端搜索过滤
  static filterData(data, keyword) {
    if (!keyword) return data
    
    const lowerKeyword = keyword.toLowerCase()
    return data.filter(item => item.searchKeywords.includes(lowerKeyword))
  }
  
  // 数据排序
  static sortData(data, sortKey, sortOrder = 'asc') {
    return [...data].sort((a, b) => {
      let aVal = a[sortKey]
      let bVal = b[sortKey]
      
      // 处理数字类型
      if (typeof aVal === 'string' && !isNaN(aVal)) {
        aVal = Number(aVal)
        bVal = Number(bVal)
      }
      
      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })
  }
} 