<template>
  <div class="statistics-overview">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon lab-icon">
              <el-icon><House /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalLabs }}</div>
              <div class="stat-label">实验室总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon equipment-icon">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalEquipment }}</div>
              <div class="stat-label">设备总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon user-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalUsers }}</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon reservation-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalReservations }}</div>
              <div class="stat-label">预约总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>预约趋势</span>
          </template>
          <div ref="reservationTrendChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>实验室使用率</span>
          </template>
          <div ref="labUsageChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>设备状态分布</span>
          </template>
          <div ref="equipmentStatusChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>用户类型分布</span>
          </template>
          <div ref="userTypeChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近活动 -->
    <el-card class="recent-activities">
      <template #header>
        <span>最近活动</span>
      </template>
      
      <el-timeline>
        <el-timeline-item
          v-for="activity in recentActivities"
          :key="activity.id"
          :timestamp="activity.timestamp"
          :type="activity.type"
        >
          {{ activity.content }}
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { House, Monitor, User, Calendar } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getReservationStatsApi } from '@/api/reservation'
import { getEquipmentStatisticsApi } from '@/api/equipment'
import { getMaintenanceStatsApi } from '@/api/maintenance'
import { getLabsApi } from '@/api/lab'
import { getUsersApi } from '@/api/user'

const reservationTrendChart = ref()
const labUsageChart = ref()
const equipmentStatusChart = ref()
const userTypeChart = ref()

const stats = reactive({
  totalLabs: 0,
  totalEquipment: 0,
  totalUsers: 0,
  totalReservations: 0
})

const recentActivities = ref([])
const users = ref([])

const loadStats = async () => {
  try {
    const [resStats, eqStats, mStats, labsRes, usersRes] = await Promise.all([
      getReservationStatsApi({}),
      getEquipmentStatisticsApi(),
      getMaintenanceStatsApi({}),
      getLabsApi({ page: 1, page_size: 1 }),
      getUsersApi({ page: 1, page_size: 1000 })
    ])
    const totalReservations = resStats.code === 200 ? (resStats.data.total_reservations || 0) : 0
    Object.assign(stats, {
      totalLabs: labsRes.code === 200 ? (labsRes?.data?.total || 0) : 0,
      totalEquipment: eqStats.code === 200 ? ((eqStats?.data?.total || eqStats?.data?.count || 0)) : 0,
      totalUsers: usersRes.code === 200 ? (usersRes?.data?.total || 0) : 0,
      totalReservations
    })
    const daily = resStats.code === 200 ? (resStats.data.daily_trend || resStats.data.by_date || []) : []
    const labDist = resStats.code === 200 ? (resStats.data.laboratory_distribution || resStats.data.by_laboratory || []) : []
    const eqDist = eqStats.code === 200 ? (eqStats.data || {}) : {}
    users.value = usersRes.code === 200 ? (usersRes?.data?.list || []) : []
    nextTick(() => {
      initReservationTrendChart(daily)
      initLabUsageChart(labDist)
      initEquipmentStatusChart(eqDist)
      initUserTypeChart(users.value)
    })
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadRecentActivities = async () => {
  try {
    const m = await getMaintenanceStatsApi({})
    recentActivities.value = m.code === 200 ? [
      {
        id: 1,
        content: `本月维修 ${m.data.thisMonth} 条`,
        timestamp: new Date().toISOString().slice(0,16).replace('T',' '),
        type: 'warning'
      }
    ] : []
  } catch (error) {
    console.error('加载最近活动失败:', error)
  }
}

const initReservationTrendChart = (daily) => {
  const chart = echarts.init(reservationTrendChart.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: { type: 'category', data: (daily || []).map(d => d.date) },
    yAxis: {
      type: 'value'
    },
    series: [{ data: (daily || []).map(d => d.count), type: 'line', smooth: true, itemStyle: { color: '#409EFF' } }]
  }
  chart.setOption(option)
}

const initLabUsageChart = (dist) => {
  const chart = echarts.init(labUsageChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}% ({d}%)'
    },
    series: [{
      name: '使用率',
      type: 'pie',
      radius: ['40%', '70%'],
      data: (dist || []).map(d => ({ value: d.reservation_count || d.count, name: d.laboratory_name })),
      itemStyle: {
        color: function(params) {
          const colors = ['#67C23A', '#E6A23C', '#F56C6C']
          return colors[params.dataIndex]
        }
      }
    }]
  }
  chart.setOption(option)
}

const initEquipmentStatusChart = (eqStats) => {
  const chart = echarts.init(equipmentStatusChart.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    series: [{
      type: 'pie',
      radius: '60%',
      data: [
        { value: eqStats.available || 0, name: '可用' },
        { value: eqStats.in_use || 0, name: '使用中' },
        { value: eqStats.maintenance || 0, name: '维护中' },
        { value: eqStats.damaged || 0, name: '故障' },
        { value: eqStats.retired || 0, name: '退役' }
      ],
      itemStyle: {
        color: function(params) {
          const colors = ['#67C23A', '#E6A23C', '#F56C6C']
          return colors[params.dataIndex]
        }
      }
    }]
  }
  chart.setOption(option)
}

const initUserTypeChart = (list) => {
  const chart = echarts.init(userTypeChart.value)
  const counts = { student: 0, teacher: 0, admin: 0 }
  for (const u of (list || [])) {
    if (u.role && counts.hasOwnProperty(u.role)) counts[u.role] += 1
  }
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ['学生', '教师', '管理员']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: [counts.student, counts.teacher, counts.admin],
      type: 'bar',
      itemStyle: {
        color: '#409EFF'
      }
    }]
  }
  chart.setOption(option)
}

onMounted(async () => {
  await loadStats()
  await loadRecentActivities()
})
</script>

<style scoped>
.statistics-overview {
  padding: 20px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
  color: white;
}

.lab-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.equipment-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.user-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.reservation-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.charts-row {
  margin-bottom: 20px;
}

.recent-activities {
  margin-top: 20px;
}
</style>