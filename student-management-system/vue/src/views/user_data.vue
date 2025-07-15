<template>
  <!-- 工具栏开始 -->
  <div>
    <!-- 移除性能监控组件 -->
    <!-- <PerformanceMonitor 
      :show-monitor="showPerformanceMonitor"
      :data-count="tableData.length" 
    /> -->
    
    <div style="margin-bottom: 15px;" class="card search-toolbar">
      <div>
        <el-input v-model="searchForm.keyword" style="width: 240px; margin-right: 12px;" placeholder="请输入姓名、学号或身份证号" />
        <el-button type="primary" plain @click="handleSearch">查询</el-button>
        <el-button type="warning" plain @click="handleReset">重置</el-button>
      </div>
      <div style="display: flex; justify-content: right;">
        <!-- 导入按钮 - 仅管理员可见 -->
        <PermissionWrapper permission="import">
          <el-button type="success" plain @click="DataImportVisible = true">导入数据</el-button>
        </PermissionWrapper>
        
        <!-- 导出按钮 - 所有用户可见 -->
        <PermissionWrapper permission="export">
          <el-button type="primary" plain @click="handleExport">导出数据</el-button>
        </PermissionWrapper>
        
        <!-- 批量删除按钮 - 仅管理员可见 -->
        <PermissionWrapper permission="delete">
          <el-button type="danger" plain @click="handleBatchDelete" :disabled="selectedRows.length === 0">
            批量删除 {{ selectedRows.length > 0 ? `(${selectedRows.length})` : '' }}
          </el-button>
        </PermissionWrapper>
      </div>
    </div>
    <!-- 工具栏结束 -->

    <!-- 虚拟滚动表格开始 -->
    <div class="card">
      <!-- 表格容器 -->
      <div class="virtual-table-container" v-loading="tableLoading">
        <el-auto-resizer>
          <template #default="{ height, width }">
            <el-table-v2
              :columns="tableColumns"
              :data="tableData"
              :width="width"
              :height="height - 60"
              :row-height="50"
              :header-height="50"
              fixed
              @row-click="handleRowClick"
            />
          </template>
        </el-auto-resizer>
      </div>

      <!-- 分页组件 -->
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 10px; border-top: 1px solid #ebeef5;">
        <!-- 左侧：页面大小选择器 -->
        <div style="display: flex; align-items: center;">
          <span style="margin-right: 8px; color: #606266; font-size: 14px;">每页显示</span>
          <el-select 
            v-model="pagination.pageSize" 
            @change="handleSizeChange"
            style="width: 120px; margin-right: 10px;">
            <el-option label="20 条/页" :value="20" />
            <el-option label="50 条/页" :value="50" />
            <el-option label="100 条/页" :value="100" />
            <el-option label="200 条/页" :value="200" />
            <el-option label="500 条/页" :value="500" />
            <el-option label="1000 条/页" :value="1000" />
            <el-option label="全部数据" :value="0" />
          </el-select>
          <span style="color: #909399; font-size: 12px;">
            已选择 {{ selectedRows.length }} 项
          </span>
        </div>
        
        <!-- 右侧：标准分页组件 -->
        <el-pagination 
          v-if="pagination.pageSize !== 0"
          background 
          layout="total, prev, pager, next, jumper" 
          :total="pagination.total"
          :page-size="pagination.pageSize"
          :current-page="pagination.currentPage"
          @current-change="handlePageChange" />
        
        <!-- 显示全部时只显示总数 -->
        <div v-else style="color: #606266; font-size: 14px;">
          共 {{ pagination.total }} 条数据
        </div>
      </div>
    </div>
    <!-- 虚拟滚动表格结束 -->

    <!-- 删除确认弹窗开始 -->
    <div>
      <el-dialog v-model="DataDeleteVisible" title="删除确认" width="400px" align-center>
        <div style="text-align: center; padding: 20px;">
          <el-icon style="font-size: 48px; color: #f56c6c; margin-bottom: 16px;">
            <WarningFilled />
          </el-icon>
          <p style="margin: 0; font-size: 16px; color: #606266;">
            {{ deleteType === 'batch' ? '确定要删除选中的数据吗？' : '确定要删除这条数据吗？' }}
          </p>
          <p style="margin: 8px 0 0 0; font-size: 14px; color: #909399;">
            {{ deleteType === 'batch' 
                ? `将删除 ${selectedRows.length} 条记录，此操作不可恢复` 
                : '此操作不可恢复' }}
          </p>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="DataDeleteVisible = false">取消</el-button>
            <el-button type="danger" @click="confirmDelete" :loading="deleteLoading">
              确认删除
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
    <!-- 删除确认弹窗结束 -->

    <!-- 导入弹窗开始 -->
    <div>
      <el-dialog v-model="DataImportVisible" title="数据导入" width="35%" align-center>
        <!-- 模板下载区域 -->
        <div
          style="margin-bottom: 20px; padding: 15px; background-color: #f0f9ff; border-radius: 6px; border: 1px solid #bfdbfe;">
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
              <el-icon style="color: #3b82f6; margin-right: 8px;">
                <Download />
              </el-icon>
              <span style="color: #1e40af; font-weight: 500;">首次使用请先下载模板</span>
            </div>
            <el-button type="primary" link @click="downloadTemplate">
              <el-icon>
                <Download />
              </el-icon>
              下载模板
            </el-button>
          </div>
          <div style="margin-top: 8px; font-size: 12px; color: #6b7280;">
            请按照模板格式填写数据，确保所有数据都是正确数据
          </div>
        </div>

        <!-- 文件上传区域 -->
        <el-upload class="upload-demo" drag :auto-upload="false" :on-change="handleFileChange" :file-list="fileList"
          accept=".xlsx,.xls,.csv">
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持xlsx/xls/csv文件，文件大小不超过5MB
            </div>
          </template>
        </el-upload>

        <!-- 导入结果显示 -->
        <div v-if="importResult" style="margin-top: 15px; padding: 10px; background-color: #f5f7fa;">
          <h4>导入结果：</h4>
          <p>总记录数: {{ importResult.total_records }}</p>
          <p style="color: #67c23a;">成功记录数: {{ importResult.success_records }}</p>
          <p style="color: #f56c6c;">失败记录数: {{ importResult.error_records }}</p>
          <div v-if="importResult.errors && importResult.errors.length > 0">
            <h5 style="color: #f56c6c;">错误信息：</h5>
            <ul style="max-height: 150px; overflow-y: auto;">
              <li v-for="(error, index) in importResult.errors" :key="index" style="color: #f56c6c;">
                {{ error }}
              </li>
            </ul>
          </div>
        </div>

        <template #footer>
          <span class="dialog-footer">
            <el-button @click="closeImportDialog">取消</el-button>
            <el-button type="primary" @click="handleImport" :loading="importLoading" :disabled="!selectedFile">
              导入
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
    <!-- 导入弹窗结束 -->

    <!-- 编辑弹窗开始 -->
    <el-dialog v-model="DataEditVisible" title="编辑学生信息" width="70%" align-center>
      <el-form 
        ref="editFormRef" 
        :model="editForm" 
        :rules="editRules" 
        label-width="140px" 
        style="padding: 0 20px;">
        
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="姓名" prop="name">
                <el-input v-model="editForm.name" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="学号" prop="school_id">
                <el-input v-model="editForm.school_id" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="年级" prop="grade">
                <el-select v-model="editForm.grade" placeholder="请选择年级" style="width: 100%">
                  <el-option label="七年级" value="七年级" />
                  <el-option label="八年级" value="八年级" />
                  <el-option label="九年级" value="九年级" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="班级" prop="class_name">
                <el-input v-model="editForm.class_name" placeholder="如：1班" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="身份证号" prop="id_card">
                <el-input v-model="editForm.id_card" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="广州学籍号" prop="gz_student_id">
                <el-input v-model="editForm.gz_student_id" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="全国学籍号" prop="national_student_id">
                <el-input v-model="editForm.national_student_id" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <h3 class="section-title">地址信息</h3>
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="户籍所在地" prop="household_address">
                <el-input v-model="editForm.household_address" type="textarea" :rows="2" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="居住所在地" prop="living_address">
                <el-input v-model="editForm.living_address" type="textarea" :rows="2" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <h3 class="section-title">监护人信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="监护人(父亲)" prop="guardian_father">
                <el-input v-model="editForm.guardian_father" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="监护人(母亲)" prop="guardian_mother">
                <el-input v-model="editForm.guardian_mother" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="监护人(父亲)电话" prop="guardian_father_phone">
                <el-input v-model="editForm.guardian_father_phone" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="监护人(母亲)电话" prop="guardian_mother_phone">
                <el-input v-model="editForm.guardian_mother_phone" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="DataEditVisible = false">取消</el-button>
          <el-button type="primary" @click="handleUpdate" :loading="updateLoading">
            确认更新
          </el-button>
        </span>
      </template>
    </el-dialog>
    <!-- 编辑弹窗结束 -->

    <!-- 详情查看弹窗开始 -->
    <el-dialog v-model="DataDetailVisible" title="学生详细信息" width="70%" align-center>
      <div v-if="currentDetail" class="detail-container">
        
        <!-- 基本信息 -->
        <el-descriptions 
          title="基本信息" 
          :column="3" 
          border 
          class="detail-descriptions">
          <template #title>
            <div class="descriptions-title">
              <el-icon color="#409eff"><User /></el-icon>
              <span>基本信息</span>
            </div>
          </template>
          
          <el-descriptions-item 
            label="姓名" 
            label-width="110px">
            <el-tag type="primary" size="large">{{ currentDetail.name }}</el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="学号" 
            label-width="110px">
            <span class="info-text">{{ currentDetail.school_id }}</span>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="年级" 
            label-width="110px">
            <el-tag type="success" size="small">{{ currentDetail.grade || '未设置' }}</el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="班级" 
            label-width="110px">
            <el-tag type="info" size="small">{{ currentDetail.class_name || '未分班' }}</el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="当前状态" 
            label-width="110px">
            <el-tag 
              :type="currentDetail.status_color || 'success'" 
              size="small"
              :effect="currentDetail.current_status === 'suspended' ? 'dark' : 'light'">
              <el-icon v-if="currentDetail.current_status === 'suspended'">
                <WarningFilled />
              </el-icon>
              {{ currentDetail.status_display || '在校' }}
            </el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="身份证号" 
            label-width="110px">
            <span class="info-text">{{ currentDetail.id_card }}</span>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="年龄" 
            label-width="110px">
            <span class="info-text">{{ currentDetail.age }}岁</span>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="广州学籍号"
            label-width="110px">
            <span class="info-text">{{ currentDetail.gz_student_id }}</span>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="全国学籍号" 
            label-width="110px">
            <span class="info-text">{{ currentDetail.national_student_id || '暂无' }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 地址信息 -->
        <el-descriptions 
          title="地址信息" 
          :column="1" 
          border 
          class="detail-descriptions">
          <template #title>
            <div class="descriptions-title">
              <el-icon color="#67c23a"><Location /></el-icon>
              <span>地址信息</span>
            </div>
          </template>
          
          <el-descriptions-item label="户籍所在地" label-width="120px">
            <span class="address-text">{{ currentDetail.household_address || '暂无' }}</span>
          </el-descriptions-item>
          
          <el-descriptions-item label="居住所在地" label-width="120px">
            <span class="address-text">{{ currentDetail.living_address || '暂无' }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 监护人信息 -->
        <el-descriptions 
          title="监护人信息" 
          :column="2" 
          border 
          class="detail-descriptions">
          <template #title>
            <div class="descriptions-title">
              <el-icon color="#e6a23c"><Avatar /></el-icon>
              <span>监护人信息</span>
            </div>
          </template>
          
          <el-descriptions-item 
            label="监护人(父亲)" 
            label-width="130px">
            <div class="guardian-info">
              <el-avatar 
                :size="30" 
                style="background-color: #409eff; margin-right: 8px;">
                <el-icon><Male /></el-icon>
              </el-avatar>
              <span class="info-text">{{ currentDetail.guardian_father || '暂无' }}</span>
            </div>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="监护人(母亲)" 
            label-width="130px">
            <div class="guardian-info">
              <el-avatar 
                :size="30" 
                style="background-color: #f56c6c; margin-right: 8px;">
                <el-icon><Female /></el-icon>
              </el-avatar>
              <span class="info-text">{{ currentDetail.guardian_mother || '暂无' }}</span>
            </div>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="父亲联系电话">
            <div class="phone-info">
              <el-icon color="#409eff" style="margin-right: 5px;"><Phone /></el-icon>
              <span class="info-text">{{ currentDetail.guardian_father_phone || '暂无' }}</span>
              <el-button 
                v-if="currentDetail.guardian_father_phone" 
                type="primary" 
                size="small" 
                text 
                style="margin-left: 10px;"
                @click="callPhone(currentDetail.guardian_father_phone)">
                拨打
              </el-button>
            </div>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="母亲联系电话">
            <div class="phone-info">
              <el-icon color="#f56c6c" style="margin-right: 5px;"><Phone /></el-icon>
              <span class="info-text">{{ currentDetail.guardian_mother_phone || '暂无' }}</span>
              <el-button 
                v-if="currentDetail.guardian_mother_phone" 
                type="danger" 
                size="small" 
                text 
                style="margin-left: 10px;"
                @click="callPhone(currentDetail.guardian_mother_phone)">
                拨打
              </el-button>
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 系统信息 -->
        <el-descriptions 
          title="系统信息" 
          :column="2" 
          border 
          class="detail-descriptions">
          <template #title>
            <div class="descriptions-title">
              <el-icon color="#909399"><InfoFilled /></el-icon>
              <span>系统信息</span>
            </div>
          </template>
          
          <el-descriptions-item 
            label="创建时间" 
            :width="120">
            <span class="info-text">{{ formatDate(currentDetail.created_at) }}</span>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="更新时间" 
            :width="120">
            <span class="info-text">{{ formatDate(currentDetail.updated_at) }}</span>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="学生状态" 
            :width="120">
            <el-tag 
              :type="currentDetail.status_color || 'success'" 
              size="small"
              :effect="currentDetail.current_status === 'suspended' ? 'dark' : 'light'">
              {{ currentDetail.status_display || '在校' }}
            </el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item 
            label="数据完整度" 
            :width="120">
            <div class="completeness-info">
              <el-progress 
                :percentage="calculateCompleteness(currentDetail)" 
                :color="getCompletenessColor(calculateCompleteness(currentDetail))"
                :stroke-width="8"
                style="width: 120px;" />
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 状态说明 -->
        <div v-if="currentDetail.current_status === 'suspended'" 
             class="status-notice">
          <el-alert
            title="休学状态提醒"
            type="warning"
            :closable="false"
            show-icon>
            <template #default>
              <p>该学生当前处于休学状态，部分操作可能受限。</p>
              <p>如需恢复学习，请办理复学手续。</p>
            </template>
          </el-alert>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="DataDetailVisible = false">关闭</el-button>
          <el-button type="primary" @click="handleEditFromDetail"
                     :disabled="currentDetail?.current_status === 'suspended'">
            <el-icon><Edit /></el-icon>
            编辑信息
          </el-button>
        </span>
      </template>
    </el-dialog>
    <!-- 详情查看弹窗结束 -->

  </div>
</template>

<script setup>
import { reactive, ref, onMounted, onUnmounted, h, computed } from 'vue'
import {
  Check,
  Delete,
  Edit,
  Message,
  Search,
  Star,
  UploadFilled,
  Download,
  WarningFilled,
  User,
  Location,
  Avatar,
  Male,
  Female,
  Phone,
  InfoFilled
} from '@element-plus/icons-vue'
import { ElLoading, ElMessage, ElMessageBox, ElButton, ElIcon, ElTag, ElCheckbox } from 'element-plus'
import { studentAPI } from '@/api/student'
import { generateStudentTemplate } from '@/utils/excelTemplate'
import * as XLSX from 'xlsx'
import PermissionWrapper from '@/components/PermissionWrapper.vue'
import { useUserStore } from '@/utils/userStore'

// 搜索表单
const searchForm = reactive({
  keyword: ''
})

// 分页信息
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 表格数据和加载状态
const tableData = ref([])
const tableLoading = ref(false)

// 弹窗状态
const DataImportVisible = ref(false)
const DataExportVisible = ref(false)
const DataDeleteVisible = ref(false)

// 导入相关
const importLoading = ref(false)
const selectedFile = ref(null)
const fileList = ref([])
const importResult = ref(null)

// 选中的行数据
const selectedRows = ref([])

// 删除相关
const deleteLoading = ref(false)
const deleteType = ref('batch') // 'batch' 或 'single'
const deleteTarget = ref(null) // 单个删除时的目标行

// 详情查看相关
const DataDetailVisible = ref(false)
const currentDetail = ref(null)

// 编辑相关
const DataEditVisible = ref(false)
const editFormRef = ref()
const updateLoading = ref(false)
const editForm = reactive({
  id: null,
  name: '',
  school_id: '',
  grade: '',
  class_name: '',
  id_card: '',
  age: null,
  gz_student_id: '',
  national_student_id: '',
  household_address: '',
  living_address: '',
  guardian_father: '',
  guardian_mother: '',
  guardian_father_phone: '',
  guardian_mother_phone: ''
})

// 表单验证规则
const editRules = reactive({
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  school_id: [
    { required: true, message: '请输入学号', trigger: 'blur' }
  ],
  id_card: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/, message: '身份证号格式不正确', trigger: 'blur' }
  ],
  age: [
    { required: true, message: '请输入年龄', trigger: 'blur' }
  ],
  gz_student_id: [
    { required: true, message: '请输入广州学籍号', trigger: 'blur' }
  ]
})

// 虚拟滚动表格列配置
const tableColumns = computed(() => [
  // 选择列
  {
    key: 'selection',
    title: '选择',
    width: 60,
    align: 'center',
    fixed: 'left',
    cellRenderer: ({ rowData, rowIndex }) => {
      const isSelected = selectedRows.value.some(row => row.id === rowData.id)
      return h(ElCheckbox, {
        modelValue: isSelected,
        disabled: rowData.current_status === 'suspended',
        onChange: (val) => handleSingleSelection(rowData, val)
      })
    },
    headerCellRenderer: () => {
      const selectableRows = getSelectableRows()
      const isIndeterminate = selectedRows.value.length > 0 && selectedRows.value.length < selectableRows.length
      const isAllSelected = selectedRows.value.length > 0 && selectedRows.value.length === selectableRows.length
      
      return h(ElCheckbox, {
        modelValue: isAllSelected,
        indeterminate: isIndeterminate,
        onChange: handleSelectAll
      })
    }
  },
  
  // 姓名列
  {
    key: 'name',
    title: '姓名',
    width: 120,
    align: 'center',
    fixed: 'left',
    cellRenderer: ({ rowData }) => {
      return h('span', {
        style: {
          fontWeight: '500',
          color: rowData.current_status === 'suspended' ? '#909399' : '#303133'
        }
      }, rowData.name || '')
    }
  },
  
  // 学号列 - 修复显示问题
  {
    key: 'school_id',
    title: '学号',
    width: 120,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.school_id || '')
    }
  },
  
  // 年级列 - 修复显示问题
  {
    key: 'grade',
    title: '年级',
    width: 100,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.grade || '')
    }
  },
  
  // 班级列 - 修复显示问题
  {
    key: 'class_name',
    title: '班级',
    width: 100,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.class_name || '')
    }
  },
  
  // 状态列
  {
    key: 'status',
    title: '状态',
    width: 120,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      const statusConfig = getStatusConfig(rowData.current_status)
      return h(ElTag, {
        type: statusConfig.type,
        size: 'small',
        effect: statusConfig.effect
      }, () => statusConfig.text)
    }
  },
  
  // 身份证号列 - 修复显示问题
  {
    key: 'id_card',
    title: '身份证号',
    width: 200,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.id_card || '')
    }
  },
  
  // 年龄列
  {
    key: 'age',
    title: '年龄',
    width: 80,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.age ? `${rowData.age}岁` : '')
    }
  },
  
  // 广州学籍号列 - 修复显示问题
  {
    key: 'gz_student_id',
    title: '广州学籍号',
    width: 200,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.gz_student_id || '')
    }
  },
  
  // 全国学籍号列
  {
    key: 'national_student_id',
    title: '全国学籍号',
    width: 200,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.national_student_id || '暂无')
    }
  },
  
  // 户籍所在地列
  {
    key: 'household_address',
    title: '户籍所在地',
    width: 300,
    cellRenderer: ({ rowData }) => {
      return h('div', {
        style: { 
          textAlign: 'left', 
          padding: '0 10px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        },
        title: rowData.household_address || '暂无'
      }, rowData.household_address || '暂无')
    }
  },
  
  // 居住所在地列
  {
    key: 'living_address',
    title: '居住所在地',
    width: 300,
    cellRenderer: ({ rowData }) => {
      return h('div', {
        style: { 
          textAlign: 'left', 
          padding: '0 10px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        },
        title: rowData.living_address || '暂无'
      }, rowData.living_address || '暂无')
    }
  },
  
  // 监护人(父亲)列
  {
    key: 'guardian_father',
    title: '监护人(父亲)',
    width: 130,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.guardian_father || '暂无')
    }
  },
  
  // 监护人(母亲)列
  {
    key: 'guardian_mother',
    title: '监护人(母亲)',
    width: 130,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.guardian_mother || '暂无')
    }
  },
  
  // 监护人(父亲)电话列
  {
    key: 'guardian_father_phone',
    title: '监护人(父亲)电话',
    width: 180,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.guardian_father_phone || '暂无')
    }
  },
  
  // 监护人(母亲)电话列
  {
    key: 'guardian_mother_phone',
    title: '监护人(母亲)电话',
    width: 180,
    align: 'center',
    cellRenderer: ({ rowData }) => {
      return h('span', {}, rowData.guardian_mother_phone || '暂无')
    }
  },
  
  // 操作列
  {
    key: 'actions',
    title: '操作',
    width: 180,
    align: 'center',
    fixed: 'right',
    cellRenderer: ({ rowData }) => {
      const isSuspended = rowData.current_status === 'suspended'
      const userStore = useUserStore()
      const canEdit = userStore.canPerform('edit')
      const canDelete = userStore.canPerform('delete')
      
      return h('div', {
        style: { display: 'flex', justifyContent: 'center', gap: '8px' }
      }, [
        // 查看详情按钮 - 所有用户都可以查看
        h(ElButton, {
          icon: Search,
          circle: true,
          size: 'default',
          onClick: () => handleViewDetail(rowData)
        }),
        
        // 编辑按钮 - 仅管理员可见
        canEdit && h(ElButton, {
          type: 'primary',
          icon: Edit,
          circle: true,
          size: 'default',
          disabled: isSuspended,
          onClick: () => handleEdit(rowData)
        }),
        
        // 删除按钮 - 仅管理员可见
        canDelete && h(ElButton, {
          type: 'danger',
          icon: Delete,
          circle: true,
          size: 'default',
          disabled: isSuspended,
          onClick: () => handleSingleDelete(rowData)
        })
      ].filter(Boolean)) // 过滤掉falsy值
    }
  }
])

// 获取状态配置
const getStatusConfig = (status) => {
  switch (status) {
    case 'suspended':
      return { type: 'warning', effect: 'dark', text: '休学' }
    case 'transferred_out':
      return { type: 'info', effect: 'light', text: '已转出' }
    default:
      return { type: 'success', effect: 'light', text: '在校' }
  }
}

// 获取可选择的行（排除休学状态）
const getSelectableRows = () => {
  return tableData.value.filter(row => row.current_status !== 'suspended')
}

// 处理单个选择
const handleSingleSelection = (rowData, selected) => {
  if (rowData.current_status === 'suspended') {
    ElMessage.warning('休学状态的学生无法选择')
    return
  }
  
  if (selected) {
    if (!selectedRows.value.some(row => row.id === rowData.id)) {
      selectedRows.value.push(rowData)
    }
  } else {
    const index = selectedRows.value.findIndex(row => row.id === rowData.id)
    if (index > -1) {
      selectedRows.value.splice(index, 1)
    }
  }
}

// 处理全选
const handleSelectAll = (selected) => {
  const selectableRows = getSelectableRows()
  
  if (selected) {
    // 全选：添加所有可选择的行
    selectableRows.forEach(row => {
      if (!selectedRows.value.some(selectedRow => selectedRow.id === row.id)) {
        selectedRows.value.push(row)
      }
    })
  } else {
    // 取消全选：移除当前页面的所有行
    const currentPageIds = selectableRows.map(row => row.id)
    selectedRows.value = selectedRows.value.filter(row => !currentPageIds.includes(row.id))
  }
}

// 处理行点击（可选功能）
const handleRowClick = (event) => {
  console.log('行被点击:', event)
}

// 修复数据加载函数
const loadStudentData = async () => {
  tableLoading.value = true
  try {
    const params = {
      page: pagination.pageSize === 0 ? 1 : pagination.currentPage,
      page_size: pagination.pageSize === 0 ? 999999 : pagination.pageSize,
      search: searchForm.keyword
    }
    
    const response = await studentAPI.getStudentList(params)
    
    // 直接使用原始数据，不进行额外处理
    tableData.value = response.data || []
    pagination.total = response.total || 0
    
    // 清空选择
    selectedRows.value = []
    
    console.log('数据加载完成:', response.data?.length || 0, '条记录')
    
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  } finally {
    tableLoading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.currentPage = 1
  loadStudentData()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  pagination.currentPage = 1
  loadStudentData()
}

// 分页处理
const handlePageChange = (page) => {
  pagination.currentPage = page
  loadStudentData()
}

// 页面大小变化处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadStudentData()
}

// 文件选择处理
const handleFileChange = (file) => {
  selectedFile.value = file.raw
  importResult.value = null
}

// 导入处理函数
const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要导入的文件')
    return
  }

  importLoading.value = true

  try {
    const response = await studentAPI.importData(selectedFile.value)

    ElMessage.success('导入完成!')
    importResult.value = response.data

    // 刷新表格数据
    loadStudentData()

  } catch (error) {
    console.error('导入失败:', error)
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error('导入失败: ' + error.response.data.error)
    } else {
      ElMessage.error('导入失败: ' + error.message)
    }
  } finally {
    importLoading.value = false
  }
}

// 关闭导入弹窗
const closeImportDialog = () => {
  DataImportVisible.value = false
  selectedFile.value = null
  fileList.value = []
  importResult.value = null
}

// 下载模板
const downloadTemplate = () => {
  try {
    generateStudentTemplate()
    ElMessage.success('模板下载成功！')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败: ' + error.message)
  }
}

// 处理表格选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 批量删除处理
const handleBatchDelete = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的数据')
    return
  }
  
  // 检查是否有休学状态的学生
  const suspendedStudents = selectedRows.value.filter(row => row.current_status === 'suspended')
  if (suspendedStudents.length > 0) {
    ElMessage.warning(`选中的学生中有 ${suspendedStudents.length} 名处于休学状态，无法删除`)
    return
  }
  
  deleteType.value = 'batch'
  DataDeleteVisible.value = true
}

// 单个删除处理
const handleSingleDelete = (row) => {
  if (row.current_status === 'suspended') {
    ElMessage.warning('休学状态的学生无法删除')
    return
  }
  
  deleteType.value = 'single'
  deleteTarget.value = row
  DataDeleteVisible.value = true
}

// 确认删除
const confirmDelete = async () => {
  deleteLoading.value = true
  
  try {
    let idsToDelete = []
    
    if (deleteType.value === 'batch') {
      idsToDelete = selectedRows.value.map(row => row.id)
    } else {
      idsToDelete = [deleteTarget.value.id]
    }
    
    const response = await studentAPI.deleteStudents(idsToDelete)
    
    ElMessage.success(response.message || '删除成功！')
    
    // 关闭弹窗
    DataDeleteVisible.value = false
    
    // 清空选中状态
    selectedRows.value = []
    deleteTarget.value = null
    
    // 刷新数据
    await loadStudentData()
    
  } catch (error) {
    console.error('删除失败:', error)
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error('删除失败: ' + error.response.data.error)
    } else {
      ElMessage.error('删除失败: ' + error.message)
    }
  } finally {
    deleteLoading.value = false
  }
}

// 导出处理函数
const handleExport = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '正在导出数据...',
    background: 'rgba(0, 0, 0, 0.7)',
  })

  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    // 准备导出数据
    const exportData = tableData.value.map(item => ({
      '学号': item.school_id,
      '姓名': item.name,
      '年级': item.grade,
      '班级': item.class_name,
      '身份证号': item.id_card,
      '年龄': item.age,
      '广州学籍号': item.gz_student_id,
      '全国学籍号': item.national_student_id,
      '户籍所在地': item.household_address,
      '居住所在地': item.living_address,
      '监护人(父亲)': item.guardian_father,
      '监护人(母亲)': item.guardian_mother,
      '监护人(父亲)电话': item.guardian_father_phone,
      '监护人(母亲)电话': item.guardian_mother_phone
    }))

    // 创建工作表
    const ws = XLSX.utils.json_to_sheet(exportData)
    
    // 设置列宽
    const colWidths = [
      { wch: 10 }, { wch: 10 }, { wch: 20 }, { wch: 8 },
      { wch: 15 }, { wch: 18 }, { wch: 30 }, { wch: 30 },
      { wch: 12 }, { wch: 12 }, { wch: 15 }, { wch: 15 }
    ]
    ws['!cols'] = colWidths

    // 创建工作簿
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '学生数据')

    // 生成文件名
    const fileName = `学生数据导出_${new Date().getFullYear()}${String(new Date().getMonth() + 1).padStart(2, '0')}${String(new Date().getDate()).padStart(2, '0')}.xlsx`
    
    // 下载文件
    XLSX.writeFile(wb, fileName)
    
    ElMessage.success('导出成功！')
    
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + error.message)
  } finally {
    loading.close()
  }
}

// 查看详情处理
const handleViewDetail = (row) => {
  currentDetail.value = row
  DataDetailVisible.value = true
}

// 编辑处理
const handleEdit = (row) => {
  if (row.current_status === 'suspended') {
    ElMessage.warning('休学状态的学生信息无法编辑')
    return
  }
  
  // 复制数据到编辑表单
  Object.keys(editForm).forEach(key => {
    editForm[key] = row[key] || ''
  })
  editForm.id = row.id
  DataEditVisible.value = true
}

// 更新处理
const handleUpdate = async () => {
  try {
    // 表单验证
    await editFormRef.value.validate()
    
    updateLoading.value = true
    
    // 准备更新数据
    const updateData = { ...editForm }
    delete updateData.id // 移除id字段
    
    const response = await studentAPI.updateStudent(editForm.id, updateData)
    
    ElMessage.success(response.message || '更新成功！')
    
    // 关闭弹窗
    DataEditVisible.value = false
    
    // 刷新数据
    await loadStudentData()
    
  } catch (error) {
    console.error('更新失败:', error)
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error('更新失败: ' + error.response.data.error)
    } else {
      ElMessage.error('更新失败: ' + error.message)
    }
  } finally {
    updateLoading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '暂无'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 计算数据完整度（更新字段列表）
const calculateCompleteness = (student) => {
    // 必填字段
    const requiredFields = [
        'name', 'school_id', 'id_card', 'age', 'grade', 'class_name', 'gz_student_id'
    ]
    
    // 可选字段
    const optionalFields = [
        'national_student_id', 'household_address', 'living_address',
        'guardian_father', 'guardian_mother', 'guardian_father_phone', 'guardian_mother_phone'
    ]
    
    // 计算必填字段完成度
    const requiredFilled = requiredFields.filter(field => 
        student[field] && student[field].toString().trim() !== ''
    )
    
    // 计算可选字段完成度
    const optionalFilled = optionalFields.filter(field => 
        student[field] && student[field].toString().trim() !== ''
    )
    
    // 必填字段权重80%，可选字段权重20%
    const requiredRate = (requiredFilled.length / requiredFields.length) * 0.8
    const optionalRate = (optionalFilled.length / optionalFields.length) * 0.2
    
    return Math.round((requiredRate + optionalRate) * 100)
}

// 获取完整度颜色
const getCompletenessColor = (percentage) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 70) return '#e6a23c'
  return '#f56c6c'
}

// 从详情页面跳转到编辑
const handleEditFromDetail = () => {
  if (currentDetail.value?.current_status === 'suspended') {
    ElMessage.warning('休学状态的学生信息无法编辑')
    return
  }
  
  DataDetailVisible.value = false
  handleEdit(currentDetail.value)
}

// 页面加载时获取数据并添加事件监听
onMounted(() => {
  loadStudentData()
  
  // **监听学生转出事件**
  window.addEventListener('student-transferred-out', handleStudentTransferredOut)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener('student-transferred-out', handleStudentTransferredOut)
})

// **处理学生转出事件**
const handleStudentTransferredOut = (event) => {
  const { studentId, studentName, targetSchool } = event.detail
  
  console.log(`学生 ${studentName} 已转出到 ${targetSchool}`)
  
  // 从表格数据中移除该学生
  const index = tableData.value.findIndex(student => student.id === studentId)
  if (index !== -1) {
    tableData.value.splice(index, 1)
    pagination.total = Math.max(0, pagination.total - 1)
  }
  
  // 清空选中状态（如果被选中的学生被转出）
  selectedRows.value = selectedRows.value.filter(row => row.id !== studentId)
  
  // 显示提示消息
  ElMessage.info({
    message: `学生 ${studentName} 已成功转出，已从列表中移除`,
    duration: 3000
  })
}
</script>

<style scoped>
.search-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.virtual-table-container {
  height: calc(82vh - 100px); /* 调整高度以适应新的分页区域 */
  border: 1px solid #ebeef5;
  border-radius: 6px;
}

.dialog-footer button:first-child {
  margin-right: 10px;
}

.upload-demo {
  margin-top: 10px;
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

/* 休学状态行的特殊样式 */
:deep(.el-table-v2__row[data-status="suspended"]) {
  background-color: #fef0f0 !important;
}

/* 自定义滚动条样式 */
:deep(.el-table-v2__scrollbar) {
  width: 8px;
}

:deep(.el-table-v2__scrollbar-thumb) {
  background-color: #c1c1c1;
  border-radius: 4px;
}

/* 详情页面样式保持不变 */
.detail-container {
  padding: 0;
}

.detail-descriptions {
  margin-bottom: 20px;
}

.descriptions-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.info-text {
  color: #303133;
  font-size: 14px;
}

.address-text {
  color: #303133;
  font-size: 14px;
  line-height: 1.5;
}

.guardian-info {
  display: flex;
  align-items: center;
}

.phone-info {
  display: flex;
  align-items: center;
}

.completeness-info {
  display: flex;
  align-items: center;
}

.status-notice {
  margin-top: 20px;
}
</style>