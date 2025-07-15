<template>
    <div>
        <!-- 导航栏开始 -->
        <div style="height: 60px; background-color: #313a46; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center;">
                <img src="../assets/logo.png" style="padding: 5px; margin-left: 10px; width: 50px;">
                <div style="width: 200px; display: flex; align-items: center; font-size: 24px; color: white; padding: 0 10px;"
                    class="custom-title">Jnua学生管理系统</div>
            </div>
            
            <!-- 用户信息区域 -->
            <div style="margin-right: 20px;">
                <el-dropdown @command="handleUserCommand">
                    <span style="color: white; cursor: pointer; display: flex; align-items: center;">
                        <el-icon style="margin-right: 5px;"><User /></el-icon>
                        {{ (userStore.state.user?.first_name || '') + (userStore.state.user?.last_name || '') || userStore.state.user?.username || '管理员' }}
                        <el-icon style="margin-left: 5px;"><ArrowDown /></el-icon>
                    </span>
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item command="profile">
                                <el-icon><User /></el-icon>
                                个人信息
                            </el-dropdown-item>
                            <el-dropdown-item command="logout" divided>
                                <el-icon><SwitchButton /></el-icon>
                                退出登录
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </div>
        </div>
        <!-- 导航栏结束 -->

        <!-- 下面部分开始开始 -->
        <div style="display: flex;">
            <!-- 侧边栏开始 -->
            <div style="width: 180px; border: 1px solid #ddd; min-height: calc(100vh - 60px);">
                <el-menu 
                    router 
                    style="border: 0;" 
                    :default-active="$route.path" 
                    class="el-menu-vertical-demo" 
                    @open="handleOpen" 
                    @close="handleClose"
                    @select="handleMenuSelect">
                    
                    <el-menu-item index="/manage/home" style="border-bottom: 1px solid #ddd;">
                        <el-icon><House /></el-icon>
                        <span>首页</span>
                    </el-menu-item>
                    
                    <el-menu-item index="/manage/user_data" style="border-bottom: 1px solid #ddd;">
                        <el-icon><User /></el-icon>
                        <span>学生信息</span>
                    </el-menu-item>
                    
                    <el-sub-menu index="1" style="border-bottom: 1px solid #ddd;">
                        <template #title>
                            <el-icon><School /></el-icon>
                            <span>异动情况管理</span>
                        </template>
                        <el-menu-item index="/manage/transfer_process" style="margin-left: -10px;">
                            <el-icon><Promotion /></el-icon>
                            <span>异动办理</span>
                        </el-menu-item>
                        <el-menu-item index="/manage/transfer_data" style="margin-left: -10px;">
                            <el-icon><Histogram /></el-icon>
                            <span>异动数据详情</span>
                        </el-menu-item>
                    </el-sub-menu>

                    <el-sub-menu index="2" style="border-bottom: 1px solid #ddd;">
                        <template #title>
                            <el-icon><DataAnalysis /></el-icon>
                            <span>成绩管理</span>
                        </template>
                        <el-menu-item index="/manage/grade_query" style="margin-left: -10px;">
                            <el-icon><Search /></el-icon>
                            <span>成绩查询</span>
                        </el-menu-item>
                        <el-menu-item index="/manage/grade_analysis" style="margin-left: -10px;">
                            <el-icon><TrendCharts /></el-icon>
                            <span>成绩分析</span>
                        </el-menu-item>
                    </el-sub-menu>

                    <!-- 用户管理菜单 - 仅超级管理员可见 -->
                    <el-menu-item 
                        v-if="userStore.isSuperUser()" 
                        index="/manage/user_management" 
                        style="border-bottom: 1px solid #ddd;">
                        <el-icon><Setting /></el-icon>
                        <span>用户管理</span>
                    </el-menu-item>
                </el-menu>
            </div>
            <!-- 侧边栏结束 -->

            <!-- 主要内容区域开始 -->
            <div style="flex: 1; width: 0; background-color: #f8f8f8;">
                <!-- 标签页导航 -->
                <el-tabs 
                    v-model="activeTabName" 
                    type="border-card" 
                    closable 
                    @tab-remove="removeTab"
                    @tab-click="handleTabClick"
                    style="margin: 0; background-color: white;">
                    <el-tab-pane 
                        v-for="tab in openTabs" 
                        :key="tab.name"
                        :label="tab.title" 
                        :name="tab.name"
                        :closable="tab.name !== '/manage/home'">
                        <!-- 页面内容 -->
                        <div style="padding: 10px; min-height: calc(100vh - 120px); overflow-y: auto;">
                            <router-view v-if="tab.name === activeTabName" :key="tab.name" />
                        </div>
                    </el-tab-pane>
                </el-tabs>
            </div>
            <!-- 主要内容区域结束 -->
        </div>
        <!-- 下面部分结束 -->
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    HomeFilled as House,
    User,
    School,
    Promotion,
    DataBoard as Histogram,
    Search,
    TrendCharts,
    DataAnalysis,
    ArrowDown,
    SwitchButton,
    Setting
} from '@element-plus/icons-vue'
import { useUserStore } from '@/utils/userStore'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 标签页管理
const activeTabName = ref('/manage/home')
const openTabs = ref([
    {
        name: '/manage/home',
        title: '首页',
        closable: false
    }
])

// 路由标题映射
const routeTitleMap = {
    '/manage/home': '首页',
    '/manage/user_data': '学生信息',
    '/manage/transfer_process': '异动办理',
    '/manage/transfer_data': '异动数据详情',
    '/manage/grade_query': '成绩查询',
    '/manage/grade_analysis': '成绩分析',
    '/manage/user_management': '用户管理'
}

// 添加标签页
const addTab = (routePath) => {
    const title = routeTitleMap[routePath] || '未知页面'
    
    // 检查标签是否已存在
    const existingTab = openTabs.value.find(tab => tab.name === routePath)
    if (!existingTab) {
        openTabs.value.push({
            name: routePath,
            title: title,
            closable: routePath !== '/manage/home'
        })
    }
    
    activeTabName.value = routePath
}

// 移除标签页
const removeTab = (targetName) => {
    if (targetName === '/manage/home') {
        ElMessage.warning('首页标签不能关闭')
        return
    }
    
    const tabIndex = openTabs.value.findIndex(tab => tab.name === targetName)
    if (tabIndex === -1) return
    
    // 如果关闭的是当前活跃标签，需要切换到其他标签
    if (activeTabName.value === targetName) {
        const nextTab = openTabs.value[tabIndex + 1] || openTabs.value[tabIndex - 1]
        if (nextTab) {
            activeTabName.value = nextTab.name
            router.push(nextTab.name)
        }
    }
    
    openTabs.value.splice(tabIndex, 1)
}

// 标签页点击处理
const handleTabClick = (tab) => {
    router.push(tab.props.name)
}

// 菜单选择处理
const handleMenuSelect = (index) => {
    addTab(index)
}

// 监听路由变化
watch(() => route.path, (newPath) => {
    if (newPath.startsWith('/manage/') && routeTitleMap[newPath]) {
        addTab(newPath)
    }
}, { immediate: true })

// 页面加载时初始化
onMounted(() => {
    const currentPath = route.path
    if (currentPath.startsWith('/manage/') && routeTitleMap[currentPath]) {
        addTab(currentPath)
    }
})

const handleOpen = (key, keyPath) => {
    console.log('菜单打开:', key, keyPath)
}

const handleClose = (key, keyPath) => {
    console.log('菜单关闭:', key, keyPath)
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command) => {
    switch (command) {
        case 'profile':
            ElMessage.info('个人信息功能待开发')
            break
        case 'logout':
            try {
                await ElMessageBox.confirm('确定要退出登录吗？', '确认退出', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                })
                
                // 清除用户状态
                userStore.logout()
                router.push('/login')
            } catch (error) {
                // 用户取消退出
            }
            break
    }
}
</script>

<style scoped>
/* 定义自定义字体 */
@font-face {
    font-family: "阿里妈妈东方大楷 Regular";
    font-weight: 400;
    src: url("//at.alicdn.com/wf/webfont/A9PDoAadadrN/cIN5jHUJ5kU2.woff2") format("woff2"),
        url("//at.alicdn.com/wf/webfont/A9PDoAadadrN/dIpvkMDrNwbA.woff") format("woff");
    font-display: swap;
}

/* 应用字体到标题 */
.custom-title {
    font-family: "阿里妈妈东方大楷 Regular", "Microsoft YaHei", "微软雅黑", sans-serif;
}

.el-menu .is-active {
    background-color: #e6ecf7 !important;
}

/* 菜单项样式优化 */
:deep(.el-menu-item) {
    height: 50px !important;
    line-height: 50px !important;
}

:deep(.el-sub-menu .el-menu-item) {
    height: 45px !important;
    line-height: 45px !important;
}

/* 标签页样式优化 */
:deep(.el-tabs__header) {
    margin: 0;
    border-bottom: 1px solid #e4e7ed;
}

:deep(.el-tabs__nav-wrap::after) {
    display: none;
}

:deep(.el-tabs__item) {
    height: 36px;
    line-height: 36px;
    border: 1px solid #e4e7ed;
    border-bottom: none;
    margin-right: 2px;
    background-color: #f5f7fa;
}

:deep(.el-tabs__item.is-active) {
    background-color: white;
    border-bottom: 1px solid white;
}

:deep(.el-tabs__content) {
    padding: 0;
}

:deep(.el-tab-pane) {
    height: 100%;
}
</style>