<template>
    <div class="transfer-data-container">
        <!-- 工具栏 -->
        <div class="toolbar-card">
            <div class="toolbar-content">
                <div class="search-controls">
                    <el-input 
                        v-model="searchForm.keyword" 
                        size="default"
                        placeholder="请输入学生姓名或学号"
                        @keyup.enter="handleSearch" 
                        clearable
                        class="search-input">
                        <template #prepend>
                            <el-icon size="16"><Search /></el-icon>
                        </template>
                    </el-input>
                    <el-select 
                        v-model="searchForm.transferType" 
                        placeholder="异动类型" 
                        size="default"
                        clearable
                        @change="handleSearch"
                        class="type-select">
                        <el-option label="转入" value="transfer_in" />
                        <el-option label="转出" value="transfer_out" />
                        <el-option label="休学" value="suspend" />
                        <el-option label="复学" value="resume" />
                    </el-select>
                    <el-button type="primary" size="default" @click="handleSearch" :loading="tableLoading">
                        <el-icon size="16"><Search /></el-icon>
                        查询
                    </el-button>
                    <el-button size="default" @click="handleReset">
                        <el-icon size="16"><RefreshLeft /></el-icon>
                        重置
                    </el-button>
                </div>
                
                <el-button type="success" size="default" @click="refreshData">
                    <el-icon size="16"><Refresh /></el-icon>
                    刷新数据
                </el-button>
            </div>
        </div>

        <!-- 统计信息 -->
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-icon">
                    <el-icon size="20"><InfoFilled /></el-icon>
                </div>
                <div class="stat-content">
                    <div class="stat-number">{{ stats.totalRecords }}</div>
                    <div class="stat-label">转学记录总数</div>
                </div>
            </div>
            <div class="stat-card transfer-in">
                <div class="stat-icon">
                    <el-icon size="20"><Right /></el-icon>
                </div>
                <div class="stat-content">
                    <div class="stat-number">{{ stats.transferInCount }}</div>
                    <div class="stat-label">转入记录</div>
                </div>
            </div>
            <div class="stat-card transfer-out">
                <div class="stat-icon">
                    <el-icon size="20"><Back /></el-icon>
                </div>
                <div class="stat-content">
                    <div class="stat-number">{{ stats.transferOutCount }}</div>
                    <div class="stat-label">转出记录</div>
                </div>
            </div>
            <div class="stat-card pending">
                <div class="stat-icon">
                    <el-icon size="20"><CloseBold /></el-icon>
                </div>
                <div class="stat-content">
                    <div class="stat-number">{{ stats.pendingCount }}</div>
                    <div class="stat-label">待处理</div>
                </div>
            </div>
        </div>

        <!-- 表格区域 -->
        <div class="table-card">
            <div class="virtual-table-container" v-loading="tableLoading">
                <el-auto-resizer>
                    <template #default="{ height, width }">
                        <el-table-v2
                            :columns="tableColumns"
                            :data="tableData"
                            :width="width"
                            :height="height"
                            :row-height="70"
                            :header-height="45"
                            fixed
                            row-key="id"
                        />
                    </template>
                </el-auto-resizer>
            </div>

            <!-- 分页组件 -->
            <div class="pagination-container">
                <div class="page-size-selector">
                    <span class="page-size-label">每页显示</span>
                    <el-select 
                        v-model="pagination.pageSize" 
                        @change="handleSizeChange"
                        size="default"
                        class="page-size-select">
                        <el-option label="10 条/页" :value="10" />
                        <el-option label="20 条/页" :value="20" />
                        <el-option label="50 条/页" :value="50" />
                        <el-option label="100 条/页" :value="100" />
                        <el-option label="200 条/页" :value="200" />
                        <el-option label="全部数据" :value="0" />
                    </el-select>
                </div>
                
                <el-pagination 
                    v-if="pagination.pageSize !== 0"
                    background 
                    layout="total, prev, pager, next, jumper" 
                    :total="pagination.total"
                    :page-size="pagination.pageSize"
                    :current-page="pagination.currentPage"
                    @current-change="handlePageChange"
                    size="default" />
                
                <div v-else class="total-count">
                    共 {{ pagination.total }} 条数据
                </div>
            </div>
        </div>

        <!-- 详情弹窗 -->
        <el-dialog v-model="detailVisible" title="转学记录详情" width="70%" align-center class="detail-dialog">
            <div v-if="currentRecord" class="detail-container">
                
                <!-- 学生基本信息 -->
                <el-descriptions 
                    title="学生信息" 
                    :column="3" 
                    border 
                    size="default"
                    class="detail-descriptions">
                    <template #title>
                        <div class="descriptions-title">
                            <el-icon color="#409eff" size="18"><User /></el-icon>
                            <span>学生信息</span>
                        </div>
                    </template>
                    
                    <el-descriptions-item label="姓名">
                        <el-tag type="primary" size="default">{{ currentRecord.student_name }}</el-tag>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="学号">
                        <span class="info-text">{{ currentRecord.student_school_id }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="年级班级">
                        <span class="info-text">{{ currentRecord.student_grade }}{{ currentRecord.student_class_name }}</span>
                    </el-descriptions-item>
                </el-descriptions>

                <!-- 转学信息 -->
                <el-descriptions 
                    title="转学信息" 
                    :column="2" 
                    border 
                    size="default"
                    class="detail-descriptions">
                    <template #title>
                        <div class="descriptions-title">
                            <el-icon color="#67c23a" size="18"><Promotion /></el-icon>
                            <span>转学信息</span>
                        </div>
                    </template>
                    
                    <el-descriptions-item label="转学类型">
                        <el-tag 
                            :type="currentRecord.transfer_type === 'transfer_in' ? 'success' : 'warning'" 
                            size="default">
                            {{ currentRecord.transfer_type_display }}
                        </el-tag>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="转学日期">
                        <span class="info-text">{{ currentRecord.transfer_date }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="原学校" v-if="currentRecord.previous_school">
                        <span class="info-text">{{ currentRecord.previous_school }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="目标学校" v-if="currentRecord.target_school">
                        <span class="info-text">{{ currentRecord.target_school }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="转学原因" :span="2">
                        <span class="info-text">{{ currentRecord.transfer_reason }}</span>
                    </el-descriptions-item>
                </el-descriptions>

                <!-- 处理信息 -->
                <el-descriptions 
                    title="处理信息" 
                    :column="2" 
                    border 
                    size="default"
                    class="detail-descriptions">
                    <template #title>
                        <div class="descriptions-title">
                            <el-icon color="#e6a23c" size="18"><Operation /></el-icon>
                            <span>处理信息</span>
                        </div>
                    </template>
                    
                    <el-descriptions-item label="处理状态">
                        <el-tag :type="getStatusTagType(currentRecord.status)" size="default">
                            {{ currentRecord.status_display }}
                        </el-tag>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="处理人">
                        <span class="info-text">{{ currentRecord.processor }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="处理时间">
                        <span class="info-text">{{ formatDate(currentRecord.process_time) }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="创建时间">
                        <span class="info-text">{{ formatDate(currentRecord.created_at) }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="备注" :span="2">
                        <span class="info-text">{{ currentRecord.remarks || '暂无备注' }}</span>
                    </el-descriptions-item>
                </el-descriptions>
            </div>
            
            <template #footer>
                <span class="dialog-footer">
                    <el-button size="default" @click="detailVisible = false">关闭</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed, h } from 'vue'
import { ElMessage, ElButton, ElIcon, ElTag } from 'element-plus'
import { 
    Search, 
    RefreshLeft, 
    Refresh,
    View,
    User,
    Promotion,
    Operation,
    Right,
    Back,
    Check,
    CloseBold,
    InfoFilled
} from '@element-plus/icons-vue'
import { studentAPI } from '@/api/student'

// 搜索表单
const searchForm = reactive({
    keyword: '',
    transferType: ''
})

// 分页信息
const pagination = reactive({
    currentPage: 1,
    pageSize: 20,
    total: 0
})

// 表格数据和状态
const tableData = ref([])
const tableLoading = ref(false)

// 详情弹窗
const detailVisible = ref(false)
const currentRecord = ref(null)

// 虚拟滚动表格列配置
const tableColumns = computed(() => [
    // 学生姓名列
    {
        key: 'student_name',
        title: '学生姓名',
        width: 110,
        align: 'center',
        fixed: 'left',
        cellRenderer: ({ rowData }) => {
            return h('span', {
                style: { fontWeight: '500', color: '#303133', fontSize: '14px' }
            }, rowData.student_name || '')
        }
    },
    
    // 学号列
    {
        key: 'student_school_id',
        title: '学号',
        width: 120,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h('span', {
                style: { fontSize: '13px' }
            }, rowData.student_school_id || '')
        }
    },
    
    // 年级列
    {
        key: 'student_grade',
        title: '年级',
        width: 80,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h('span', {
                style: { fontSize: '13px' }
            }, rowData.student_grade || '')
        }
    },
    
    // 班级列
    {
        key: 'student_class_name',
        title: '班级',
        width: 80,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h('span', {
                style: { fontSize: '13px' }
            }, rowData.student_class_name || '')
        }
    },
    
    // 异动类型列
    {
        key: 'transfer_type',
        title: '异动类型',
        width: 100,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h(ElTag, {
                type: getTransferTypeTagType(rowData.transfer_type),
                size: 'default'
            }, () => rowData.transfer_type_display || '')
        }
    },
    
    // 异动日期列
    {
        key: 'transfer_date',
        title: '异动日期',
        width: 130,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h('span', {
                style: { fontSize: '13px' }
            }, rowData.transfer_date || '')
        }
    },
    
    // 异动详情列（复杂渲染）
    {
        key: 'transfer_details',
        title: '异动详情',
        width: 280,
        cellRenderer: ({ rowData }) => {
            return renderTransferDetails(rowData)
        }
    },
    
    // 异动原因列
    {
        key: 'transfer_reason',
        title: '异动原因',
        width: 220,
        cellRenderer: ({ rowData }) => {
            return h('div', {
                style: {
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    padding: '0 8px',
                    fontSize: '13px'
                },
                title: rowData.transfer_reason || ''
            }, rowData.transfer_reason || '')
        }
    },
    
    // 处理状态列
    {
        key: 'status',
        title: '处理状态',
        width: 100,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h(ElTag, {
                type: getStatusTagType(rowData.status),
                size: 'default'
            }, () => rowData.status_display || '')
        }
    },
    
    // 处理人列
    {
        key: 'processor',
        title: '处理人',
        width: 100,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h('span', {
                style: { fontSize: '13px' }
            }, rowData.processor || '')
        }
    },
    
    // 处理时间列
    {
        key: 'process_time',
        title: '处理时间',
        width: 160,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h('span', {
                style: { fontSize: '12px' }
            }, formatDate(rowData.process_time))
        }
    },
    
    // 操作列
    {
        key: 'actions',
        title: '操作',
        width: 80,
        align: 'center',
        fixed: 'right',
        cellRenderer: ({ rowData }) => {
            return h('div', {
                style: { display: 'flex', justifyContent: 'center' }
            }, [
                h(ElButton, {
                    icon: View,
                    circle: true,
                    size: 'default',
                    onClick: () => handleViewDetail(rowData)
                })
            ])
        }
    }
])

// 渲染异动详情的复杂函数
const renderTransferDetails = (rowData) => {
    const createTransferInfo = (iconName, iconColor, directionText, details) => {
        return h('div', {
            class: 'school-transfer-info'
        }, [
            h('div', {
                class: 'transfer-direction'
            }, [
                h(ElIcon, { color: iconColor, size: 16 }, () => h(iconName)),
                h('span', { class: 'direction-text' }, directionText)
            ]),
            ...details.map(detail => 
                h('div', { class: 'school-name' }, [
                    h('span', { class: 'label' }, detail.label),
                    h('span', { 
                        class: detail.isCurrentSchool ? 'value current-school' : 'value' 
                    }, detail.value)
                ])
            )
        ])
    }

    switch (rowData.transfer_type) {
        case 'transfer_in':
            return createTransferInfo(Right, '#67c23a', '转入', [
                { label: '原学校：', value: rowData.previous_school || '未填写', isCurrentSchool: true },
                { label: '目标：', value: rowData.target_school || '本校', isCurrentSchool: true }
            ])
            
        case 'transfer_out':
            return createTransferInfo(Back, '#e6a23c', '转出', [
                { label: '原学校：', value: '本校', isCurrentSchool: true },
                { label: '目标：', value: rowData.target_school || '未填写', isCurrentSchool: true }
            ])
            
        case 'suspend':
            const suspendDetails = [
                { label: '休学时间：', value: rowData.transfer_date }
            ]
            if (rowData.expected_resume_date) {
                suspendDetails.push({ label: '预期复学：', value: rowData.expected_resume_date })
            }
            if (rowData.contact_person) {
                suspendDetails.push({ label: '联系人：', value: rowData.contact_person })
            }
            return createTransferInfo(CloseBold, '#f56c6c', '休学', suspendDetails)
            
        case 'resume':
            const resumeDetails = [
                { label: '复学时间：', value: rowData.transfer_date },
                { label: '复学年级：', value: `${rowData.transfer_grade}${rowData.transfer_class}`, isCurrentSchool: true }
            ]
            if (rowData.previous_school) {
                resumeDetails.push({ label: '休学前：', value: rowData.previous_school || '本校' })
            }
            return createTransferInfo(Check, '#409eff', '复学', resumeDetails)
            
        default:
            return createTransferInfo(InfoFilled, '#909399', rowData.transfer_type_display, [
                { label: '详情：', value: rowData.transfer_reason || '无详细信息' }
            ])
    }
}

// 统计信息
const stats = computed(() => {
    const totalRecords = tableData.value.length
    const transferInCount = tableData.value.filter(item => item.transfer_type === 'transfer_in').length
    const transferOutCount = tableData.value.filter(item => item.transfer_type === 'transfer_out').length
    const pendingCount = tableData.value.filter(item => item.status === 'pending').length
    
    return {
        totalRecords: pagination.total || totalRecords,
        transferInCount,
        transferOutCount,
        pendingCount
    }
})

// 页面加载时获取数据
onMounted(() => {
    loadTransferData()
})

// 加载转学数据
const loadTransferData = async () => {
    tableLoading.value = true
    try {
        const params = {
            page: pagination.pageSize === 0 ? 1 : pagination.currentPage,
            page_size: pagination.pageSize === 0 ? 999999 : pagination.pageSize,
            search: searchForm.keyword,
            transfer_type: searchForm.transferType
        }
        
        const response = await studentAPI.getTransferRecords(params)
        tableData.value = response.data
        pagination.total = response.total
        
        console.log('转学数据加载完成:', response.data?.length || 0, '条记录')
        
    } catch (error) {
        console.error('加载转学数据失败:', error)
        ElMessage.error('加载数据失败: ' + error.message)
    } finally {
        tableLoading.value = false
    }
}

// 搜索处理
const handleSearch = () => {
    pagination.currentPage = 1
    loadTransferData()
}

// 重置搜索
const handleReset = () => {
    searchForm.keyword = ''
    searchForm.transferType = ''
    pagination.currentPage = 1
    loadTransferData()
}

// 刷新数据
const refreshData = () => {
    loadTransferData()
    ElMessage.success('数据已刷新')
}

// 分页处理
const handlePageChange = (page) => {
    pagination.currentPage = page
    loadTransferData()
}

// 页面大小变化处理
const handleSizeChange = (size) => {
    pagination.pageSize = size
    pagination.currentPage = 1
    loadTransferData()
}

// 查看详情
const handleViewDetail = async (row) => {
    try {
        const response = await studentAPI.getTransferRecordDetail(row.id)
        currentRecord.value = response
        detailVisible.value = true
    } catch (error) {
        console.error('获取详情失败:', error)
        ElMessage.error('获取详情失败: ' + error.message)
    }
}

// 获取状态标签类型
const getStatusTagType = (status) => {
    const statusMap = {
        'pending': 'warning',      // 待处理 - 橙色
        'rejected': 'danger',      // 已拒绝 - 红色  
        'completed': 'success'     // 已完成 - 绿色
    }
    return statusMap[status] || 'info'
}

// 获取异动类型标签类型
const getTransferTypeTagType = (transferType) => {
    const typeMap = {
        'transfer_in': 'success',    // 转入 - 绿色
        'transfer_out': 'warning',   // 转出 - 橙色  
        'suspend': 'danger',         // 休学 - 红色
        'resume': 'primary'          // 复学 - 蓝色
    }
    return typeMap[transferType] || 'info'
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
</script>

<style scoped>
/* 整体容器 */
.transfer-data-container {
    padding: 16px;
    background: #f8fafc;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* 工具栏 */
.toolbar-card {
    background: white;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toolbar-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.search-controls {
    display: flex;
    align-items: center;
    gap: 12px;
}

.search-input {
    width: 240px;
}

.type-select {
    width: 120px;
}

/* 统计卡片 */
.stats-container {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
}

.stat-card {
    flex: 1;
    background: white;
    border-radius: 8px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
    cursor: pointer;
}

.stat-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}

.stat-card .stat-icon {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.transfer-in .stat-icon {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.transfer-out .stat-icon {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.pending .stat-icon {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    color: #333;
}

.stat-content {
    flex: 1;
}

.stat-number {
    font-size: 20px;
    font-weight: 700;
    color: #1f2937;
    line-height: 1;
}

.stat-label {
    font-size: 13px;
    color: #6b7280;
    margin-top: 4px;
}

/* 表格卡片 */
.table-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.virtual-table-container {
    flex: 1;
    min-height: 0;
}

/* 分页容器 */
.pagination-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    border-top: 1px solid #e5e7eb;
    background: #fafbfc;
}

.page-size-selector {
    display: flex;
    align-items: center;
    gap: 8px;
}

.page-size-label {
    font-size: 13px;
    color: #6b7280;
}

.page-size-select {
    width: 100px;
}

.total-count {
    color: #6b7280;
    font-size: 13px;
}

/* 虚拟滚动表格样式优化 */
:deep(.el-table-v2__header) {
    background-color: #f8fafc;
    font-weight: 600;
    font-size: 13px;
}

:deep(.el-table-v2__row) {
    border-bottom: 1px solid #f3f4f6;
    font-size: 13px;
}

:deep(.el-table-v2__row:hover) {
    background-color: #f9fafb;
}

:deep(.el-table-v2__cell) {
    padding: 8px 10px;
}

/* 异动详情样式 */
.school-transfer-info {
    font-size: 12px;
    line-height: 1.4;
    padding: 4px;
}

.transfer-direction {
    display: flex;
    align-items: center;
    margin-bottom: 4px;
    font-weight: 600;
}

.direction-text {
    margin-left: 4px;
    font-size: 11px;
}

.school-name {
    margin-bottom: 2px;
}

.school-name .label {
    color: #9ca3af;
    font-size: 11px;
}

.school-name .value {
    color: #374151;
    font-size: 12px;
    font-weight: 500;
}

.school-name .current-school {
    color: #3b82f6;
    font-weight: 600;
}

/* 详情弹窗 */
.detail-dialog {
    --el-dialog-padding-primary: 20px;
}

:deep(.el-dialog__header) {
    padding: 20px 20px 10px;
}

:deep(.el-dialog__body) {
    padding: 10px 20px 20px;
}

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
    color: #1f2937;
}

.info-text {
    color: #374151;
    font-size: 14px;
}

:deep(.el-descriptions__title) {
    margin-bottom: 16px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}

:deep(.el-descriptions__label) {
    font-weight: 600 !important;
    color: #6b7280 !important;
    font-size: 13px !important;
}

:deep(.el-descriptions__content) {
    color: #374151 !important;
    font-size: 14px !important;
}

:deep(.el-descriptions__table .el-descriptions__cell) {
    padding: 10px 16px !important;
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .transfer-data-container {
        padding: 12px;
    }
}

@media (max-width: 768px) {
    .transfer-data-container {
        padding: 8px;
    }
    
    .toolbar-content {
        flex-direction: column;
        gap: 12px;
        align-items: stretch;
    }
    
    .search-controls {
        justify-content: space-between;
        flex-wrap: wrap;
    }
    
    .search-input {
        width: 100%;
        order: 3;
        margin-top: 8px;
    }
    
    .stats-container {
        flex-direction: column;
        gap: 8px;
    }
    
    .stat-card {
        padding: 12px;
    }
    
    .stat-icon {
        width: 36px;
        height: 36px;
    }
    
    .stat-number {
        font-size: 18px;
    }
    
    .pagination-container {
        flex-direction: column;
        gap: 12px;
        align-items: stretch;
    }
}

@media (max-width: 480px) {
    .search-controls {
        gap: 8px;
    }
    
    .type-select {
        width: 100px;
    }
}
</style>