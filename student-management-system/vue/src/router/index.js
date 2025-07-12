import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/utils/userStore'
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
router.beforeEach((to, from, next) => {
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
  
  next()
})

export default router
