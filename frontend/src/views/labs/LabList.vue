<template>
  <div class="lab-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>实验室管理</span>
          <el-button
            v-if="hasPermission(['admin', 'teacher'])"
            type="primary"
            @click="showCreateDialog"
          >
            <el-icon><Plus /></el-icon>
            新建实验室
          </el-button>
        </div>
      </template>
      
      <!-- 搜索筛选 -->
      <div class="search-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索实验室名称或位置"
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
              v-model="searchForm.status"
              placeholder="状态"
              clearable
            >
              <el-option label="全部" value="" />
              <el-option label="可用" value="available" />
              <el-option label="维护中" value="maintenance" />
              <el-option label="停用" value="disabled" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-input-number
              v-model="searchForm.minCapacity"
              placeholder="最小容量"
              :min="1"
              :max="1000"
              controls-position="right"
            />
          </el-col>
          <el-col :span="4">
            <el-input-number
              v-model="searchForm.maxCapacity"
              placeholder="最大容量"
              :min="1"
              :max="1000"
              controls-position="right"
            />
          </el-col>
          <el-col :span="6">
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
      
      <!-- 数据表格 -->
      <el-table
        v-loading="tableLoading"
        :data="tableData"
        stripe
        class="lab-table"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="实验室名称" min-width="150">
          <template #default="{ row }">
            <el-link type="primary" @click="showDetail(row)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="位置" min-width="120" />
        <el-table-column prop="capacity" label="容量" width="80">
          <template #default="{ row }">
            {{ row.capacity }}人
          </template>
        </el-table-column>
        <el-table-column prop="manager" label="负责人" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="equipment_count" label="设备数量" width="100">
          <template #default="{ row }">
            <el-link type="primary" @click="showEquipment(row)">
              {{ row.equipment_count }}台
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="reservation_count" label="预约数" width="100">
          <template #default="{ row }">
            <el-link type="primary" @click="showReservations(row)">
              {{ row.reservation_count }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
          v-if="hasPermission(['admin', 'teacher'])"
          label="操作"
          width="200"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="showEditDialog(row)"
            >
              编辑
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="showAvailability(row)"
            >
              可用性
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
        ref="labFormRef"
        :model="labForm"
        :rules="labRules"
        label-width="100px"
      >
        <el-form-item label="实验室名称" prop="name">
          <el-input
            v-model="labForm.name"
            placeholder="请输入实验室名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input
            v-model="labForm.location"
            placeholder="请输入实验室位置"
            clearable
          />
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number
            v-model="labForm.capacity"
            :min="1"
            :max="1000"
            placeholder="请输入容量"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="负责人" prop="manager">
          <el-input
            v-model="labForm.manager"
            placeholder="请输入负责人姓名"
            clearable
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="labForm.status" style="width: 100%">
            <el-option label="可用" value="available" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="停用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="labForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入实验室描述（可选）"
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
      title="实验室详情"
      width="800px"
    >
      <div v-if="selectedLab" class="lab-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">
            {{ selectedLab.id }}
          </el-descriptions-item>
          <el-descriptions-item label="名称">
            {{ selectedLab.name }}
          </el-descriptions-item>
          <el-descriptions-item label="位置">
            {{ selectedLab.location }}
          </el-descriptions-item>
          <el-descriptions-item label="容量">
            {{ selectedLab.capacity }}人
          </el-descriptions-item>
          <el-descriptions-item label="负责人">
            {{ selectedLab.manager }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedLab.status)">
              {{ getStatusText(selectedLab.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="设备数量">
            {{ selectedLab.equipment_count }}台
          </el-descriptions-item>
          <el-descriptions-item label="预约数量">
            {{ selectedLab.reservation_count }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ selectedLab.description || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(selectedLab.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(selectedLab.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 设备列表 -->
        <div v-if="selectedLab.equipment && selectedLab.equipment.length > 0" class="equipment-section">
          <h4>实验室设备</h4>
          <el-table :data="selectedLab.equipment" size="small">
            <el-table-column prop="name" label="设备名称" />
            <el-table-column prop="model" label="型号" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getEquipmentStatusType(row.status)" size="small">
                  {{ getEquipmentStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="purchase_date" label="购买日期" />
          </el-table>
        </div>
      </div>
    </el-dialog>
    
    <!-- 可用性对话框 -->
    <el-dialog
      v-model="availabilityDialogVisible"
      title="实验室可用性"
      width="600px"
    >
      <div v-if="selectedLab">
        <el-form :model="availabilityForm" label-width="100px">
          <el-form-item label="查询日期">
            <el-date-picker
              v-model="availabilityForm.date"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="loadAvailability"
            />
          </el-form-item>
        </el-form>
        
        <div v-if="availabilityData.length > 0" class="availability-timeline">
          <h4>{{ availabilityForm.date }} 可用性时间线</h4>
          <div class="timeline">
            <div
              v-for="slot in availabilityData"
              :key="slot.time"
              :class="['time-slot', slot.available ? 'available' : 'occupied']"
            >
              <span class="time">{{ slot.time }}</span>
              <span class="status">{{ slot.available ? '可用' : '已预约' }}</span>
              <span v-if="!slot.available" class="reservation-info">
                {{ slot.reservation_info }}
              </span>
            </div>
          </div>
        </div>
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
  getLabsApi,
  createLabApi,
  updateLabApi,
  deleteLabApi,
  getLabByIdApi,
  getLabAvailabilityApi
} from '@/api/reservation'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const tableLoading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const availabilityDialogVisible = ref(false)
const isEdit = ref(false)
const tableData = ref([])
const selectedLab = ref(null)
const availabilityData = ref([])
const labFormRef = ref()

const searchForm = reactive({
  keyword: '',
  status: '',
  minCapacity: null,
  maxCapacity: null
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const labForm = reactive({
  id: null,
  name: '',
  location: '',
  capacity: 1,
  manager: '',
  status: 'available',
  description: ''
})

const availabilityForm = reactive({
  date: dayjs().format('YYYY-MM-DD')
})

// 计算属性
const userInfo = computed(() => userStore.userInfo)

const dialogTitle = computed(() => {
  return isEdit.value ? '编辑实验室' : '新建实验室'
})

// 表单验证规则
const labRules = {
  name: [
    { required: true, message: '请输入实验室名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入实验室位置', trigger: 'blur' },
    { min: 2, max: 100, message: '位置长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  capacity: [
    { required: true, message: '请输入容量', trigger: 'blur' },
    { type: 'number', min: 1, max: 1000, message: '容量必须在 1 到 1000 之间', trigger: 'blur' }
  ],
  manager: [
    { required: true, message: '请输入负责人姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '负责人姓名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 方法
const hasPermission = (roles) => {
  return roles.includes(userInfo.value.user_type)
}

const loadTableData = async () => {
  tableLoading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size
    }
    
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.minCapacity) params.min_capacity = searchForm.minCapacity
    if (searchForm.maxCapacity) params.max_capacity = searchForm.maxCapacity
    
    const response = await getLabsApi(params)
    if (response.code === 200) {
      tableData.value = response.data.list
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('加载实验室列表失败:', error)
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
  searchForm.status = ''
  searchForm.minCapacity = null
  searchForm.maxCapacity = null
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
  Object.assign(labForm, row)
  dialogVisible.value = true
}

const showDetail = async (row) => {
  try {
    const response = await getLabByIdApi(row.id)
    if (response.code === 200) {
      selectedLab.value = response.data
      detailDialogVisible.value = true
    }
  } catch (error) {
    console.error('获取实验室详情失败:', error)
  }
}

const showEquipment = (row) => {
  router.push(`/equipment?lab_id=${row.id}`)
}

const showReservations = (row) => {
  router.push(`/reservation/list?lab_id=${row.id}`)
}

const showAvailability = async (row) => {
  selectedLab.value = row
  availabilityDialogVisible.value = true
  await loadAvailability()
}

const loadAvailability = async () => {
  if (!selectedLab.value || !availabilityForm.date) return
  
  try {
    const response = await getLabAvailabilityApi(selectedLab.value.id, {
      date: availabilityForm.date
    })
    if (response.code === 200) {
      availabilityData.value = response.data
    }
  } catch (error) {
    console.error('获取可用性数据失败:', error)
  }
}

const handleSubmit = async () => {
  if (!labFormRef.value) return
  
  try {
    await labFormRef.value.validate()
    submitLoading.value = true
    
    const api = isEdit.value ? updateLabApi : createLabApi
    const params = isEdit.value ? [labForm.id, labForm] : [labForm]
    
    const response = await api(...params)
    if (response.code === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadTableData()
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
      `确定要删除实验室 "${row.name}" 吗？此操作不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )
    
    const response = await deleteLabApi(row.id)
    if (response.code === 200) {
      ElMessage.success('删除成功')
      loadTableData()
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
  labForm.id = null
  labForm.name = ''
  labForm.location = ''
  labForm.capacity = 1
  labForm.manager = ''
  labForm.status = 'available'
  labForm.description = ''
  
  if (labFormRef.value) {
    labFormRef.value.clearValidate()
  }
}

// 格式化方法
const formatDateTime = (datetime) => {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const statusMap = {
    available: 'success',
    maintenance: 'warning',
    disabled: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    available: '可用',
    maintenance: '维护中',
    disabled: '停用'
  }
  return statusMap[status] || status
}

const getEquipmentStatusType = (status) => {
  const statusMap = {
    normal: 'success',
    maintenance: 'warning',
    broken: 'danger'
  }
  return statusMap[status] || 'info'
}

const getEquipmentStatusText = (status) => {
  const statusMap = {
    normal: '正常',
    maintenance: '维护中',
    broken: '故障'
  }
  return statusMap[status] || status
}

// 生命周期
onMounted(() => {
  loadTableData()
})
</script>

<style lang="scss" scoped>
.lab-list-container {
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

.lab-table {
  margin-bottom: 20px;
}

.pagination-section {
  display: flex;
  justify-content: center;
}

.lab-detail {
  .equipment-section {
    margin-top: 20px;
    
    h4 {
      margin-bottom: 16px;
      color: #303133;
    }
  }
}

.availability-timeline {
  .timeline {
    .time-slot {
      display: flex;
      align-items: center;
      padding: 8px 12px;
      margin-bottom: 4px;
      border-radius: 4px;
      
      .time {
        width: 80px;
        font-weight: 600;
      }
      
      .status {
        width: 60px;
        margin-left: 10px;
      }
      
      .reservation-info {
        margin-left: 10px;
        font-size: 12px;
        color: #666;
      }
      
      &.available {
        background: #f0f9ff;
        color: #67c23a;
      }
      
      &.occupied {
        background: #fef0f0;
        color: #f56c6c;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .lab-list-container {
    padding: 10px;
  }
  
  .search-section {
    .el-col {
      margin-bottom: 10px;
    }
  }
  
  .lab-table {
    :deep(.el-table__body-wrapper) {
      overflow-x: auto;
    }
  }
}
</style>