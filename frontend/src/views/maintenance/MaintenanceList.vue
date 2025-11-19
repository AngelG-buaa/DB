<template>
  <div class="maintenance-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>设备维修记录</span>
          <el-button
            v-if="hasPermission(['admin', 'teacher'])"
            type="primary"
            @click="showCreateDialog"
          >
            <el-icon><Plus /></el-icon>
            新建维修记录
          </el-button>
        </div>
      </template>
      
      <!-- 搜索筛选 -->
      <div class="search-section">
        <el-row :gutter="20">
          <el-col :span="5">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索设备名称或维修人员"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select
              v-model="searchForm.equipmentId"
              placeholder="选择设备"
              clearable
              filterable
            >
              <el-option label="全部设备" value="" />
              <el-option
                v-for="equipment in equipmentOptions"
                :key="equipment.id"
                :label="`${equipment.name} (${equipment.model})`"
                :value="equipment.id"
              />
            </el-select>
          </el-col>
          <el-col :span="3">
            <el-select
              v-model="searchForm.type"
              placeholder="维修类型"
              clearable
            >
              <el-option label="全部类型" value="" />
              <el-option label="定期保养" value="maintenance" />
              <el-option label="故障维修" value="repair" />
              <el-option label="升级改造" value="upgrade" />
            </el-select>
          </el-col>
          <el-col :span="3">
            <el-select
              v-model="searchForm.status"
              placeholder="维修状态"
              clearable
            >
              <el-option label="全部状态" value="" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-col>
          <el-col :span="5">
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 统计卡片 -->
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="总维修记录" :value="stats.total" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="进行中" :value="stats.inProgress" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="本月完成" :value="stats.thisMonth" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="总费用" :value="stats.totalCost" prefix="¥" />
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 数据表格 -->
      <el-table
        v-loading="tableLoading"
        :data="tableData"
        stripe
        class="maintenance-table"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="equipment_name" label="设备名称" min-width="150">
          <template #default="{ row }">
            <el-link type="primary" @click="goToEquipment(row.equipment_id)">
              {{ row.equipment_name }}
            </el-link>
            <div class="equipment-model">{{ row.equipment_model }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="维修类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">
              {{ getTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="technician" label="维修人员" width="100" />
        <el-table-column prop="cost" label="费用" width="100">
          <template #default="{ row }">
            <span v-if="row.cost > 0">¥{{ formatPrice(row.cost) }}</span>
            <span v-else class="no-cost">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.start_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="expected_completion_date" label="预计完成" width="120">
          <template #default="{ row }">
            <span :class="{ 'overdue': isOverdue(row) }">
              {{ formatDate(row.expected_completion_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="actual_completion_date" label="实际完成" width="120">
          <template #default="{ row }">
            {{ row.actual_completion_date ? formatDate(row.actual_completion_date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="问题描述" min-width="200" show-overflow-tooltip />
        <el-table-column
          v-if="hasPermission(['admin', 'teacher'])"
          label="操作"
          width="180"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="showDetail(row)"
            >
              详情
            </el-button>
            <el-button
              v-if="row.status === 'in_progress'"
              type="success"
              size="small"
              @click="completeRecord(row)"
            >
              完成
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="showEditDialog(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-section">
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
    
    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="maintenanceFormRef"
        :model="maintenanceForm"
        :rules="maintenanceRules"
        label-width="120px"
      >
        <el-form-item label="设备" prop="equipmentId">
          <el-select
            v-model="maintenanceForm.equipmentId"
            placeholder="请选择设备"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="equipment in equipmentOptions"
              :key="equipment.id"
              :label="`${equipment.name} (${equipment.model})`"
              :value="equipment.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="维修类型" prop="type">
          <el-select v-model="maintenanceForm.type" style="width: 100%">
            <el-option label="定期保养" value="maintenance" />
            <el-option label="故障维修" value="repair" />
            <el-option label="升级改造" value="upgrade" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题描述" prop="description">
          <el-input
            v-model="maintenanceForm.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述设备问题或维修内容"
          />
        </el-form-item>
        <el-form-item label="维修人员" prop="technician">
          <el-input
            v-model="maintenanceForm.technician"
            placeholder="请输入维修人员姓名"
            clearable
          />
        </el-form-item>
        <el-form-item label="维修费用">
          <el-input-number
            v-model="maintenanceForm.cost"
            :min="0"
            :precision="2"
            placeholder="请输入维修费用"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开始日期" prop="startDate">
          <el-date-picker
            v-model="maintenanceForm.startDate"
            type="date"
            placeholder="请选择开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预计完成日期" prop="expectedCompletionDate">
          <el-date-picker
            v-model="maintenanceForm.expectedCompletionDate"
            type="date"
            placeholder="请选择预计完成日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="maintenanceForm.status" style="width: 100%">
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="maintenanceForm.status === 'completed'" label="实际完成日期">
          <el-date-picker
            v-model="maintenanceForm.actualCompletionDate"
            type="date"
            placeholder="请选择实际完成日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="maintenanceForm.remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button
          type="primary"
          :loading="submitLoading"
          @click="handleSubmit"
        >
          {{ submitLoading ? '提交中...' : '确定' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="维修记录详情"
      width="700px"
    >
      <div v-if="selectedRecord" class="maintenance-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="记录ID">
            {{ selectedRecord.id }}
          </el-descriptions-item>
          <el-descriptions-item label="设备">
            {{ selectedRecord.equipment_name }} ({{ selectedRecord.equipment_model }})
          </el-descriptions-item>
          <el-descriptions-item label="维修类型">
            <el-tag :type="getTypeTagType(selectedRecord.type)">
              {{ getTypeText(selectedRecord.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedRecord.status)">
              {{ getStatusText(selectedRecord.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="维修人员">
            {{ selectedRecord.technician }}
          </el-descriptions-item>
          <el-descriptions-item label="费用">
            {{ selectedRecord.cost > 0 ? `¥${formatPrice(selectedRecord.cost)}` : '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">
            {{ formatDate(selectedRecord.start_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="预计完成日期">
            <span :class="{ 'overdue': isOverdue(selectedRecord) }">
              {{ formatDate(selectedRecord.expected_completion_date) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="实际完成日期">
            {{ selectedRecord.actual_completion_date ? formatDate(selectedRecord.actual_completion_date) : '未完成' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ selectedRecord.created_by_name }}
          </el-descriptions-item>
          <el-descriptions-item label="问题描述" :span="2">
            {{ selectedRecord.description }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ selectedRecord.remarks || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(selectedRecord.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(selectedRecord.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'
import {
  getMaintenanceRecordsApi,
  createMaintenanceRecordApi,
  updateMaintenanceRecordApi,
  deleteMaintenanceRecordApi,
  getMaintenanceRecordByIdApi,
  getMaintenanceStatsApi
} from '@/api/maintenance'
import { getEquipmentApi } from '@/api/equipment'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const tableLoading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const isEdit = ref(false)
const tableData = ref([])
const selectedRecord = ref(null)
const equipmentOptions = ref([])
const maintenanceFormRef = ref()

const searchForm = reactive({
  keyword: '',
  equipmentId: '',
  type: '',
  status: '',
  dateRange: []
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const stats = reactive({
  total: 0,
  inProgress: 0,
  thisMonth: 0,
  totalCost: 0
})

const maintenanceForm = reactive({
  id: null,
  equipmentId: '',
  type: 'maintenance',
  description: '',
  technician: '',
  cost: 0,
  startDate: dayjs().format('YYYY-MM-DD'),
  expectedCompletionDate: '',
  actualCompletionDate: '',
  status: 'in_progress',
  remarks: ''
})

// 计算属性
const userInfo = computed(() => userStore.userInfo)

const dialogTitle = computed(() => {
  return isEdit.value ? '编辑维修记录' : '新建维修记录'
})

// 表单验证规则
const maintenanceRules = {
  equipmentId: [
    { required: true, message: '请选择设备', trigger: 'change' }
  ],
  type: [
    { required: true, message: '请选择维修类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入问题描述', trigger: 'blur' },
    { min: 10, max: 500, message: '描述长度在 10 到 500 个字符', trigger: 'blur' }
  ],
  technician: [
    { required: true, message: '请输入维修人员姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  startDate: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  expectedCompletionDate: [
    { required: true, message: '请选择预计完成日期', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 方法
const hasPermission = (roles) => {
  return roles.includes(userInfo.value?.role)
}

const loadEquipmentOptions = async () => {
  try {
    const response = await getEquipmentApi({ page: 1, size: 1000 })
    if (response.code === 200) {
      equipmentOptions.value = response.data.list
    }
  } catch (error) {
    console.error('加载设备选项失败:', error)
  }
}

const loadStats = async () => {
  try {
    const response = await getMaintenanceStatsApi()
    if (response.code === 200) {
      Object.assign(stats, response.data)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadTableData = async () => {
  tableLoading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size
    }
    
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.equipmentId) params.equipment_id = searchForm.equipmentId
    if (searchForm.type) params.type = searchForm.type
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = searchForm.dateRange[0]
      params.end_date = searchForm.dateRange[1]
    }
    
    const response = await getMaintenanceRecordsApi(params)
    if (response.code === 200) {
      tableData.value = response.data.list
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('加载维修记录失败:', error)
  } finally {
    tableLoading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadTableData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.equipmentId = ''
  searchForm.type = ''
  searchForm.status = ''
  searchForm.dateRange = []
  pagination.page = 1
  loadTableData()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadTableData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadTableData()
}

const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  Object.assign(maintenanceForm, {
    id: row.id,
    equipmentId: row.equipment_id,
    type: row.type,
    description: row.description,
    technician: row.technician,
    cost: row.cost,
    startDate: row.start_date,
    expectedCompletionDate: row.expected_completion_date,
    actualCompletionDate: row.actual_completion_date,
    status: row.status,
    remarks: row.remarks
  })
  dialogVisible.value = true
}

const showDetail = async (row) => {
  try {
    const response = await getMaintenanceRecordByIdApi(row.id)
    if (response.code === 200) {
      selectedRecord.value = response.data
      detailDialogVisible.value = true
    }
  } catch (error) {
    console.error('获取维修记录详情失败:', error)
  }
}

const completeRecord = async (row) => {
  try {
    await ElMessageBox.confirm('确定要标记此维修记录为已完成吗？', '确认完成', {
      type: 'success'
    })
    
    const updateData = {
      status: 'completed',
      actual_completion_date: dayjs().format('YYYY-MM-DD')
    }
    
    const response = await updateMaintenanceRecordApi(row.id, updateData)
    if (response.code === 200) {
      ElMessage.success('维修记录已标记为完成')
      loadTableData()
      loadStats()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('完成维修记录失败:', error)
    }
  }
}

const goToEquipment = (equipmentId) => {
  router.push(`/equipment?id=${equipmentId}`)
}

const handleSubmit = async () => {
  if (!maintenanceFormRef.value) return
  
  try {
    await maintenanceFormRef.value.validate()
    submitLoading.value = true
    
    const submitData = {
      equipment_id: maintenanceForm.equipmentId,
      type: maintenanceForm.type,
      description: maintenanceForm.description,
      technician: maintenanceForm.technician,
      cost: maintenanceForm.cost,
      start_date: maintenanceForm.startDate,
      expected_completion_date: maintenanceForm.expectedCompletionDate,
      status: maintenanceForm.status,
      remarks: maintenanceForm.remarks
    }
    
    if (maintenanceForm.actualCompletionDate) {
      submitData.actual_completion_date = maintenanceForm.actualCompletionDate
    }
    
    const api = isEdit.value ? updateMaintenanceRecordApi : createMaintenanceRecordApi
    const params = isEdit.value ? [maintenanceForm.id, submitData] : [submitData]
    
    const response = await api(...params)
    if (response.code === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadTableData()
      loadStats()
    }
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条维修记录吗？此操作不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )
    
    const response = await deleteMaintenanceRecordApi(row.id)
    if (response.code === 200) {
      ElMessage.success('删除成功')
      loadTableData()
      loadStats()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const handleDialogClose = () => {
  dialogVisible.value = false
  resetForm()
}

const resetForm = () => {
  maintenanceForm.id = null
  maintenanceForm.equipmentId = ''
  maintenanceForm.type = 'maintenance'
  maintenanceForm.description = ''
  maintenanceForm.technician = ''
  maintenanceForm.cost = 0
  maintenanceForm.startDate = dayjs().format('YYYY-MM-DD')
  maintenanceForm.expectedCompletionDate = ''
  maintenanceForm.actualCompletionDate = ''
  maintenanceForm.status = 'in_progress'
  maintenanceForm.remarks = ''
  
  if (maintenanceFormRef.value) {
    maintenanceFormRef.value.clearValidate()
  }
}

// 格式化和判断方法
const formatDateTime = (datetime) => {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm')
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const formatPrice = (price) => {
  return Number(price).toLocaleString()
}

const isOverdue = (record) => {
  return record.status === 'in_progress' && 
         dayjs(record.expected_completion_date).isBefore(dayjs())
}

const getTypeTagType = (type) => {
  const typeMap = {
    maintenance: 'success',
    repair: 'warning',
    upgrade: 'primary'
  }
  return typeMap[type] || 'info'
}

const getTypeText = (type) => {
  const typeMap = {
    maintenance: '定期保养',
    repair: '故障维修',
    upgrade: '升级改造'
  }
  return typeMap[type] || type
}

const getStatusType = (status) => {
  const statusMap = {
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

// 生命周期
onMounted(() => {
  loadEquipmentOptions()
  loadTableData()
  loadStats()
})
</script>

<style lang="scss" scoped>
.maintenance-list-container {
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
  
  .el-col {
    margin-bottom: 10px;
  }
}

.stats-section {
  margin-bottom: 20px;
  
  .stat-card {
    text-align: center;
    
    :deep(.el-card__body) {
      padding: 20px;
    }
  }
}

.maintenance-table {
  margin-bottom: 20px;
  
  .equipment-model {
    font-size: 12px;
    color: #909399;
  }
  
  .no-cost {
    color: #909399;
  }
  
  .overdue {
    color: #f56c6c;
    font-weight: 600;
  }
}

.pagination-section {
  display: flex;
  justify-content: center;
}

.maintenance-detail {
  .overdue {
    color: #f56c6c;
    font-weight: 600;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .maintenance-list-container {
    padding: 10px;
  }
  
  .search-section {
    .el-col {
      margin-bottom: 10px;
    }
  }
  
  .stats-section {
    .el-col {
      margin-bottom: 10px;
    }
  }
  
  .maintenance-table {
    :deep(.el-table__body-wrapper) {
      overflow-x: auto;
    }
  }
}
</style>