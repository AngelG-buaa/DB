<template>
  <div class="reservation-statistics">
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="实验室">
          <el-select
            v-model="filterForm.lab_id"
            placeholder="请选择实验室"
            clearable
            filterable
          >
            <el-option
              v-for="lab in laboratories"
              :key="lab.lab_id"
              :label="lab.lab_name"
              :value="lab.lab_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="预约状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
          >
            <el-option label="待审核" value="Pending" />
            <el-option label="已批准" value="Approved" />
            <el-option label="已拒绝" value="Rejected" />
            <el-option label="已完成" value="Completed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ reservationStats.total }}</div>
              <div class="stat-label">总预约数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon approved-icon">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ reservationStats.approved }}</div>
              <div class="stat-label">已批准</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending-icon">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ reservationStats.pending }}</div>
              <div class="stat-label">待审核</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon rate-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ reservationStats.approvalRate }}%</div>
              <div class="stat-label">批准率</div>
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
            <span>预约状态分布</span>
          </template>
          <div ref="statusChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>每日预约趋势</span>
          </template>
          <div ref="dailyTrendChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>实验室预约排行</span>
          </template>
          <div ref="labRankingChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>时段预约分布</span>
          </template>
          <div ref="timeSlotChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 详细数据表格 -->
    <el-card class="table-card">
      <template #header>
        <span>预约详细统计</span>
      </template>
      
      <el-table :data="detailData" stripe style="width: 100%">
        <el-table-column prop="lab_name" label="实验室" min-width="120" />
        <el-table-column prop="total_reservations" label="总预约数" width="100" />
        <el-table-column prop="approved_count" label="已批准" width="80" />
        <el-table-column prop="pending_count" label="待审核" width="80" />
        <el-table-column prop="rejected_count" label="已拒绝" width="80" />
        <el-table-column prop="completed_count" label="已完成" width="80" />
        <el-table-column prop="approval_rate" label="批准率" width="80">
          <template #default="{ row }">
            {{ row.approval_rate }}%
          </template>
        </el-table-column>
        <el-table-column prop="utilization_rate" label="使用率" width="80">
          <template #default="{ row }">
            {{ row.utilization_rate }}%
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Calendar, Check, Clock, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const statusChart = ref()
const dailyTrendChart = ref()
const labRankingChart = ref()
const timeSlotChart = ref()

const laboratories = ref([])
const detailData = ref([])

const filterForm = reactive({
  dateRange: [],
  lab_id: null,
  status: null
})

const reservationStats = reactive({
  total: 0,
  approved: 0,
  pending: 0,
  rejected: 0,
  completed: 0,
  approvalRate: 0
})

const loadLaboratories = async () => {
  try {
    // TODO: 调用API获取实验室列表
    // const response = await api.getLaboratories()
    // laboratories.value = response.data
    
    // 模拟数据
    laboratories.value = [
      { lab_id: 1, lab_name: '物理实验室A' },
      { lab_id: 2, lab_name: '化学实验室B' },
      { lab_id: 3, lab_name: '生物实验室C' },
      { lab_id: 4, lab_name: '计算机实验室D' }
    ]
  } catch (error) {
    console.error('加载实验室列表失败:', error)
  }
}

const loadReservationStats = async () => {
  try {
    // TODO: 调用API获取预约统计数据
    // const response = await api.getReservationStats(filterForm)
    // Object.assign(reservationStats, response.data)
    
    // 模拟数据
    Object.assign(reservationStats, {
      total: 1234,
      approved: 980,
      pending: 154,
      rejected: 100,
      completed: 850,
      approvalRate: 79.4
    })
  } catch (error) {
    console.error('加载预约统计失败:', error)
  }
}

const loadDetailData = async () => {
  try {
    // TODO: 调用API获取详细统计数据
    // const response = await api.getReservationDetailStats(filterForm)
    // detailData.value = response.data
    
    // 模拟数据
    detailData.value = [
      {
        lab_name: '物理实验室A',
        total_reservations: 350,
        approved_count: 280,
        pending_count: 40,
        rejected_count: 30,
        completed_count: 250,
        approval_rate: 80.0,
        utilization_rate: 75.5
      },
      {
        lab_name: '化学实验室B',
        total_reservations: 420,
        approved_count: 340,
        pending_count: 50,
        rejected_count: 30,
        completed_count: 310,
        approval_rate: 81.0,
        utilization_rate: 82.3
      },
      {
        lab_name: '生物实验室C',
        total_reservations: 280,
        approved_count: 220,
        pending_count: 35,
        rejected_count: 25,
        completed_count: 195,
        approval_rate: 78.6,
        utilization_rate: 68.9
      },
      {
        lab_name: '计算机实验室D',
        total_reservations: 184,
        approved_count: 140,
        pending_count: 29,
        rejected_count: 15,
        completed_count: 125,
        approval_rate: 76.1,
        utilization_rate: 65.2
      }
    ]
  } catch (error) {
    console.error('加载详细统计失败:', error)
  }
}

const initStatusChart = () => {
  const chart = echarts.init(statusChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [{
      name: '预约状态',
      type: 'pie',
      radius: '60%',
      data: [
        { value: reservationStats.approved, name: '已批准' },
        { value: reservationStats.pending, name: '待审核' },
        { value: reservationStats.rejected, name: '已拒绝' },
        { value: reservationStats.completed, name: '已完成' }
      ],
      itemStyle: {
        color: function(params) {
          const colors = ['#67C23A', '#E6A23C', '#F56C6C', '#409EFF']
          return colors[params.dataIndex]
        }
      }
    }]
  }
  chart.setOption(option)
}

const initDailyTrendChart = () => {
  const chart = echarts.init(dailyTrendChart.value)
  const option = {
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
      data: [45, 52, 38, 65, 48, 25, 15],
      type: 'line',
      smooth: true,
      itemStyle: {
        color: '#409EFF'
      },
      areaStyle: {
        color: 'rgba(64, 158, 255, 0.2)'
      }
    }]
  }
  chart.setOption(option)
}

const initLabRankingChart = () => {
  const chart = echarts.init(labRankingChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: ['计算机实验室D', '生物实验室C', '物理实验室A', '化学实验室B']
    },
    series: [{
      data: [184, 280, 350, 420],
      type: 'bar',
      itemStyle: {
        color: '#67C23A'
      }
    }]
  }
  chart.setOption(option)
}

const initTimeSlotChart = () => {
  const chart = echarts.init(timeSlotChart.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['8:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: [25, 45, 35, 65, 55, 40, 20],
      type: 'bar',
      itemStyle: {
        color: '#E6A23C'
      }
    }]
  }
  chart.setOption(option)
}

const handleFilter = async () => {
  await loadReservationStats()
  await loadDetailData()
  
  nextTick(() => {
    initStatusChart()
    initDailyTrendChart()
    initLabRankingChart()
    initTimeSlotChart()
  })
}

const handleReset = () => {
  Object.assign(filterForm, {
    dateRange: [],
    lab_id: null,
    status: null
  })
  handleFilter()
}

onMounted(async () => {
  await loadLaboratories()
  await loadReservationStats()
  await loadDetailData()
  
  nextTick(() => {
    initStatusChart()
    initDailyTrendChart()
    initLabRankingChart()
    initTimeSlotChart()
  })
})
</script>

<style scoped>
.reservation-statistics {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
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

.total-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.approved-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.pending-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.rate-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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

.table-card {
  margin-top: 20px;
}
</style>