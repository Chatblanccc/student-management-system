<template>
  <div class="card">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>正在加载数据...</p>
    </div>

    <!-- 主要内容 -->
    <div v-else>
      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <div class="welcome-content">
          <h1 class="welcome-title">
            <el-icon class="welcome-icon" :class="smartGreeting.iconClass">
              <component :is="smartGreeting.icon" />
            </el-icon>
            {{ smartGreeting.greeting }}，{{ userName }}
          </h1>
          <p class="welcome-subtitle">
            <el-icon><Calendar /></el-icon>
            今天是 {{ currentDateTime.date }}，{{ currentDateTime.weekday }}
          </p>
          <p class="welcome-time">{{ currentDateTime.time }}</p>
        </div>
        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="navigateTo('/manage/user_data')">
            <el-icon><User /></el-icon>
            管理学生信息
          </el-button>
          <!-- 办理异动按钮 - 仅管理员可见 -->
          <el-button 
            v-if="userStore.isAdmin()" 
            type="success" 
            size="large" 
            @click="navigateTo('/manage/transfer_process')">
            <el-icon><Promotion /></el-icon>
            办理异动
          </el-button>
        </div>
      </div>

      <!-- 数据统计卡片 -->
      <div class="stats-section">
        <div class="stats-container">
          <!-- 主要统计卡片 - 大卡片 -->
          <div class="primary-stats">
            <div class="stat-card-large primary-gradient">
              <div class="stat-card-content">
                <div class="stat-icon-large">
                  <el-icon><User /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number-large">{{ statistics.totalStudents }}</div>
                  <div class="stat-label-large">在校学生总数</div>
                  <div class="stat-change-large positive">
                    <el-icon><ArrowUp /></el-icon>
                    +{{ statistics.newStudentsThisMonth }} 本月新增
                  </div>
                </div>
              </div>
              <div class="stat-decoration">
                <div class="decoration-circle"></div>
                <div class="decoration-circle"></div>
              </div>
            </div>
          </div>

          <!-- 异动统计卡片组 -->
          <div class="transfer-stats">
            <div class="stats-row">
              <div class="stat-card-medium success-gradient">
                <div class="stat-icon-medium">
                  <el-icon><Right /></el-icon>
                </div>
                <div class="stat-content-medium">
                  <div class="stat-number-medium">{{ statistics.transferInCount }}</div>
                  <div class="stat-label-medium">转入学生</div>
                  <div class="stat-badge">本学期</div>
                </div>
              </div>

              <div class="stat-card-medium warning-gradient">
                <div class="stat-icon-medium">
                  <el-icon><Back /></el-icon>
                </div>
                <div class="stat-content-medium">
                  <div class="stat-number-medium">{{ statistics.transferOutCount }}</div>
                  <div class="stat-label-medium">转出学生</div>
                  <div class="stat-badge">本学期</div>
                </div>
              </div>
            </div>

            <div class="stats-row">
              <div class="stat-card-medium danger-gradient">
                <div class="stat-icon-medium">
                  <el-icon><CloseBold /></el-icon>
                </div>
                <div class="stat-content-medium">
                  <div class="stat-number-medium">{{ statistics.suspendCount || 0 }}</div>
                  <div class="stat-label-medium">休学学生</div>
                  <div class="stat-badge suspend">当前</div>
                </div>
              </div>

              <div class="stat-card-medium info-gradient">
                <div class="stat-icon-medium">
                  <el-icon><Check /></el-icon>
                </div>
                <div class="stat-content-medium">
                  <div class="stat-number-medium">{{ statistics.resumeCount || 0 }}</div>
                  <div class="stat-label-medium">复学学生</div>
                  <div class="stat-badge">本学期</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 待处理异动卡片 -->
          <div class="pending-stats">
            <div class="stat-card-special" :class="{ 'urgent': statistics.pendingTransfers > 0 }">
              <div class="stat-special-header">
                <div class="stat-icon-special">
                  <el-icon><Clock /></el-icon>
                </div>
                <div class="urgent-indicator" v-if="statistics.pendingTransfers > 0">
                  <el-icon><Warning /></el-icon>
                </div>
              </div>
              <div class="stat-special-content">
                <div class="stat-number-special">{{ statistics.pendingTransfers }}</div>
                <div class="stat-label-special">待处理异动</div>
                <div class="stat-action-hint" v-if="statistics.pendingTransfers > 0">
                  <el-icon><Bell /></el-icon>
                  需要及时处理
                </div>
                <div class="stat-action-hint success" v-else>
                  <el-icon><CircleCheck /></el-icon>
                  暂无待处理
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="content-section">
        <div class="content-grid">
          <!-- 快速操作 -->
          <div class="content-card">
            <div class="card-header">
              <h3>
                <el-icon><Operation /></el-icon>
                快速操作
              </h3>
            </div>
            <div class="quick-actions">
              <div class="action-item" @click="showImportDialog">
                <el-icon class="action-icon"><Upload /></el-icon>
                <div class="action-content">
                  <div class="action-title">导入学生数据</div>
                  <div class="action-desc">批量导入Excel文件</div>
                </div>
              </div>
              <div class="action-item" @click="showExportOptions">
                <el-icon class="action-icon"><Download /></el-icon>
                <div class="action-content">
                  <div class="action-title">导出数据</div>
                  <div class="action-desc">导出学生信息</div>
                </div>
              </div>
              <div class="action-item" @click="navigateTo('/manage/transfer_data')">
                <el-icon class="action-icon"><DataBoard /></el-icon>
                <div class="action-content">
                  <div class="action-title">异动数据</div>
                  <div class="action-desc">查看异动记录</div>
                </div>
              </div>
              <div class="action-item" @click="showHelp">
                <el-icon class="action-icon"><QuestionFilled /></el-icon>
                <div class="action-content">
                  <div class="action-title">使用帮助</div>
                  <div class="action-desc">系统操作指南</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 数据趋势图表 -->
          <div class="content-card">
            <div class="card-header">
              <h3>
                <el-icon><TrendCharts /></el-icon>
                学生数据趋势
              </h3>
              <el-select v-model="chartPeriod" size="small" style="width: 100px;" @change="updateChart">
                <el-option label="本周" value="week" />
                <el-option label="本月" value="month" />
                <el-option label="本年" value="year" />
              </el-select>
            </div>
            <div class="chart-container">
              <v-chart 
                ref="chartRef"
                class="chart" 
                :option="chartOption" 
                :loading="chartLoading"
                loading-options="{
                  text: '数据加载中...',
                  color: '#409EFF',
                  textColor: '#666',
                  maskColor: 'rgba(255, 255, 255, 0.8)',
                  zlevel: 0
                }"
              />
            </div>
          </div>
        </div>

        <div class="content-grid">
          <!-- 最近活动 -->
          <div class="content-card">
            <div class="card-header">
              <h3>
                <el-icon><Bell /></el-icon>
                最近活动
              </h3>
              <el-link type="primary" @click="navigateTo('/manage/transfer_data')">查看更多</el-link>
            </div>
            <div class="activity-list">
              <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
                <div class="activity-icon" :class="activity.type">
                  <el-icon>
                    <Right v-if="activity.type === 'transfer_in'" />
                    <Back v-else-if="activity.type === 'transfer_out'" />
                    <CloseBold v-else-if="activity.type === 'suspend'" />
                    <Check v-else-if="activity.type === 'resume'" />
                    <Upload v-else-if="activity.type === 'import'" />
                    <Download v-else-if="activity.type === 'export'" />
                    <Bell v-else />
                  </el-icon>
                </div>
                <div class="activity-content">
                  <div class="activity-title">{{ activity.title }}</div>
                  <div class="activity-desc">{{ activity.description }}</div>
                  <div class="activity-time">{{ formatRelativeTime(activity.time) }}</div>
                </div>
              </div>
              <div v-if="recentActivities.length === 0" class="no-activity">
                <el-icon><Document /></el-icon>
                <p>暂无最近活动</p>
              </div>
            </div>
          </div>

          <!-- 年级分布 -->
          <div class="content-card">
            <div class="card-header">
              <h3>
                <el-icon><PieChart /></el-icon>
                年级分布
              </h3>
            </div>
            <div class="grade-distribution">
              <div v-for="grade in gradeDistribution" :key="grade.name" class="grade-item">
                <div class="grade-info">
                  <span class="grade-name">{{ grade.name }}</span>
                  <span class="grade-count">{{ grade.count }}人</span>
                </div>
                <div class="grade-bar">
                  <div class="grade-progress" :style="{ width: grade.percentage + '%' }"></div>
                </div>
                <span class="grade-percentage">{{ grade.percentage }}%</span>
              </div>
              <div v-if="gradeDistribution.length === 0" class="no-data">
                <p>暂无年级分布数据</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统状态栏 -->
      <div class="status-section">
        <div class="status-items">
          <div class="status-item">
            <el-icon class="status-icon success"><CircleCheck /></el-icon>
            <span>系统运行正常</span>
          </div>
          <div class="status-item">
            <el-icon class="status-icon"><Coin /></el-icon>
            <span>数据库连接正常</span>
          </div>
          <div class="status-item">
            <el-icon class="status-icon"><Clock /></el-icon>
            <span>最后更新：{{ lastUpdateTime }}</span>
          </div>
        </div>
      </div>
    </div>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/utils/userStore'
import { studentAPI } from '@/api/student'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import {
  CanvasRenderer
} from 'echarts/renderers'
import {
  LineChart,
  BarChart
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  MarkLineComponent
} from 'echarts/components'
import {
  Sunrise, Calendar, User, Promotion, ArrowUp, TrendCharts, Right, Back, Clock, Warning,
  Operation, Upload, Download, DataBoard, QuestionFilled, Bell, Document,
  PieChart, CircleCheck, Coin, Loading, CloseBold, Check,
  Sunny, Moon, MoonNight
} from '@element-plus/icons-vue'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  MarkLineComponent
])

const router = useRouter()
const userStore = useUserStore()

// 加载状态
const loading = ref(true)
const chartLoading = ref(false)

// 当前时间
const currentDateTime = reactive({
  date: '',
  time: '',
  weekday: ''
})

// 统计数据
const statistics = reactive({
  totalStudents: 0,
  newStudentsThisMonth: 0,
  transferInCount: 0,
  transferOutCount: 0,
  suspendCount: 0,      // 新增休学统计
  resumeCount: 0,       // 新增复学统计
  pendingTransfers: 0
})

// 图表相关
const chartRef = ref()
const chartPeriod = ref('month')
const trendData = ref({
  period: 'month',
  dates: [],
  transferIn: [],
  transferOut: [],
  studentCount: [],
  currentDateIndex: 0
})

// 最近活动
const recentActivities = ref([])

// 年级分布
const gradeDistribution = ref([])

// 最后更新时间
const lastUpdateTime = ref('')

// 时间更新定时器
let timeInterval = null

// 用户姓名计算属性
const userName = computed(() => {
  const user = userStore.state.user
  if (user?.first_name || user?.last_name) {
    return (user.first_name || '') + (user.last_name || '')
  }
  return '用户'
})

// 智能问候计算属性
const smartGreeting = computed(() => {
  const now = new Date()
  const hour = now.getHours()
  
  if (hour >= 6 && hour < 12) {
    return {
      greeting: '早上好',
      icon: Sunrise,
      iconClass: 'morning-icon'
    }
  } else if (hour >= 12 && hour < 18) {
    return {
      greeting: '下午好',
      icon: Sunny,
      iconClass: 'afternoon-icon'
    }
  } else if (hour >= 18 && hour < 22) {
    return {
      greeting: '晚上好',
      icon: Moon,
      iconClass: 'evening-icon'
    }
  } else {
    return {
      greeting: '夜深了',
      icon: MoonNight,
      iconClass: 'night-icon'
    }
  }
})

// ECharts配置选项
const chartOption = computed(() => {
  if (!trendData.value.dates.length) {
    return {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 16
        }
      }
    }
  }

  const currentIndex = trendData.value.currentDateIndex || 0
  const currentDate = trendData.value.dates[currentIndex]

  return {
    title: {
      text: `学生数据趋势 (${trendData.value.period === 'week' ? '周' : trendData.value.period === 'month' ? '月' : '年'}视图)`,
      left: 'center',
      textStyle: {
        fontSize: 16,
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      textStyle: {
        color: '#fff'
      },
      formatter: function(params) {
        const dataIndex = params[0].dataIndex
        const currentIndex = trendData.value.currentDateIndex
        const isFuture = dataIndex > currentIndex
        
        let result = `<div>${params[0].axisValue}${isFuture ? ' (未来)' : ''}</div>`
        
        params.forEach(param => {
          const value = param.value
          const color = param.color
          const seriesName = param.seriesName
          
          if (value === null || value === undefined) {
            result += `<div style="color: ${color}">● ${seriesName}: 暂无数据</div>`
          } else {
            result += `<div style="color: ${color}">● ${seriesName}: ${value}人</div>`
          }
        })
        
        return result
      }
    },
    legend: {
      data: ['转入学生', '转出学生', '在校学生总数'],
      top: 30,
      textStyle: {
        fontSize: 12
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trendData.value.dates,
      axisLabel: {
        fontSize: 11,
        color: '#666',
        formatter: function(value, index) {
          const currentIndex = trendData.value.currentDateIndex
          return index === currentIndex ? `【${value}】` : value
        }
      },
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '人数',
        position: 'left',
        axisLabel: {
          formatter: '{value}',
          fontSize: 11,
          color: '#666'
        },
        nameTextStyle: {
          fontSize: 12,
          color: '#666'
        },
        axisLine: {
          lineStyle: {
            color: '#ddd'
          }
        }
      }
    ],
    series: [
      {
        name: '转入学生',
        type: 'bar',
        data: trendData.value.transferIn,
        itemStyle: {
          color: function(params) {
            const currentIndex = trendData.value.currentDateIndex
            return params.dataIndex > currentIndex ? '#a8d8a8' : '#2ecc71'  // 未来数据用浅色
          }
        },
        emphasis: {
          itemStyle: {
            color: '#27ae60'
          }
        }
      },
      {
        name: '转出学生',
        type: 'bar',
        data: trendData.value.transferOut,
        itemStyle: {
          color: function(params) {
            const currentIndex = trendData.value.currentDateIndex
            return params.dataIndex > currentIndex ? '#f5c99b' : '#f39c12'  // 未来数据用浅色
          }
        },
        emphasis: {
          itemStyle: {
            color: '#e67e22'
          }
        }
      },
      {
        name: '在校学生总数',
        type: 'line',
        data: trendData.value.studentCount,
        itemStyle: {
          color: '#3498db'
        },
        lineStyle: {
          width: 3,
          type: function(params) {
            const currentIndex = trendData.value.currentDateIndex
            return params.dataIndex > currentIndex ? 'dashed' : 'solid'  // 未来数据用虚线
          }
        },
        symbol: 'circle',
        symbolSize: function(value, params) {
          const currentIndex = trendData.value.currentDateIndex
          return params.dataIndex === currentIndex ? 8 : 6  // 今天的点更大
        },
        emphasis: {
          itemStyle: {
            color: '#2980b9'
          }
        }
      }
    ],
    markLine: {
      silent: true,
      data: [
        {
          xAxis: currentIndex,
          lineStyle: {
            color: '#e74c3c',
            type: 'solid',
            width: 2
          },
          label: {
            formatter: '今天',
            position: 'insideEndTop',
            color: '#e74c3c'
          }
        }
      ]
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        start: Math.max(0, (currentIndex - 3) / trendData.value.dates.length * 100),
        end: Math.min(100, (currentIndex + 4) / trendData.value.dates.length * 100),
        height: 20,
        bottom: 10
      }
    ]
  }
})

// 获取仪表盘数据
const fetchDashboardData = async (period = 'month') => {
  try {
    loading.value = true
    const response = await studentAPI.getDashboardStats(period)
    
    // 更新统计数据
    Object.assign(statistics, response.statistics)
    
    // 更新年级分布
    gradeDistribution.value = response.gradeDistribution || []
    
    // 更新最近活动
    recentActivities.value = response.recentActivities || []
    
    // 更新趋势数据
    if (response.trendData) {
      trendData.value = response.trendData
    }
    
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    ElMessage.error('获取数据失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateChart = async (period) => {
  try {
    chartLoading.value = true
    await fetchDashboardData(period)
  } catch (error) {
    console.error('更新图表失败:', error)
    ElMessage.error('更新图表失败')
  } finally {
    chartLoading.value = false
  }
}

// 页面方法
const navigateTo = (path) => {
  router.push(path)
}

const showImportDialog = () => {
  navigateTo('/manage/user_data')
}

const showExportOptions = () => {
  ElMessageBox.confirm(
    '选择导出格式和范围',
    '导出数据',
    {
      confirmButtonText: '导出Excel',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    navigateTo('/manage/user_data')
  })
}

const showHelp = () => {
  ElMessageBox.alert(
    `系统功能说明：
    
    1. 学生信息管理：添加、修改、删除学生信息
    2. 学生异动办理：处理学生转入、转出、休学、复学申请
    3. 数据导入导出：批量处理学生数据
    4. 异动数据详情：查看异动记录和统计
    
    如需更多帮助，请联系系统管理员。`,
    '使用帮助',
    {
      confirmButtonText: '知道了',
      type: 'info'
    }
  )
}

const formatRelativeTime = (timeString) => {
  const time = new Date(timeString)
  const now = new Date()
  const diff = now - time
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(hours / 24)
  
  if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else {
    return '刚刚'
  }
}

const updateTime = () => {
  const now = new Date()
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  
  currentDateTime.date = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
  currentDateTime.time = now.toLocaleTimeString('zh-CN')
  currentDateTime.weekday = weekdays[now.getDay()]
  
  lastUpdateTime.value = now.toLocaleTimeString('zh-CN')
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  // 获取仪表盘数据
  fetchDashboardData(chartPeriod.value)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #666;
}

.loading-container .el-icon {
  font-size: 40px;
  margin-bottom: 20px;
}

/* 图表容器样式 */
.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 10px;
}

.chart {
  width: 100%;
  height: 100%;
}

/* 原有样式保持不变 */
.home-container {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: calc(100vh - 100px);
}

/* 欢迎区域 */
.welcome-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.welcome-title {
  font-size: 32px;
  color: #2c3e50;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.welcome-icon {
  font-size: 36px;
  color: #f39c12;
}

.welcome-subtitle {
  font-size: 18px;
  color: #7f8c8d;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.welcome-time {
  font-size: 24px;
  color: #3498db;
  font-weight: 600;
  margin: 0;
}

.welcome-actions {
  display: flex;
  gap: 15px;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 30px;
}

.stats-container {
  display: grid;
  grid-template-columns: 2fr 2fr 1fr;
  gap: 24px;
  align-items: start;
}

/* 主要统计卡片 - 大卡片 */
.primary-stats {
  grid-column: span 1;
}

.stat-card-large {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 32px;
  color: white;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-height: 180px;
}

.stat-card-large:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
}

.stat-card-content {
  display: flex;
  align-items: center;
  gap: 24px;
  position: relative;
  z-index: 2;
}

.stat-icon-large {
  font-size: 48px;
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-number-large {
  font-size: 48px;
  font-weight: 800;
  color: white;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label-large {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 12px;
  font-weight: 500;
}

.stat-change-large {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.1);
  padding: 6px 12px;
  border-radius: 20px;
  width: fit-content;
}

.stat-decoration {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  opacity: 0.3;
}

.decoration-circle {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: white;
  animation: pulse 2s ease-in-out infinite;
}

.decoration-circle:nth-child(2) {
  animation-delay: 1s;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.2); }
}

/* 异动统计卡片组 */
.transfer-stats {
  grid-column: span 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-row {
  display: flex;
  gap: 16px;
}

.stat-card-medium {
  background: white;
  border-radius: 16px;
  padding: 20px;
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #f0f2f5;
}

.stat-card-medium:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.success-gradient {
  border-left: 4px solid #52c41a;
}

.warning-gradient {
  border-left: 4px solid #faad14;
}

.danger-gradient {
  border-left: 4px solid #ff4d4f;
}

.info-gradient {
  border-left: 4px solid #1890ff;
}

.stat-icon-medium {
  font-size: 32px;
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.success-gradient .stat-icon-medium {
  background: linear-gradient(135deg, #b7eb8f, #52c41a);
  color: white;
}

.warning-gradient .stat-icon-medium {
  background: linear-gradient(135deg, #ffe58f, #faad14);
  color: white;
}

.danger-gradient .stat-icon-medium {
  background: linear-gradient(135deg, #ffccc7, #ff4d4f);
  color: white;
}

.info-gradient .stat-icon-medium {
  background: linear-gradient(135deg, #91d5ff, #1890ff);
  color: white;
}

.stat-content-medium {
  flex: 1;
  min-width: 0;
}

.stat-number-medium {
  font-size: 28px;
  font-weight: 700;
  color: #262626;
  line-height: 1;
  margin-bottom: 6px;
}

.stat-label-medium {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-badge {
  font-size: 11px;
  color: #595959;
  padding: 2px 8px;
  background: #f5f5f5;
  border-radius: 10px;
  width: fit-content;
  font-weight: 500;
}

.stat-badge.suspend {
  background: #fff2f0;
  color: #cf1322;
}

/* 待处理异动卡片 */
.pending-stats {
  grid-column: span 1;
}

.stat-card-special {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #f0f2f5;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-card-special:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.stat-card-special.urgent {
  background: linear-gradient(135deg, #fff5f5, #ffffff);
  border-left: 4px solid #ff4d4f;
  animation: urgentGlow 2s ease-in-out infinite;
}

@keyframes urgentGlow {
  0%, 100% { box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); }
  50% { box-shadow: 0 8px 30px rgba(255, 77, 79, 0.2); }
}

.stat-special-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.stat-icon-special {
  font-size: 40px;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f6ffed, #52c41a);
  color: #389e0d;
  position: relative;
}

.stat-card-special.urgent .stat-icon-special {
  background: linear-gradient(135deg, #fff2f0, #ff4d4f);
  color: #cf1322;
}

.urgent-indicator {
  position: absolute;
  top: -8px;
  right: -8px;
  font-size: 18px;
  color: #ff4d4f;
  animation: bounce 1s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.stat-special-content {
  text-align: center;
}

.stat-number-special {
  font-size: 36px;
  font-weight: 800;
  color: #262626;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-card-special.urgent .stat-number-special {
  color: #cf1322;
}

.stat-label-special {
  font-size: 15px;
  color: #8c8c8c;
  margin-bottom: 12px;
  font-weight: 500;
}

.stat-action-hint {
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #cf1322;
  background: #fff2f0;
  padding: 8px 12px;
  border-radius: 12px;
  font-weight: 500;
}

.stat-action-hint.success {
  color: #389e0d;
  background: #f6ffed;
}

/* 内容区域 */
.content-section {
  margin-bottom: 30px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.content-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 快速操作 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.action-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-item:hover {
  border-color: #3498db;
  background: #f8f9fa;
  transform: translateY(-1px);
}

.action-icon {
  font-size: 24px;
  color: #3498db;
  margin-right: 12px;
}

.action-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.action-desc {
  font-size: 12px;
  color: #7f8c8d;
}

/* 活动列表 */
.activity-list {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 14px;
}

.activity-icon.transfer_in { background: #e8f5e8; color: #27ae60; }
.activity-icon.transfer_out { background: #fff3e0; color: #f39c12; }
.activity-icon.import { background: #e3f2fd; color: #1976d2; }
.activity-icon.export { background: #e8f5e8; color: #27ae60; }
.activity-icon.suspend { background: #fdedec; color: #e74c3c; }
.activity-icon.resume { background: #d1ecf1; color: #17a2b8; }

.activity-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.activity-desc {
  font-size: 13px;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 11px;
  color: #bdc3c7;
}

.no-activity {
  text-align: center;
  padding: 40px;
  color: #bdc3c7;
}

.grade-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.grade-info {
  display: flex;
  justify-content: space-between;
  width: 120px;
  margin-right: 15px;
}

.grade-name {
  font-weight: 600;
  color: #2c3e50;
}

.grade-count {
  color: #7f8c8d;
  font-size: 14px;
}

.grade-bar {
  flex: 1;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  margin-right: 10px;
  overflow: hidden;
}

.grade-progress {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2980b9);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.grade-percentage {
  font-size: 12px;
  color: #7f8c8d;
  width: 35px;
  text-align: right;
}

.no-data {
  text-align: center;
  color: #bdc3c7;
  padding: 20px;
}

/* 状态区域 */
.status-section {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  padding: 16px 24px;
  backdrop-filter: blur(10px);
}

.status-items {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7f8c8d;
  font-size: 14px;
}

.status-icon {
  font-size: 16px;
}

.status-icon.success {
  color: #27ae60;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-container {
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  
  .primary-stats {
    grid-column: span 2;
  }
  
  .transfer-stats {
    grid-column: span 1;
  }
  
  .pending-stats {
    grid-column: span 1;
  }
}

@media (max-width: 968px) {
  .stats-container {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .primary-stats,
  .transfer-stats,
  .pending-stats {
    grid-column: span 1;
  }
  
  .stat-card-large {
    padding: 24px;
    min-height: 140px;
  }
  
  .stat-number-large {
    font-size: 36px;
  }
  
  .stat-label-large {
    font-size: 16px;
  }
  
  .stat-icon-large {
    width: 64px;
    height: 64px;
    font-size: 32px;
  }
  
  .stats-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .stat-card-medium {
    padding: 16px;
  }
  
  .stat-number-medium {
    font-size: 24px;
  }
  
  .stat-icon-medium {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }
}

@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    text-align: center;
    gap: 20px;
    padding: 24px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-subtitle {
    font-size: 16px;
  }
  
  .welcome-time {
    font-size: 20px;
  }
  
  .stat-card-large {
    padding: 20px;
    min-height: 120px;
  }
  
  .stat-card-content {
    gap: 16px;
  }
  
  .stat-icon-large {
    width: 56px;
    height: 56px;
    font-size: 28px;
  }
  
  .stat-number-large {
    font-size: 32px;
  }
  
  .stat-label-large {
    font-size: 15px;
  }
  
  .stat-change-large {
    font-size: 12px;
    padding: 4px 8px;
  }
  
  .stat-card-medium {
    padding: 14px;
    gap: 12px;
  }
  
  .stat-icon-medium {
    width: 44px;
    height: 44px;
    font-size: 20px;
  }
  
  .stat-number-medium {
    font-size: 20px;
  }
  
  .stat-label-medium {
    font-size: 12px;
  }
  
  .stat-card-special {
    padding: 20px;
  }
  
  .stat-icon-special {
    width: 56px;
    height: 56px;
    font-size: 32px;
  }
  
  .stat-number-special {
    font-size: 28px;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .status-items {
    flex-direction: column;
    gap: 10px;
  }
}

/* 智能图标样式 */
.welcome-icon.morning-icon {
  color: #ff9500;
  animation: sunrise 3s ease-in-out infinite alternate;
}

.welcome-icon.afternoon-icon {
  color: #ffd700;
  animation: sunshine 2s ease-in-out infinite;
}

.welcome-icon.evening-icon {
  color: #4a90e2;
  animation: moonrise 4s ease-in-out infinite alternate;
}

.welcome-icon.night-icon {
  color: #2c3e50;
  animation: twinkle 2s ease-in-out infinite alternate;
}

/* 动画效果 */
@keyframes sunrise {
  0% { transform: translateY(2px); opacity: 0.8; }
  100% { transform: translateY(-2px); opacity: 1; }
}

@keyframes sunshine {
  0%, 100% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.1); }
}

@keyframes moonrise {
  0% { transform: translateY(3px); opacity: 0.7; }
  100% { transform: translateY(-3px); opacity: 1; }
}

@keyframes twinkle {
  0% { opacity: 0.6; transform: scale(0.95); }
  100% { opacity: 1; transform: scale(1.05); }
}
</style>
