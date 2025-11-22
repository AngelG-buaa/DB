<template>
  <div class="equipment-statistics">
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" inline>
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
        <el-form-item label="设备状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
          >
            <el-option label="正常" value="Normal" />
            <el-option label="维护中" value="Maintenance" />
            <el-option label="故障" value="Broken" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备类型">
          <el-input
            v-model="filterForm.equipment_type"
            placeholder="请输入设备类型"
            clearable
            style="width: 200px"
          />
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
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ equipmentStats.total }}</div>
              <div class="stat-label">设备总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon normal-icon">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ equipmentStats.normal }}</div>
              <div class="stat-label">正常设备</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon maintenance-icon">
              <el-icon><Tools /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ equipmentStats.maintenance }}</div>
              <div class="stat-label">维护中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon broken-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ equipmentStats.broken }}</div>
              <div class="stat-label">故障设备</div>
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
            <span>设备状态分布</span>
          </template>
          <div ref="statusChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>实验室设备分布</span>
          </template>
          <div ref="typeChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>实验室设备数量</span>
          </template>
          <div ref="labEquipmentChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>保修到期分布</span>
          </template>
          <div ref="usageFrequencyChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 维护记录趋势 -->
    <el-card class="maintenance-trend-card">
      <template #header>
        <span>设备维护趋势</span>
      </template>
      <div ref="maintenanceTrendChart" style="height: 400px;"></div>
    </el-card>
    
    <!-- 详细数据表格 -->
    <el-card class="table-card">
      <template #header>
        <span>设备详细统计</span>
      </template>
      
      <el-table :data="detailData" stripe style="width: 100%">
        <el-table-column prop="lab_name" label="实验室" min-width="120" />
        <el-table-column prop="total_equipment" label="设备总数" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Monitor, Check, Tools, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getEquipmentStatisticsApi } from '@/api/equipment'
import { getLabsApi } from '@/api/lab'
import { getMaintenanceTrendApi } from '@/api/maintenance'

const statusChart = ref()
const typeChart = ref()
const labEquipmentChart = ref()
const usageFrequencyChart = ref()
const maintenanceTrendChart = ref()

const laboratories = ref([])
const detailData = ref([])
const labDist = ref([])
const warrantySoon = ref([])

const filterForm = reactive({
  lab_id: null,
  status: null,
  equipment_type: ''
})

const equipmentStats = reactive({
  total: 0,
  normal: 0,
  maintenance: 0,
  broken: 0
})

const loadLaboratories = async () => {
  try {
    const response = await getLabsApi({ page: 1, page_size: 100 })
    laboratories.value = response.code === 200 ? (response.data.list || []) : []
  } catch (error) {
    console.error('加载实验室列表失败:', error)
  }
}

const loadEquipmentStats = async () => {
  try {
    const response = await getEquipmentStatisticsApi()
    if (response.code === 200) {
      const d = response.data || {}
      const dist = d.status_distribution || {}
      equipmentStats.total = d.total_equipment || 0
      const aliasSum = (obj, keys) => keys.reduce((s, k) => s + Number(obj[k] || 0), 0)
      equipmentStats.normal = aliasSum(dist, ['available', 'normal', 'Normal', '正常'])
      equipmentStats.maintenance = aliasSum(dist, ['maintenance', 'Maintenance', '维修中'])
      equipmentStats.broken = aliasSum(dist, ['damaged', 'broken', 'Broken', '故障'])
      labDist.value = d.laboratory_distribution || []
      warrantySoon.value = d.warranty_expiring_soon || []
      nextTick(() => {
        initStatusChart()
        initTypeChart()
        initLabEquipmentChart()
        initUsageFrequencyChart()
      })
    }
  } catch (error) {
    console.error('加载设备统计失败:', error)
  }
}

const loadDetailData = async () => {
  try {
    const response = await getEquipmentStatisticsApi()
    if (response.code === 200) {
      const labs = response.data?.laboratory_distribution || []
      detailData.value = labs.map(i => ({
        lab_name: i.laboratory_name,
        total_equipment: i.equipment_count
      }))
    }
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
      name: '设备状态',
      type: 'pie',
      radius: '60%',
      data: [
        { value: equipmentStats.normal, name: '正常' },
        { value: equipmentStats.maintenance, name: '维护中' },
        { value: equipmentStats.broken, name: '故障' }
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

const initTypeChart = () => {
  const chart = echarts.init(typeChart.value)
  const data = (labDist.value || []).map(l => ({ value: l.equipment_count, name: l.laboratory_name }))
  const option = {
    tooltip: { trigger: 'item' },
    series: [{ type: 'pie', radius: ['40%', '70%'], data }]
  }
  chart.setOption(option)
}

const initLabEquipmentChart = () => {
  const chart = echarts.init(labEquipmentChart.value)
  const cats = (labDist.value || []).map(l => l.laboratory_name)
  const vals = (labDist.value || []).map(l => l.equipment_count)
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: cats },
    yAxis: { type: 'value' },
    series: [{ data: vals, type: 'bar', itemStyle: { color: '#409EFF' } }]
  }
  chart.setOption(option)
}

const initUsageFrequencyChart = () => {
  const chart = echarts.init(usageFrequencyChart.value)
  const buckets = { '0-7天': 0, '8-15天': 0, '16-30天': 0 }
  for (const w of (warrantySoon.value || [])) {
    const days = Number(w.days_left || 0)
    if (days <= 7) buckets['0-7天'] += 1
    else if (days <= 15) buckets['8-15天'] += 1
    else buckets['16-30天'] += 1
  }
  const cats = Object.keys(buckets)
  const vals = cats.map(k => buckets[k])
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: cats },
    yAxis: { type: 'value' },
    series: [{ data: vals, type: 'bar', itemStyle: { color: '#67C23A' } }]
  }
  chart.setOption(option)
}

const initMaintenanceTrendChart = async () => {
  const chart = echarts.init(maintenanceTrendChart.value)
  const res = await getMaintenanceTrendApi({ months: 6 })
  const months = res.code === 200 ? (res.data.months || []) : []
  const seriesData = res.code === 200 ? (res.data.series || []) : []
  const counts = seriesData.map(i => i.count)
  const costs = seriesData.map(i => i.total_cost)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['维护次数', '维护成本'] },
    xAxis: { type: 'category', data: months },
    yAxis: [{ type: 'value', name: '维护次数', position: 'left' }, { type: 'value', name: '维护成本(元)', position: 'right' }],
    series: [
      { name: '维护次数', type: 'bar', data: counts, itemStyle: { color: '#409EFF' } },
      { name: '维护成本', type: 'line', yAxisIndex: 1, data: costs, itemStyle: { color: '#E6A23C' } }
    ]
  }
  chart.setOption(option)
}

const handleFilter = async () => {
  await loadEquipmentStats()
  await loadDetailData()
  
  nextTick(() => {
    initStatusChart()
    initTypeChart()
    initLabEquipmentChart()
    initUsageFrequencyChart()
    initMaintenanceTrendChart()
  })
}

const handleReset = () => {
  Object.assign(filterForm, {
    lab_id: null,
    status: null,
    equipment_type: ''
  })
  handleFilter()
}

onMounted(async () => {
  await loadLaboratories()
  await loadEquipmentStats()
  await loadDetailData()
  
  nextTick(() => {
    initStatusChart()
    initTypeChart()
    initLabEquipmentChart()
    initUsageFrequencyChart()
    initMaintenanceTrendChart()
  })
})
</script>

<style scoped>
.equipment-statistics {
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

.total-icon { background: var(--primary-color); }
.normal-icon { background: var(--success-color); }
.maintenance-icon { background: var(--warning-color); }
.broken-icon { background: var(--danger-color); }

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

.maintenance-trend-card {
  margin-bottom: 20px;
}

.table-card {
  margin-top: 20px;
}
</style>