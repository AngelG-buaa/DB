import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NProgress from 'nprogress'
import { ElMessage } from 'element-plus'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: {
      title: '用户登录',
      requiresAuth: false
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: {
      title: '用户注册',
      requiresAuth: false
    }
  },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Dashboard.vue'),
        meta: {
          title: '仪表盘',
          icon: 'DataBoard'
        }
      },
      // 实验室管理
      {
        path: 'laboratory',
        name: 'Laboratory',
        redirect: '/laboratory/list',
        meta: {
          title: '实验室管理',
          icon: 'OfficeBuilding',
          roles: ['admin', 'teacher']
        },
        children: [
          {
            path: 'list',
            name: 'LaboratoryList',
            component: () => import('@/views/labs/LabList.vue'),
            meta: {
              title: '实验室列表'
            }
          },
          {
            path: 'create',
            name: 'LaboratoryCreate',
            component: () => import('@/views/laboratory/Create.vue'),
            meta: {
              title: '新建实验室',
              roles: ['admin']
            }
          },
          {
            path: 'edit/:id',
            name: 'LaboratoryEdit',
            component: () => import('@/views/laboratory/Edit.vue'),
            meta: {
              title: '编辑实验室',
              roles: ['admin']
            }
          }
        ]
      },
      // 设备管理
      {
        path: 'equipment',
        name: 'Equipment',
        redirect: '/equipment/list',
        meta: {
          title: '设备管理',
          icon: 'Monitor',
          roles: ['admin', 'teacher']
        },
        children: [
          {
            path: 'list',
            name: 'EquipmentList',
            component: () => import('@/views/equipment/EquipmentList.vue'),
            meta: {
              title: '设备列表'
            }
          },
          {
            path: 'create',
            name: 'EquipmentCreate',
            component: () => import('@/views/equipment/Create.vue'),
            meta: {
              title: '新增设备',
              roles: ['admin']
            }
          },
          
          {
            path: 'maintenance',
            name: 'EquipmentMaintenance',
            component: () => import('@/views/maintenance/MaintenanceList.vue'),
            meta: {
              title: '设备维修',
              roles: ['admin', 'teacher']
            }
          }
        ]
      },
      // 预约管理
      {
        path: 'reservation',
        name: 'Reservation',
        redirect: '/reservation/list',
        meta: {
          title: '预约管理',
          icon: 'Calendar'
        },
        children: [
          {
            path: 'list',
            name: 'ReservationList',
            component: () => import('@/views/reservations/ReservationList.vue'),
            meta: {
              title: '预约列表'
            }
          },
          {
            path: 'create',
            name: 'ReservationCreate',
            component: () => import('@/views/reservations/ReservationCreate.vue'),
            meta: {
              title: '新建预约'
            }
          },
          
          {
            path: 'calendar',
            name: 'ReservationCalendar',
            component: () => import('@/views/reservations/ReservationCalendar.vue'),
            meta: {
              title: '预约日历'
            }
          },
          {
            path: 'approval',
            name: 'ReservationApproval',
            component: () => import('@/views/reservation/Approval.vue'),
            meta: {
              title: '预约审批',
              roles: ['admin', 'teacher']
            }
          }
        ]
      },
      // 耗材管理
      {
        path: 'consumable',
        name: 'Consumable',
        redirect: '/consumable/list',
        meta: {
          title: '耗材管理',
          icon: 'Box',
          roles: ['admin', 'teacher']
        },
        children: [
          {
            path: 'list',
            name: 'ConsumableList',
            component: () => import('@/views/consumables/ConsumableList.vue'),
            meta: {
              title: '耗材列表'
            }
          },
          {
            path: 'create',
            name: 'ConsumableCreate',
            component: () => import('@/views/consumable/Create.vue'),
            meta: {
              title: '新增耗材',
              roles: ['admin']
            }
          },
          {
            path: 'usage',
            name: 'ConsumableUsage',
            component: () => import('@/views/consumables/UsageRecords.vue'),
            meta: {
              title: '使用记录'
            }
          }
        ]
      },
      // 课程管理
      {
        path: 'course',
        name: 'Course',
        redirect: '/course/list',
        meta: {
          title: '课程管理',
          icon: 'Reading',
          roles: ['admin', 'teacher']
        },
        children: [
          {
            path: 'list',
            name: 'CourseList',
            component: () => import('@/views/course/List.vue'),
            meta: {
              title: '课程列表'
            }
          },
          {
            path: 'create',
            name: 'CourseCreate',
            component: () => import('@/views/course/Create.vue'),
            meta: {
              title: '新建课程',
              roles: ['admin', 'teacher']
            }
          }
        ]
      },
      // 用户管理
      {
        path: 'user',
        name: 'User',
        redirect: '/user/list',
        meta: {
          title: '用户管理',
          icon: 'User',
          roles: ['admin']
        },
        children: [
          {
            path: 'list',
            name: 'UserList',
            component: () => import('@/views/user/List.vue'),
            meta: {
              title: '用户列表'
            }
          },
          {
            path: 'create',
            name: 'UserCreate',
            component: () => import('@/views/user/Create.vue'),
            meta: {
              title: '新建用户'
            }
          }
        ]
      },
      // 统计报表
      {
        path: 'statistics',
        name: 'Statistics',
        redirect: '/statistics/overview',
        meta: {
          title: '统计报表',
          icon: 'DataAnalysis',
          roles: ['admin', 'teacher']
        },
        children: [
          {
            path: 'overview',
            name: 'StatisticsOverview',
            component: () => import('@/views/statistics/Overview.vue'),
            meta: {
              title: '数据概览'
            }
          },
          {
            path: 'reservation',
            name: 'StatisticsReservation',
            component: () => import('@/views/statistics/Reservation.vue'),
            meta: {
              title: '预约统计'
            }
          },
          {
            path: 'equipment',
            name: 'StatisticsEquipment',
            component: () => import('@/views/statistics/Equipment.vue'),
            meta: {
              title: '设备统计'
            }
          }
        ]
      },
      // 个人中心
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/Profile.vue'),
        meta: {
          title: '个人中心',
          icon: 'UserFilled'
        }
      },
      // 系统设置
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/Index.vue'),
        meta: {
          title: '系统设置',
          icon: 'Setting',
          roles: ['admin']
        }
      }
    ]
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/404.vue'),
    meta: {
      title: '页面不存在'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const userStore = useUserStore()
  const isAuthenticated = userStore.isAuthenticated
  // 刷新后若有token但未加载用户信息，先拉取用户信息再进行角色判断
  if (isAuthenticated && !userStore.userInfo) {
    try {
      await userStore.getUserInfo()
    } catch (e) {
      // 拉取失败则视为未登录
    }
  }
  const userRole = userStore.userInfo?.role
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 高校实验室预约与设备管理系统`
  }
  
  // 检查是否需要登录
  if (to.meta.requiresAuth !== false && !isAuthenticated) {
    next('/login')
    return
  }
  
  // 已登录用户访问登录页面，重定向到首页
  if (isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    next('/')
    return
  }
  
  // 检查角色权限
  if (to.meta.roles && to.meta.roles.length > 0) {
    if (!to.meta.roles.includes(userRole)) {
      ElMessage.error('您没有权限访问该页面')
      next('/')
      return
    }
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router