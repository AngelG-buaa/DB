<template>
  <div class="main-layout">
    <el-container class="layout-container">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '260px'" class="sidebar">
        <div class="logo">
          <img src="/logo.svg" alt="Logo" v-if="!isCollapse" />
          <img src="/logo-mini.svg" alt="Logo" v-else />
          <span v-if="!isCollapse" class="title">Lab System</span>
        </div>
        
        <el-scrollbar>
          <el-menu
            :default-active="activeMenu"
            :collapse="isCollapse"
            :unique-opened="true"
            router
            class="sidebar-menu"
          >
            <template v-for="route in menuRoutes" :key="route.path">
              <el-sub-menu
                v-if="route.children && route.children.length > 1"
                :index="route.path"
              >
                <template #title>
                  <el-icon><component :is="route.meta.icon" /></el-icon>
                  <span>{{ route.meta.title }}</span>
                </template>
                <el-menu-item
                  v-for="child in route.children.filter(c => !c.meta?.roles || userStore.hasRole(c.meta.roles))"
                  :key="child.path"
                  :index="fullPath(route.path, child.path)"
                >
                  {{ child.meta.title }}
                </el-menu-item>
              </el-sub-menu>
              
              <el-menu-item
                v-else-if="route.children && route.children.length === 1"
                :index="fullPath(route.path, route.children[0].path)"
              >
                <el-icon><component :is="route.meta.icon" /></el-icon>
                <template #title>{{ route.meta.title }}</template>
              </el-menu-item>
              
              <el-menu-item v-else :index="fullPath(route.path)">
                <el-icon><component :is="route.meta.icon" /></el-icon>
                <template #title>{{ route.meta.title }}</template>
              </el-menu-item>
            </template>
          </el-menu>
        </el-scrollbar>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container class="content-container">
        <!-- 顶部导航栏 -->
        <el-header class="header">
          <div class="header-left">
            <div
              class="collapse-btn"
              @click="toggleCollapse"
            >
              <el-icon :size="20"><Expand v-if="isCollapse" /><Fold v-else /></el-icon>
            </div>
            
            <!-- 面包屑导航 -->
            <el-breadcrumb separator="/" class="breadcrumb">
              <el-breadcrumb-item
                v-for="item in breadcrumbList"
                :key="item.path"
                :to="item.path"
              >
                {{ item.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          
          <div class="header-right">
            <!-- 通知 -->
            <el-tooltip content="系统通知" placement="bottom">
              <div class="action-item" @click="showNotifications">
                <el-badge :value="notificationCount" :hidden="notificationCount === 0" is-dot>
                  <el-icon :size="20"><Bell /></el-icon>
                </el-badge>
              </div>
            </el-tooltip>
            
            <!-- 用户菜单 -->
            <el-dropdown @command="handleUserCommand" trigger="click">
              <div class="user-info">
                <el-avatar :size="36" :src="userStore.userInfo?.avatar" class="user-avatar">
                  {{ (userStore.userInfo?.name || userStore.userInfo?.username || '').charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="user-details">
                  <span class="username">{{ userStore.userInfo?.name || userStore.userInfo?.username }}</span>
                  <span class="role-tag">{{ getRoleName(userStore.userInfo?.role || userStore.userInfo?.user_type) }}</span>
                </div>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="user-dropdown">
                  <div class="dropdown-header">
                    <p>已登录为</p>
                    <strong>{{ userStore.userInfo?.username }}</strong>
                  </div>
                  <el-dropdown-item divided command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  
                  <el-dropdown-item divided command="logout" class="danger-item">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 主内容 -->
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade-slide" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 通知抽屉 -->
    <el-drawer
      v-model="notificationDrawer"
      title="系统通知"
      direction="rtl"
      size="380px"
      class="notification-drawer"
    >
      <div class="notification-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-item"
          :class="{ unread: !notification.is_read }"
        >
          <div class="notification-icon">
            <div class="icon-bg">
              <el-icon><BellFilled /></el-icon>
            </div>
          </div>
          <div class="notification-body">
            <div class="notification-header">
              <span class="title">{{ notification.title }}</span>
              <span class="time">{{ formatTime(notification.created_at) }}</span>
            </div>
            <div class="notification-content">
              {{ notification.content }}
            </div>
            <div class="notification-actions" v-if="!notification.is_read">
              <el-button
                type="primary"
                link
                size="small"
                @click="markAsRead(notification.id)"
              >
                标记已读
              </el-button>
            </div>
          </div>
        </div>
        
        <div v-if="notifications.length === 0" class="empty-notifications">
          <el-empty description="暂无通知" :image-size="100" />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { getReservationStatsApi, getMyReservationsApi } from '@/api/reservation'
import { getMaintenanceStatsApi } from '@/api/maintenance'
import { getConsumableStats } from '@/api/consumable'
import { BellFilled } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const isCollapse = ref(false)
const notificationDrawer = ref(false)
const notifications = ref([])
const notificationCount = ref(0)

// 计算属性
const activeMenu = computed(() => {
  const { path } = route
  return path
})

const breadcrumbList = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta.title
  }))
})

const menuRoutes = computed(() => {
  const routes = router.getRoutes()
  const mainRoute = routes.find(route => route.path === '/')
  
  if (!mainRoute || !mainRoute.children) return []
  
  return mainRoute.children.filter(route => {
    // 过滤掉不需要在菜单中显示的路由
    if (!route.meta || !route.meta.title || !route.meta.icon) return false
    
    // 检查权限
    if (route.meta.roles && route.meta.roles.length > 0) {
      return userStore.hasRole(route.meta.roles)
    }
    
    return true
  })
})

// 方法
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 生成完整路由路径（用于侧边栏跳转）
const fullPath = (parentPath, childPath) => {
  const segments = [parentPath, childPath].filter(Boolean)
  const path = '/' + segments.join('/')
  return path.replace(/\/+/, '/')
}

const getRoleName = (role) => {
  const roles = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return roles[role] || role
}

const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    userStore.logout().then(() => {
      router.push('/login')
    })
  })
}

const showNotifications = () => {
  notificationDrawer.value = true
  loadNotifications()
}

const loadNotifications = async () => {
  try {
    const role = userStore.userInfo?.role || userStore.userInfo?.user_type
    const list = []
    if (['admin', 'teacher'].includes(role)) {
      try {
        const [resStats, maintStats, consStats] = await Promise.all([
          getReservationStatsApi({}).catch(() => ({})),
          getMaintenanceStatsApi({}).catch(() => ({})),
          getConsumableStats().catch(() => ({}))
        ])
        
        if (resStats?.code === 200) {
          const dist = resStats.data?.status_distribution || {}
          const pending = dist.pending || 0
          if (pending > 0) list.push({ id: 'pending-resv', title: `待审核预约`, content: `有 ${pending} 条预约待审核`, is_read: false, created_at: new Date().toISOString() })
        }
        if (maintStats?.code === 200) {
          const inProgress = maintStats.data?.inProgress || 0
          if (inProgress > 0) list.push({ id: 'maint-ip', title: `设备维修`, content: `有 ${inProgress} 台设备正在维修中`, is_read: false, created_at: new Date().toISOString() })
        }
        if (consStats?.code === 200) {
          const low = consStats.data?.lowStock || 0
          if (low > 0) list.push({ id: 'cons-low', title: `耗材库存预警`, content: `有 ${low} 种耗材库存不足`, is_read: false, created_at: new Date().toISOString() })
        }
      } catch (e) {
        console.error('Fetch stats error', e)
      }
    } else {
      try {
        const myRes = await getMyReservationsApi({ page: 1, page_size: 200 }).catch(() => ({}))
        if (myRes?.code === 200) {
          const arr = myRes.data?.list || []
          const now = dayjs()
          const upcoming = arr.filter(r => {
            const date = r.reservation_date
            const start = r.start_time || '00:00:00'
            const dt = dayjs(`${date} ${start}`)
            return dt.isAfter(now) && dt.diff(now, 'hour') <= 48 && ['pending', 'confirmed'].includes(r.status)
          })
          if (upcoming.length > 0) list.push({ id: 'my-upcoming', title: `近期预约`, content: `未来48小时内有 ${upcoming.length} 条预约`, is_read: false, created_at: new Date().toISOString() })
        }
      } catch (e) {
        console.error('Fetch my reservations error', e)
      }
    }
    notifications.value = list
    notificationCount.value = notifications.value.filter(n => !n.is_read).length
  } catch (e) {
    notifications.value = []
    notificationCount.value = 0
  }
}

const markAsRead = async (notificationId) => {
  const notification = notifications.value.find(n => n.id === notificationId)
  if (notification) {
    notification.is_read = true
    notificationCount.value = notifications.value.filter(n => !n.is_read).length
  }
}

const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// 生命周期
onMounted(() => {
  loadNotifications()
})

// 监听路由变化，移动端自动收起侧边栏
watch(() => route.path, () => {
  if (window.innerWidth < 768) {
    isCollapse.value = true
  }
})
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  width: 100vw;
  background-color: var(--background-base);
  overflow: hidden;
}

.layout-container {
  height: 100%;
}

.sidebar {
  height: 100%;
  background-color: #fff;
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.02);

  .logo {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    border-bottom: 1px solid var(--border-light);
    
    img {
      height: 32px;
      width: auto;
    }
    
    .title {
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary);
      white-space: nowrap;
      background: linear-gradient(120deg, var(--primary-color), var(--primary-dark));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  }
  
  .sidebar-menu {
    border-right: none;
    flex: 1;
    
    :deep(.el-menu-item), :deep(.el-sub-menu__title) {
      height: 50px;
      margin: 4px 8px;
      border-radius: 8px;
      
      &:hover {
        background-color: var(--background-base);
      }
      
      &.is-active {
        background-color: var(--primary-color);
        color: #fff;
        font-weight: 500;
        
        .el-icon {
          color: #fff;
        }
      }
    }
  }
}

.content-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.header {
  height: 64px;
  background-color: #fff;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
  z-index: 9;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .collapse-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      cursor: pointer;
      color: var(--text-regular);
      transition: all 0.3s;
      
      &:hover {
        background-color: var(--background-base);
        color: var(--primary-color);
      }
    }
    
    .breadcrumb {
      font-size: 14px;
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 24px;
    
    .action-item {
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      cursor: pointer;
      color: var(--text-regular);
      transition: all 0.3s;
      
      &:hover {
        background-color: var(--background-base);
        color: var(--primary-color);
      }
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 24px;
      transition: all 0.3s;
      
      &:hover {
        background-color: var(--background-base);
      }
      
      .user-avatar {
        background-color: var(--primary-color);
        color: #fff;
        font-weight: 600;
      }
      
      .user-details {
        display: flex;
        flex-direction: column;
        line-height: 1.2;
        
        .username {
          font-size: 14px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .role-tag {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
      
      .dropdown-icon {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
  }
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: var(--background-base);
}

// 动画效果
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

// 下拉菜单样式
.user-dropdown {
  padding: 8px;
  
  .dropdown-header {
    padding: 12px 16px;
    
    p {
      margin: 0;
      font-size: 12px;
      color: var(--text-secondary);
    }
    
    strong {
      font-size: 16px;
      color: var(--text-primary);
    }
  }
  
  .danger-item {
    color: var(--danger-color);
    
    &:hover {
      color: var(--danger-color);
      background-color: #fef0f0;
    }
  }
}

// 通知列表样式
.notification-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  
  .notification-item {
    display: flex;
    gap: 16px;
    padding: 16px;
    border-radius: 12px;
    background-color: var(--background-light);
    transition: all 0.3s;
    border: 1px solid transparent;
    
    &:hover {
      background-color: #fff;
      box-shadow: var(--shadow-sm);
      border-color: var(--border-light);
    }
    
    &.unread {
      background-color: #eff6ff;
      
      .notification-icon .icon-bg {
        background-color: var(--primary-color);
        color: #fff;
      }
    }
    
    .notification-icon {
      flex-shrink: 0;
      
      .icon-bg {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background-color: var(--border-light);
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
      }
    }
    
    .notification-body {
      flex: 1;
      
      .notification-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        
        .title {
          font-weight: 600;
          font-size: 15px;
          color: var(--text-primary);
        }
        
        .time {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
      
      .notification-content {
        font-size: 14px;
        color: var(--text-regular);
        line-height: 1.5;
        margin-bottom: 8px;
      }
      
      .notification-actions {
        display: flex;
        justify-content: flex-end;
      }
    }
  }
}
</style>
