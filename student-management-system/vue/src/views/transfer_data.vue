<template>
    <div>
        <!-- 工具栏开始 -->
        <div class="card" style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <el-input 
                        v-model="searchForm.keyword" 
                        style="width: 250px;" 
                        placeholder="请输入学生姓名或学号"
                        @keyup.enter="handleSearch" 
                        clearable>
                        <template #prepend>
                            <el-icon><Search /></el-icon>
                        </template>
                    </el-input>
                    <el-select 
                        v-model="searchForm.transferType" 
                        placeholder="异动类型" 
                        style="width: 120px;"
                        clearable
                        @change="handleSearch">
                        <el-option label="转入" value="transfer_in" />
                        <el-option label="转出" value="transfer_out" />
                        <el-option label="休学" value="suspend" />
                        <el-option label="复学" value="resume" />
                    </el-select>
                    <el-button type="primary" @click="handleSearch" :loading="tableLoading">
                        <el-icon><Search /></el-icon>
                        查询
                    </el-button>
                    <el-button @click="handleReset" style="margin-left: 0px;">
                        <el-icon><RefreshLeft /></el-icon>
                        重置
                    </el-button>
                </div>
                
                <div>
                    <el-button type="success" @click="refreshData">
                        <el-icon><Refresh /></el-icon>
                        刷新数据
                    </el-button>
                </div>
            </div>
        </div>
        <!-- 工具栏结束 -->

        <!-- 统计信息 -->
        <div class="stats-container" style="margin-bottom: 15px;">
            <div class="stat-card">
                <div class="stat-number">{{ stats.totalRecords }}</div>
                <div class="stat-label">转学记录总数</div>
            </div>
            <div class="stat-card transfer-in">
                <div class="stat-number">{{ stats.transferInCount }}</div>
                <div class="stat-label">转入记录</div>
            </div>
            <div class="stat-card transfer-out">
                <div class="stat-number">{{ stats.transferOutCount }}</div>
                <div class="stat-label">转出记录</div>
            </div>
            <div class="stat-card pending">
                <div class="stat-number">{{ stats.pendingCount }}</div>
                <div class="stat-label">待处理</div>
            </div>
        </div>

        <!-- 虚拟滚动表格开始 -->
        <div class="card">
            <div class="virtual-table-container" v-loading="tableLoading">
                <el-auto-resizer>
                    <template #default="{ height, width }">
                        <el-table-v2
                            :columns="tableColumns"
                            :data="tableData"
                            :width="width"
                            :height="height - 60"
                            :row-height="80"
                            :header-height="50"
                            fixed
                            row-key="id"
                        />
                    </template>
                </el-auto-resizer>
            </div>

            <!-- 分页组件 -->
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 10px; border-top: 1px solid #ebeef5;">
                <div style="display: flex; align-items: center;">
                    <span style="margin-right: 8px; color: #606266; font-size: 14px;">每页显示</span>
                    <el-select 
                        v-model="pagination.pageSize" 
                        @change="handleSizeChange"
                        style="width: 100px; margin-right: 10px;">
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
                    @current-change="handlePageChange" />
                
                <!-- 显示全部时只显示总数 -->
                <div v-else style="color: #606266; font-size: 14px;">
                    共 {{ pagination.total }} 条数据
                </div>
            </div>
        </div>
        <!-- 虚拟滚动表格结束 -->

        <!-- 详情弹窗 -->
        <el-dialog v-model="detailVisible" title="转学记录详情" width="70%" align-center>
            <div v-if="currentRecord" class="detail-container">
                
                <!-- 学生基本信息 -->
                <el-descriptions 
                    title="学生信息" 
                    :column="3" 
                    border 
                    class="detail-descriptions">
                    <template #title>
                        <div class="descriptions-title">
                            <el-icon color="#409eff"><User /></el-icon>
                            <span>学生信息</span>
                        </div>
                    </template>
                    
                    <el-descriptions-item label="姓名">
                        <el-tag type="primary" size="large">{{ currentRecord.student_name }}</el-tag>
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
                    class="detail-descriptions">
                    <template #title>
                        <div class="descriptions-title">
                            <el-icon color="#67c23a"><Promotion /></el-icon>
                            <span>转学信息</span>
                        </div>
                    </template>
                    
                    <el-descriptions-item label="转学类型">
                        <el-tag 
                            :type="currentRecord.transfer_type === 'transfer_in' ? 'success' : 'warning'" 
                            size="large">
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
                    class="detail-descriptions">
                    <template #title>
                        <div class="descriptions-title">
                            <el-icon color="#e6a23c"><Operation /></el-icon>
                            <span>处理信息</span>
                        </div>
                    </template>
                    
                    <el-descriptions-item label="处理状态">
                        <el-tag :type="getStatusTagType(currentRecord.status)" size="large">
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
                    <el-button @click="detailVisible = false">关闭</el-button>
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
        width: 120,
        align: 'center',
        fixed: 'left',
        cellRenderer: ({ rowData }) => {
            return h('span', {
                style: { fontWeight: '500', color: '#303133' }
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
            return h('span', {}, rowData.student_school_id || '')
        }
    },
    
    // 年级列
    {
        key: 'student_grade',
        title: '年级',
        width: 80,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h('span', {}, rowData.student_grade || '')
        }
    },
    
    // 班级列
    {
        key: 'student_class_name',
        title: '班级',
        width: 80,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h('span', {}, rowData.student_class_name || '')
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
                size: 'small'
            }, () => rowData.transfer_type_display || '')
        }
    },
    
    // 异动日期列
    {
        key: 'transfer_date',
        title: '异动日期',
        width: 160,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h('span', {}, rowData.transfer_date || '')
        }
    },
    
    // 异动详情列（复杂渲染）
    {
        key: 'transfer_details',
        title: '异动详情',
        width: 280,
        cellRenderer: ({ rowData }) => {
            return renderTransferDetails(rowData,)
        }
    },
    
    // 异动原因列
    {
        key: 'transfer_reason',
        title: '异动原因',
        width: 250,
        cellRenderer: ({ rowData }) => {
            return h('div', {
                style: {
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    padding: '0 8px'
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
                size: 'small'
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
            return h('span', {}, rowData.processor || '')
        }
    },
    
    // 处理时间列
    {
        key: 'process_time',
        title: '处理时间',
        width: 180,
        align: 'center',
        cellRenderer: ({ rowData }) => {
            return h('span', {}, formatDate(rowData.process_time))
        }
    },
    
    // 操作列 - 只保留查看详情按钮
    {
        key: 'actions',
        title: '操作',
        width: 80,
        align: 'center',
        fixed: 'right',
        cellRenderer: ({ rowData }) => {
            return h('div', {
                style: { display: 'flex', justifyContent: 'center', gap: '8px' }
            }, [
                // 只保留查看详情按钮
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
                h(ElIcon, { color: iconColor }, () => h(iconName)),
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
.stats-container {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
}

.stat-card {
    flex: 1;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.stat-card.transfer-in {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.transfer-out {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.pending {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    color: #333;
}

.stat-number {
    font-size: 2em;
    font-weight: bold;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 0.9em;
    opacity: 0.9;
}

.virtual-table-container {
    height: calc(75vh - 120px);
    border: 1px solid #ebeef5;
    border-radius: 6px;
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
    color: #909399;
    font-size: 11px;
}

.school-name .value {
    color: #303133;
    font-size: 12px;
    font-weight: 500;
}

.school-name .current-school {
    color: #409eff;
    font-weight: 600;
}

.school-info {
    font-size: 13px;
    color: #606266;
}

.text-muted {
    color: #909399;
    font-style: italic;
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
    color: #303133;
}

.info-text {
    color: #303133;
    font-size: 14px;
}

:deep(.el-descriptions__title) {
    margin-bottom: 16px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}

:deep(.el-descriptions__label) {
    font-weight: 600 !important;
    color: #606266 !important;
}

:deep(.el-descriptions__content) {
    color: #303133 !important;
}

:deep(.el-descriptions__table .el-descriptions__cell) {
    padding: 12px 16px !important;
}

.student-info-display {
    margin-bottom: 25px;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 6px;
    border-left: 4px solid #409eff;
}

:deep(.el-select-dropdown__item) {
    height: auto !important;
    padding: 8px 20px !important;
}
</style>