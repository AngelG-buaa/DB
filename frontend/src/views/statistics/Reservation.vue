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
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="confirmed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已完成" value="completed" />
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
              <div class="stat-number">{{ reservationStats.confirmed }}</div>
              <div class="stat-label">已通过</div>
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
              <div class="stat-label">通过率</div>
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
        <el-table-column prop="confirmed_count" label="已通过" width="80" />
        <el-table-column prop="pending_count" label="待审核" width="80" />
        <el-table-column prop="cancelled_count" label="已取消" width="80" />
        <el-table-column prop="completed_count" label="已完成" width="80" />
        <el-table-column prop="approval_rate" label="通过率" width="80">
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
import dayjs from 'dayjs'
import { getReservationStatsApi, getReservationCalendarApi } from '@/api/reservation'
import { getLabsApi } from '@/api/lab'

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
  confirmed: 0,
  pending: 0,
  cancelled: 0,
  completed: 0,
  approvalRate: 0
})

const loadLaboratories = async () => {
  try {
    const response = await getLabsApi({ page: 1, page_size: 100 })
    laboratories.value = response.code === 200 ? (response.data.list || []) : []
  } catch (error) {
    console.error('加载实验室列表失败:', error)
  }
}

const loadReservationStats = async () => {
  try {
    const params = {}
    if (filterForm.lab_id) params.laboratory_id = filterForm.lab_id
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.dateRange?.length === 2) {
      params.date_from = filterForm.dateRange[0]
      params.date_to = filterForm.dateRange[1]
    }
    const response = await getReservationStatsApi(params)
    if (response.code === 200) {
      const dist = response.data.status_distribution || {}
      reservationStats.total = response.data.total_reservations || 0
      reservationStats.confirmed = dist.confirmed || 0
      reservationStats.pending = dist.pending || 0
      reservationStats.cancelled = dist.cancelled || 0
      reservationStats.completed = dist.completed || 0
      reservationStats.approvalRate = reservationStats.total > 0 ? ((reservationStats.confirmed / reservationStats.total) * 100).toFixed(1) : 0
      initDailyTrendChart(response.data.daily_trend || response.data.by_date || [])
      initLabRankingChartData(response.data.laboratory_distribution || response.data.by_laboratory || [])
    }
  } catch (error) {
    console.error('加载预约统计失败:', error)
  }
}

const loadDetailData = async () => {
  try {
    const now = new Date()
    const start = filterForm.dateRange?.[0] || dayjs(now).subtract(30, 'day').format('YYYY-MM-DD')
    const end = filterForm.dateRange?.[1] || dayjs(now).format('YYYY-MM-DD')
    const params = { start_date: start, end_date: end }
    if (filterForm.lab_id) params.laboratory_id = filterForm.lab_id
    if (filterForm.status) params.status = filterForm.status
    const res = await getReservationCalendarApi(params)
    const groups = {}
    if (res.code === 200) {
      for (const r of (res.data || [])) {
        const name = r.laboratory_name || '未知实验室'
        if (!groups[name]) {
          groups[name] = { total: 0, confirmed: 0, pending: 0, cancelled: 0, completed: 0 }
        }
        groups[name].total += 1
        const s = r.status
        if (s === 'confirmed') groups[name].confirmed += 1
        else if (s === 'pending') groups[name].pending += 1
        else if (s === 'cancelled') groups[name].cancelled += 1
        else if (s === 'completed') groups[name].completed += 1
      }
    }
    detailData.value = Object.keys(groups).map(name => {
      const g = groups[name]
      const approvalRate = g.total > 0 ? Number(((g.confirmed / g.total) * 100).toFixed(1)) : 0
      return {
        lab_name: name,
        total_reservations: g.total,
        confirmed_count: g.confirmed,
        pending_count: g.pending,
        cancelled_count: g.cancelled,
        completed_count: g.completed,
        approval_rate: approvalRate,
        utilization_rate: 0
      }
    })
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
        { value: reservationStats.confirmed, name: '已通过' },
        { value: reservationStats.pending, name: '待审核' },
        { value: reservationStats.cancelled, name: '已取消' },
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

const initDailyTrendChart = (daily) => {
  const chart = echarts.init(dailyTrendChart.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: { type: 'category', data: (daily || []).map(d => d.date) },
    yAxis: {
      type: 'value'
    },
    series: [{ data: (daily || []).map(d => d.count), type: 'line', smooth: true, itemStyle: { color: '#409EFF' }, areaStyle: { color: 'rgba(64, 158, 255, 0.2)' } }]
  }
  chart.setOption(option)
}

const initLabRankingChartData = (labs) => {
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
    yAxis: { type: 'category', data: (labs || []).map(l => l.laboratory_name) },
    series: [{ data: (labs || []).map(l => l.reservation_count || l.count), type: 'bar', itemStyle: { color: '#67C23A' } }]
  }
  chart.setOption(option)
}

const loadTimeSlotData = async () => {
  const now = new Date()
  const start = filterForm.dateRange?.[0] || dayjs(now).subtract(7, 'day').format('YYYY-MM-DD')
  const end = filterForm.dateRange?.[1] || dayjs(now).format('YYYY-MM-DD')
  const params = { start_date: start, end_date: end }
  if (filterForm.lab_id) params.laboratory_id = filterForm.lab_id
  if (filterForm.status) params.status = filterForm.status
  const res = await getReservationCalendarApi(params)
  const slots = ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00']
  const counts = new Array(slots.length).fill(0)
  if (res.code === 200) {
    for (const r of (res.data || [])) {
      const h = dayjs(r.start_time).format('HH:mm')
      const idx = slots.findIndex(s => h <= s)
      if (idx >= 0) counts[idx] += 1
    }
  }
  const chart = echarts.init(timeSlotChart.value)
  const option = { tooltip: { trigger: 'axis' }, xAxis: { type: 'category', data: slots.map(s => s.replace(':', ':')) }, yAxis: { type: 'value' }, series: [{ data: counts, type: 'bar', itemStyle: { color: '#E6A23C' } }] }
  chart.setOption(option)
}

const handleFilter = async () => {
  await loadReservationStats()
  await loadDetailData()
  
  nextTick(() => {
    initStatusChart()
    loadTimeSlotData()
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
    loadTimeSlotData()
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