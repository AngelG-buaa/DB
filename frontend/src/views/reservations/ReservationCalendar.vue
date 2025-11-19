<template>
  <div class="reservation-calendar-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>预约日历</span>
          <div class="header-actions">
            <el-button type="primary" @click="goToCreate">
              <el-icon><Plus /></el-icon>
              新建预约
            </el-button>
            <el-button @click="refreshCalendar">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-select
              v-model="filterForm.labId"
              placeholder="选择实验室"
              clearable
              @change="loadCalendarData"
            >
              <el-option label="全部实验室" value="" />
              <el-option
                v-for="lab in labOptions"
                :key="lab.id"
                :label="lab.name"
                :value="lab.id"
              />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select
              v-model="filterForm.status"
              placeholder="预约状态"
              clearable
              @change="loadCalendarData"
            >
              <el-option label="全部状态" value="" />
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
              <el-option label="已取消" value="cancelled" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select
              v-model="filterForm.viewType"
              @change="handleViewTypeChange"
            >
              <el-option label="月视图" value="month" />
              <el-option label="周视图" value="week" />
              <el-option label="日视图" value="day" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-switch
              v-model="filterForm.onlyMine"
              active-text="仅我的预约"
              @change="loadCalendarData"
            />
          </el-col>
        </el-row>
      </div>
      
      <!-- 日历组件 -->
      <div class="calendar-section">
        <el-calendar
          v-model="currentDate"
          :range="calendarRange"
          class="reservation-calendar"
        >
          <template #header="{ date }">
            <div class="calendar-header">
              <el-button-group>
                <el-button @click="goToPrevious">
                  <el-icon><ArrowLeft /></el-icon>
                </el-button>
                <el-button @click="goToToday">今天</el-button>
                <el-button @click="goToNext">
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </el-button-group>
              <span class="current-date">{{ formatHeaderDate(date) }}</span>
            </div>
          </template>
          
          <template #date-cell="{ data }">
            <div class="calendar-cell">
              <div class="cell-date">{{ data.day.split('-').slice(-1)[0] }}</div>
              <div class="cell-reservations">
                <div
                  v-for="reservation in getDateReservations(data.day)"
                  :key="reservation.id"
                  :class="['reservation-item', `status-${reservation.status}`]"
                  @click="showReservationDetail(reservation)"
                >
                  <div class="reservation-time">
                    {{ formatTime(reservation.start_time) }}-{{ formatTime(reservation.end_time) }}
                  </div>
                  <div class="reservation-lab">{{ reservation.lab_name }}</div>
                  <div class="reservation-user" v-if="!filterForm.onlyMine">
                    {{ reservation.user_name }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </el-calendar>
      </div>
      
      <!-- 统计信息 -->
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总预约数" :value="stats.total" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="待审核" :value="stats.pending" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="已通过" :value="stats.approved" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="本月预约" :value="stats.thisMonth" />
          </el-col>
        </el-row>
      </div>
    </el-card>
    
    <!-- 预约详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="预约详情"
      width="600px"
      :before-close="handleDetailClose"
    >
      <div v-if="selectedReservation" class="reservation-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="预约ID">
            {{ selectedReservation.id }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedReservation.status)">
              {{ getStatusText(selectedReservation.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="实验室">
            {{ selectedReservation.lab_name }}
          </el-descriptions-item>
          <el-descriptions-item label="预约人">
            {{ selectedReservation.user_name }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDateTime(selectedReservation.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ formatDateTime(selectedReservation.end_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="使用目的" :span="2">
            {{ selectedReservation.purpose }}
          </el-descriptions-item>
          <el-descriptions-item label="预计人数">
            {{ selectedReservation.expected_people }}人
          </el-descriptions-item>
          <el-descriptions-item label="课程" v-if="selectedReservation.course_name">
            {{ selectedReservation.course_name }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2" v-if="selectedReservation.remarks">
            {{ selectedReservation.remarks }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(selectedReservation.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="审核时间" v-if="selectedReservation.reviewed_at">
            {{ formatDateTime(selectedReservation.reviewed_at) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 操作按钮 -->
        <div class="detail-actions">
          <el-button
            v-if="canEdit(selectedReservation)"
            type="primary"
            @click="editReservation"
          >
            编辑
          </el-button>
          <el-button
            v-if="canCancel(selectedReservation)"
            type="warning"
            @click="cancelReservation"
          >
            取消预约
          </el-button>
          <el-button
            v-if="canApprove(selectedReservation)"
            type="success"
            @click="approveReservation"
          >
            通过
          </el-button>
          <el-button
            v-if="canReject(selectedReservation)"
            type="danger"
            @click="rejectReservation"
          >
            拒绝
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'
import {
  getReservationCalendarApi,
  approveReservationApi,
  rejectReservationApi,
  cancelReservationApi,
  getReservationStatsApi
} from '@/api/reservation'
import { getLabsApi } from '@/api/lab'
import { getLabsApi } from '@/api/lab'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const currentDate = ref(new Date())
const detailDialogVisible = ref(false)
const selectedReservation = ref(null)
const labOptions = ref([])
const reservations = ref([])
const stats = ref({
  total: 0,
  pending: 0,
  approved: 0,
  thisMonth: 0
})

const filterForm = reactive({
  labId: '',
  status: '',
  viewType: 'month',
  onlyMine: false
})

// 计算属性
const userInfo = computed(() => userStore.userInfo)

const calendarRange = computed(() => {
  const start = dayjs(currentDate.value).startOf(filterForm.viewType)
  const end = dayjs(currentDate.value).endOf(filterForm.viewType)
  return [start.toDate(), end.toDate()]
})

// 方法
const loadLabOptions = async () => {
  try {
    const response = await getLabsApi({ page: 1, size: 100 })
    if (response.code === 200) {
      labOptions.value = response.data.list
    }
  } catch (error) {
    console.error('加载实验室选项失败:', error)
  }
}

const loadCalendarData = async () => {
  try {
    const start = dayjs(currentDate.value).startOf(filterForm.viewType).format('YYYY-MM-DD')
    const end = dayjs(currentDate.value).endOf(filterForm.viewType).format('YYYY-MM-DD')
    
    const params = {
      start_date: start,
      end_date: end
    }
    
    if (filterForm.labId) params.lab_id = filterForm.labId
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.onlyMine) params.user_id = userInfo.value.id
    
    const response = await getReservationCalendarApi(params)
    if (response.code === 200) {
      reservations.value = response.data
    }
  } catch (error) {
    console.error('加载日历数据失败:', error)
  }
}

const loadStats = async () => {
  try {
    const params = {}
    if (filterForm.onlyMine) params.user_id = userInfo.value.id
    
    const response = await getReservationStatsApi(params)
    if (response.code === 200) {
      stats.value = response.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const getDateReservations = (date) => {
  return reservations.value.filter(reservation => {
    const reservationDate = dayjs(reservation.start_time).format('YYYY-MM-DD')
    return reservationDate === date
  })
}

const showReservationDetail = (reservation) => {
  selectedReservation.value = reservation
  detailDialogVisible.value = true
}

const handleDetailClose = () => {
  detailDialogVisible.value = false
  selectedReservation.value = null
}

const handleViewTypeChange = () => {
  loadCalendarData()
}

const goToPrevious = () => {
  currentDate.value = dayjs(currentDate.value).subtract(1, filterForm.viewType).toDate()
}

const goToNext = () => {
  currentDate.value = dayjs(currentDate.value).add(1, filterForm.viewType).toDate()
}

const goToToday = () => {
  currentDate.value = new Date()
}

const goToCreate = () => {
  router.push('/reservation/create')
}

const refreshCalendar = () => {
  loadCalendarData()
  loadStats()
}

const editReservation = () => {
  router.push(`/reservation/edit/${selectedReservation.value.id}`)
}

const cancelReservation = async () => {
  try {
    await ElMessageBox.confirm('确定要取消这个预约吗？', '确认取消', {
      type: 'warning'
    })
    
    const response = await cancelReservationApi(selectedReservation.value.id)
    if (response.code === 200) {
      ElMessage.success('预约已取消')
      handleDetailClose()
      loadCalendarData()
      loadStats()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消预约失败:', error)
    }
  }
}

const approveReservation = async () => {
  try {
    const response = await approveReservationApi(selectedReservation.value.id)
    if (response.code === 200) {
      ElMessage.success('预约已通过')
      handleDetailClose()
      loadCalendarData()
      loadStats()
    }
  } catch (error) {
    console.error('通过预约失败:', error)
  }
}

const rejectReservation = async () => {
  try {
    const { value: reason } = await ElMessageBox.prompt('请输入拒绝原因', '拒绝预约', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValidator: (value) => {
        if (!value || value.trim().length < 5) {
          return '拒绝原因不能少于5个字符'
        }
        return true
      }
    })
    
    const response = await rejectReservationApi(selectedReservation.value.id, { reason })
    if (response.code === 200) {
      ElMessage.success('预约已拒绝')
      handleDetailClose()
      loadCalendarData()
      loadStats()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('拒绝预约失败:', error)
    }
  }
}

// 权限检查方法
const canEdit = (reservation) => {
  return reservation.user_id === userInfo.value.id && 
         ['pending', 'approved'].includes(reservation.status)
}

const canCancel = (reservation) => {
  return reservation.user_id === userInfo.value.id && 
         ['pending', 'approved'].includes(reservation.status)
}

const canApprove = (reservation) => {
  return ['admin', 'teacher'].includes(userInfo.value.user_type) && 
         reservation.status === 'pending'
}

const canReject = (reservation) => {
  return ['admin', 'teacher'].includes(userInfo.value.user_type) && 
         reservation.status === 'pending'
}

// 格式化方法
const formatHeaderDate = (date) => {
  return dayjs(date).format('YYYY年MM月')
}

const formatTime = (datetime) => {
  return dayjs(datetime).format('HH:mm')
}

const formatDateTime = (datetime) => {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const statusMap = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info',
    completed: 'success'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    cancelled: '已取消',
    completed: '已完成'
  }
  return statusMap[status] || status
}

// 监听器
watch(currentDate, () => {
  loadCalendarData()
})

// 生命周期
onMounted(() => {
  loadLabOptions()
  loadCalendarData()
  loadStats()
})
</script>

<style lang="scss" scoped>
.reservation-calendar-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  
  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.calendar-section {
  margin-bottom: 20px;
  
  .reservation-calendar {
    :deep(.el-calendar__header) {
      display: none;
    }
    
    :deep(.el-calendar__body) {
      padding: 12px;
    }
  }
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .current-date {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }
}

.calendar-cell {
  height: 120px;
  padding: 4px;
  
  .cell-date {
    font-weight: 600;
    color: #303133;
    margin-bottom: 4px;
  }
  
  .cell-reservations {
    .reservation-item {
      margin-bottom: 2px;
      padding: 2px 4px;
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        opacity: 0.8;
        transform: translateY(-1px);
      }
      
      .reservation-time {
        font-weight: 600;
      }
      
      .reservation-lab,
      .reservation-user {
        font-size: 11px;
        opacity: 0.8;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      
      &.status-pending {
        background: #fdf6ec;
        color: #e6a23c;
        border: 1px solid #f5dab1;
      }
      
      &.status-approved {
        background: #f0f9ff;
        color: #409eff;
        border: 1px solid #b3d8ff;
      }
      
      &.status-rejected {
        background: #fef0f0;
        color: #f56c6c;
        border: 1px solid #fbc4c4;
      }
      
      &.status-cancelled {
        background: #f4f4f5;
        color: #909399;
        border: 1px solid #d3d4d6;
      }
      
      &.status-completed {
        background: #f0f9ff;
        color: #67c23a;
        border: 1px solid #c2e7b0;
      }
    }
  }
}

.stats-section {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.reservation-detail {
  .detail-actions {
    margin-top: 20px;
    text-align: center;
    
    .el-button {
      margin: 0 5px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .reservation-calendar-container {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .filter-section {
    .el-col {
      margin-bottom: 10px;
    }
  }
  
  .calendar-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .calendar-cell {
    height: 80px;
    
    .reservation-item {
      .reservation-lab,
      .reservation-user {
        display: none;
      }
    }
  }
}
</style>