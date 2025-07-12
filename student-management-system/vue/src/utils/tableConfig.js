// 虚拟滚动表格配置
export const virtualTableConfig = {
  // 行高配置
  rowHeight: 50,
  headerHeight: 50,
  
  // 缓冲区配置（渲染可视区域外的行数）
  overscan: 5,
  
  // 估算总高度（用于滚动条计算）
  estimatedRowHeight: 50,
  
  // 是否启用行高度自适应
  dynamicHeight: false,
  
  // 滚动性能优化
  scrollbarAlwaysOn: true,
  
  // 表格样式
  tableStyle: {
    fontSize: '14px',
    lineHeight: '1.5'
  }
}

// 列宽度预设
export const columnWidths = {
  selection: 60,
  name: 120,
  school_id: 120,
  grade: 100,
  class_name: 100,
  status: 120,
  id_card: 200,
  age: 80,
  gz_student_id: 200,
  national_student_id: 200,
  household_address: 300,
  living_address: 300,
  guardian_father: 130,
  guardian_mother: 130,
  guardian_father_phone: 180,
  guardian_mother_phone: 180,
  actions: 180
} 