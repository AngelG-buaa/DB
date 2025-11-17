<template>
  <div class="reservation-approval">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>预约审批</span>
          <div class="header-actions">
            <el-button
              type="success"
              :disabled="!selectedReservations.length"
              @click="handleBatchApproval('已批准')"
            >
              批量通过
            </el-button>
            <el-button
              type="danger"
              :disabled="!selectedReservations.length"
              @click="handleBatchApproval('已拒绝')"
            >
              批量拒绝
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :model="filters" inline>
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="请选择状态" clearable>
              <el-option label="待审批" value="待审批" />
              <el-option label="已批准" value="已批准" />
              <el-option label="已拒绝" value="已拒绝" />
            </el-select>
          </el-form-item>
          <el-form-item label="实验室">
            <el-select v-model="filters.lab_id" placeholder="请选择实验室" clearable>
              <el-option
                v-for="lab in laboratories"
                :key="lab.lab_id"
                :label="lab.lab_name"
                :value="lab.lab_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="预约日期">
            <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadReservations">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 预约列表 -->
      <el-table
        :data="reservations"
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="reservation_id" label="预约ID" width="80" />
        <el-table-column prop="user_name" label="申请人" width="100" />
        <el-table-column prop="lab_name" label="实验室" width="120" />
        <el-table-column prop="reservation_date" label="预约日期" width="120" />
        <el-table-column prop="reservation_time" label="预约时间" width="120" />
        <el-table-column prop="student_number" label="学生人数" width="100" />
        <el-table-column prop="reservation_status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.reservation_status)"
              size="small"
            >
              {{ row.reservation_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="150" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.reservation_status === '待审批'"
              type="success"
              size="small"
              @click="handleApproval(row, '已批准')"
            >
              通过
            </el-button>
            <el-button
              v-if="row.reservation_status === '待审批'"
              type="danger"
              size="small"
              @click="handleApproval(row, '已拒绝')"
            >
              拒绝
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="viewDetails(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadReservations"
          @current-change="loadReservations"
        />
      </div>
    </el-card>
    
    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="预约详情"
      width="600px"
    >
      <div v-if="currentReservation" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="预约ID">
            {{ currentReservation.reservation_id }}
          </el-descriptions-item>
          <el-descriptions-item label="申请人">
            {{ currentReservation.user_name }}
          </el-descriptions-item>
          <el-descriptions-item label="实验室">
            {{ currentReservation.lab_name }}
          </el-descriptions-item>
          <el-descriptions-item label="预约日期">
            {{ currentReservation.reservation_date }}
          </el-descriptions-item>
          <el-descriptions-item label="预约时间">
            {{ currentReservation.reservation_time }}
          </el-descriptions-item>
          <el-descriptions-item label="学生人数">
            {{ currentReservation.student_number }}
          </el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag :type="getStatusType(currentReservation.reservation_status)">
              {{ currentReservation.reservation_status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="申请时间" :span="2">
            {{ currentReservation.created_at }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <div v-if="currentReservation?.reservation_status === '待审批'">
          <el-button
            type="success"
            @click="handleApproval(currentReservation, '已批准')"
          >
            通过
          </el-button>
          <el-button
            type="danger"
            @click="handleApproval(currentReservation, '已拒绝')"
          >
            拒绝
          </el-button>
        </div>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const detailVisible = ref(false)
const reservations = ref([])
const laboratories = ref([])
const selectedReservations = ref([])
const currentReservation = ref(null)

const filters = reactive({
  status: '',
  lab_id: null,
  dateRange: []
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const loadReservations = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取预约列表
    // const params = {
    //   page: pagination.page,
    //   size: pagination.size,
    //   status: filters.status,
    //   lab_id: filters.lab_id,
    //   start_date: filters.dateRange?.[0],
    //   end_date: filters.dateRange?.[1]
    // }
    // const response = await api.getReservationsForApproval(params)
    // reservations.value = response.data.list
    // pagination.total = response.data.total
    
    // 模拟数据
    reservations.value = [
      {
        reservation_id: 1,
        user_name: '张三',
        lab_name: '物理实验室A',
        reservation_date: '2024-01-20',
        reservation_time: '09:00-11:00',
        student_number: 25,
        reservation_status: '待审批',
        created_at: '2024-01-15 14:30:00'
      },
      {
        reservation_id: 2,
        user_name: '李四',
        lab_name: '化学实验室B',
        reservation_date: '2024-01-21',
        reservation_time: '14:00-16:00',
        student_number: 30,
        reservation_status: '已批准',
        created_at: '2024-01-16 10:20:00'
      }
    ]
    pagination.total = 2
  } catch (error) {
    ElMessage.error('加载预约列表失败')
  } finally {
    loading.value = false
  }
}

const loadLaboratories = async () => {
  try {
    // TODO: 调用API获取实验室列表
    // const response = await api.getLaboratories()
    // laboratories.value = response.data
    
    // 模拟数据
    laboratories.value = [
      { lab_id: 1, lab_name: '物理实验室A' },
      { lab_id: 2, lab_name: '化学实验室B' },
      { lab_id: 3, lab_name: '生物实验室C' }
    ]
  } catch (error) {
    ElMessage.error('加载实验室列表失败')
  }
}

const handleSelectionChange = (selection) => {
  selectedReservations.value = selection
}

const handleApproval = async (reservation, status) => {
  const action = status === '已批准' ? '通过' : '拒绝'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}这个预约申请吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API更新预约状态
    // await api.updateReservationStatus(reservation.reservation_id, status)
    
    ElMessage.success(`预约${action}成功`)
    detailVisible.value = false
    loadReservations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`操作失败，请重试`)
    }
  }
}

const handleBatchApproval = async (status) => {
  const action = status === '已批准' ? '通过' : '拒绝'
  
  try {
    await ElMessageBox.confirm(
      `确定要批量${action}选中的 ${selectedReservations.value.length} 个预约申请吗？`,
      '确认批量操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const ids = selectedReservations.value.map(item => item.reservation_id)
    
    // TODO: 调用API批量更新预约状态
    // await api.batchUpdateReservationStatus(ids, status)
    
    ElMessage.success(`批量${action}成功`)
    loadReservations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`批量操作失败，请重试`)
    }
  }
}

const viewDetails = (reservation) => {
  currentReservation.value = reservation
  detailVisible.value = true
}

const getStatusType = (status) => {
  const statusMap = {
    '待审批': 'warning',
    '已批准': 'success',
    '已拒绝': 'danger'
  }
  return statusMap[status] || 'info'
}

const resetFilters = () => {
  Object.assign(filters, {
    status: '',
    lab_id: null,
    dateRange: []
  })
  loadReservations()
}

onMounted(() => {
  loadReservations()
  loadLaboratories()
})
</script>

<style scoped>
.reservation-approval {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.detail-content {
  padding: 20px 0;
}
</style>