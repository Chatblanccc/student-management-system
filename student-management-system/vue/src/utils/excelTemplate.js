import * as XLSX from 'xlsx'

// 生成学生数据导入模板
export function generateStudentTemplate() {
  // 定义表头
  const headers = [
    '学号', '姓名', '年级', '班级', '身份证号', '年龄', '广州学籍号', '全国学籍号',
    '户籍所在地', '居住所在地', '监护人(父亲)', '监护人(母亲)', 
    '监护人(父亲)电话', '监护人(母亲)电话'
  ]
  
  // 示例数据
  const sampleData = [
    [
      '2024016', '张三', '七年级', '1班', '440101200001010001', 13, 'GZ202400016', '', 
      '广东省广州市天河区天河路123号', '广东省广州市天河区珠江新城456号',
      '张大明', '李小红', '13800138001', '13900139001'
    ],
    [
      '2024017', '李四', '八年级', '2班', '440101200002020002', 14, 'GZ202400017', 'QG2024000000017',
      '广东省深圳市南山区科技园789号', '广东省深圳市福田区中心城101号',
      '李建国', '王美丽', '13800138002', '13900139002'
    ],
    [
      '2024018', '王五', '九年级', '3班', '440101200003030003', 15, 'GZ202400018', 'QG2024000000018',
      '广东省广州市越秀区中山路321号', '广东省广州市海珠区新港路654号',
      '王国强', '陈丽华', '13800138003', '13900139003'
    ]
  ]
  
  // 创建工作表数据
  const wsData = [headers, ...sampleData]
  
  // 创建工作表
  const ws = XLSX.utils.aoa_to_sheet(wsData)
  
  // 设置列宽
  const colWidths = [
    { wch: 10 }, // 学号
    { wch: 10 }, // 姓名
    { wch: 10 }, // 年级
    { wch: 8 },  // 班级
    { wch: 20 }, // 身份证号
    { wch: 8 },  // 年龄
    { wch: 15 }, // 广州学籍号
    { wch: 18 }, // 全国学籍号
    { wch: 30 }, // 户籍所在地
    { wch: 30 }, // 居住所在地
    { wch: 12 }, // 监护人(父亲)
    { wch: 12 }, // 监护人(母亲)
    { wch: 15 }, // 监护人(父亲)电话
    { wch: 15 }  // 监护人(母亲)电话
  ]
  ws['!cols'] = colWidths
  
  // 设置表头样式
  const headerStyle = {
    fill: { fgColor: { rgb: "4F81BD" } },
    font: { color: { rgb: "FFFFFF" }, bold: true },
    alignment: { horizontal: "center", vertical: "center" }
  }
  
  // 应用表头样式
  for (let i = 0; i < headers.length; i++) {
    const cellRef = XLSX.utils.encode_cell({ r: 0, c: i })
    if (!ws[cellRef]) ws[cellRef] = {}
    ws[cellRef].s = headerStyle
  }
  
  // 设置数据验证（年级下拉选项）
  // 注意：XLSX.js 对数据验证的支持有限，这里添加注释说明
  
  // 添加工作表备注
  const remarks = [
    [],
    ['填写说明：'],
    ['1. 学号：必填，不能重复'],
    ['2. 姓名：必填'],
    ['3. 年级：必填，可选值：七年级、八年级、九年级'],
    ['4. 班级：必填，格式如：1班、2班、3班等'],
    ['5. 身份证号：必填，18位有效身份证号'],
    ['6. 年龄：必填，数字'],
    ['7. 广州学籍号：必填，不能重复'],
    ['8. 全国学籍号：选填，为空时不显示'],
    ['9. 户籍所在地：选填，为空时不显示'],
    ['10. 居住所在地：选填，为空时不显示'],
    ['11. 监护人(父亲)：选填，为空时不显示'],
    ['12. 监护人(母亲)：选填，为空时不显示'],
    ['13. 监护人(父亲)电话：选填，为空时不显示'],
    ['14. 监护人(母亲)电话：选填，为空时不显示'],
    [],
    ['必填字段：学号、姓名、年级、班级、身份证号、年龄、广州学籍号'],
    ['选填字段：全国学籍号、地址信息、监护人信息']
  ]
  
  // 在示例数据下方添加说明
  const startRow = sampleData.length + 2
  remarks.forEach((remark, index) => {
    if (remark.length > 0) {
      const cellRef = XLSX.utils.encode_cell({ r: startRow + index, c: 0 })
      ws[cellRef] = { v: remark[0], t: 's' }
    }
  })
  
  // 创建工作簿
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '学生数据模板')
  
  // 生成文件名
  const fileName = `学生数据导入模板_${new Date().getFullYear()}${String(new Date().getMonth() + 1).padStart(2, '0')}${String(new Date().getDate()).padStart(2, '0')}.xlsx`
  
  // 直接下载，无权限检查
  XLSX.writeFile(wb, fileName)
}

// 生成年级班级对照表
export function generateGradeClassReference() {
  const headers = ['年级', '建议班级编号', '说明']
  const data = [
    ['七年级', '1班、2班、3班、4班...', '入学新生'],
    ['八年级', '1班、2班、3班、4班...', '二年级学生'],
    ['九年级', '1班、2班、3班、4班...', '毕业班学生']
  ]
  
  const wsData = [headers, ...data]
  const ws = XLSX.utils.aoa_to_sheet(wsData)
  
  // 设置列宽
  ws['!cols'] = [
    { wch: 12 },
    { wch: 25 },
    { wch: 15 }
  ]
  
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '年级班级对照表')
  
  const fileName = `年级班级对照表_${new Date().getFullYear()}${String(new Date().getMonth() + 1).padStart(2, '0')}${String(new Date().getDate()).padStart(2, '0')}.xlsx`
  
  // 直接下载，无权限检查
  XLSX.writeFile(wb, fileName)
}
