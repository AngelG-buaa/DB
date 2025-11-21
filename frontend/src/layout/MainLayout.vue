<template>
  <div class="main-layout">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '240px'" class="sidebar">
        <div class="logo">
          <img src="/logo.svg" alt="Logo" v-if="!isCollapse" />
          <img src="/logo-mini.svg" alt="Logo" v-else />
          <span v-if="!isCollapse" class="title">实验室管理系统</span>
        </div>
        
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
                v-for="child in route.children"
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
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header class="header">
          <div class="header-left">
            <el-button
              type="text"
              @click="toggleCollapse"
              class="collapse-btn"
            >
              <el-icon><Expand v-if="isCollapse" /><Fold v-else /></el-icon>
            </el-button>
            
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
            <el-badge :value="notificationCount" :hidden="notificationCount === 0">
              <el-button type="text" @click="showNotifications">
                <el-icon><Bell /></el-icon>
              </el-button>
            </el-badge>
            
            <!-- 用户菜单 -->
            <el-dropdown @command="handleUserCommand">
              <div class="user-info">
                <el-avatar :size="32" :src="userStore.userInfo?.avatar">
                  {{ userStore.userInfo?.real_name?.charAt(0) }}
                </el-avatar>
                <span class="username">{{ userStore.userInfo?.real_name }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="settings" v-if="userStore.isAdmin">
                    <el-icon><Setting /></el-icon>
                    系统设置
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
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
            <transition name="fade-transform" mode="out-in">
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
      size="400px"
    >
      <div class="notification-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-item"
          :class="{ unread: !notification.is_read }"
        >
          <div class="notification-header">
            <span class="title">{{ notification.title }}</span>
            <span class="time">{{ formatTime(notification.created_at) }}</span>
          </div>
          <div class="notification-content">
            {{ notification.content }}
          </div>
          <div class="notification-actions">
            <el-button
              v-if="!notification.is_read"
              type="text"
              size="small"
              @click="markAsRead(notification.id)"
            >
              标记已读
            </el-button>
          </div>
        </div>
        
        <div v-if="notifications.length === 0" class="empty-notifications">
          <el-empty description="暂无通知" />
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

const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
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
      const [resStats, maintStats, consStats] = await Promise.all([
        getReservationStatsApi({}),
        getMaintenanceStatsApi({}),
        getConsumableStats()
      ])
      if (resStats.code === 200) {
        const dist = resStats.data?.status_distribution || {}
        const pending = dist.pending || 0
        if (pending > 0) list.push({ id: 'pending-resv', title: `待审核预约 ${pending} 条`, content: `待审核预约 ${pending} 条`, is_read: false, created_at: new Date().toISOString() })
      }
      if (maintStats.code === 200) {
        const inProgress = maintStats.data?.inProgress || 0
        if (inProgress > 0) list.push({ id: 'maint-ip', title: `设备维修进行中 ${inProgress} 条`, content: `设备维修进行中 ${inProgress} 条`, is_read: false, created_at: new Date().toISOString() })
      }
      if (consStats.code === 200) {
        const low = consStats.data?.lowStock || 0
        if (low > 0) list.push({ id: 'cons-low', title: `耗材低库存 ${low} 项`, content: `耗材低库存 ${low} 项`, is_read: false, created_at: new Date().toISOString() })
      }
    } else {
      const myRes = await getMyReservationsApi({ page: 1, page_size: 200 })
      if (myRes.code === 200) {
        const arr = myRes.data?.list || []
        const now = dayjs()
        const upcoming = arr.filter(r => {
          const date = r.reservation_date
          const start = r.start_time || '00:00:00'
          const dt = dayjs(`${date} ${start}`)
          return dt.isAfter(now) && dt.diff(now, 'hour') <= 48 && ['pending', 'confirmed'].includes(r.status)
        })
        if (upcoming.length > 0) list.push({ id: 'my-upcoming', title: `未来48小时内有 ${upcoming.length} 条预约`, content: `未来48小时内有 ${upcoming.length} 条预约`, is_read: false, created_at: new Date().toISOString() })
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
  // TODO: 调用API标记通知为已读
  // await markNotificationAsReadApi(notificationId)
  
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

// 监听路由变化，更新面包屑
watch(route, () => {
  // 可以在这里添加一些路由变化的处理逻辑
})
</script>

<style lang="scss" scoped>
.main-layout {
  height: 100vh;
  
  .el-container {
    height: 100%;
  }
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  
  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 60px;
    padding: 0 16px;
    background-color: #2b3a4b;
    
    img {
      height: 32px;
      margin-right: 8px;
    }
    
    .title {
      color: #ffffff;
      font-size: 16px;
      font-weight: 600;
      white-space: nowrap;
    }
  }
  
  .sidebar-menu {
    border: none;
    background-color: #304156;
    
    .el-menu-item,
    .el-sub-menu__title {
      color: #bfcbd9;
      
      &:hover {
        background-color: #263445;
        color: #ffffff;
      }
      
      &.is-active {
        background-color: #409eff;
        color: #ffffff;
      }
    }
    
    .el-sub-menu {
      .el-menu-item {
        background-color: #1f2d3d;
        
        &:hover {
          background-color: #001528;
        }
        
        &.is-active {
          background-color: #409eff;
        }
      }
    }
  }
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  
  .header-left {
    display: flex;
    align-items: center;
    
    .collapse-btn {
      margin-right: 20px;
      font-size: 18px;
    }
    
    .breadcrumb {
      font-size: 14px;
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 8px;
      border-radius: 4px;
      transition: background-color 0.3s;
      
      &:hover {
        background-color: #f5f7fa;
      }
      
      .username {
        font-size: 14px;
        color: #606266;
      }
    }
  }
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.notification-list {
  .notification-item {
    padding: 16px;
    border-bottom: 1px solid #ebeef5;
    
    &.unread {
      background-color: #f0f9ff;
      border-left: 3px solid #409eff;
    }
    
    .notification-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      
      .title {
        font-weight: 600;
        color: #303133;
      }
      
      .time {
        font-size: 12px;
        color: #909399;
      }
    }
    
    .notification-content {
      color: #606266;
      font-size: 14px;
      line-height: 1.5;
      margin-bottom: 8px;
    }
    
    .notification-actions {
      text-align: right;
    }
  }
  
  .empty-notifications {
    padding: 40px 0;
  }
}

// 页面切换动画
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>