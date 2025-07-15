import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/utils/userStore'
import { getUserInfo, getUserPermissions } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue'),
      meta: { 
        title: '登录',
        requiresAuth: false 
      }
    },
    { 
      path: '/', 
      redirect: '/manage/home' 
    },
    { 
      path: '/manage', 
      component: () => import('../views/Manage.vue'),
      meta: { requiresAuth: true },
      children: [
        { 
          path: 'home', 
          name: 'home', 
          meta: { title: '主页', requiresAuth: true }, 
          component: () => import('../views/Home.vue')
        },
        { 
          path: 'user_data', 
          name: 'user_data', 
          meta: { title: '学生信息管理', requiresAuth: true }, 
          component: () => import('../views/user_data.vue')
        },
        { 
          path: 'transfer_process', 
          name: 'transfer_process', 
          meta: { title: '转学办理', requiresAuth: true }, 
          component: () => import('../views/transfer_process.vue')
        },
        { 
          path: 'transfer_data', 
          name: 'transfer_data',
          meta: { title: '转学数据详情', requiresAuth: true }, 
          component: () => import('../views/transfer_data.vue')
        },
        { 
          path: 'grade_query', 
          name: 'grade_query', 
          meta: { title: '成绩查询', requiresAuth: true }, 
          component: () => import('../views/GradeQuery.vue')
        },
        { 
          path: 'grade_analysis', 
          name: 'grade_analysis', 
          meta: { title: '成绩分析', requiresAuth: true }, 
          component: () => import('../views/GradeAnalysis.vue')
        }
      ] 
    }
  ],
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  const userStore = useUserStore()
  const isLoggedIn = userStore.state.isLoggedIn
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !isLoggedIn) {
    ElMessage.warning('请先登录')
    next('/login')
    return
  }
  
  // 已登录用户访问登录页，重定向到首页
  if (to.path === '/login' && isLoggedIn) {
    next('/manage/home')
    return
  }
  
  // 如果已登录但没有权限信息，获取权限
  if (isLoggedIn && !userStore.state.permissions.is_admin && !userStore.state.permissions.can_view) {
    try {
      const [userResponse, permissionsResponse] = await Promise.all([
        getUserInfo(),
        getUserPermissions()
      ])
      
      userStore.setUser(userResponse.user)
      userStore.setPermissions(permissionsResponse)
    } catch (error) {
      console.error('获取用户权限失败:', error)
      // 如果获取权限失败，可能是token过期，清除登录状态
      userStore.clearAllStorage()
      next('/login')
      return
    }
  }
  
  // 检查管理员权限（如果路由需要）
  if (to.meta.adminOnly && !userStore.isAdmin()) {
    ElMessage.error('权限不足，需要管理员权限')
    next('/manage/home')
    return
  }
  
  next()
})

export default router
