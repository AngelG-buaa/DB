<template>
  <div class="dashboard-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <el-card class="welcome-card">
        <div class="welcome-content">
          <div class="welcome-text">
            <h2>欢迎回来，{{ userInfo.real_name || userInfo.username }}！</h2>
            <p>今天是 {{ currentDate }}，{{ welcomeMessage }}</p>
          </div>
          <div class="welcome-avatar">
            <el-avatar :size="60" :src="userInfo.avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardStats.totalReservations }}</div>
                <div class="stat-label">总预约数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon active">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardStats.activeReservations }}</div>
                <div class="stat-label">进行中</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon pending">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dashboardStats.pendingReservations }}</div>
                <div class="stat-label">待审核</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon labs">
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
    <el-row :gutter="20" class="main-content">
      <!-- 我的预约 -->
      <el-col :span="12">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <span>我的预约</span>
              <el-button type="text" @click="goToReservations">查看全部</el-button>
            </div>
          </template>
          
          <div class="reservation-list">
            <div
              v-for="reservation in recentReservations"
              :key="reservation.id"
              class="reservation-item"
            >
              <div class="reservation-info">
                <div class="lab-name">{{ reservation.lab_name }}</div>
                <div class="reservation-time">
                  {{ formatDateTime(reservation.start_time) }} - {{ formatTime(reservation.end_time) }}
                </div>
              </div>
              <div class="reservation-status">
                <el-tag :type="getStatusType(reservation.status)">
                  {{ getStatusText(reservation.status) }}
                </el-tag>
              </div>
            </div>
            
            <div v-if="recentReservations.length === 0" class="empty-state">
              <el-empty description="暂无预约记录" />
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 通知公告 -->
      <el-col :span="12">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <span>通知公告</span>
              <el-button type="text" @click="goToNotifications">查看全部</el-button>
            </div>
          </template>
          
          <div class="notification-list">
            <div
              v-for="notification in recentNotifications"
              :key="notification.id"
              class="notification-item"
              @click="readNotification(notification)"
            >
              <div class="notification-content">
                <div class="notification-title">
                  <span :class="{ 'unread': !notification.is_read }">
                    {{ notification.title }}
                  </span>
                  <el-tag v-if="!notification.is_read" type="danger" size="small">新</el-tag>
                </div>
                <div class="notification-time">
                  {{ formatDateTime(notification.created_at) }}
                </div>
              </div>
            </div>
            
            <div v-if="recentNotifications.length === 0" class="empty-state">
              <el-empty description="暂无通知" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-section">
      <!-- 预约趋势图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>预约趋势</span>
            </div>
          </template>
          
          <div ref="reservationChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <!-- 实验室使用率 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>实验室使用率</span>
            </div>
          </template>
          
          <div ref="usageChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>快速操作</span>
          </div>
        </template>
        
        <div class="action-buttons">
          <el-button
            type="primary"
            size="large"
            @click="goToCreateReservation"
          >
            <el-icon><Plus /></el-icon>
            新建预约
          </el-button>
          
          <el-button
            type="success"
            size="large"
            @click="goToLabs"
          >
            <el-icon><OfficeBuilding /></el-icon>
            浏览实验室
          </el-button>
          
          <el-button
            type="warning"
            size="large"
            @click="goToEquipment"
          >
            <el-icon><Monitor /></el-icon>
            设备管理
          </el-button>
          
          <el-button
            v-if="userInfo.role === 'teacher'"
            type="info"
            size="large"
            @click="goToCourses"
          >
            <el-icon><Reading /></el-icon>
            课程管理
          </el-button>
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
  Reading
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'

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
    // 这里应该调用API获取仪表板数据
    // 暂时使用模拟数据
    dashboardStats.totalReservations = 25
    dashboardStats.activeReservations = 3
    dashboardStats.pendingReservations = 2
    dashboardStats.availableLabs = 15
    
    recentReservations.value = [
      {
        id: 1,
        lab_name: '计算机实验室A',
        start_time: '2024-01-15 14:00:00',
        end_time: '2024-01-15 16:00:00',
        status: 'approved'
      },
      {
        id: 2,
        lab_name: '物理实验室B',
        start_time: '2024-01-16 09:00:00',
        end_time: '2024-01-16 11:00:00',
        status: 'pending'
      },
      {
        id: 3,
        lab_name: '化学实验室C',
        start_time: '2024-01-17 15:00:00',
        end_time: '2024-01-17 17:00:00',
        status: 'completed'
      }
    ]
    
    recentNotifications.value = [
      {
        id: 1,
        title: '实验室设备维护通知',
        created_at: '2024-01-15 10:00:00',
        is_read: false
      },
      {
        id: 2,
        title: '新学期实验室使用规定',
        created_at: '2024-01-14 15:30:00',
        is_read: true
      },
      {
        id: 3,
        title: '系统维护公告',
        created_at: '2024-01-13 09:00:00',
        is_read: true
      }
    ]
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
  }
}

const initCharts = async () => {
  await nextTick()
  
  // 预约趋势图
  if (reservationChartRef.value) {
    const reservationChart = echarts.init(reservationChartRef.value)
    const reservationOption = {
      title: {
        text: '最近7天预约趋势',
        textStyle: {
          fontSize: 14,
          color: '#606266'
        }
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        data: [5, 8, 12, 6, 9, 4, 7],
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#409EFF'
        }
      }]
    }
    reservationChart.setOption(reservationOption)
  }
  
  // 实验室使用率图
  if (usageChartRef.value) {
    const usageChart = echarts.init(usageChartRef.value)
    const usageOption = {
      title: {
        text: '实验室使用率',
        textStyle: {
          fontSize: 14,
          color: '#606266'
        }
      },
      tooltip: {
        trigger: 'item'
      },
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: 35, name: '计算机实验室' },
          { value: 25, name: '物理实验室' },
          { value: 20, name: '化学实验室' },
          { value: 15, name: '生物实验室' },
          { value: 5, name: '其他' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }
    usageChart.setOption(usageOption)
  }
}

const formatDateTime = (dateTime) => {
  return dayjs(dateTime).format('MM-DD HH:mm')
}

const formatTime = (dateTime) => {
  return dayjs(dateTime).format('HH:mm')
}

const getStatusType = (status) => {
  const statusMap = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    completed: 'info',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || '未知'
}

const readNotification = (notification) => {
  if (!notification.is_read) {
    notification.is_read = true
    // 这里应该调用API标记通知为已读
  }
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
  await initCharts()
})
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.welcome-section {
  margin-bottom: 20px;
  
  .welcome-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    
    :deep(.el-card__body) {
      padding: 30px;
    }
    
    .welcome-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .welcome-text {
        h2 {
          margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 600;
        }
        
        p {
          margin: 0;
          font-size: 16px;
          opacity: 0.9;
        }
      }
      
      .welcome-avatar {
        .el-avatar {
          border: 3px solid rgba(255, 255, 255, 0.3);
        }
      }
    }
  }
}

.stats-section {
  margin-bottom: 20px;
  
  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      gap: 16px;
      
      .stat-icon {
        width: 60px;
        height: 60px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        
        &.total {
          background: linear-gradient(135deg, #667eea, #764ba2);
        }
        
        &.active {
          background: linear-gradient(135deg, #f093fb, #f5576c);
        }
        
        &.pending {
          background: linear-gradient(135deg, #ffecd2, #fcb69f);
        }
        
        &.labs {
          background: linear-gradient(135deg, #a8edea, #fed6e3);
        }
      }
      
      .stat-info {
        .stat-value {
          font-size: 28px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }
}

.main-content {
  margin-bottom: 20px;
  
  .content-card {
    height: 400px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
    
.reservation-list,
.notification-list {
  height: 320px;
  overflow-y: auto;
  :deep(.el-card__header) {
    border-bottom: none;
  }
      
      .reservation-item,
      .notification-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
        cursor: pointer;
        
        &:hover {
          background: #f8f9fa;
        }
        
        &:last-child {
          border-bottom: none;
        }
      }
      
      .reservation-info {
        .lab-name {
          font-weight: 600;
          color: #303133;
          margin-bottom: 4px;
        }
        
        .reservation-time {
          font-size: 14px;
          color: #909399;
        }
      }
      
      .notification-content {
        flex: 1;
        
        .notification-title {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 4px;
          
          .unread {
            font-weight: 600;
            color: #303133;
          }
        }
        
        .notification-time {
          font-size: 14px;
          color: #909399;
        }
      }
    }
    
    .empty-state {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

.chart-section {
  margin-bottom: 20px;
  
  .chart-card {
    :deep(.el-card__header) {
      border-bottom: none;
    }
    .card-header {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
    
    .chart-container {
      height: 300px;
    }
  }
}

.quick-actions {
  :deep(.el-card__header) {
    border-bottom: none;
  }
  .card-header {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }
  
  .action-buttons {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    
    .el-button {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .stats-section .el-col {
    margin-bottom: 10px;
  }
  
  .main-content .el-col {
    margin-bottom: 20px;
  }
  
  .chart-section .el-col {
    margin-bottom: 20px;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 10px;
  }
  
  .welcome-content {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .action-buttons {
    justify-content: center;
    
    .el-button {
      flex: 1;
      min-width: 120px;
    }
  }
}
</style>