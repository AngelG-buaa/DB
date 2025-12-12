<template>
  <div class="dashboard-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <el-card class="welcome-card" shadow="hover">
        <div class="welcome-content">
          <div class="welcome-text">
            <h2>欢迎回来，{{ userInfo.name || userInfo.username }}！</h2>
            <p>今天是 {{ currentDate }}，{{ welcomeMessage }}</p>
          </div>
          <div class="welcome-avatar">
            <el-avatar :size="72" :src="userInfo.avatar" class="user-avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="24">
        <el-col :xs="24" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon-wrapper total">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardStats.totalReservations }}</div>
                <div class="stat-label">总预约数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon-wrapper active">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardStats.activeReservations }}</div>
                <div class="stat-label">进行中</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon-wrapper pending">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardStats.pendingReservations }}</div>
                <div class="stat-label">待审核</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon-wrapper labs">
                <el-icon><OfficeBuilding /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardStats.availableLabs }}</div>
                <div class="stat-label">可用实验室</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 主要内容区域 -->
    <el-row :gutter="24" class="main-content">
      <!-- 我的预约 -->
      <el-col :xs="24" :lg="12">
        <el-card class="content-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon class="header-icon"><Calendar /></el-icon>
                <span>我的预约</span>
              </div>
              <el-button link type="primary" @click="goToReservations">查看全部</el-button>
            </div>
          </template>
          
          <div class="list-container">
            <div
              v-for="reservation in recentReservations"
              :key="reservation.id"
              class="list-item"
            >
              <div class="item-main">
                <div class="item-title">{{ reservation.lab_name }}</div>
                <div class="item-meta">
                  <el-icon><Clock /></el-icon>
                  {{ formatDateTimeFromParts(reservation.reservation_date, reservation.start_time) }} - {{ formatTimeFromParts(reservation.reservation_date, reservation.end_time) }}
                </div>
              </div>
              <div class="item-status">
                <el-tag :type="getStatusType(reservation.status)" effect="light" round size="small">
                  {{ getStatusText(reservation.status) }}
                </el-tag>
              </div>
            </div>
            
            <div v-if="recentReservations.length === 0" class="empty-state">
              <el-empty description="暂无预约记录" :image-size="100" />
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 通知公告 -->
      <el-col :xs="24" :lg="12">
        <el-card class="content-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon class="header-icon"><Bell /></el-icon>
                <span>通知公告</span>
              </div>
              <el-button link type="primary" @click="goToNotifications">查看全部</el-button>
            </div>
          </template>
          
          <div class="list-container">
            <div
              v-for="notification in recentNotifications"
              :key="notification.id"
              class="list-item notification-item"
              @click="readNotification(notification)"
            >
              <div class="item-icon">
                <div class="dot" :class="{ 'unread': !notification.is_read }"></div>
              </div>
              <div class="item-main">
                <div class="item-title" :class="{ 'unread-text': !notification.is_read }">
                  {{ notification.title }}
                </div>
                <div class="item-meta">
                  {{ formatDateTime(notification.created_at) }}
                </div>
              </div>
              <div class="item-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
            
            <div v-if="recentNotifications.length === 0" class="empty-state">
              <el-empty description="暂无通知" :image-size="100" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="24" class="chart-section">
      <!-- 预约趋势图 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon class="header-icon"><TrendCharts /></el-icon>
                <span>预约趋势</span>
              </div>
            </div>
          </template>
          
          <div ref="reservationChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- 实验室使用率 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon class="header-icon"><PieChart /></el-icon>
                <span>实验室使用率</span>
              </div>
            </div>
          </template>
          
          <div ref="usageChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <el-icon class="header-icon"><Operation /></el-icon>
              <span>快速操作</span>
            </div>
          </div>
        </template>
        
        <div class="action-buttons">
          <div class="action-item" @click="goToCreateReservation">
            <div class="action-icon primary">
              <el-icon><Plus /></el-icon>
            </div>
            <span class="action-text">新建预约</span>
          </div>
          
          <div class="action-item" @click="goToLabs">
            <div class="action-icon success">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <span class="action-text">浏览实验室</span>
          </div>
          
          <div class="action-item" @click="goToEquipment">
            <div class="action-icon warning">
              <el-icon><Monitor /></el-icon>
            </div>
            <span class="action-text">设备管理</span>
          </div>
          
          <div class="action-item" v-if="userInfo.role === 'teacher'" @click="goToCourses">
            <div class="action-icon info">
              <el-icon><Reading /></el-icon>
            </div>
            <span class="action-text">课程管理</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User,
  Calendar,
  Clock,
  Warning,
  OfficeBuilding,
  Plus,
  Monitor,
  Reading,
  Bell,
  ArrowRight,
  TrendCharts,
  PieChart,
  Operation
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'
import { getReservationStatsApi, getMyReservationsApi } from '@/api/reservation'
import { getMaintenanceStatsApi } from '@/api/maintenance'
import { getConsumableStats } from '@/api/consumable'
import { getLabsApi } from '@/api/lab'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const reservationChartRef = ref()
const usageChartRef = ref()

const dashboardStats = reactive({
  totalReservations: 0,
  activeReservations: 0,
  pendingReservations: 0,
  availableLabs: 0
})

const dashboardRaw = reactive({ byDate: [], byLaboratory: [] })

const recentReservations = ref([])
const recentNotifications = ref([])

// 计算属性
const userInfo = computed(() => userStore.userInfo)

const currentDate = computed(() => {
  return dayjs().format('YYYY年MM月DD日')
})

const welcomeMessage = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了，注意休息'
  if (hour < 12) return '早上好，新的一天开始了'
  if (hour < 18) return '下午好，工作顺利'
  return '晚上好，辛苦了'
})

// 方法
const loadDashboardData = async () => {
  try {
    const role = userInfo.value?.role
    if (['admin', 'teacher'].includes(role)) {
      const statsRes = await getReservationStatsApi()
      if (statsRes.code === 200) {
        const d = statsRes.data || {}
        const dist = d.status_distribution || {}
        dashboardStats.totalReservations = d.total_reservations || 0
        dashboardStats.activeReservations = (dist.confirmed || 0)
        dashboardStats.pendingReservations = dist.pending || 0
        dashboardRaw.byDate = d.by_date || d.daily_trend || []
        dashboardRaw.byLaboratory = d.by_laboratory || d.laboratory_distribution || []
      }
    }
    const labsRes = await getLabsApi({ page: 1, page_size: 1, status: 'available' })
    if (labsRes.code === 200) {
      dashboardStats.availableLabs = labsRes.data.total || (Array.isArray(labsRes.data) ? labsRes.data.length : 0)
    }
    const myRes = await getMyReservationsApi({ page: 1, page_size: 5 })
    if (myRes.code === 200) {
      const list = myRes.data.list || []
      recentReservations.value = list.map(r => ({
        id: r.id,
        lab_name: r.laboratory?.name || '',
        reservation_date: r.reservation_date,
        start_time: r.start_time,
        end_time: r.end_time,
        status: r.status
      }))
    }
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
  }
}

const loadDerivedNotifications = async () => {
  try {
    const role = userInfo.value?.role
    const notifications = []
    if (['admin', 'teacher'].includes(role)) {
      const [resStats, maintStats, consStats] = await Promise.all([
        getReservationStatsApi({}),
        getMaintenanceStatsApi({}),
        getConsumableStats()
      ])
      if (resStats.code === 200) {
        const dist = resStats.data?.status_distribution || {}
        const pending = dist.pending || 0
        if (pending > 0) notifications.push({ id: 'pending-resv', title: `待审核预约 ${pending} 条`, is_read: false, created_at: new Date().toISOString() })
      }
      if (maintStats.code === 200) {
        const inProgress = maintStats.data?.inProgress || 0
        if (inProgress > 0) notifications.push({ id: 'maint-ip', title: `设备维修进行中 ${inProgress} 条`, is_read: false, created_at: new Date().toISOString() })
      }
      if (consStats.code === 200) {
        const low = consStats.data?.lowStock || 0
        if (low > 0) notifications.push({ id: 'cons-low', title: `耗材低库存 ${low} 项`, is_read: false, created_at: new Date().toISOString() })
      }
    } else {
      const myRes = await getMyReservationsApi({ page: 1, page_size: 200 })
      if (myRes.code === 200) {
        const list = myRes.data?.list || []
        const now = dayjs()
        const upcoming = list.filter(r => {
          const date = r.reservation_date
          const start = r.start_time || '00:00:00'
          const dt = dayjs(`${date} ${start}`)
          return dt.isAfter(now) && dt.diff(now, 'hour') <= 48 && ['pending', 'confirmed'].includes(r.status)
        })
        if (upcoming.length > 0) {
          notifications.push({ id: 'my-upcoming', title: `未来48小时内有 ${upcoming.length} 条预约`, is_read: false, created_at: new Date().toISOString() })
        }
      }
    }
    recentNotifications.value = notifications
  } catch (error) {
    recentNotifications.value = []
  }
}

const initCharts = async () => {
  await nextTick()
  
  // 预约趋势图
  if (reservationChartRef.value) {
    const reservationChart = echarts.init(reservationChartRef.value)
    const last7 = (dashboardRaw.byDate || []).slice(-7)
    const x = last7.map(i => dayjs(i.date).format('MM-DD'))
    const y = last7.map(i => i.count)
    const reservationOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: x,
        axisLine: { lineStyle: { color: '#E0E6ED' } },
        axisLabel: { color: '#606266' }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { type: 'dashed', color: '#E0E6ED' } }
      },
      series: [{
        data: y,
        type: 'bar',
        barWidth: '40%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }]
    }
    reservationChart.setOption(reservationOption)
    
    window.addEventListener('resize', () => {
      reservationChart.resize()
    })
  }
  
  // 实验室使用率图
  if (usageChartRef.value) {
    const usageChart = echarts.init(usageChartRef.value)
    const data = (dashboardRaw.byLaboratory || []).map(l => ({ value: l.count || l.reservation_count, name: l.laboratory_name }))
    const usageOption = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        bottom: '0%',
        left: 'center',
        itemWidth: 10,
        itemHeight: 10,
        textStyle: {
          fontSize: 12
        }
      },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data
      }]
    }
    usageChart.setOption(usageOption)
    
    window.addEventListener('resize', () => {
      usageChart.resize()
    })
  }
}

const formatDateTime = (dateTime) => {
  return dayjs(dateTime).format('MM-DD HH:mm')
}

const formatTime = (dateTime) => {
  return dayjs(dateTime).format('HH:mm')
}

const normalizeTime = (t) => {
  if (!t) return ''
  const s = String(t)
  return s.length === 5 ? `${s}:00` : s
}

const formatDateTimeFromParts = (dateStr, timeStr) => {
  if (!dateStr || !timeStr) return ''
  const composed = `${dateStr} ${normalizeTime(timeStr)}`
  return dayjs(composed).isValid() ? dayjs(composed).format('MM-DD HH:mm') : ''
}

const formatTimeFromParts = (dateStr, timeStr) => {
  if (!dateStr || !timeStr) return ''
  const composed = `${dateStr} ${normalizeTime(timeStr)}`
  return dayjs(composed).isValid() ? dayjs(composed).format('HH:mm') : ''
}

const getStatusType = (status) => {
  const statusMap = {
    pending: 'warning',
    confirmed: 'success',
    completed: 'info',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待审核',
    confirmed: '已通过',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || '未知'
}

const readNotification = (notification) => {
  // 暂无“标记已读”功能，保留点击行为用于未来扩展
}

// 导航方法
const goToReservations = () => {
  router.push('/reservation/list')
}

const goToNotifications = () => {
  ElMessage.info('请点击右上角铃铛查看通知')
}

const goToCreateReservation = () => {
  router.push('/reservation/create')
}

const goToLabs = () => {
  router.push('/laboratory/list')
}

const goToEquipment = () => {
  router.push('/equipment/list')
}

const goToCourses = () => {
  router.push('/course/list')
}

// 生命周期
onMounted(async () => {
  await loadDashboardData()
  await loadDerivedNotifications()
  await initCharts()
})
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 24px;
  background-color: var(--background-base, #f5f7fa);
  min-height: calc(100vh - 60px);
}

.welcome-section {
  margin-bottom: 24px;
  
  .welcome-card {
    border: none;
    background: linear-gradient(135deg, #409EFF, #337ecc);
    color: white;
    overflow: hidden;
    position: relative;
    
    &::after {
      content: '';
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      background-image: radial-gradient(circle at 90% 10%, rgba(255, 255, 255, 0.1) 0%, transparent 60%),
                        radial-gradient(circle at 10% 90%, rgba(255, 255, 255, 0.1) 0%, transparent 60%);
      pointer-events: none;
    }
    
    :deep(.el-card__body) {
      padding: 32px;
    }
    
    .welcome-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: relative;
      z-index: 1;
      
      .welcome-text {
        h2 {
          margin: 0 0 12px 0;
          font-size: 28px;
          font-weight: 600;
          letter-spacing: 0.5px;
        }
        
        p {
          margin: 0;
          font-size: 16px;
          opacity: 0.9;
          font-weight: 400;
        }
      }
      
      .welcome-avatar {
        .user-avatar {
          border: 4px solid rgba(255, 255, 255, 0.3);
          background: rgba(255, 255, 255, 0.2);
          transition: transform 0.3s ease;
          
          &:hover {
            transform: scale(1.05);
          }
        }
      }
    }
  }
}

.stats-section {
  margin-bottom: 24px;
  
  .stat-card {
    border: none;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
    }
    
    :deep(.el-card__body) {
      padding: 24px;
    }
    
    .stat-content {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .stat-icon-wrapper {
        width: 64px;
        height: 64px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        color: white;
        transition: transform 0.3s ease;
        
        &.total {
          background: linear-gradient(135deg, #667eea, #764ba2);
          box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        }
        
        &.active {
          background: linear-gradient(135deg, #2af598, #009efd);
          box-shadow: 0 8px 16px rgba(42, 245, 152, 0.3);
        }
        
        &.pending {
          background: linear-gradient(135deg, #ff9a9e, #fecfef);
          box-shadow: 0 8px 16px rgba(255, 154, 158, 0.3);
        }
        
        &.labs {
          background: linear-gradient(135deg, #a18cd1, #fbc2eb);
          box-shadow: 0 8px 16px rgba(161, 140, 209, 0.3);
        }
      }
      
      &:hover .stat-icon-wrapper {
        transform: scale(1.1);
      }
      
      .stat-info {
        .stat-value {
          font-size: 32px;
          font-weight: 700;
          color: var(--text-primary, #303133);
          line-height: 1.2;
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 14px;
          color: var(--text-secondary, #909399);
        }
      }
    }
  }
}

.main-content {
  margin-bottom: 24px;
  
  .content-card {
    height: 100%;
    min-height: 450px;
    border: none;
    display: flex;
    flex-direction: column;
    
    :deep(.el-card__header) {
      padding: 20px 24px;
      border-bottom: 1px solid var(--border-light, #ebeef5);
    }
    
    :deep(.el-card__body) {
      flex: 1;
      padding: 0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .header-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary, #303133);
        
        .header-icon {
          font-size: 18px;
          color: var(--primary-color, #409EFF);
        }
      }
    }
    
    .list-container {
      flex: 1;
      overflow-y: auto;
      padding: 12px 0;
      
      .list-item {
        display: flex;
        align-items: center;
        padding: 16px 24px;
        transition: background-color 0.2s ease;
        cursor: pointer;
        
        &:hover {
          background-color: var(--background-light, #f8f9fa);
        }
        
        .item-main {
          flex: 1;
          
          .item-title {
            font-size: 15px;
            font-weight: 500;
            color: var(--text-primary, #303133);
            margin-bottom: 6px;
            
            &.unread-text {
              font-weight: 600;
            }
          }
          
          .item-meta {
            font-size: 13px;
            color: var(--text-secondary, #909399);
            display: flex;
            align-items: center;
            gap: 6px;
          }
        }
        
        &.notification-item {
          gap: 16px;
          
          .item-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            
            .dot {
              width: 8px;
              height: 8px;
              border-radius: 50%;
              background-color: transparent;
              
              &.unread {
                background-color: #f56c6c;
                box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.2);
              }
            }
          }
          
          .item-arrow {
            color: var(--text-placeholder, #c0c4cc);
            font-size: 14px;
          }
        }
      }
      
      .empty-state {
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 40px 0;
      }
    }
  }
}

.chart-section {
  margin-bottom: 24px;
  
  .chart-card {
    border: none;
    margin-bottom: 24px;
    
    :deep(.el-card__header) {
      padding: 20px 24px;
      border-bottom: 1px solid var(--border-light, #ebeef5);
    }
    
    .card-header {
      .header-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary, #303133);
        
        .header-icon {
          font-size: 18px;
          color: var(--warning-color, #E6A23C);
        }
      }
    }
    
    .chart-container {
      height: 320px;
      width: 100%;
    }
  }
}

.quick-actions {
  .card-header {
    .header-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary, #303133);
      
      .header-icon {
        font-size: 18px;
        color: var(--success-color, #67C23A);
      }
    }
  }
  
  .action-buttons {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    padding: 10px 0;
    
    .action-item {
      background-color: var(--background-light, #f8f9fa);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      cursor: pointer;
      transition: all 0.3s ease;
      border: 1px solid transparent;
      
      &:hover {
        transform: translateY(-2px);
        background-color: white;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
        border-color: var(--border-light, #ebeef5);
      }
      
      .action-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        
        &.primary { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
        &.success { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
        &.warning { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
        &.info { background: rgba(144, 147, 153, 0.1); color: #909399; }
      }
      
      .action-text {
        font-size: 16px;
        font-weight: 500;
        color: var(--text-primary, #303133);
      }
    }
  }
}

// 响应式适配
@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }
  
  .welcome-section .welcome-card .welcome-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
    
    .welcome-avatar {
      order: -1;
    }
  }
  
  .stats-section {
    .el-col {
      margin-bottom: 16px;
    }
  }
  
  .main-content {
    .el-col {
      margin-bottom: 16px;
    }
  }
  
  .quick-actions .action-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .quick-actions .action-buttons {
    grid-template-columns: 1fr;
  }
}
</style>
