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

const loadStats = async () => {
  try {
    // TODO: 调用API获取统计数据
    // const response = await api.getOverviewStats()
    // Object.assign(stats, response.data)
    
    // 模拟数据
    Object.assign(stats, {
      totalLabs: 15,
      totalEquipment: 128,
      totalUsers: 456,
      totalReservations: 1234
    })
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadRecentActivities = async () => {
  try {
    // TODO: 调用API获取最近活动
    // const response = await api.getRecentActivities()
    // recentActivities.value = response.data
    
    // 模拟数据
    recentActivities.value = [
      {
        id: 1,
        content: '张三预约了物理实验室A',
        timestamp: '2024-01-15 14:30',
        type: 'primary'
      },
      {
        id: 2,
        content: '新增设备：显微镜 Model-X100',
        timestamp: '2024-01-15 13:20',
        type: 'success'
      },
      {
        id: 3,
        content: '李四的预约被批准',
        timestamp: '2024-01-15 12:10',
        type: 'success'
      },
      {
        id: 4,
        content: '化学实验室B进入维护状态',
        timestamp: '2024-01-15 11:00',
        type: 'warning'
      },
      {
        id: 5,
        content: '新用户王五注册成功',
        timestamp: '2024-01-15 10:30',
        type: 'primary'
      }
    ]
  } catch (error) {
    console.error('加载最近活动失败:', error)
  }
}

const initReservationTrendChart = () => {
  const chart = echarts.init(reservationTrendChart.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: [120, 200, 150, 80, 70, 110, 130],
      type: 'line',
      smooth: true,
      itemStyle: {
        color: '#409EFF'
      }
    }]
  }
  chart.setOption(option)
}

const initLabUsageChart = () => {
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
      data: [
        { value: 35, name: '高使用率' },
        { value: 45, name: '中等使用率' },
        { value: 20, name: '低使用率' }
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

const initEquipmentStatusChart = () => {
  const chart = echarts.init(equipmentStatusChart.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    series: [{
      type: 'pie',
      radius: '60%',
      data: [
        { value: 85, name: '正常' },
        { value: 25, name: '维护中' },
        { value: 18, name: '故障' }
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

const initUserTypeChart = () => {
  const chart = echarts.init(userTypeChart.value)
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
      data: [380, 65, 11],
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
  
  nextTick(() => {
    initReservationTrendChart()
    initLabUsageChart()
    initEquipmentStatusChart()
    initUserTypeChart()
  })
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