<template>
  <div class="equipment-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>设备管理</span>
          <el-button
            v-if="hasPermission(['admin', 'teacher'])"
            type="primary"
            @click="showCreateDialog"
          >
            <el-icon><Plus /></el-icon>
            新增设备
          </el-button>
        </div>
      </template>
      
      <!-- 搜索筛选 -->
      <div class="search-section">
        <el-row :gutter="20">
          <el-col :span="5">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索设备名称或型号"
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
              v-model="searchForm.labId"
              placeholder="选择实验室"
              clearable
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
          <el-col :span="4">
            <el-select
              v-model="searchForm.status"
              placeholder="设备状态"
              clearable
            >
              <el-option label="全部状态" value="" />
              <el-option label="正常" value="normal" />
              <el-option label="维护中" value="maintenance" />
              <el-option label="故障" value="broken" />
              <el-option label="报废" value="scrapped" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-date-picker
              v-model="searchForm.purchaseDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="购买开始日期"
              end-placeholder="购买结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-col>
          <el-col :span="7">
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
            <el-button type="success" @click="exportData">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 数据表格 -->
      <el-table
        v-loading="tableLoading"
        :data="tableData"
        stripe
        class="equipment-table"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="设备名称" min-width="150">
          <template #default="{ row }">
            <el-link type="primary" @click="showDetail(row)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="型号" min-width="120" />
        <el-table-column prop="lab_name" label="所属实验室" min-width="120">
          <template #default="{ row }">
            <el-link type="primary" @click="goToLab(row.lab_id)">
              {{ row.lab_name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            ¥{{ formatPrice(row.price) }}
          </template>
        </el-table-column>
        <el-table-column prop="purchase_date" label="购买日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.purchase_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="warranty_until" label="保修期至" width="120">
          <template #default="{ row }">
            <span :class="{ 'warranty-expired': isWarrantyExpired(row.warranty_until) }">
              {{ formatDate(row.warranty_until) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="maintenance_count" label="维修次数" width="100">
          <template #default="{ row }">
            <el-link
              v-if="row.maintenance_count > 0"
              type="primary"
              @click="showMaintenanceHistory(row)"
            >
              {{ row.maintenance_count }}次
            </el-link>
            <span v-else>0次</span>
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
              type="warning"
              size="small"
              @click="showMaintenanceDialog(row)"
            >
              维修
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
        ref="equipmentFormRef"
        :model="equipmentForm"
        :rules="equipmentRules"
        label-width="100px"
      >
        <el-form-item label="设备名称" prop="name">
          <el-input
            v-model="equipmentForm.name"
            placeholder="请输入设备名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="型号" prop="model">
          <el-input
            v-model="equipmentForm.model"
            placeholder="请输入设备型号"
            clearable
          />
        </el-form-item>
        <el-form-item label="序列号" prop="serialNumber">
          <el-input
            v-model="equipmentForm.serialNumber"
            placeholder="请输入设备序列号"
            clearable
          />
        </el-form-item>
        <el-form-item label="所属实验室" prop="labId">
          <el-select v-model="equipmentForm.labId" style="width: 100%">
            <el-option
              v-for="lab in labOptions"
              :key="lab.id"
              :label="lab.name"
              :value="lab.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="equipmentForm.status" style="width: 100%">
            <el-option label="正常" value="normal" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="故障" value="broken" />
            <el-option label="报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number
            v-model="equipmentForm.price"
            :min="0"
            :precision="2"
            placeholder="请输入设备价格"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="购买日期" prop="purchaseDate">
          <el-date-picker
            v-model="equipmentForm.purchaseDate"
            type="date"
            placeholder="请选择购买日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="保修期至" prop="warrantyUntil">
          <el-date-picker
            v-model="equipmentForm.warrantyUntil"
            type="date"
            placeholder="请选择保修期结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input
            v-model="equipmentForm.supplier"
            placeholder="请输入供应商名称（可选）"
            clearable
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="equipmentForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入设备描述（可选）"
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
      title="设备详情"
      width="800px"
    >
      <div v-if="selectedEquipment" class="equipment-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">
            {{ selectedEquipment.id }}
          </el-descriptions-item>
          <el-descriptions-item label="名称">
            {{ selectedEquipment.name }}
          </el-descriptions-item>
          <el-descriptions-item label="型号">
            {{ selectedEquipment.model }}
          </el-descriptions-item>
          <el-descriptions-item label="所属实验室">
            {{ selectedEquipment.lab_name }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedEquipment.status)">
              {{ getStatusText(selectedEquipment.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="价格">
            ¥{{ formatPrice(selectedEquipment.price) }}
          </el-descriptions-item>
          <el-descriptions-item label="购买日期">
            {{ formatDate(selectedEquipment.purchase_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="保修期至">
            <span :class="{ 'warranty-expired': isWarrantyExpired(selectedEquipment.warranty_until) }">
              {{ formatDate(selectedEquipment.warranty_until) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="供应商">
            {{ selectedEquipment.supplier || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="维修次数">
            {{ selectedEquipment.maintenance_count }}次
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ selectedEquipment.description || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(selectedEquipment.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(selectedEquipment.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
    
    <!-- 维修对话框 -->
    <el-dialog
      v-model="maintenanceDialogVisible"
      title="设备维修"
      width="600px"
    >
      <el-form
        ref="maintenanceFormRef"
        :model="maintenanceForm"
        :rules="maintenanceRules"
        label-width="100px"
      >
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
            placeholder="请描述设备问题或维修内容"
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
        <el-form-item label="维修人员">
          <el-input
            v-model="maintenanceForm.technician"
            placeholder="请输入维修人员姓名"
            clearable
          />
        </el-form-item>
        <el-form-item label="预计完成时间">
          <el-date-picker
            v-model="maintenanceForm.expectedCompletionDate"
            type="date"
            placeholder="请选择预计完成时间"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="maintenanceDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="maintenanceSubmitLoading"
          @click="handleMaintenanceSubmit"
        >
          {{ maintenanceSubmitLoading ? '提交中...' : '提交维修' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Download } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'
import {
  getEquipmentApi,
  createEquipmentApi,
  updateEquipmentApi,
  deleteEquipmentApi,
  getEquipmentByIdApi
} from '@/api/equipment'
import { createMaintenanceRecordApi } from '@/api/maintenance'
import { getLabsApi } from '@/api/lab'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const tableLoading = ref(false)
const submitLoading = ref(false)
const maintenanceSubmitLoading = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const maintenanceDialogVisible = ref(false)
const isEdit = ref(false)
const tableData = ref([])
const selectedEquipment = ref(null)
const labOptions = ref([])
const equipmentFormRef = ref()
const maintenanceFormRef = ref()

const searchForm = reactive({
  keyword: '',
  labId: '',
  status: '',
  purchaseDateRange: []
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const equipmentForm = reactive({
  id: null,
  name: '',
  model: '',
  serialNumber: '',
  labId: '',
  status: 'available',
  purchaseDate: '',
  warrantyUntil: '',
  description: ''
})

const maintenanceForm = reactive({
  equipmentId: null,
  type: 'maintenance',
  description: '',
  cost: 0,
  technician: '',
  expectedCompletionDate: ''
})

// 计算属性
const userInfo = computed(() => userStore.userInfo)

const dialogTitle = computed(() => {
  return isEdit.value ? '编辑设备' : '新增设备'
})

// 表单验证规则
const equipmentRules = {
  name: [
    { required: true, message: '请输入设备名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请输入设备型号', trigger: 'blur' },
    { min: 1, max: 50, message: '型号长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  serialNumber: [
    { required: true, message: '请输入设备序列号', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  labId: [
    { required: true, message: '请选择所属实验室', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择设备状态', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入设备价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格不能为负数', trigger: 'blur' }
  ],
  purchaseDate: [
    { required: true, message: '请选择购买日期', trigger: 'change' }
  ]
}

onMounted(() => {
  loadTableData()
  loadLabOptions()
})

onActivated(() => {
  loadTableData()
})

const maintenanceRules = {
  type: [
    { required: true, message: '请选择维修类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入问题描述', trigger: 'blur' },
    { min: 10, max: 500, message: '描述长度在 10 到 500 个字符', trigger: 'blur' }
  ]
}

// 方法
const hasPermission = (roles) => {
  return roles.includes(userInfo.value.user_type)
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

const loadTableData = async () => {
  tableLoading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size
    }
    
    if (searchForm.keyword) params.search = searchForm.keyword
    if (searchForm.labId) params.laboratory_id = searchForm.labId
    if (searchForm.status) params.status = searchForm.status === 'normal' ? 'available' : (searchForm.status === 'broken' ? 'damaged' : (searchForm.status === 'scrapped' ? 'retired' : searchForm.status))
    // 设备列表后端未支持采购日期筛选，先不传递日期参数
    
    const response = await getEquipmentApi(params)
    if (response.code === 200) {
      tableData.value = (response.data.list || []).map(e => ({
        id: e.id,
        name: e.name,
        model: e.model,
        lab_id: e.laboratory_id || undefined,
        lab_name: e.laboratory?.name || '',
        status: e.status === 'available' ? 'normal' : (e.status === 'damaged' ? 'broken' : (e.status === 'retired' ? 'scrapped' : e.status)),
        price: e.price || 0,
        purchase_date: e.purchase_date,
        warranty_until: e.warranty_date,
        supplier: e.supplier || '',
        description: e.description,
        maintenance_count: e.maintenance_count || 0,
        created_at: e.created_at,
        updated_at: e.updated_at
      }))
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('加载设备列表失败:', error)
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
  searchForm.labId = ''
  searchForm.status = ''
  searchForm.purchaseDateRange = []
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
  Object.assign(equipmentForm, {
    id: row.id,
    name: row.name,
    model: row.model,
    labId: row.lab_id,
    status: row.status,
    price: row.price,
    purchaseDate: row.purchase_date,
    warrantyUntil: row.warranty_until,
    supplier: row.supplier,
    description: row.description
  })
  dialogVisible.value = true
}

const showDetail = async (row) => {
  try {
    const response = await getEquipmentByIdApi(row.id)
    if (response.code === 200) {
      selectedEquipment.value = response.data
      detailDialogVisible.value = true
    }
  } catch (error) {
    console.error('获取设备详情失败:', error)
  }
}

const showMaintenanceDialog = (row) => {
  selectedEquipment.value = row
  maintenanceForm.equipmentId = row.id
  maintenanceForm.type = 'maintenance'
  maintenanceForm.description = ''
  maintenanceForm.cost = 0
  maintenanceForm.technician = ''
  maintenanceForm.expectedCompletionDate = ''
  maintenanceDialogVisible.value = true
}

const showMaintenanceHistory = (row) => {
  router.push(`/equipment/maintenance?equipment_id=${row.id}`)
}

const goToLab = (labId) => {
  router.push(`/laboratory/list?id=${labId}`)
}

const exportData = () => {
  // 导出功能实现
  ElMessage.info('导出功能开发中...')
}

const handleSubmit = async () => {
  if (!equipmentFormRef.value) return
  
  try {
    await equipmentFormRef.value.validate()
    submitLoading.value = true
    
    const submitData = {
      name: equipmentForm.name,
      model: equipmentForm.model,
      serial_number: equipmentForm.serialNumber,
      laboratory_id: equipmentForm.labId,
      status: equipmentForm.status === 'normal' ? 'available' : (equipmentForm.status === 'broken' ? 'damaged' : (equipmentForm.status === 'scrapped' ? 'retired' : equipmentForm.status)),
      purchase_date: equipmentForm.purchaseDate,
      warranty_date: equipmentForm.warrantyUntil,
      description: equipmentForm.description
    }
    
    const api = isEdit.value ? updateEquipmentApi : createEquipmentApi
    const params = isEdit.value ? [equipmentForm.id, submitData] : [submitData]
    
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

const handleMaintenanceSubmit = async () => {
  if (!maintenanceFormRef.value) return
  
  try {
    await maintenanceFormRef.value.validate()
    maintenanceSubmitLoading.value = true
    
    const submitData = {
      equipment_id: maintenanceForm.equipmentId,
      type: maintenanceForm.type,
      description: maintenanceForm.description,
      cost: maintenanceForm.cost,
      technician: maintenanceForm.technician,
      expected_completion_date: maintenanceForm.expectedCompletionDate
    }
    
    const response = await createMaintenanceRecordApi(submitData)
    if (response.code === 200) {
      ElMessage.success('维修记录创建成功')
      maintenanceDialogVisible.value = false
      loadTableData()
    }
  } catch (error) {
    console.error('提交维修记录失败:', error)
  } finally {
    maintenanceSubmitLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除设备 "${row.name}" 吗？此操作不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )
    
    const response = await deleteEquipmentApi(row.id)
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
  equipmentForm.id = null
  equipmentForm.name = ''
  equipmentForm.model = ''
  equipmentForm.serialNumber = ''
  equipmentForm.labId = ''
  equipmentForm.status = 'normal'
  equipmentForm.purchaseDate = ''
  equipmentForm.warrantyUntil = ''
  equipmentForm.description = ''
  
  if (equipmentFormRef.value) {
    equipmentFormRef.value.clearValidate()
  }
}

// 格式化方法
const formatDateTime = (datetime) => {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm')
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const formatPrice = (price) => {
  return Number(price).toLocaleString()
}

const isWarrantyExpired = (warrantyUntil) => {
  return dayjs(warrantyUntil).isBefore(dayjs())
}

const getStatusType = (status) => {
  const statusMap = {
    normal: 'success',
    maintenance: 'warning',
    broken: 'danger',
    scrapped: 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    normal: '正常',
    maintenance: '维护中',
    broken: '故障',
    scrapped: '报废'
  }
  return statusMap[status] || status
}

// 生命周期
onMounted(() => {
  loadLabOptions()
  loadTableData()
})
</script>

<style lang="scss" scoped>
.equipment-list-container {
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

.equipment-table {
  margin-bottom: 20px;
  
  .warranty-expired {
    color: #f56c6c;
    font-weight: 600;
  }
}

.pagination-section {
  display: flex;
  justify-content: center;
}

.equipment-detail {
  .warranty-expired {
    color: #f56c6c;
    font-weight: 600;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .equipment-list-container {
    padding: 10px;
  }
  
  .search-section {
    .el-col {
      margin-bottom: 10px;
    }
  }
  
  .equipment-table {
    :deep(.el-table__body-wrapper) {
      overflow-x: auto;
    }
  }
}
</style>