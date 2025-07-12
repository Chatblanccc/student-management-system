<template>
    <div>
        <!-- 转学类型选择区域 -->
        <div class="card" style="margin-bottom: 15px;">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="display: flex; align-items: center;">
                    <span style="margin-right: 12px; font-weight: 600; color: #303133;">异动类型：</span>
                    <el-select 
                        v-model="transferType" 
                        placeholder="请选择异动类型" 
                        style="width: 160px;"
                        @change="handleTransferTypeChange">
                        <el-option 
                            label="转入" 
                            value="transfer_in"
                            :icon="Right" />
                        <el-option 
                            label="转出" 
                            value="transfer_out"
                            :icon="Back" />
                        <el-option 
                            label="休学" 
                            value="suspend"
                            :icon="CloseBold" />
                        <el-option 
                            label="复学" 
                            value="resume"
                            :icon="Check" />
                    </el-select>
                </div>
                
                <!-- 转出、休学、复学时的查询区域 -->
                <div v-if="['transfer_out', 'suspend', 'resume'].includes(transferType)" style="display: flex; align-items: center; gap: 12px;">
                    <el-input 
                        v-model="searchForm.keyword" 
                        style="width: 240px;" 
                        :placeholder="getSearchPlaceholder()"
                        @keyup.enter="handleSearch" />
                    <el-button type="primary" plain @click="handleSearch" :loading="searchLoading">
                        <el-icon><Search /></el-icon>
                        查询
                    </el-button>
                    <el-button type="warning" plain @click="handleReset">
                        <el-icon><RefreshLeft /></el-icon>
                        重置
                    </el-button>
                </div>
            </div>
        </div>

        <!-- 转入表单区域 -->
        <div class="card full-width-form" v-if="transferType === 'transfer_in'">
            
            <el-form 
                ref="transferInFormRef"
                :model="transferInForm" 
                :rules="transferInRules"
                label-width="140px" 
                class="transfer-form">
                
                <!-- 基本信息 -->
                <div class="form-section">
                    <h3 class="section-title">基本信息</h3>
                    <el-row :gutter="30">
                        <el-col :span="6">
                            <el-form-item label="学生姓名" prop="name">
                                <el-input v-model="transferInForm.name" placeholder="请输入学生姓名" size="large" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="学号" prop="school_id">
                                <el-input v-model="transferInForm.school_id" placeholder="请输入学号" size="large" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="年级" prop="grade">
                                <el-select v-model="transferInForm.grade" placeholder="请选择年级" size="large" style="width: 100%">
                                    <el-option label="一年级" value="一年级" />
                                    <el-option label="二年级" value="二年级" />
                                    <el-option label="三年级" value="三年级" />
                                    <el-option label="四年级" value="四年级" />
                                    <el-option label="五年级" value="五年级" />
                                    <el-option label="六年级" value="六年级" />
                                    <el-option label="七年级" value="七年级" />
                                    <el-option label="八年级" value="八年级" />
                                    <el-option label="九年级" value="九年级" />
                                </el-select>
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="班级" prop="class_name">
                                <el-input v-model="transferInForm.class_name" placeholder="如：1班" size="large" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                    <el-row :gutter="30">
                        <el-col :span="12">
                            <el-form-item label="身份证号" prop="id_card">
                                <el-input v-model="transferInForm.id_card" placeholder="请输入身份证号" size="large" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="广州学籍号" prop="gz_student_id">
                                <el-input v-model="transferInForm.gz_student_id" placeholder="请输入广州学籍号" size="large" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                    <el-row :gutter="30">
                        <el-col :span="12">
                            <el-form-item label="全国学籍号" prop="national_student_id">
                                <el-input v-model="transferInForm.national_student_id" placeholder="请输入全国学籍号（选填）" size="large" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="年龄" prop="age">
                                <el-input-number 
                                    v-model="transferInForm.age" 
                                    :min="6" 
                                    :max="18" 
                                    placeholder="请输入年龄" 
                                    size="large" 
                                    style="width: 100%" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="转入时间" prop="transfer_date">
                                <el-date-picker
                                    v-model="transferInForm.transfer_date"
                                    type="date"
                                    placeholder="请选择转入时间"
                                    size="large"
                                    format="YYYY-MM-DD"
                                    value-format="YYYY-MM-DD"
                                    style="width: 100%" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                    <el-row :gutter="30">
                        <el-col :span="12">
                            <el-form-item label="原学校" prop="previous_school">
                                <el-input 
                                    v-model="transferInForm.previous_school" 
                                    placeholder="请输入学生的原学校名称"
                                    size="large" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="转学备注" prop="transfer_notes">
                                <el-input 
                                    v-model="transferInForm.transfer_notes" 
                                    placeholder="请输入转学相关备注信息（选填）"
                                    size="large" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                </div>

                <!-- 地址信息 -->
                <div class="form-section">
                    <h3 class="section-title">地址信息</h3>
                    <el-row :gutter="30">
                        <el-col :span="12">
                            <el-form-item label="户籍所在地" prop="household_address">
                                <el-input 
                                    v-model="transferInForm.household_address" 
                                    type="textarea" 
                                    :rows="3"
                                    placeholder="请输入户籍所在地详细地址"
                                    size="large" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="居住所在地" prop="living_address">
                                <el-input 
                                    v-model="transferInForm.living_address" 
                                    type="textarea" 
                                    :rows="3"
                                    placeholder="请输入居住所在地详细地址"
                                    size="large" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                </div>

                <!-- 监护人信息 -->
                <div class="form-section">
                    <h3 class="section-title">监护人信息</h3>
                    <el-row :gutter="30">
                        <el-col :span="6">
                            <el-form-item label="监护人(父亲)" prop="guardian_father">
                                <el-input v-model="transferInForm.guardian_father" placeholder="请输入父亲姓名" size="large" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="父亲联系电话" prop="guardian_father_phone">
                                <el-input v-model="transferInForm.guardian_father_phone" placeholder="请输入父亲联系电话" size="large" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="监护人(母亲)" prop="guardian_mother">
                                <el-input v-model="transferInForm.guardian_mother" placeholder="请输入母亲姓名" size="large" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="6">
                            <el-form-item label="母亲联系电话" prop="guardian_mother_phone">
                                <el-input v-model="transferInForm.guardian_mother_phone" placeholder="请输入母亲联系电话" size="large" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                </div>

                <!-- 转学信息 -->
                <div class="form-section">
                    <h3 class="section-title">转学信息</h3>
                    <el-row :gutter="30">
                        <el-col :span="24">
                            <el-form-item label="转学原因" prop="transfer_reason">
                                <el-input 
                                    v-model="transferInForm.transfer_reason" 
                                    type="textarea" 
                                    :rows="4"
                                    placeholder="请详细说明转学原因"
                                    size="large" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                </div>

                <!-- 提交按钮 -->
                <div class="form-footer">
                    <el-button type="primary" size="large" @click="handleTransferInSubmit" :loading="submitLoading">
                        <el-icon><Check /></el-icon>
                        确认转入登记
                    </el-button>
                    <el-button size="large" @click="handleTransferInReset">
                        <el-icon><RefreshLeft /></el-icon>
                        重置表单
                    </el-button>
                </div>
            </el-form>
        </div>

        <!-- 休学查询和表单区域 -->
        <div v-if="transferType === 'suspend'">
            <!-- 未查询时的提示 -->
            <div v-if="!showDetail" class="card" style="text-align: center; padding: 60px 20px;">
                <el-empty 
                    description="请输入学生姓名进行查询" 
                    :image-size="120">
                    <template #description>
                        <div style="color: #606266;">
                            <p style="font-size: 16px; margin-bottom: 10px;">请输入需要办理休学的学生姓名</p>
                            <p style="font-size: 14px; color: #909399;">支持按姓名、学号或身份证号查询</p>
                        </div>
                    </template>
                </el-empty>
            </div>
            
            <!-- 查询结果显示 -->
            <div v-if="showDetail" class="card full-width-form">
                <!-- 查询成功显示学生信息和休学表单 -->
                <div v-if="currentStudent" class="detail-container" style="margin-bottom: 20px;">
                    <div class="detail-header">
                        <h2 style="margin: 0; color: #303133;">休学学生信息</h2>
                        <div>
                            <el-tag type="success" size="large">查询成功</el-tag>
                            <el-tag type="warning" size="large" style="margin-left: 8px;">待休学</el-tag>
                        </div>
                    </div>
                    
                    <!-- 学生基本信息显示 -->
                    <el-descriptions 
                        title="学生基本信息" 
                        :column="3" 
                        border 
                        class="detail-descriptions">
                        <template #title>
                            <div class="descriptions-title">
                                <el-icon color="#409eff"><User /></el-icon>
                                <span>学生基本信息</span>
                            </div>
                        </template>
                        
                        <el-descriptions-item label="姓名">
                            <el-tag type="primary" size="large">{{ currentStudent.name }}</el-tag>
                        </el-descriptions-item>
                        
                        <el-descriptions-item label="学号">
                            <span class="info-text">{{ currentStudent.school_id }}</span>
                        </el-descriptions-item>
                        
                        <el-descriptions-item label="年级班级">
                            <span class="info-text">{{ currentStudent.grade }}{{ currentStudent.class_name }}</span>
                        </el-descriptions-item>
                    </el-descriptions>

                    <!-- 休学信息表单 -->
                    <el-form 
                        ref="suspendFormRef"
                        :model="suspendForm" 
                        :rules="suspendRules"
                        label-width="120px" 
                        style="margin-top: 20px;">
                        
                        <!-- 休学基本信息 -->
                        <div class="form-section">
                            <h4 class="section-title">休学信息</h4>
                            <el-row :gutter="20">
                                <el-col :span="12">
                                    <el-form-item label="休学开始日期" prop="suspend_start_date">
                                        <el-date-picker
                                            v-model="suspendForm.suspend_start_date"
                                            type="date"
                                            placeholder="请选择休学开始日期"
                                            format="YYYY-MM-DD"
                                            value-format="YYYY-MM-DD"
                                            style="width: 100%" />
                                    </el-form-item>
                                </el-col>
                                <el-col :span="12">
                                    <el-form-item label="预期复学日期" prop="expected_resume_date">
                                        <el-date-picker
                                            v-model="suspendForm.expected_resume_date"
                                            type="date"
                                            placeholder="请选择预期复学日期"
                                            format="YYYY-MM-DD"
                                            value-format="YYYY-MM-DD"
                                            style="width: 100%" />
                                    </el-form-item>
                                </el-col>
                            </el-row>
                            
                            <el-form-item label="休学原因" prop="suspend_reason">
                                <el-select 
                                    v-model="suspendForm.suspend_reason_type" 
                                    placeholder="请选择休学原因类型"
                                    style="width: 200px; margin-bottom: 10px;"
                                    @change="handleSuspendReasonTypeChange">
                                    <el-option label="疾病休学" value="illness" />
                                    <el-option label="事假休学" value="personal" />
                                    <el-option label="其他原因" value="other" />
                                </el-select>
                                <el-input 
                                    v-model="suspendForm.suspend_reason" 
                                    type="textarea" 
                                    :rows="3"
                                    placeholder="请详细说明休学原因" 
                                    style="margin-top: 10px;" />
                            </el-form-item>
                        </div>
                        
                        <!-- 联系信息 -->
                        <div class="form-section">
                            <h4 class="section-title">联系信息</h4>
                            <el-row :gutter="20">
                                <el-col :span="12">
                                    <el-form-item label="联系人" prop="contact_person">
                                        <el-input 
                                            v-model="suspendForm.contact_person" 
                                            placeholder="休学期间联系人姓名" />
                                    </el-form-item>
                                </el-col>
                                <el-col :span="12">
                                    <el-form-item label="联系电话" prop="contact_phone">
                                        <el-input 
                                            v-model="suspendForm.contact_phone" 
                                            placeholder="休学期间联系电话" />
                                    </el-form-item>
                                </el-col>
                            </el-row>
                        </div>
                        
                        <!-- 处理信息 -->
                        <div class="form-section">
                            <h4 class="section-title">处理信息</h4>
                            <el-row :gutter="20">
                                <el-col :span="12">
                                    <el-form-item label="处理人" prop="processor">
                                        <el-input 
                                            v-model="suspendForm.processor" 
                                            readonly
                                            disabled
                                            placeholder="自动设置为当前登录用户">
                                            <template #prepend>
                                                <el-icon><User /></el-icon>
                                            </template>
                                        </el-input>
                                    </el-form-item>
                                </el-col>
                            </el-row>
                            
                            <el-form-item label="备注信息" prop="remarks">
                                <el-input 
                                    v-model="suspendForm.remarks" 
                                    type="textarea" 
                                    :rows="2"
                                    placeholder="其他备注信息（选填）" />
                            </el-form-item>
                        </div>
                        
                        <!-- 提交按钮 -->
                        <div class="form-footer">
                            <el-button @click="handleReset">取消</el-button>
                            <el-button 
                                type="warning" 
                                @click="handleSuspendSubmit" 
                                :loading="submitLoading">
                                <el-icon><CloseBold /></el-icon>
                                确认休学
                            </el-button>
                        </div>
                    </el-form>
                </div>
                
                <!-- 查询结果为空 -->
                <div v-else class="no-data">
                    <el-empty 
                        description="未找到匹配的学生信息，请检查输入信息是否正确" 
                        :image-size="120">
                        <template #description>
                            <div style="color: #606266;">
                                <p>未找到匹配的学生信息</p>
                                <p style="font-size: 14px; margin-top: 5px;">请检查姓名、学号或身份证号是否正确</p>
                            </div>
                        </template>
                        <el-button type="primary" @click="handleReset">重新查询</el-button>
                    </el-empty>
                </div>
            </div>
        </div>

        <!-- 复学查询和表单区域 -->
        <div v-if="transferType === 'resume'">
            <!-- 未查询时的提示 -->
            <div v-if="!showDetail" class="card" style="text-align: center; padding: 60px 20px;">
                <el-empty 
                    description="请输入学生姓名进行查询" 
                    :image-size="120">
                    <template #description>
                        <div style="color: #606266;">
                            <p style="font-size: 16px; margin-bottom: 10px;">请输入需要办理复学的学生姓名</p>
                            <p style="font-size: 14px; color: #909399;">只有处于休学状态的学生才能办理复学</p>
                        </div>
                    </template>
                </el-empty>
            </div>
            
            <!-- 查询结果显示 -->
            <div v-if="showDetail" class="card full-width-form">
                <!-- 查询成功显示学生信息和复学表单 -->
                <div v-if="currentStudent" class="detail-container" style="margin-bottom: 20px;">
                    <div class="detail-header">
                        <h2 style="margin: 0; color: #303133;">复学学生信息</h2>
                        <div>
                            <el-tag type="success" size="large">查询成功</el-tag>
                            <el-tag type="primary" size="large" style="margin-left: 8px;">待复学</el-tag>
                        </div>
                    </div>
                    
                    <!-- 学生基本信息显示 -->
                    <el-descriptions 
                        title="学生基本信息" 
                        :column="3" 
                        border 
                        class="detail-descriptions">
                        <template #title>
                            <div class="descriptions-title">
                                <el-icon color="#67c23a"><User /></el-icon>
                                <span>学生基本信息</span>
                            </div>
                        </template>
                        
                        <el-descriptions-item label="姓名">
                            <el-tag type="primary" size="large">{{ currentStudent.name }}</el-tag>
                        </el-descriptions-item>
                        
                        <el-descriptions-item label="学号">
                            <span class="info-text">{{ currentStudent.school_id }}</span>
                        </el-descriptions-item>
                        
                        <el-descriptions-item label="休学前年级班级">
                            <span class="info-text">{{ currentStudent.grade }}{{ currentStudent.class_name }}</span>
                        </el-descriptions-item>
                    </el-descriptions>

                    <!-- 复学信息表单 -->
                    <el-form 
                        ref="resumeFormRef"
                        :model="resumeForm" 
                        :rules="resumeRules"
                        label-width="120px" 
                        style="margin-top: 20px;">
                        
                        <!-- 复学基本信息 -->
                        <div class="form-section">
                            <h4 class="section-title">复学信息</h4>
                            <el-row :gutter="20">
                                <el-col :span="12">
                                    <el-form-item label="复学日期" prop="resume_date">
                                        <el-date-picker
                                            v-model="resumeForm.resume_date"
                                            type="date"
                                            placeholder="请选择复学日期"
                                            format="YYYY-MM-DD"
                                            value-format="YYYY-MM-DD"
                                            style="width: 100%" />
                                    </el-form-item>
                                </el-col>
                                <el-col :span="6">
                                    <el-form-item label="复学年级" prop="resume_grade">
                                        <el-select v-model="resumeForm.resume_grade" placeholder="请选择复学年级" style="width: 100%">
                                            <el-option label="一年级" value="一年级" />
                                            <el-option label="二年级" value="二年级" />
                                            <el-option label="三年级" value="三年级" />
                                            <el-option label="四年级" value="四年级" />
                                            <el-option label="五年级" value="五年级" />
                                            <el-option label="六年级" value="六年级" />
                                            <el-option label="七年级" value="七年级" />
                                            <el-option label="八年级" value="八年级" />
                                            <el-option label="九年级" value="九年级" />
                                        </el-select>
                                    </el-form-item>
                                </el-col>
                                <el-col :span="6">
                                    <el-form-item label="复学班级" prop="resume_class">
                                        <el-input 
                                            v-model="resumeForm.resume_class" 
                                            placeholder="如：1班" />
                                    </el-form-item>
                                </el-col>
                            </el-row>
                            
                            <el-form-item label="复学说明" prop="resume_reason">
                                <el-input 
                                    v-model="resumeForm.resume_reason" 
                                    type="textarea" 
                                    :rows="3"
                                    placeholder="请说明复学情况（如身体恢复情况、学习准备情况等）" />
                            </el-form-item>
                        </div>
                        
                        <!-- 处理信息 -->
                        <div class="form-section">
                            <h4 class="section-title">处理信息</h4>
                            <el-row :gutter="20">
                                <el-col :span="12">
                                    <el-form-item label="处理人" prop="processor">
                                        <el-input 
                                            v-model="resumeForm.processor" 
                                            readonly
                                            disabled
                                            placeholder="自动设置为当前登录用户">
                                            <template #prepend>
                                                <el-icon><User /></el-icon>
                                            </template>
                                        </el-input>
                                    </el-form-item>
                                </el-col>
                            </el-row>
                            
                            <el-form-item label="审批意见" prop="approval_notes">
                                <el-input 
                                    v-model="resumeForm.approval_notes" 
                                    type="textarea" 
                                    :rows="2"
                                    placeholder="审批意见或处理说明（选填）" />
                            </el-form-item>
                            
                            <el-form-item label="备注信息" prop="remarks">
                                <el-input 
                                    v-model="resumeForm.remarks" 
                                    type="textarea" 
                                    :rows="2"
                                    placeholder="其他备注信息（选填）" />
                            </el-form-item>
                        </div>
                        
                        <!-- 提交按钮 -->
                        <div class="form-footer">
                            <el-button @click="handleReset">取消</el-button>
                            <el-button 
                                type="primary" 
                                @click="handleResumeSubmit" 
                                :loading="submitLoading">
                                <el-icon><Check /></el-icon>
                                确认复学
                            </el-button>
                        </div>
                    </el-form>
                </div>
                
                <!-- 查询结果为空 -->
                <div v-else class="no-data">
                    <el-empty 
                        description="未找到匹配的学生信息，请检查输入信息是否正确" 
                        :image-size="120">
                        <template #description>
                            <div style="color: #606266;">
                                <p>未找到匹配的学生信息</p>
                                <p style="font-size: 14px; margin-top: 5px;">请检查姓名、学号或身份证号是否正确</p>
                            </div>
                        </template>
                        <el-button type="primary" @click="handleReset">重新查询</el-button>
                    </el-empty>
                </div>
            </div>
        </div>

        <!-- 转出查询和显示区域 -->
        <div v-if="transferType === 'transfer_out'">
            <!-- 未查询时的提示 -->
            <div v-if="!showDetail" class="card" style="text-align: center; padding: 60px 20px;">
                <el-empty 
                    description="请输入学生姓名进行查询" 
                    :image-size="120">
                    <template #description>
                        <div style="color: #606266;">
                            <p style="font-size: 16px; margin-bottom: 10px;">请输入需要办理转出的学生姓名</p>
                            <p style="font-size: 14px; color: #909399;">支持按姓名、学号或身份证号查询</p>
                        </div>
                    </template>
                </el-empty>
            </div>
            
            <!-- 查询结果显示区域 -->
            <div v-if="showDetail" class="card">
            <!-- 查询成功显示学生详细信息 -->
            <div v-if="currentStudent" class="detail-container">
                <div class="detail-header">
                    <h2 style="margin: 0; color: #303133;">转出学生详细信息</h2>
                    <div>
                        <el-tag type="success" size="large">查询成功</el-tag>
                        <el-tag type="warning" size="large" style="margin-left: 8px;">待转出</el-tag>
                    </div>
                </div>
                
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
                        <el-tag type="primary" size="large">{{ currentStudent.name }}</el-tag>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="学号" 
                        label-width="110px">
                        <span class="info-text">{{ currentStudent.school_id }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="年级" 
                        label-width="110px">
                        <el-tag type="success" size="small">{{ currentStudent.grade || '未设置' }}</el-tag>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="班级" 
                        label-width="110px">
                        <el-tag type="info" size="small">{{ currentStudent.class_name || '未分班' }}</el-tag>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="年龄" 
                        label-width="110px">
                        <span class="info-text">{{ currentStudent.age }}岁</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="身份证号" 
                        label-width="110px">
                        <span class="info-text">{{ currentStudent.id_card }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="广州学籍号"
                        label-width="110px">
                        <span class="info-text">{{ currentStudent.gz_student_id }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="全国学籍号" 
                        label-width="110px">
                        <span class="info-text">{{ currentStudent.national_student_id || '暂无' }}</span>
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
                        <span class="address-text">{{ currentStudent.household_address || '暂无' }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="居住所在地" label-width="120px">
                        <span class="address-text">{{ currentStudent.living_address || '暂无' }}</span>
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
                            <span class="info-text">{{ currentStudent.guardian_father || '暂无' }}</span>
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
                            <span class="info-text">{{ currentStudent.guardian_mother || '暂无' }}</span>
                        </div>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="父亲联系电话">
                        <div class="phone-info">
                            <el-icon color="#409eff" style="margin-right: 5px;"><Phone /></el-icon>
                            <span class="info-text">{{ currentStudent.guardian_father_phone || '暂无' }}</span>
                            <el-button 
                                v-if="currentStudent.guardian_father_phone" 
                                type="primary" 
                                size="small" 
                                text 
                                style="margin-left: 10px;"
                            </el-button>
                        </div>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="母亲联系电话">
                        <div class="phone-info">
                            <el-icon color="#f56c6c" style="margin-right: 5px;"><Phone /></el-icon>
                            <span class="info-text">{{ currentStudent.guardian_mother_phone || '暂无' }}</span>
                            <el-button 
                                v-if="currentStudent.guardian_mother_phone" 
                                type="danger" 
                                size="small" 
                                text 
                                style="margin-left: 10px;"
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
                        <span class="info-text">{{ formatDate(currentStudent.created_at) }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="更新时间" 
                        :width="120">
                        <span class="info-text">{{ formatDate(currentStudent.updated_at) }}</span>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="学生状态" 
                        :width="120">
                        <el-tag type="success" size="small">{{ currentStudent.status_display }}</el-tag>
                    </el-descriptions-item>
                    
                    <el-descriptions-item 
                        label="数据完整度" 
                        :width="120">
                        <div class="completeness-info">
                            <el-progress 
                                :percentage="calculateCompleteness(currentStudent)" 
                                :color="getCompletenessColor(calculateCompleteness(currentStudent))"
                                :stroke-width="8"
                                style="width: 120px;" />
                            <span style="margin-left: 10px; font-size: 12px; color: #606266;">
                                {{ calculateCompleteness(currentStudent) }}%
                            </span>
                        </div>
                    </el-descriptions-item>
                </el-descriptions>

                <!-- 转出操作按钮区域 -->
                <div class="transfer-actions">
                    <el-alert 
                        title="转出办理说明" 
                        type="warning" 
                        :closable="false"
                        style="margin-bottom: 20px;">
                        <template #default>
                            <p style="margin: 0;">请核实以上学生信息无误后，点击办理转出按钮进行转出手续办理。</p>
                        </template>
                    </el-alert>
                    
                    <div class="action-buttons">
                        <el-button 
                            type="warning" 
                            size="large" 
                            @click="handleTransferOut"
                            :disabled="currentStudent.status !== 'active'">
                            <el-icon><Back /></el-icon>
                            办理转出
                        </el-button>
                        <el-button size="large" @click="handleReset">
                            <el-icon><RefreshLeft /></el-icon>
                            重新查询
                        </el-button>
                    </div>
                    
                    <!-- 状态提示 -->
                    <div v-if="currentStudent.status !== 'active'" class="status-warning">
                        <el-alert 
                            :title="`该学生当前状态为` + currentStudent.status_display + `，无法办理转出`"
                            type="info" 
                            :closable="false"
                            show-icon />
                    </div>
                </div>
            </div>
            
            <!-- 查询结果为空 -->
            <div v-else class="no-data">
                <el-empty 
                    description="未找到匹配的学生信息，请检查输入信息是否正确" 
                    :image-size="120">
                    <template #description>
                        <div style="color: #606266;">
                            <p>未找到匹配的学生信息</p>
                            <p style="font-size: 14px; margin-top: 5px;">请检查姓名、学号或身份证号是否正确</p>
                        </div>
                    </template>
                    <el-button type="primary" @click="handleReset">重新查询</el-button>
                </el-empty>
                </div>
        </div>
        </div>

        <!-- 转出信息填写弹窗 -->
        <el-dialog 
            v-model="transferOutVisible" 
            title="办理转出手续" 
            width="60%" 
            align-center
            :close-on-click-modal="false">
            
            <div class="transfer-out-header">
                <el-descriptions title="转出学生信息" :column="3" border size="small">
                    <el-descriptions-item label="姓名">
                        <el-tag type="primary">{{ currentStudent?.name }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="学号">{{ currentStudent?.school_id }}</el-descriptions-item>
                    <el-descriptions-item label="年级班级">{{ currentStudent?.grade }}{{ currentStudent?.class_name }}</el-descriptions-item>
                </el-descriptions>
            </div>
            
            <el-form 
                ref="transferOutFormRef"
                :model="transferOutForm" 
                :rules="transferOutRules"
                label-width="120px" 
                style="margin-top: 20px;">
                
                <!-- 基本转出信息 -->
                <div class="form-section">
                    <h4 class="section-title">转出信息</h4>
                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="目标学校" prop="target_school">
                                <el-input 
                                    v-model="transferOutForm.target_school" 
                                    placeholder="请输入目标学校全称" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="转出日期" prop="transfer_date">
                                <el-date-picker
                                    v-model="transferOutForm.transfer_date"
                                    type="date"
                                    placeholder="请选择转出日期"
                                    format="YYYY-MM-DD"
                                    value-format="YYYY-MM-DD"
                                    style="width: 100%" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                    
                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="目标年级" prop="target_grade">
                                <el-select v-model="transferOutForm.target_grade" placeholder="选择转入年级" style="width: 100%">
                                    <el-option label="一年级" value="一年级" />
                                    <el-option label="二年级" value="二年级" />
                                    <el-option label="三年级" value="三年级" />
                                    <el-option label="四年级" value="四年级" />
                                    <el-option label="五年级" value="五年级" />
                                    <el-option label="六年级" value="六年级" />
                                    <el-option label="七年级" value="七年级" />
                                    <el-option label="八年级" value="八年级" />
                                    <el-option label="九年级" value="九年级" />
                                </el-select>
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="目标班级" prop="target_class">
                                <el-input 
                                    v-model="transferOutForm.target_class" 
                                    placeholder="如：1班、2班等" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                    
                    <el-form-item label="转出原因" prop="transfer_reason">
                        <el-input 
                            v-model="transferOutForm.transfer_reason" 
                            type="textarea" 
                            :rows="3"
                            placeholder="请详细说明转出原因" />
                    </el-form-item>
                </div>
                
                <!-- 目标学校联系信息 -->
                <div class="form-section">
                    <h4 class="section-title">目标学校信息（选填）</h4>
                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="联系人" prop="target_school_contact">
                                <el-input 
                                    v-model="transferOutForm.target_school_contact" 
                                    placeholder="目标学校联系人姓名" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="联系电话" prop="target_school_phone">
                                <el-input 
                                    v-model="transferOutForm.target_school_phone" 
                                    placeholder="目标学校联系电话" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                    
                    <el-form-item label="学校地址" prop="target_school_address">
                        <el-input 
                            v-model="transferOutForm.target_school_address" 
                            placeholder="目标学校详细地址" />
                    </el-form-item>
                </div>
                
                <!-- 处理信息 -->
                <div class="form-section">
                    <h4 class="section-title">处理信息</h4>
                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="处理人" prop="processor">
                                <el-input 
                                    v-model="transferOutForm.processor" 
                                    readonly
                                    disabled
                                    placeholder="自动设置为当前登录用户">
                                    <template #prepend>
                                        <el-icon><User /></el-icon>
                                    </template>
                                </el-input>
                            </el-form-item>
                        </el-col>
                    </el-row>
                    
                    <el-form-item label="审批意见" prop="approval_notes">
                        <el-input 
                            v-model="transferOutForm.approval_notes" 
                            type="textarea" 
                            :rows="2"
                            placeholder="审批意见或处理说明（选填）" />
                    </el-form-item>
                    
                    <el-form-item label="备注信息" prop="remarks">
                        <el-input 
                            v-model="transferOutForm.remarks" 
                            type="textarea" 
                            :rows="2"
                            placeholder="其他备注信息（选填）" />
                    </el-form-item>
                </div>
            </el-form>
            
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="cancelTransferOut">取消</el-button>
                    <el-button 
                        type="warning" 
                        @click="handleTransferOutSubmit" 
                        :loading="transferOutLoading">
                        确认转出
                    </el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
    Search, 
    RefreshLeft, 
    User, 
    Location, 
    Avatar, 
    Male, 
    Female, 
    Phone, 
    InfoFilled,
    Right,
    Back,
    Check,
    CloseBold
} from '@element-plus/icons-vue'
import { studentAPI } from '@/api/student'
import { useUserStore } from '@/utils/userStore'

// 用户状态管理
const userStore = useUserStore()

// 用户姓名计算属性
const currentUserName = computed(() => {
    const user = userStore.state.user
    if (user?.first_name || user?.last_name) {
        return (user.first_name || '') + (user.last_name || '')
    }
    return '系统管理员' // 备用默认值
})

// 转学类型
const transferType = ref('')

// 查询表单（转出用）
const searchForm = reactive({
  keyword: ''
})

// 转入表单
const transferInForm = reactive({
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
    guardian_mother_phone: '',
    transfer_date: '',
    transfer_reason: '',
    previous_school: '',
    transfer_notes: ''
})

// 表单验证规则
const transferInRules = reactive({
    name: [
        { required: true, message: '请输入学生姓名', trigger: 'blur' }
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
    ],
    transfer_date: [
        { required: true, message: '请选择转入时间', trigger: 'change' }
    ],
    transfer_reason: [
        { required: true, message: '请填写转学原因', trigger: 'blur' }
    ],
    grade: [
        { required: true, message: '请选择年级', trigger: 'change' }
    ],
    class_name: [
        { required: true, message: '请输入班级', trigger: 'blur' }
    ],
    previous_school: [
        { required: false, message: '请输入原学校名称', trigger: 'blur' }
    ]
})

// 状态管理
const searchLoading = ref(false)
const submitLoading = ref(false)
const showDetail = ref(false)
const currentStudent = ref(null)
const transferInFormRef = ref()

// 转出相关状态
const transferOutVisible = ref(false)
const transferOutLoading = ref(false)
const transferOutFormRef = ref()

// 转出表单数据 - 直接使用computed属性初始化processor
const transferOutForm = reactive({
    target_school: '',
    transfer_date: '',
    transfer_reason: '',
    target_grade: '',
    target_class: '',
    target_school_contact: '',
    target_school_phone: '',
    target_school_address: '',
    processor: currentUserName.value, // 直接设置为当前用户姓名
    approval_notes: '',
    remarks: ''
})

// 转出表单验证规则
const transferOutRules = reactive({
    target_school: [
        { required: true, message: '请输入目标学校名称', trigger: 'blur' }
    ],
    transfer_date: [
        { required: true, message: '请选择转出日期', trigger: 'change' }
    ],
    transfer_reason: [
        { required: true, message: '请填写转出原因', trigger: 'blur' },
        { min: 5, message: '转出原因至少需要5个字符', trigger: 'blur' }
    ],
    processor: [
        { required: true, message: '请输入处理人姓名', trigger: 'blur' }
    ]
})

// 休学表单数据
const suspendForm = reactive({
    suspend_start_date: '',
    expected_resume_date: '',
    suspend_reason_type: '',
    suspend_reason: '',
    contact_person: '',
    contact_phone: '',
    processor: currentUserName.value, // 直接设置为当前用户姓名
    remarks: ''
})

// 休学表单验证规则
const suspendRules = reactive({
    suspend_start_date: [
        { required: true, message: '请选择休学开始日期', trigger: 'change' }
    ],
    suspend_reason: [
        { required: true, message: '请填写休学原因', trigger: 'blur' },
        { min: 5, message: '休学原因至少需要5个字符', trigger: 'blur' }
    ],
    contact_person: [
        { required: true, message: '请输入联系人姓名', trigger: 'blur' }
    ],
    contact_phone: [
        { required: true, message: '请输入联系电话', trigger: 'blur' },
        { pattern: /^1[3456789]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
    ],
    processor: [
        { required: true, message: '请输入处理人姓名', trigger: 'blur' }
    ]
})

// 复学表单数据
const resumeForm = reactive({
    resume_date: '',
    resume_grade: '',
    resume_class: '',
    resume_reason: '',
    processor: currentUserName.value, // 直接设置为当前用户姓名
    approval_notes: '',
    remarks: ''
})

// 复学表单验证规则
const resumeRules = reactive({
    resume_date: [
        { required: true, message: '请选择复学日期', trigger: 'change' }
    ],
    resume_grade: [
        { required: true, message: '请选择复学年级', trigger: 'change' }
    ],
    resume_class: [
        { required: true, message: '请输入复学班级', trigger: 'blur' }
    ],
    resume_reason: [
        { required: true, message: '请填写复学说明', trigger: 'blur' },
        { min: 5, message: '复学说明至少需要5个字符', trigger: 'blur' }
    ],
    processor: [
        { required: true, message: '请输入处理人姓名', trigger: 'blur' }
    ]
})

// 表单引用
const suspendFormRef = ref()
const resumeFormRef = ref()

// 转学类型变化处理
const handleTransferTypeChange = () => {
    // 清空所有状态
    handleReset()
    handleTransferInReset()
}

// 查询处理（转出）
const handleSearch = async () => {
    if (!searchForm.keyword.trim()) {
        ElMessage.warning('请输入查询关键词')
        return
    }

    searchLoading.value = true
    try {
        const params = {
            search: searchForm.keyword,
            page_size: 10
        }
        
        const response = await studentAPI.getStudentList(params)
        
        if (response.data.length === 0) {
            currentStudent.value = null
            showDetail.value = true
            ElMessage.info('未找到匹配的学生信息')
        } else if (response.data.length === 1) {
            currentStudent.value = response.data[0]
            showDetail.value = true
            ElMessage.success('查询成功，找到学生信息')
        } else {
            ElMessage.warning({
                message: `找到 ${response.data.length} 个匹配结果，请输入更精确的信息`,
                duration: 5000
            })
            
            currentStudent.value = response.data[0]
            showDetail.value = true
            
            const otherStudents = response.data.slice(1).map(s => `${s.name}(${s.school_id})`).join('、')
            ElMessage.info({
                message: `其他匹配结果：${otherStudents}`,
                duration: 8000
            })
        }
        
    } catch (error) {
        console.error('查询失败:', error)
        ElMessage.error('查询失败: ' + error.message)
        showDetail.value = false
    } finally {
        searchLoading.value = false
    }
}

// 重置查询（转出）
const handleReset = () => {
    searchForm.keyword = ''
    currentStudent.value = null
    showDetail.value = false
}

// 重置转入表单
const handleTransferInReset = () => {
    if (transferInFormRef.value) {
        transferInFormRef.value.resetFields()
    }
    Object.keys(transferInForm).forEach(key => {
        if (key === 'age') {
            transferInForm[key] = null
        } else {
            transferInForm[key] = ''
        }
    })
}

// 转入表单提交
const handleTransferInSubmit = async () => {
    try {
        await transferInFormRef.value.validate()
        
        submitLoading.value = true
        
        // 格式化日期函数
        const formatDate = (date) => {
            if (!date) return null
            const d = new Date(date)
            const year = d.getFullYear()
            const month = String(d.getMonth() + 1).padStart(2, '0')
            const day = String(d.getDate()).padStart(2, '0')
            return `${year}-${month}-${day}`
        }
        
        // 准备提交数据
        const submitData = {
            name: transferInForm.name,
            school_id: transferInForm.school_id,
            grade: transferInForm.grade,
            class_name: transferInForm.class_name,
            id_card: transferInForm.id_card,
            age: parseInt(transferInForm.age) || null,
            gz_student_id: transferInForm.gz_student_id,
            national_student_id: transferInForm.national_student_id || '',
            household_address: transferInForm.household_address || '',
            living_address: transferInForm.living_address || '',
            guardian_father: transferInForm.guardian_father || '',
            guardian_mother: transferInForm.guardian_mother || '',
            guardian_father_phone: transferInForm.guardian_father_phone || '',
            guardian_mother_phone: transferInForm.guardian_mother_phone || '',
            transfer_date: formatDate(transferInForm.transfer_date), // 格式化日期
            transfer_reason: transferInForm.transfer_reason,
            previous_school: transferInForm.previous_school || '',
            transfer_notes: transferInForm.transfer_notes || ''
        }
        
        console.log('提交转入数据:', submitData)
        
        // 数据验证
        if (!submitData.name || !submitData.school_id || !submitData.grade || 
            !submitData.class_name || !submitData.id_card || !submitData.gz_student_id ||
            !submitData.transfer_date || !submitData.transfer_reason) {
            ElMessage.error('请填写所有必填字段')
            return
        }
        
        // 调用转入API
        const response = await studentAPI.transferIn(submitData)
        
        ElMessage.success({
            message: `学生 ${response.data.name} 转入登记成功！`,
            duration: 3000
        })
        
        // 显示详细信息
        ElMessageBox.alert(
            `学生信息已成功录入系统！
            \n• 姓名：${response.data.name}
            \n• 学号：${response.data.school_id}
            \n• 年级班级：${response.data.grade}${response.data.class_name}
            \n• 原学校：${submitData.previous_school || '未填写'}
            \n• 转入时间：${submitData.transfer_date}
            \n• 转学原因：${submitData.transfer_reason}`,
            '转入成功',
            {
                confirmButtonText: '确定',
                type: 'success'
            }
        )
        
        handleTransferInReset()
        
    } catch (error) {
        console.error('转入登记失败:', error)
        console.error('错误详情:', error.response?.data)
        
        if (error.response && error.response.data) {
            if (error.response.data.details) {
                // 显示详细的验证错误
                const errorMessages = []
                for (const [field, messages] of Object.entries(error.response.data.details)) {
                    errorMessages.push(`${field}: ${messages.join(', ')}`)
                }
                ElMessage.error(`数据验证失败：\n${errorMessages.join('\n')}`)
            } else {
                ElMessage.error('转入登记失败: ' + error.response.data.error)
            }
        } else {
            ElMessage.error('转入登记失败: ' + error.message)
        }
    } finally {
        submitLoading.value = false
    }
}

// 修改原有的转出处理函数
const handleTransferOut = () => {
    if (!currentStudent.value) {
        ElMessage.error('请先查询学生信息')
        return
    }
    
    if (currentStudent.value.status !== 'active') {
        ElMessage.error(`该学生当前状态为"${currentStudent.value.status_display}"，无法办理转出`)
        return
    }
    
    // 重置表单并打开弹窗
    resetTransferOutForm()
    transferOutVisible.value = true
}

// 重置转出表单
const resetTransferOutForm = () => {
    if (transferOutFormRef.value) {
        transferOutFormRef.value.resetFields()
    }
    Object.keys(transferOutForm).forEach(key => {
        if (key === 'processor') {
            transferOutForm[key] = currentUserName.value
        } else {
            transferOutForm[key] = ''
        }
    })
}

// 取消转出
const cancelTransferOut = () => {
    transferOutVisible.value = false
    resetTransferOutForm()
}

// 转出表单提交
const handleTransferOutSubmit = async () => {
    try {
        await transferOutFormRef.value.validate()
        
        submitLoading.value = true
        
        // 准备提交数据
        const submitData = {
            student_id: currentStudent.value.id,
            target_school: transferOutForm.target_school,
            transfer_date: transferOutForm.transfer_date,
            target_grade: transferOutForm.target_grade,
            target_class: transferOutForm.target_class,
            transfer_reason: transferOutForm.transfer_reason,
            target_school_contact: transferOutForm.target_school_contact,
            target_school_phone: transferOutForm.target_school_phone,
            target_school_address: transferOutForm.target_school_address,
            processor: transferOutForm.processor,
            approval_notes: transferOutForm.approval_notes,
            remarks: transferOutForm.remarks
        }
        
        console.log('提交转出数据:', submitData)
        
        const response = await studentAPI.transferOut(submitData)
        
        console.log('转出响应数据:', response)
        
        // **修复：更安全的数据访问方式**
        const studentName = response?.data?.student_name || response?.student_name || currentStudent.value?.name || '该学生'
        const targetSchool = response?.data?.target_school || response?.target_school || transferOutForm.target_school
        const message = response?.data?.message || response?.message || '转出办理成功'
        
        ElMessage.success({
            message: `${studentName} 同学转出到 ${targetSchool} 办理成功！`,
            duration: 4000
        })
        
        // **通知 transfer_data.vue 刷新数据**
        window.dispatchEvent(new CustomEvent('transfer-record-updated', {
            detail: {
                type: 'transfer_out',
                studentId: currentStudent.value.id,
                studentName: studentName,
                targetSchool: targetSchool
            }
        }))
        
        // 关闭弹窗
        transferOutVisible.value = false
        
        // 重置表单和状态
        handleReset()
        resetTransferOutForm()
        
    } catch (error) {
        console.error('转出失败:', error)
        console.error('错误响应:', error.response)
        
        // **更详细的错误处理**
        let errorMessage = '转出失败'
        
        if (error.response) {
            // 服务器返回了错误响应
            if (error.response.data && error.response.data.error) {
                errorMessage = '转出失败: ' + error.response.data.error
            } else if (error.response.data && error.response.data.message) {
                errorMessage = '转出失败: ' + error.response.data.message
            } else {
                errorMessage = `转出失败: HTTP ${error.response.status}`
            }
        } else if (error.request) {
            // 请求发送了但没有收到响应
            errorMessage = '转出失败: 网络连接错误，请检查网络连接'
        } else if (error.message) {
            // 其他错误
            errorMessage = '转出失败: ' + error.message
        }
        
        ElMessage.error({
            message: errorMessage,
            duration: 5000
        })
    } finally {
        submitLoading.value = false
    }
}

// 获取搜索提示文本
const getSearchPlaceholder = () => {
    const placeholders = {
        'transfer_out': '请输入需要转出学生的姓名',
        'suspend': '请输入需要休学学生的姓名',
        'resume': '请输入需要复学学生的姓名'
    }
    return placeholders[transferType.value] || '请输入学生姓名'
}

// 休学原因类型变化处理
const handleSuspendReasonTypeChange = () => {
    const reasonMap = {
        'illness': '因疾病需要休学治疗',
        'personal': '因个人事务需要休学',
        'other': ''
    }
    suspendForm.suspend_reason = reasonMap[suspendForm.suspend_reason_type] || ''
}

// 休学提交处理
const handleSuspendSubmit = async () => {
    try {
        await suspendFormRef.value.validate()
        
        submitLoading.value = true
        
        // 准备提交数据
        const submitData = {
            student_id: currentStudent.value.id,
            transfer_type: 'suspend',
            suspend_start_date: suspendForm.suspend_start_date,
            expected_resume_date: suspendForm.expected_resume_date,
            transfer_reason: suspendForm.suspend_reason,
            contact_person: suspendForm.contact_person,
            contact_phone: suspendForm.contact_phone,
            processor: suspendForm.processor,
            remarks: suspendForm.remarks
        }
        
        console.log('提交休学数据:', submitData)
        
        // 调用API（需要在后端实现对应的接口）
        const response = await studentAPI.submitSuspend(submitData)
        
        ElMessage.success(`学生 ${currentStudent.value.name} 休学申请提交成功！`)
        
        // 重置表单和状态
        handleReset()
        resetSuspendForm()
        
    } catch (error) {
        console.error('休学申请失败:', error)
        ElMessage.error('休学申请失败: ' + (error.response?.data?.error || error.message))
    } finally {
        submitLoading.value = false
    }
}

// 复学提交处理
const handleResumeSubmit = async () => {
    try {
        await resumeFormRef.value.validate()
        
        submitLoading.value = true
        
        // 准备提交数据
        const submitData = {
            student_id: currentStudent.value.id,
            transfer_type: 'resume',
            resume_date: resumeForm.resume_date,
            resume_grade: resumeForm.resume_grade,
            resume_class: resumeForm.resume_class,
            transfer_reason: resumeForm.resume_reason,
            processor: resumeForm.processor,
            approval_notes: resumeForm.approval_notes,
            remarks: resumeForm.remarks
        }
        
        console.log('提交复学数据:', submitData)
        
        // 调用API（需要在后端实现对应的接口）
        const response = await studentAPI.submitResume(submitData)
        
        ElMessage.success(`学生 ${currentStudent.value.name} 复学申请提交成功！`)
        
        // 重置表单和状态
        handleReset()
        resetResumeForm()
        
    } catch (error) {
        console.error('复学申请失败:', error)
        ElMessage.error('复学申请失败: ' + (error.response?.data?.error || error.message))
    } finally {
        submitLoading.value = false
    }
}

// 重置休学表单
const resetSuspendForm = () => {
    Object.keys(suspendForm).forEach(key => {
        if (key === 'processor') {
            suspendForm[key] = currentUserName.value
        } else if (key === 'contact_phone') {
            suspendForm[key] = ''
        } else {
            suspendForm[key] = ''
        }
    })
    
    if (suspendFormRef.value) {
        suspendFormRef.value.resetFields()
    }
}

// 重置复学表单
const resetResumeForm = () => {
    Object.keys(resumeForm).forEach(key => {
        if (key === 'processor') {
            resumeForm[key] = currentUserName.value
        } else {
            resumeForm[key] = ''
        }
    })
    
    if (resumeFormRef.value) {
        resumeFormRef.value.resetFields()
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

// 计算数据完整度
const calculateCompleteness = (student) => {
    const fields = [
        'name', 'school_id', 'id_card', 'age', 'gz_student_id',
        'national_student_id', 'household_address', 'living_address',
        'guardian_father', 'guardian_mother', 'guardian_father_phone', 'guardian_mother_phone'
    ]
    
    const filledFields = fields.filter(field => 
        student[field] && student[field].toString().trim() !== ''
    )
    
    return Math.round((filledFields.length / fields.length) * 100)
}

// 获取完整度颜色
const getCompletenessColor = (percentage) => {
    if (percentage >= 90) return '#67c23a'
    if (percentage >= 70) return '#e6a23c'
    return '#f56c6c'
}

// 监听用户姓名变化，自动更新表单中的处理人
watch(currentUserName, (newName) => {
    transferOutForm.processor = newName
    suspendForm.processor = newName
    resumeForm.processor = newName
}, { immediate: true })
</script>

<style scoped>

.full-width-form {
    padding: 10px;
    margin: 0;
    width: 100%;
    box-sizing: border-box;
}

.transfer-form {
    width: 100%;
    margin: 0;
    padding: 0;
}

.form-section {
    margin-bottom: 20px;
    background: #fafbfc;
    padding: 10px;
    border-radius: 8px;
    border-left: 4px solid #409eff;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.section-title {
    color: #409eff;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 25px;
    padding-bottom: 12px;
    border-bottom: 2px solid #e4e7ed;
    display: flex;
    align-items: center;
}

.section-title::before {
    content: '';
    width: 4px;
    height: 18px;
    background: #409eff;
    margin-right: 10px;
    border-radius: 2px;
}

.form-footer {
    text-align: center;
    margin-top: 50px;
    padding-top: 30px;
    border-top: 2px solid #e4e7ed;
}

.form-footer .el-button {
    padding: 15px 40px;
    font-size: 16px;
    margin: 0 15px;
    border-radius: 6px;
}

/* 表单项样式增强 */
:deep(.el-form-item) {
    margin-bottom: 25px;
}

:deep(.el-form-item__label) {
    font-weight: 600;
    color: #303133;
    font-size: 14px;
    line-height: 40px;
}

:deep(.el-input__wrapper) {
    border-radius: 6px;
    box-shadow: 0 0 0 1px #dcdfe6 inset;
    transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
    box-shadow: 0 0 0 1px #c0c4cc inset;
}

:deep(.el-input__wrapper.is-focus) {
    box-shadow: 0 0 0 1px #409eff inset;
}

:deep(.el-textarea__inner) {
    border-radius: 6px;
    border: 1px solid #dcdfe6;
    transition: all 0.3s ease;
}

:deep(.el-textarea__inner:hover) {
    border-color: #c0c4cc;
}

:deep(.el-textarea__inner:focus) {
    border-color: #409eff;
}

/* 选择器样式 */
:deep(.el-select) {
    width: 100%;
}

:deep(.el-date-editor) {
    width: 100%;
}

/* 响应式调整 */
@media (max-width: 1200px) {
    .full-width-form {
        padding: 10px;
    }
    
    .form-section {
        padding: 20px;
        margin-bottom: 30px;
    }
    
    .section-title {
        font-size: 16px;
        margin-bottom: 20px;
    }
}

@media (max-width: 768px) {
    .transfer-form :deep(.el-col) {
        margin-bottom: 15px;
    }
    
    .form-footer .el-button {
        width: 100%;
        margin-bottom: 10px;
    }
}

/* 详情部分样式保持不变 */
.detail-container {
    padding: 0;
}

.detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 2px solid #f0f0f0;
}

.detail-descriptions {
    margin-bottom: 10px;
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

.transfer-actions {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 2px solid #f0f0f0;
}

.action-buttons {
    text-align: center;
}

.action-buttons .el-button {
    margin: 0 10px 10px 0;
}

.no-data {
    text-align: center;
    padding: 40px;
}

/* 自定义 descriptions 样式 */
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

.transfer-out-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #ebeef5;
}

.form-section {
    margin-bottom: 25px;
    padding: 15px;
    background: #fafafa;
    border-radius: 6px;
    border-left: 3px solid #409eff;
}

.section-title {
    margin: 0 0 15px 0;
    font-size: 14px;
    font-weight: 600;
    color: #409eff;
}

.status-warning {
    margin-top: 15px;
}

.dialog-footer {
    text-align: right;
}
</style>
