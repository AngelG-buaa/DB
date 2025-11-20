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
            <span>设备类型分布</span>
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
            <span>设备使用频率</span>
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
        <el-table-column prop="total_equipment" label="设备总数" width="100" />
        <el-table-column prop="normal_count" label="正常" width="80" />
        <el-table-column prop="maintenance_count" label="维护中" width="80" />
        <el-table-column prop="broken_count" label="故障" width="80" />
        <el-table-column prop="normal_rate" label="正常率" width="80">
          <template #default="{ row }">
            <el-tag :type="row.normal_rate >= 90 ? 'success' : row.normal_rate >= 80 ? 'warning' : 'danger'">
              {{ row.normal_rate }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="avg_usage" label="平均使用率" width="100">
          <template #default="{ row }">
            {{ row.avg_usage }}%
          </template>
        </el-table-column>
        <el-table-column prop="maintenance_cost" label="维护成本" width="100">
          <template #default="{ row }">
            ¥{{ row.maintenance_cost }}
          </template>
        </el-table-column>
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

const statusChart = ref()
const typeChart = ref()
const labEquipmentChart = ref()
const usageFrequencyChart = ref()
const maintenanceTrendChart = ref()

const laboratories = ref([])
const detailData = ref([])

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
      equipmentStats.normal = dist.available || 0
      equipmentStats.maintenance = dist.maintenance || 0
      equipmentStats.broken = dist.damaged || 0
      nextTick(() => {
        initStatusChart()
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
        total_equipment: i.equipment_count,
        normal_count: 0,
        maintenance_count: 0,
        broken_count: 0,
        normal_rate: 0,
        avg_usage: 0,
        maintenance_cost: 0
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
  const option = {
    tooltip: {
      trigger: 'item'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 35, name: '显微镜' },
        { value: 28, name: '计算机' },
        { value: 25, name: '实验台' },
        { value: 20, name: '测量仪器' },
        { value: 20, name: '其他设备' }
      ],
      itemStyle: {
        color: function(params) {
          const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
          return colors[params.dataIndex]
        }
      }
    }]
  }
  chart.setOption(option)
}

const initLabEquipmentChart = () => {
  const chart = echarts.init(labEquipmentChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ['物理实验室A', '化学实验室B', '生物实验室C', '计算机实验室D']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: [35, 42, 28, 23],
      type: 'bar',
      itemStyle: {
        color: '#409EFF'
      }
    }]
  }
  chart.setOption(option)
}

const initUsageFrequencyChart = () => {
  const chart = echarts.init(usageFrequencyChart.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['高频使用', '中频使用', '低频使用', '闲置']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: [45, 38, 25, 20],
      type: 'bar',
      itemStyle: {
        color: function(params) {
          const colors = ['#67C23A', '#409EFF', '#E6A23C', '#F56C6C']
          return colors[params.dataIndex]
        }
      }
    }]
  }
  chart.setOption(option)
}

const initMaintenanceTrendChart = () => {
  const chart = echarts.init(maintenanceTrendChart.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['维护次数', '维护成本']
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: [
      {
        type: 'value',
        name: '维护次数',
        position: 'left'
      },
      {
        type: 'value',
        name: '维护成本(元)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '维护次数',
        type: 'bar',
        data: [12, 8, 15, 10, 18, 14],
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '维护成本',
        type: 'line',
        yAxisIndex: 1,
        data: [15000, 12000, 18000, 14000, 22000, 16000],
        itemStyle: {
          color: '#E6A23C'
        }
      }
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

.total-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.normal-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.maintenance-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.broken-icon {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
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

.maintenance-trend-card {
  margin-bottom: 20px;
}

.table-card {
  margin-top: 20px;
}
</style>