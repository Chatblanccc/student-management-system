<template>
  <div>
    <!-- 查询条件工具栏 -->
    <div class="search-toolbar">
      <div class="search-left">
        <el-select 
          v-model="queryForm.exam_id" 
          placeholder="选择考试" 
          style="width: 250px; margin-right: 12px;"
          clearable
          @change="handleExamChange">
          <el-option
            v-for="exam in examList"
            :key="exam.id"
            :label="exam.name"
            :value="exam.id">
          </el-option>
        </el-select>
        
        <el-select 
          v-model="queryForm.grade" 
          placeholder="选择年级" 
          style="width: 120px; margin-right: 12px;"
          clearable
          :disabled="!queryForm.exam_id">
          <el-option label="全部" value=""></el-option>
          <el-option
            v-for="grade in gradeOptions"
            :key="grade.value"
            :label="grade.label"
            :value="grade.value">
          </el-option>
        </el-select>
        
        <el-input 
          v-model="queryForm.class" 
          placeholder="输入班级" 
          style="width: 120px; margin-right: 12px;"
          clearable
          :disabled="!queryForm.exam_id">
        </el-input>
        
        <el-button 
          type="primary" 
          plain 
          @click="searchGrades" 
          :loading="searching"
          :disabled="!queryForm.exam_id">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
        <el-button type="warning" plain @click="resetQuery">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
      
      <div class="search-right">
        <el-button type="success" plain @click="handleImport">
          <el-icon><Upload /></el-icon>
          导入成绩
        </el-button>
        <el-button 
          type="primary" 
          plain 
          @click="handleExport"
          :disabled="!queryForm.exam_id">
          <el-icon><Download /></el-icon>
          导出成绩
        </el-button>
      </div>
    </div>

    <!-- 成绩表格卡片 -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Grid /></el-icon>
            成绩列表
          </span>
          <div class="record-info">
            <el-tag type="info" effect="plain" size="large">
              <el-icon><DataBoard /></el-icon>
              共 {{ pagination.total }} 条记录
            </el-tag>
          </div>
        </div>
      </template>
      
      <!-- 当没有选择考试时显示提示 -->
      <div v-if="!queryForm.exam_id" class="empty-state">
        <el-empty 
          description="请先选择考试查看成绩数据">
          <el-button type="primary" @click="() => {}">选择考试</el-button>
        </el-empty>
      </div>
      
      <!-- 成绩表格 -->
      <div v-else class="virtual-table-container" v-loading="tableLoading">
        <el-auto-resizer>
          <template #default="{ height, width }">
            <el-table-v2
              :columns="tableColumns"
              :data="sortedGradeList"
              :width="width"
              :height="height - 60"
              :row-height="50"
              :header-height="50"
              fixed
            />
          </template>
        </el-auto-resizer>
      </div>

      <!-- 分页组件 -->
      <div v-if="queryForm.exam_id && gradeList.length > 0" class="pagination-container">
        <div class="pagination-left">
          <span class="pagination-label">每页显示</span>
          <el-select 
            v-model="pagination.pageSize" 
            @change="handleSizeChange"
            class="page-size-select">
            <el-option label="10 条/页" :value="10" />
            <el-option label="20 条/页" :value="20" />
            <el-option label="50 条/页" :value="50" />
            <el-option label="100 条/页" :value="100" />
            <el-option label="200 条/页" :value="200" />
            <el-option label="500 条/页" :value="500" />
            <el-option label="全部数据" :value="0" />
          </el-select>
          <span class="total-info">
            共 {{ pagination.total }} 条数据
          </span>
        </div>
        
        <!-- 标准分页组件 -->
        <el-pagination 
          v-if="pagination.pageSize !== 0"
          background 
          layout="total, prev, pager, next, jumper" 
          :total="pagination.total"
          :page-size="pagination.pageSize"
          :current-page="pagination.page"
          @current-change="handleCurrentChange" />
        
        <!-- 显示全部时只显示总数 -->
        <div v-else class="total-display">
          共 {{ pagination.total }} 条数据 (显示全部)
        </div>
      </div>
    </el-card>

    <!-- 导入对话框 -->
    <el-dialog 
      v-model="importDialogVisible" 
      title="成绩导入" 
      width="35%"
      align-center
      class="import-dialog">
      
      <!-- 模板下载区域 -->
      <div class="template-download-area">
        <div class="template-header">
          <div class="template-info">
            <el-icon class="template-icon"><Download /></el-icon>
            <span class="template-title">首次使用请先下载模板</span>
          </div>
          <el-button type="primary" link @click="downloadTemplate">
            <el-icon><Download /></el-icon>
            下载模板
          </el-button>
        </div>
        <div class="template-tips">
          请按照横向模板格式填写数据，每行一个学生，各科目分数填入对应列中
        </div>
      </div>

      <!-- 考试选择 -->
      <el-form :model="importForm" label-width="100px" class="import-form">
        <el-form-item label="选择考试" required>
          <el-select 
            v-model="importForm.exam_id" 
            placeholder="请选择要导入成绩的考试" 
            style="width: 100%"
            size="large">
            <el-option
              v-for="exam in examList"
              :key="exam.id"
              :label="exam.name"
              :value="exam.id">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 文件上传区域 -->
      <el-upload 
        class="upload-area" 
        drag 
        :auto-upload="false" 
        :on-change="handleFileChange" 
        :file-list="fileList"
        accept=".xlsx,.xls,.csv">
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">
          拖拽文件到此处或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="upload-tip">
            支持xlsx/xls/csv文件，文件大小不超过5MB
          </div>
        </template>
      </el-upload>

      <!-- 导入结果显示 -->
      <div v-if="importResult" class="import-result">
        <h4 class="result-title">导入结果：</h4>
        <div class="result-stats">
          <p class="result-item">总记录数: <span class="stat-number">{{ importResult.total_records }}</span></p>
          <p class="result-item success">成功记录数: <span class="stat-number">{{ importResult.success_records }}</span></p>
          <p class="result-item error">失败记录数: <span class="stat-number">{{ importResult.error_records }}</span></p>
        </div>
        <div v-if="importResult.errors && importResult.errors.length > 0" class="error-details">
          <h5 class="error-title">错误信息：</h5>
          <ul class="error-list">
            <li v-for="(error, index) in importResult.errors" :key="index" class="error-item">
              {{ error }}
            </li>
          </ul>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeImportDialog">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmImport" 
            :loading="importing" 
            :disabled="!importForm.file">
            <el-icon v-if="!importing"><Upload /></el-icon>
            {{ importing ? '导入中...' : '确认导入' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, h } from 'vue'
import { ElMessage, ElMessageBox, ElTag } from 'element-plus'
import { 
  Search, 
  Refresh, 
  Upload, 
  Download, 
  DataBoard,
  Grid,
  UploadFilled
} from '@element-plus/icons-vue'
import { gradeAPI } from '@/api/grade'

// 年级选项配置
const gradeOptions = [
  { label: '一年级', value: '一年级' },
  { label: '二年级', value: '二年级' },
  { label: '三年级', value: '三年级' },
  { label: '四年级', value: '四年级' },
  { label: '五年级', value: '五年级' },
  { label: '六年级', value: '六年级' },
  { label: '七年级', value: '七年级' },
  { label: '八年级', value: '八年级' },
  { label: '九年级', value: '九年级' },
  { label: '高一', value: '高一' },
  { label: '高二', value: '高二' },
  { label: '高三', value: '高三' }
]

// 响应式数据
const queryForm = reactive({
  exam_id: '',
  grade: '',
  class: ''
})

const gradeList = ref([])
const examList = ref([])
const subjectList = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 加载状态
const searching = ref(false)
const tableLoading = ref(false)

// 导入相关
const importDialogVisible = ref(false)
const importing = ref(false)
const fileList = ref([])
const importResult = ref(null)
const importForm = reactive({
  exam_id: '',
  file: null
})

// 排序状态
const sortState = reactive({
  sortBy: '',
  sortOrder: ''
})

// 排序后的数据
const sortedGradeList = computed(() => {
  if (!sortState.sortBy || !sortState.sortOrder) {
    return gradeList.value
  }
  
  const sorted = [...gradeList.value].sort((a, b) => {
    let result = 0
    
    if (sortState.sortBy === 'class_name') {
      const aVal = a.class_name || ''
      const bVal = b.class_name || ''
      result = aVal.localeCompare(bVal, 'zh-CN')
    } else if (sortState.sortBy === 'total_score') {
      const aVal = a.total_score || 0
      const bVal = b.total_score || 0
      result = bVal - aVal // 默认降序
    } else if (sortState.sortBy === 'total_rank_in_grade') {
      const aVal = a.total_rank_in_grade || Number.MAX_SAFE_INTEGER
      const bVal = b.total_rank_in_grade || Number.MAX_SAFE_INTEGER
      result = aVal - bVal // 升序排列，排名小的在前
    } else if (sortState.sortBy.startsWith('subject_')) {
      // 解析科目代码
      const parts = sortState.sortBy.split('_')
      const subjectCode = parts[1]
      const type = parts[2] // 'score' 或 'rank'
      
      if (type === 'score') {
        const aVal = a.subjects?.[subjectCode]?.score || 0
        const bVal = b.subjects?.[subjectCode]?.score || 0
        result = bVal - aVal // 降序排列，分数高的在前
      } else if (type === 'rank') {
        const aVal = a.subjects?.[subjectCode]?.rank_in_class || Number.MAX_SAFE_INTEGER
        const bVal = b.subjects?.[subjectCode]?.rank_in_class || Number.MAX_SAFE_INTEGER
        result = aVal - bVal // 升序排列，排名小的在前
      }
    }
    
    return sortState.sortOrder === 'asc' ? result : -result
  })
  
  return sorted
})

// 处理排序
const handleSort = (sortBy) => {
  if (sortState.sortBy === sortBy) {
    // 如果是同一列，切换排序方向
    if (sortState.sortOrder === 'asc') {
      sortState.sortOrder = 'desc'
    } else if (sortState.sortOrder === 'desc') {
      // 取消排序
      sortState.sortBy = ''
      sortState.sortOrder = ''
    } else {
      sortState.sortOrder = 'asc'
    }
  } else {
    // 新列排序
    sortState.sortBy = sortBy
    sortState.sortOrder = 'asc'
  }
}

// 获取排序图标
const getSortIcon = (column) => {
  if (sortState.sortBy !== column) return ''
  return sortState.sortOrder === 'asc' ? '↑' : '↓'
}

// 表格列配置 - 修改版本，添加排序功能
const tableColumns = computed(() => {
  const columns = [
    // 学号列
    {
      key: 'school_id',
      title: '学号',
      width: 120,
      align: 'center',
      fixed: 'left',
      cellRenderer: ({ rowData }) => {
        return h('span', {
          style: { color: '#409eff', fontWeight: '500' }
        }, rowData.school_id || '')
      }
    },
    
    // 姓名列
    {
      key: 'name',
      title: '姓名',
      width: 100,
      align: 'center',
      fixed: 'left',
      cellRenderer: ({ rowData }) => {
        return h('span', {
          style: { fontWeight: '600', color: '#303133' }
        }, rowData.name || '')
      }
    },
    
    // 年级列
    {
      key: 'grade',
      title: '年级',
      width: 80,
      align: 'center',
      cellRenderer: ({ rowData }) => {
        return h('span', {
          style: { color: '#606266' }
        }, rowData.grade || '未设置')
      }
    },
    
    // 班级列 - 可排序
    {
      key: 'class_name',
      title: '班级',
      width: 80,
      align: 'center',
      headerCellRenderer: () => {
        return h('div', {
          style: { 
            cursor: 'pointer', 
            userSelect: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          },
          onClick: () => handleSort('class_name')
        }, [
          h('span', {}, '班级'),
          h('span', {
            style: { marginLeft: '4px', color: '#409eff' }
          }, getSortIcon('class_name'))
        ])
      },
      cellRenderer: ({ rowData }) => {
        return h('span', {
          style: { color: '#606266' }
        }, rowData.class_name || '未设置')
      }
    }
  ]
  
  // 动态添加科目列 - 可排序
  subjectList.value.forEach(subject => {
    // 科目分数列 - 可排序
    columns.push({
      key: `subject_${subject.code}_score`,
      title: subject.name,
      width: 100,
      align: 'center',
      headerCellRenderer: () => {
        return h('div', {
          style: { 
            cursor: 'pointer', 
            userSelect: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          },
          onClick: () => handleSort(`subject_${subject.code}_score`)
        }, [
          h('span', {}, subject.name),
          h('span', {
            style: { marginLeft: '4px', color: '#409eff' }
          }, getSortIcon(`subject_${subject.code}_score`))
        ])
      },
      cellRenderer: ({ rowData }) => {
        const score = rowData.subjects?.[subject.code]?.score
        if (score !== undefined && score !== null) {
          return h('span', {
            style: { fontWeight: '600', fontSize: '14px' }
          }, score.toString())
        }
        return h('span', {
          style: { color: '#c0c4cc', fontStyle: 'italic', fontSize: '12px' }
        }, '-')
      }
    })
    
    // 科目排名列 - 可排序
    columns.push({
      key: `subject_${subject.code}_rank`,
      title: `${subject.name}排名`,
      width: 90,
      align: 'center',
      headerCellRenderer: () => {
        return h('div', {
          style: { 
            cursor: 'pointer', 
            userSelect: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          },
          onClick: () => handleSort(`subject_${subject.code}_rank`)
        }, [
          h('span', {}, `${subject.name}排名`),
          h('span', {
            style: { marginLeft: '4px', color: '#409eff' }
          }, getSortIcon(`subject_${subject.code}_rank`))
        ])
      },
      cellRenderer: ({ rowData }) => {
        const rank = rowData.subjects?.[subject.code]?.rank_in_class
        if (rank) {
          return h('span', {
            style: { color: '#606266', fontSize: '12px', fontWeight: '500' }
          }, `第${rank}名`)
        }
        return h('span', {
          style: { color: '#c0c4cc', fontStyle: 'italic', fontSize: '12px' }
        }, '-')
      }
    })
  })
  
  // 总分列 - 可排序
  columns.push({
    key: 'total_score',
    title: '总分',
    width: 100,
    align: 'center',
    fixed: 'right',
    headerCellRenderer: () => {
      return h('div', {
        style: { 
          cursor: 'pointer', 
          userSelect: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        },
        onClick: () => handleSort('total_score')
      }, [
        h('span', {}, '总分'),
        h('span', {
          style: { marginLeft: '4px', color: '#409eff' }
        }, getSortIcon('total_score'))
      ])
    },
    cellRenderer: ({ rowData }) => {
      return h('span', {
        style: { fontWeight: '600', color: '#303133' }
      }, rowData.total_score?.toString() || '0')
    }
  })
  
  // 总分排名列 - 可排序
  columns.push({
    key: 'total_rank_in_grade',
    title: '总分排名',
    width: 100,
    align: 'center',
    fixed: 'right',
    headerCellRenderer: () => {
      return h('div', {
        style: { 
          cursor: 'pointer', 
          userSelect: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        },
        onClick: () => handleSort('total_rank_in_grade')
      }, [
        h('span', {}, '总分排名'),
        h('span', {
          style: { marginLeft: '4px', color: '#409eff' }
        }, getSortIcon('total_rank_in_grade'))
      ])
    },
    cellRenderer: ({ rowData }) => {
      if (rowData.total_rank_in_grade) {
        return h('span', {
          style: { color: '#606266', fontWeight: '500', fontSize: '13px' }
        }, `第${rowData.total_rank_in_grade}名`)
      }
      return h('span', {
        style: { color: '#c0c4cc', fontStyle: 'italic', fontSize: '12px' }
      }, '-')
    }
  })
  
  return columns
})

// 排序方法
const sortSubjectScore = (a, b, subjectCode) => {
  const scoreA = a.subjects[subjectCode]?.score || 0
  const scoreB = b.subjects[subjectCode]?.score || 0
  return scoreB - scoreA // 降序排列，分数高的在前
}

const sortSubjectRank = (a, b, subjectCode) => {
  const rankA = a.subjects[subjectCode]?.rank_in_class || Number.MAX_SAFE_INTEGER
  const rankB = b.subjects[subjectCode]?.rank_in_class || Number.MAX_SAFE_INTEGER
  return rankA - rankB // 升序排列，排名小的在前
}

const sortTotalRank = (a, b) => {
  const rankA = a.total_rank_in_grade || Number.MAX_SAFE_INTEGER
  const rankB = b.total_rank_in_grade || Number.MAX_SAFE_INTEGER
  return rankA - rankB // 升序排列，排名小的在前
}

// 搜索成绩
const searchGrades = async () => {
  if (!queryForm.exam_id) {
    ElMessage.warning('请先选择考试，然后再进行查询')
    return
  }

  try {
    searching.value = true
    tableLoading.value = true
    
    const params = {
      exam_id: queryForm.exam_id,
      page: pagination.pageSize === 0 ? 1 : pagination.page,
      page_size: pagination.pageSize === 0 ? 999999 : pagination.pageSize
    }
    
    if (queryForm.grade) {
      params.grade = queryForm.grade
    }
    if (queryForm.class) {
      params.class = queryForm.class
    }
    
    const response = await gradeAPI.getGradeMatrix(params)
    
    gradeList.value = response.data || []
    subjectList.value = response.subjects || []
    pagination.total = response.total || 0
    
    if ((response.total || 0) === 0) {
      ElMessage.warning('没有找到符合条件的成绩记录')
    } else {
      const displayMsg = pagination.pageSize === 0 
        ? `查询完成，共显示全部 ${response.total} 名学生的成绩`
        : `查询完成，共找到 ${response.total} 名学生的成绩`
      ElMessage.success(displayMsg)
    }
    
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询成绩失败')
    gradeList.value = []
    subjectList.value = []
    pagination.total = 0
  } finally {
    searching.value = false
    tableLoading.value = false
  }
}

// 重置查询
const resetQuery = () => {
  Object.assign(queryForm, {
    exam_id: '',
    grade: '',
    class: ''
  })
  pagination.page = 1
  gradeList.value = []
  subjectList.value = []
  pagination.total = 0
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  searchGrades()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  searchGrades()
}

// 获取考试列表
const getExamList = async () => {
  try {
    const response = await gradeAPI.getExams({})
    examList.value = Array.isArray(response) ? response : (response.data || [])
    console.log('成功获取考试列表:', examList.value.length)
  } catch (error) {
    console.error('获取考试列表失败:', error)
    ElMessage.error('获取考试列表失败，请检查网络连接')
    examList.value = []
  }
}

// 导入成绩
const handleImport = () => {
  importDialogVisible.value = true
  importForm.exam_id = ''
  importForm.file = null
  fileList.value = []
  importResult.value = null
}

// 文件选择处理
const handleFileChange = (file) => {
  importForm.file = file.raw
  importResult.value = null
}

// 关闭导入弹窗
const closeImportDialog = () => {
  importDialogVisible.value = false
  importForm.exam_id = ''
  importForm.file = null
  fileList.value = []
  importResult.value = null
}

// 确认导入
const confirmImport = async () => {
  if (!importForm.exam_id) {
    ElMessage.warning('请选择考试')
    return
  }
  if (!importForm.file) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  try {
    importing.value = true
    const formData = new FormData()
    formData.append('file', importForm.file)
    formData.append('exam_id', importForm.exam_id)
    
    const result = await gradeAPI.importMatrixGrades(formData)
    
    importResult.value = result
    
    if (result.error_records > 0) {
      ElMessage.warning(`导入完成！成功${result.success_records}名学生，失败${result.error_records}条记录`)
    } else {
      ElMessage.success(`导入成功！共导入${result.success_records}名学生的成绩`)
    }
    
    await searchGrades()
    
  } catch (error) {
    console.error('导入失败:', error)
    const errorMsg = error.response?.data?.error || error.message || '导入失败'
    ElMessage.error(errorMsg)
  } finally {
    importing.value = false
  }
}

// 下载模板
const downloadTemplate = async () => {
  try {
    const response = await gradeAPI.downloadMatrixTemplate()
    
    const blob = new Blob([response], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '横向成绩导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('横向模板下载成功')
  } catch (error) {
    ElMessage.error('模板下载失败')
  }
}

// 导出成绩
const handleExport = async () => {
  try {
    const params = { ...queryForm }
    
    await ElMessageBox.confirm('确定要导出当前查询条件下的成绩数据吗？', '确认导出', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    const response = await gradeAPI.exportGradeMatrix(params)
    
    const blob = new Blob([response], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `成绩单_${new Date().toLocaleDateString()}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('导出失败')
    }
  }
}

// 考试选择改变时的处理
const handleExamChange = () => {
  if (queryForm.exam_id) {
    searchGrades()
  } else {
    gradeList.value = []
    subjectList.value = []
    pagination.total = 0
  }
}

onMounted(() => {
  getExamList()
})
</script>

<style scoped>
/* 工具栏样式 */
.search-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.search-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 卡片样式 */
.table-card {
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.card-title .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.record-info .el-tag {
  border: none;
  font-weight: 500;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* 表格样式 */
.grade-matrix-table {
  margin-bottom: 20px;
}

.student-name {
  font-weight: 600;
  color: #303133;
}

.subject-score {
  display: flex;
  justify-content: center;
}

.score-tag {
  font-weight: 600;
  border-radius: 4px;
}

.rank-info {
  color: #606266;
  font-size: 12px;
  font-weight: 500;
}

.total-rank {
  color: #E6A23C;
  font-weight: 600;
}

.no-score, .no-data {
  color: #C0C4CC;
  font-style: italic;
}

.total-score-tag {
  font-weight: 700;
  font-size: 14px;
}

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding: 16px 0;
  border-top: 1px solid #EBEEF5;
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-label {
  color: #606266;
  font-size: 14px;
}

.page-size-select {
  width: 140px;
}

.total-info {
  color: #909399;
  font-size: 14px;
}

.total-display {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

/* 虚拟滚动表格容器 */
.virtual-table-container {
  height: calc(70vh - 120px);
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 20px;
}

/* 虚拟滚动表格样式优化 */
:deep(.el-table-v2__header) {
  background-color: #fafafa;
  font-weight: 600;
}

:deep(.el-table-v2__row) {
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-table-v2__row:hover) {
  background-color: #f5f7fa;
}

/* 自定义滚动条样式 */
:deep(.el-table-v2__scrollbar) {
  width: 8px;
}

:deep(.el-table-v2__scrollbar-thumb) {
  background-color: #c1c1c1;
  border-radius: 4px;
}

/* 导入对话框样式 */
.import-dialog {
  border-radius: 12px;
}

.template-download-area {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px dashed #d9ecff;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.template-info {
  display: flex;
  align-items: center;
}

.template-icon {
  margin-right: 8px;
  color: #409eff;
  font-size: 18px;
}

.template-title {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.template-tips {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.import-form {
  margin-bottom: 24px;
}

/* 上传区域样式 */
.upload-area {
  margin-bottom: 20px;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
  font-size: 14px;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

/* 导入结果样式 */
.import-result {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 16px;
  margin-top: 20px;
}

.result-title {
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.result-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.result-item {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.result-item.success {
  color: #67c23a;
}

.result-item.error {
  color: #f56c6c;
}

.stat-number {
  font-weight: 600;
  font-size: 16px;
}

.error-details {
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}

.error-title {
  color: #f56c6c;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.error-list {
  margin: 0;
  padding-left: 20px;
  max-height: 120px;
  overflow-y: auto;
}

.error-item {
  color: #f56c6c;
  font-size: 12px;
  line-height: 1.6;
  margin-bottom: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 简化的分数显示样式 */
.school-id {
  color: #409eff;
  font-weight: 500;
}

.student-name {
  font-weight: 600;
  color: #303133;
}

.grade-info, .class-info {
  color: #606266;
  font-size: 14px;
}

.subject-score {
  font-weight: 600;
  font-size: 14px;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
  min-width: 40px;
  text-align: center;
}

/* 分数等级样式 */
/* .score-excellent, .score-good, .score-pass, .score-fail 等都删除 */

.total-score {
  font-weight: 600;
  color: #303133;
}

.rank-info {
  color: #606266;
  font-size: 12px;
  font-weight: 500;
}

.total-rank {
  color: #606266;
  font-weight: 500;
  font-size: 13px;
}

.no-score, .no-data {
  color: #c0c4cc;
  font-style: italic;
  font-size: 12px;
}

/* 排序列头样式 */
:deep(.el-table-v2__header-cell) {
  position: relative;
}

.sortable-header {
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.sortable-header:hover {
  color: #409eff;
}

.sort-icon {
  margin-left: 4px;
  color: #409eff;
  font-weight: bold;
}
</style>