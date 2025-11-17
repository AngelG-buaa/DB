<template>
  <div class="consumable-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>耗材管理</h2>
      <el-button 
        type="primary" 
        @click="handleCreate"
        v-if="hasPermission('consumable:create')"
      >
        <el-icon><Plus /></el-icon>
        添加耗材
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.total }}</div>
              <div class="stats-label">总耗材数</div>
            </div>
            <el-icon class="stats-icon"><Box /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.lowStock }}</div>
              <div class="stats-label">库存不足</div>
            </div>
            <el-icon class="stats-icon low-stock"><Warning /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.monthlyUsage }}</div>
              <div class="stats-label">本月使用</div>
            </div>
            <el-icon class="stats-icon"><TrendCharts /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">¥{{ stats.totalValue }}</div>
              <div class="stats-label">总价值</div>
            </div>
            <el-icon class="stats-icon"><Money /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和过滤 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入耗材名称或型号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="实验室">
          <el-select
            v-model="searchForm.labId"
            placeholder="请选择实验室"
            clearable
            style="width: 150px"
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
            style="width: 120px"
          >
            <el-option label="正常" value="normal" />
            <el-option label="库存不足" value="low_stock" />
            <el-option label="缺货" value="out_of_stock" />
          </el-select>
        </el-form-item>
        <el-form-item label="采购日期">
          <el-date-picker
            v-model="searchForm.purchaseDateRange"
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
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="耗材名称" min-width="120" />
        <el-table-column prop="model" label="型号/规格" min-width="100" />
        <el-table-column prop="labName" label="所属实验室" min-width="120" />
        <el-table-column prop="currentStock" label="当前库存" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStockTagType(row.currentStock, row.minStock)"
              size="small"
            >
              {{ row.currentStock }} {{ row.unit }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="minStock" label="最低库存" width="100">
          <template #default="{ row }">
            {{ row.minStock }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="unitPrice" label="单价" width="100">
          <template #default="{ row }">
            ¥{{ row.unitPrice }}
          </template>
        </el-table-column>
        <el-table-column prop="supplier" label="供应商" min-width="120" />
        <el-table-column prop="purchaseDate" label="采购日期" width="120" />
        <el-table-column prop="usageCount" label="使用次数" width="100" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleView(row)"
            >
              详情
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="handleUse(row)"
              v-if="hasPermission('consumable:use')"
            >
              使用
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleRestock(row)"
              v-if="hasPermission('consumable:restock')"
            >
              补货
            </el-button>
            <el-button
              size="small"
              @click="handleEdit(row)"
              v-if="hasPermission('consumable:update')"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
              v-if="hasPermission('consumable:delete')"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="100px"
      >
        <el-form-item label="耗材名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入耗材名称" />
        </el-form-item>
        <el-form-item label="型号/规格" prop="model">
          <el-input v-model="form.model" placeholder="请输入型号或规格" />
        </el-form-item>
        <el-form-item label="所属实验室" prop="labId">
          <el-select v-model="form.labId" placeholder="请选择实验室" style="width: 100%">
            <el-option
              v-for="lab in labOptions"
              :key="lab.id"
              :label="lab.name"
              :value="lab.id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="当前库存" prop="currentStock">
              <el-input-number
                v-model="form.currentStock"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最低库存" prop="minStock">
              <el-input-number
                v-model="form.minStock"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="form.unit" placeholder="如：个、瓶、包" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价" prop="unitPrice">
              <el-input-number
                v-model="form.unitPrice"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="供应商" prop="supplier">
          <el-input v-model="form.supplier" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="采购日期" prop="purchaseDate">
          <el-date-picker
            v-model="form.purchaseDate"
            type="date"
            placeholder="请选择采购日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入耗材描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      title="耗材详情"
      v-model="detailVisible"
      width="600px"
    >
      <el-descriptions :column="2" border v-if="currentConsumable">
        <el-descriptions-item label="耗材名称">
          {{ currentConsumable.name }}
        </el-descriptions-item>
        <el-descriptions-item label="型号/规格">
          {{ currentConsumable.model }}
        </el-descriptions-item>
        <el-descriptions-item label="所属实验室">
          {{ currentConsumable.labName }}
        </el-descriptions-item>
        <el-descriptions-item label="当前库存">
          <el-tag
            :type="getStockTagType(currentConsumable.currentStock, currentConsumable.minStock)"
            size="small"
          >
            {{ currentConsumable.currentStock }} {{ currentConsumable.unit }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="最低库存">
          {{ currentConsumable.minStock }} {{ currentConsumable.unit }}
        </el-descriptions-item>
        <el-descriptions-item label="单价">
          ¥{{ currentConsumable.unitPrice }}
        </el-descriptions-item>
        <el-descriptions-item label="供应商">
          {{ currentConsumable.supplier }}
        </el-descriptions-item>
        <el-descriptions-item label="采购日期">
          {{ currentConsumable.purchaseDate }}
        </el-descriptions-item>
        <el-descriptions-item label="使用次数">
          {{ currentConsumable.usageCount }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ currentConsumable.createdAt }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ currentConsumable.description || '无' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 使用记录对话框 -->
    <el-dialog
      title="使用耗材"
      v-model="useVisible"
      width="500px"
    >
      <el-form
        :model="useForm"
        :rules="useRules"
        ref="useFormRef"
        label-width="100px"
      >
        <el-form-item label="使用数量" prop="quantity">
          <el-input-number
            v-model="useForm.quantity"
            :min="0.01"
            :max="currentConsumable?.currentStock"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="使用人员" prop="userId">
          <el-input v-model="useForm.userId" placeholder="请输入使用人员ID" />
        </el-form-item>
        <el-form-item label="使用目的" prop="purpose">
          <el-input
            v-model="useForm.purpose"
            type="textarea"
            :rows="3"
            placeholder="请输入使用目的"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="useVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUseSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 补货对话框 -->
    <el-dialog
      title="补货"
      v-model="restockVisible"
      width="500px"
    >
      <el-form
        :model="restockForm"
        :rules="restockRules"
        ref="restockFormRef"
        label-width="100px"
      >
        <el-form-item label="补货数量" prop="quantity">
          <el-input-number
            v-model="restockForm.quantity"
            :min="0.01"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="单价" prop="unitPrice">
          <el-input-number
            v-model="restockForm.unitPrice"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="restockForm.supplier" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="restockForm.remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="restockVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRestockSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, Box, Warning, TrendCharts, Money
} from '@element-plus/icons-vue'
import { 
  getConsumables, 
  createConsumable, 
  updateConsumable, 
  deleteConsumable,
  useConsumable,
  restockConsumable,
  getConsumableStats,
  getLaboratories
} from '@/api/consumable'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const labOptions = ref([])
const stats = ref({
  total: 0,
  lowStock: 0,
  monthlyUsage: 0,
  totalValue: 0
})

// 搜索表单
const searchForm = reactive({
  keyword: '',
  labId: '',
  status: '',
  purchaseDateRange: []
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 对话框状态
const dialogVisible = ref(false)
const detailVisible = ref(false)
const useVisible = ref(false)
const restockVisible = ref(false)
const isEdit = ref(false)
const currentConsumable = ref(null)

// 表单数据
const form = reactive({
  id: null,
  name: '',
  model: '',
  labId: '',
  currentStock: 0,
  minStock: 0,
  unit: '',
  unitPrice: 0,
  supplier: '',
  purchaseDate: '',
  description: ''
})

const useForm = reactive({
  quantity: 1,
  userId: '',
  purpose: ''
})

const restockForm = reactive({
  quantity: 1,
  unitPrice: 0,
  supplier: '',
  remarks: ''
})

// 表单引用
const formRef = ref()
const useFormRef = ref()
const restockFormRef = ref()

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入耗材名称', trigger: 'blur' }],
  model: [{ required: true, message: '请输入型号或规格', trigger: 'blur' }],
  labId: [{ required: true, message: '请选择实验室', trigger: 'change' }],
  currentStock: [{ required: true, message: '请输入当前库存', trigger: 'blur' }],
  minStock: [{ required: true, message: '请输入最低库存', trigger: 'blur' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
  unitPrice: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  supplier: [{ required: true, message: '请输入供应商', trigger: 'blur' }],
  purchaseDate: [{ required: true, message: '请选择采购日期', trigger: 'change' }]
}

const useRules = {
  quantity: [{ required: true, message: '请输入使用数量', trigger: 'blur' }],
  userId: [{ required: true, message: '请输入使用人员ID', trigger: 'blur' }],
  purpose: [{ required: true, message: '请输入使用目的', trigger: 'blur' }]
}

const restockRules = {
  quantity: [{ required: true, message: '请输入补货数量', trigger: 'blur' }],
  unitPrice: [{ required: true, message: '请输入单价', trigger: 'blur' }]
}

// 计算属性
const dialogTitle = computed(() => isEdit.value ? '编辑耗材' : '添加耗材')

// 权限检查函数
const hasPermission = (permission) => {
  // 这里应该根据实际的权限系统来实现
  return true
}

// 获取库存状态标签类型
const getStockTagType = (currentStock, minStock) => {
  if (currentStock <= 0) return 'danger'
  if (currentStock <= minStock) return 'warning'
  return 'success'
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword,
      labId: searchForm.labId,
      status: searchForm.status,
      startDate: searchForm.purchaseDateRange?.[0],
      endDate: searchForm.purchaseDateRange?.[1]
    }
    
    const response = await getConsumables(params)
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载实验室选项
const loadLabOptions = async () => {
  try {
    const response = await getLaboratories()
    labOptions.value = response.data
  } catch (error) {
    ElMessage.error('加载实验室选项失败')
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await getConsumableStats()
    stats.value = response.data
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    keyword: '',
    labId: '',
    status: '',
    purchaseDateRange: []
  })
  pagination.page = 1
  loadData()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadData()
}

// 创建
const handleCreate = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

// 查看详情
const handleView = (row) => {
  currentConsumable.value = row
  detailVisible.value = true
}

// 使用耗材
const handleUse = (row) => {
  currentConsumable.value = row
  resetUseForm()
  useVisible.value = true
}

// 补货
const handleRestock = (row) => {
  currentConsumable.value = row
  resetRestockForm()
  restockForm.unitPrice = row.unitPrice
  restockForm.supplier = row.supplier
  restockVisible.value = true
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除耗材"${row.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteConsumable(row.id)
    ElMessage.success('删除成功')
    loadData()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await updateConsumable(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createConsumable(form)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadData()
    loadStats()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

// 使用提交
const handleUseSubmit = async () => {
  try {
    await useFormRef.value.validate()
    submitting.value = true
    
    await useConsumable(currentConsumable.value.id, useForm)
    ElMessage.success('使用记录已保存')
    
    useVisible.value = false
    loadData()
    loadStats()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('保存使用记录失败')
    }
  } finally {
    submitting.value = false
  }
}

// 补货提交
const handleRestockSubmit = async () => {
  try {
    await restockFormRef.value.validate()
    submitting.value = true
    
    await restockConsumable(currentConsumable.value.id, restockForm)
    ElMessage.success('补货成功')
    
    restockVisible.value = false
    loadData()
    loadStats()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('补货失败')
    }
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    name: '',
    model: '',
    labId: '',
    currentStock: 0,
    minStock: 0,
    unit: '',
    unitPrice: 0,
    supplier: '',
    purchaseDate: '',
    description: ''
  })
}

const resetUseForm = () => {
  Object.assign(useForm, {
    quantity: 1,
    userId: '',
    purpose: ''
  })
}

const resetRestockForm = () => {
  Object.assign(restockForm, {
    quantity: 1,
    unitPrice: 0,
    supplier: '',
    remarks: ''
  })
}

// 对话框关闭处理
const handleDialogClose = () => {
  formRef.value?.resetFields()
  resetForm()
}

// 初始化
onMounted(() => {
  loadData()
  loadLabOptions()
  loadStats()
})
</script>

<style scoped lang="scss">
.consumable-list {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      color: #303133;
    }
  }

  .stats-cards {
    margin-bottom: 20px;

    .stats-card {
      .el-card__body {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
      }

      .stats-content {
        .stats-number {
          font-size: 24px;
          font-weight: bold;
          color: #303133;
          margin-bottom: 5px;
        }

        .stats-label {
          font-size: 14px;
          color: #909399;
        }
      }

      .stats-icon {
        font-size: 32px;
        color: #409eff;

        &.low-stock {
          color: #e6a23c;
        }
      }
    }
  }

  .search-card {
    margin-bottom: 20px;
  }

  .table-card {
    .pagination-wrapper {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .consumable-list {
    padding: 10px;

    .stats-cards {
      .el-col {
        margin-bottom: 10px;
      }
    }

    .search-card {
      .el-form {
        .el-form-item {
          margin-bottom: 10px;
        }
      }
    }
  }
}
</style>