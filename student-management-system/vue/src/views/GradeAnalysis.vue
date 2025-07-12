<template>
  <div>
    <el-card>
      <template #header>
        <div>
          <span>成绩分析</span>
        </div>
      </template>

      <!-- 分析条件 -->
      <el-form :model="analysisForm" label-width="80px" inline>
        <el-form-item label="考试" required>
          <el-select v-model="analysisForm.exam_id" placeholder="选择考试" style="width: 200px;">
            <el-option
              v-for="exam in examList"
              :key="exam.id"
              :label="exam.name"
              :value="exam.id">
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="年级">
          <el-select v-model="analysisForm.grade" placeholder="选择年级" style="width: 120px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="一年级" value="1"></el-option>
            <el-option label="二年级" value="2"></el-option>
            <el-option label="三年级" value="3"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="班级">
          <el-input v-model="analysisForm.class" placeholder="输入班级" style="width: 120px;"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="getAnalysisData">分析</el-button>
        </el-form-item>
      </el-form>

      <!-- 分析结果 -->
      <div v-if="analysisData" style="margin-top: 20px;">
        <!-- 科目统计 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>科目成绩统计</template>
              <el-table :data="analysisData.subject_stats" style="width: 100%">
                <el-table-column prop="subject__name" label="科目" width="100"></el-table-column>
                <el-table-column prop="avg_score" label="平均分" width="80">
                  <template #default="scope">
                    {{ scope.row.avg_score?.toFixed(1) }}
                  </template>
                </el-table-column>
                <el-table-column prop="max_score" label="最高分" width="80"></el-table-column>
                <el-table-column prop="min_score" label="最低分" width="80"></el-table-column>
                <el-table-column prop="student_count" label="人数" width="60"></el-table-column>
              </el-table>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card>
              <template #header>分数段分布</template>
              <el-table :data="analysisData.score_distribution" style="width: 100%">
                <el-table-column prop="level" label="等级" width="60">
                  <template #default="scope">
                    <el-tag :type="getGradeType(scope.row.level)">{{ scope.row.level }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="range" label="分数段" width="80"></el-table-column>
                <el-table-column prop="count" label="人数" width="60"></el-table-column>
                <el-table-column label="占比" width="80">
                  <template #default="scope">
                    {{ getPercentage(scope.row.count) }}%
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { gradeAPI } from '@/api/grade'

// 响应式数据
const analysisForm = reactive({
  exam_id: '',
  grade: '',
  class: ''
})

const examList = ref([])
const analysisData = ref(null)

// 获取考试列表
const getExamList = async () => {
  try {
    const response = await gradeAPI.getExams()
    examList.value = response
  } catch (error) {
    ElMessage.error('获取考试列表失败')
  }
}

// 获取分析数据
const getAnalysisData = async () => {
  if (!analysisForm.exam_id) {
    ElMessage.warning('请选择考试')
    return
  }
  
  try {
    const response = await gradeAPI.getGradeAnalysis(analysisForm)
    analysisData.value = response
  } catch (error) {
    ElMessage.error('获取分析数据失败')
  }
}

// 等级类型判断
const getGradeType = (grade) => {
  const typeMap = {
    'A': 'success',
    'B': 'warning',
    'C': 'info',
    'D': 'info',
    'F': 'danger'
  }
  return typeMap[grade] || 'info'
}

// 计算百分比
const getPercentage = (count) => {
  if (!analysisData.value || !analysisData.value.score_distribution) return 0
  const total = analysisData.value.score_distribution.reduce((sum, item) => sum + item.count, 0)
  return total > 0 ? ((count / total) * 100).toFixed(1) : 0
}

// 初始化
onMounted(() => {
  getExamList()
})
</script>

<style scoped>
.grade-analysis {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>