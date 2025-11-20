<template>
  <div class="reservation-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>预约管理</span>
          <el-button
            type="primary"
            @click="goToCreate"
          >
            <el-icon><Plus /></el-icon>
            新建预约
          </el-button>
        </div>
      </template>
      
      <!-- 搜索筛选 -->
      <div class="search-section">
        <el-form
          :model="searchForm"
          :inline="true"
          class="search-form"
        >
          <el-form-item label="实验室">
            <el-select
              v-model="searchForm.labId"
              placeholder="请选择实验室"
              clearable
              style="width: 200px"
            >
              <el-option
                v-for="lab in labOptions"
                :key="lab.id"
                :label="lab.name"
                :value="lab.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="状态">
            <el-select
              v-model="searchForm.status"
              placeholder="请选择状态"
              clearable
              style="width: 150px"
            >
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="预约时间">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="reservationList"
        stripe
        class="reservation-table"
      >
        <el-table-column prop="id" label="预约ID" width="80" />
        
        <el-table-column prop="lab_name" label="实验室" width="150" />
        
        <el-table-column label="预约时间" width="220">
          <template #default="{ row }">
            <div>{{ formatDateTimeFromParts(row.reservation_date, row.start_time) }}</div>
            <div class="text-secondary">至 {{ formatTimeFromParts(row.reservation_date, row.end_time) }}</div>
          </template>
        </el-table-column>
        
        <el-table-column prop="purpose" label="使用目的" min-width="150" show-overflow-tooltip />
        
        <el-table-column label="预约人" width="120">
          <template #default="{ row }">
            <div>{{ row.user_name }}</div>
            <div class="text-secondary">{{ getUserTypeText(row.user_type) }}</div>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewDetail(row)"
            >
              查看
            </el-button>
            
            
            
            <el-dropdown
              v-if="canOperate(row)"
              @command="handleCommand"
            >
              <el-button type="info" size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-if="canApprove(row)"
                    :command="{ action: 'approve', row }"
                  >
                    通过
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="canReject(row)"
                    :command="{ action: 'reject', row }"
                  >
                    拒绝
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="canCancel(row)"
                    :command="{ action: 'cancel', row }"
                  >
                    取消
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="canDelete(row)"
                    :command="{ action: 'delete', row }"
                    divided
                  >
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 预约详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="预约详情"
      width="600px"
    >
      <div v-if="currentReservation" class="reservation-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="预约ID">
            {{ currentReservation.id }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentReservation.status)">
              {{ getStatusText(currentReservation.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="实验室">
            {{ currentReservation.lab_name }}
          </el-descriptions-item>
          <el-descriptions-item label="预约人">
            {{ currentReservation.user_name }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDateTimeFromParts(currentReservation.reservation_date, currentReservation.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ formatDateTimeFromParts(currentReservation.reservation_date, currentReservation.end_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="使用目的" :span="2">
            {{ currentReservation.purpose }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ currentReservation.remarks || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(currentReservation.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(currentReservation.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 审核记录 -->
        <div v-if="currentReservation.approval_records?.length" class="approval-records">
          <h4>审核记录</h4>
          <el-timeline>
            <el-timeline-item
              v-for="record in currentReservation.approval_records"
              :key="record.id"
              :timestamp="formatDateTime(record.created_at)"
              :type="getApprovalType(record.action)"
            >
              <div class="approval-content">
                <div class="approval-action">{{ getApprovalText(record.action) }}</div>
                <div class="approval-user">操作人：{{ record.operator_name }}</div>
                <div v-if="record.remarks" class="approval-remarks">备注：{{ record.remarks }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 审核对话框 -->
    <el-dialog
      v-model="approvalDialogVisible"
      :title="approvalAction === 'approve' ? '通过预约' : '拒绝预约'"
      width="500px"
    >
      <el-form
        ref="approvalFormRef"
        :model="approvalForm"
        :rules="approvalRules"
        label-width="80px"
      >
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="approvalForm.remarks"
            type="textarea"
            :rows="4"
            :placeholder="approvalAction === 'approve' ? '请输入通过原因（可选）' : '请输入拒绝原因'"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="approvalDialogVisible = false">取消</el-button>
          <el-button
            :type="approvalAction === 'approve' ? 'success' : 'danger'"
            :loading="approvalLoading"
            @click="confirmApproval"
          >
            确认{{ approvalAction === 'approve' ? '通过' : '拒绝' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  ArrowDown
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'
import {
  getReservationsApi,
  getReservationByIdApi,
  approveReservationApi,
  rejectReservationApi,
  cancelReservationApi,
  deleteReservationApi
} from '@/api/reservation'
import { getLabsApi } from '@/api/lab'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const reservationList = ref([])
const labOptions = ref([])
const detailDialogVisible = ref(false)
const approvalDialogVisible = ref(false)
const approvalLoading = ref(false)
const currentReservation = ref(null)
const approvalAction = ref('')
const approvalFormRef = ref()

const searchForm = reactive({
  labId: '',
  status: '',
  dateRange: []
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const approvalForm = reactive({
  remarks: ''
})

// 表单验证规则
const approvalRules = {
  remarks: [
    {
      required: true,
      message: '请输入拒绝原因',
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (approvalAction.value === 'reject' && !value) {
          callback(new Error('请输入拒绝原因'))
        } else {
          callback()
        }
      }
    }
  ]
}

// 方法
const loadReservations = async () => {
  try {
    loading.value = true
    
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      laboratory_id: searchForm.labId || undefined,
      status: searchForm.status || undefined,
      date_from: searchForm.dateRange?.[0] || undefined,
      date_to: searchForm.dateRange?.[1] || undefined
    }
    
    const response = await getReservationsApi(params)
    
    if (response.code === 200) {
      reservationList.value = response.data.list
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('加载预约列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadLabOptions = async () => {
  try {
    const response = await getLabsApi({ page: 1, page_size: 100 })
    if (response.code === 200) {
      labOptions.value = response.data.list
    }
  } catch (error) {
    console.error('加载实验室选项失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadReservations()
}

const handleReset = () => {
  searchForm.labId = ''
  searchForm.status = ''
  searchForm.dateRange = []
  pagination.page = 1
  loadReservations()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadReservations()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadReservations()
}

const viewDetail = async (row) => {
  try {
    const response = await getReservationByIdApi(row.id)
    if (response.code === 200) {
      currentReservation.value = response.data
      detailDialogVisible.value = true
    }
  } catch (error) {
    console.error('获取预约详情失败:', error)
  }
}

// 编辑功能已移除

const goToCreate = () => {
  router.push('/reservation/create')
}

const handleCommand = (command) => {
  const { action, row } = command
  
  switch (action) {
    case 'approve':
      showApprovalDialog(row, 'approve')
      break
    case 'reject':
      showApprovalDialog(row, 'reject')
      break
    case 'cancel':
      handleCancel(row)
      break
    case 'delete':
      handleDelete(row)
      break
  }
}

const showApprovalDialog = (row, action) => {
  currentReservation.value = row
  approvalAction.value = action
  approvalForm.remarks = ''
  approvalDialogVisible.value = true
}

const confirmApproval = async () => {
  if (!approvalFormRef.value) return
  
  try {
    await approvalFormRef.value.validate()
    approvalLoading.value = true
    
    const api = approvalAction.value === 'approve' ? approveReservationApi : rejectReservationApi
    const response = await api(currentReservation.value.id, {
      remarks: approvalForm.remarks
    })
    
    if (response.code === 200) {
      ElMessage.success(`预约${approvalAction.value === 'approve' ? '通过' : '拒绝'}成功`)
      approvalDialogVisible.value = false
      loadReservations()
    }
  } catch (error) {
    console.error('审核预约失败:', error)
  } finally {
    approvalLoading.value = false
  }
}

const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消这个预约吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await cancelReservationApi(row.id, {
      remarks: '用户取消'
    })
    
    if (response.code === 200) {
      ElMessage.success('预约取消成功')
      loadReservations()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消预约失败:', error)
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个预约吗？删除后无法恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await deleteReservationApi(row.id)
    
    if (response.code === 200) {
      ElMessage.success('预约删除成功')
      loadReservations()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除预约失败:', error)
    }
  }
}

// 权限判断方法
const canEdit = (row) => {
  const userInfo = userStore.userInfo
  return (
    row.status === 'pending' &&
    (userInfo.user_type === 'admin' || row.user_id === userInfo.id)
  )
}

const canOperate = (row) => {
  const userInfo = userStore.userInfo
  return userInfo.user_type === 'admin' || userInfo.user_type === 'teacher' || row.user_id === userInfo.id
}

const canApprove = (row) => {
  const userInfo = userStore.userInfo
  return row.status === 'pending' && (userInfo.user_type === 'admin' || userInfo.user_type === 'teacher')
}

const canReject = (row) => {
  const userInfo = userStore.userInfo
  return row.status === 'pending' && (userInfo.user_type === 'admin' || userInfo.user_type === 'teacher')
}

const canCancel = (row) => {
  const userInfo = userStore.userInfo
  return (
    (row.status === 'pending' || row.status === 'approved') &&
    (userInfo.user_type === 'admin' || row.user_id === userInfo.id)
  )
}

const canDelete = (row) => {
  const userInfo = userStore.userInfo
  return userInfo.user_type === 'admin'
}

// 工具方法
const formatDateTime = (dateTime) => {
  return dayjs(dateTime).isValid() ? dayjs(dateTime).format('YYYY-MM-DD HH:mm') : ''
}

const normalizeTime = (t) => {
  if (!t) return ''
  const s = String(t)
  return s.length === 5 ? `${s}:00` : s
}

const formatDateTimeFromParts = (dateStr, timeStr) => {
  if (!dateStr || !timeStr) return ''
  const composed = `${dateStr} ${normalizeTime(timeStr)}`
  return dayjs(composed).isValid() ? dayjs(composed).format('YYYY-MM-DD HH:mm') : ''
}

const formatTimeFromParts = (dateStr, timeStr) => {
  if (!dateStr || !timeStr) return ''
  const composed = `${dateStr} ${normalizeTime(timeStr)}`
  return dayjs(composed).isValid() ? dayjs(composed).format('HH:mm') : ''
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

const getUserTypeText = (userType) => {
  const typeMap = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return typeMap[userType] || '未知'
}

const getApprovalType = (action) => {
  const typeMap = {
    approve: 'success',
    reject: 'danger',
    cancel: 'warning'
  }
  return typeMap[action] || 'primary'
}

const getApprovalText = (action) => {
  const textMap = {
    approve: '通过',
    reject: '拒绝',
    cancel: '取消'
  }
  return textMap[action] || '未知'
}

// 生命周期
onMounted(() => {
  loadLabOptions()
})

onActivated(() => {
  loadReservations()
})
</script>

<style lang="scss" scoped>
.reservation-list-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.search-section {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  
  .search-form {
    .el-form-item {
      margin-bottom: 0;
    }
  }
}

.reservation-table {
  .text-secondary {
    font-size: 12px;
    color: #909399;
  }
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.reservation-detail {
  .approval-records {
    margin-top: 20px;
    
    h4 {
      margin-bottom: 16px;
      color: #303133;
    }
    
    .approval-content {
      .approval-action {
        font-weight: 600;
        margin-bottom: 4px;
      }
      
      .approval-user,
      .approval-remarks {
        font-size: 14px;
        color: #606266;
        margin-bottom: 2px;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .reservation-list-container {
    padding: 10px;
  }
  
  .search-form {
    .el-form-item {
      display: block;
      margin-bottom: 16px;
    }
  }
  
  .reservation-table {
    font-size: 14px;
  }
}
</style>