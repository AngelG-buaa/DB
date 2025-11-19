<template>
  <div class="usage-records">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>耗材使用记录</h2>
      <el-button 
        type="primary" 
        @click="handleCreate"
        v-if="hasPermission('consumable:use')"
      >
        <el-icon><Plus /></el-icon>
        添加使用记录
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalRecords }}</div>
              <div class="stats-label">总使用记录</div>
            </div>
            <el-icon class="stats-icon"><Document /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.monthlyRecords }}</div>
              <div class="stats-label">本月使用</div>
            </div>
            <el-icon class="stats-icon"><Calendar /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalQuantity }}</div>
              <div class="stats-label">总使用量</div>
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
        <el-form-item label="耗材">
          <el-select
            v-model="searchForm.consumableId"
            placeholder="请选择耗材"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option
              v-for="consumable in consumableOptions"
              :key="consumable.id"
              :label="consumable.name"
              :value="consumable.id"
            />
          </el-select>
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
        <el-form-item label="使用人员">
          <el-input
            v-model="searchForm.userId"
            placeholder="请输入使用人员ID"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="使用日期">
          <el-date-picker
            v-model="searchForm.usageDateRange"
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
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
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
        <el-table-column prop="id" label="记录ID" width="100" />
        <el-table-column prop="consumableName" label="耗材名称" min-width="120" />
        <el-table-column prop="consumableModel" label="型号/规格" min-width="100" />
        <el-table-column prop="labName" label="实验室" min-width="120" />
        <el-table-column prop="quantity" label="使用数量" width="100">
          <template #default="{ row }">
            {{ row.quantity }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="unitPrice" label="单价" width="80">
          <template #default="{ row }">
            ¥{{ row.unitPrice }}
          </template>
        </el-table-column>
        <el-table-column prop="totalValue" label="总价值" width="100">
          <template #default="{ row }">
            ¥{{ (row.quantity * row.unitPrice).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="userId" label="使用人员" width="100" />
        <el-table-column prop="userName" label="姓名" width="100" />
        <el-table-column prop="purpose" label="使用目的" min-width="150" show-overflow-tooltip />
        <el-table-column prop="usageDate" label="使用日期" width="120" />
        <el-table-column prop="createdAt" label="记录时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleView(row)"
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
        <el-form-item label="耗材" prop="consumableId">
          <el-select
            v-model="form.consumableId"
            placeholder="请选择耗材"
            filterable
            style="width: 100%"
            @change="handleConsumableChange"
          >
            <el-option
              v-for="consumable in consumableOptions"
              :key="consumable.id"
              :label="`${consumable.name} (${consumable.model})`"
              :value="consumable.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="使用数量" prop="quantity">
          <el-input-number
            v-model="form.quantity"
            :min="0.01"
            :max="selectedConsumable?.currentStock"
            :precision="2"
            style="width: 100%"
          />
          <div class="form-tip" v-if="selectedConsumable">
            当前库存：{{ selectedConsumable.currentStock }} {{ selectedConsumable.unit }}
          </div>
        </el-form-item>
        <el-form-item label="使用人员" prop="userId">
          <el-input v-model="form.userId" placeholder="请输入使用人员ID" />
        </el-form-item>
        <el-form-item label="使用日期" prop="usageDate">
          <el-date-picker
            v-model="form.usageDate"
            type="date"
            placeholder="请选择使用日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="使用目的" prop="purpose">
          <el-input
            v-model="form.purpose"
            type="textarea"
            :rows="3"
            placeholder="请输入使用目的"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="form.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
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
      title="使用记录详情"
      v-model="detailVisible"
      width="600px"
    >
      <el-descriptions :column="2" border v-if="currentRecord">
        <el-descriptions-item label="记录ID">
          {{ currentRecord.id }}
        </el-descriptions-item>
        <el-descriptions-item label="耗材名称">
          {{ currentRecord.consumableName }}
        </el-descriptions-item>
        <el-descriptions-item label="型号/规格">
          {{ currentRecord.consumableModel }}
        </el-descriptions-item>
        <el-descriptions-item label="所属实验室">
          {{ currentRecord.labName }}
        </el-descriptions-item>
        <el-descriptions-item label="使用数量">
          {{ currentRecord.quantity }} {{ currentRecord.unit }}
        </el-descriptions-item>
        <el-descriptions-item label="单价">
          ¥{{ currentRecord.unitPrice }}
        </el-descriptions-item>
        <el-descriptions-item label="总价值">
          ¥{{ (currentRecord.quantity * currentRecord.unitPrice).toFixed(2) }}
        </el-descriptions-item>
        <el-descriptions-item label="使用人员">
          {{ currentRecord.userId }} - {{ currentRecord.userName }}
        </el-descriptions-item>
        <el-descriptions-item label="使用日期">
          {{ currentRecord.usageDate }}
        </el-descriptions-item>
        <el-descriptions-item label="记录时间">
          {{ currentRecord.createdAt }}
        </el-descriptions-item>
        <el-descriptions-item label="使用目的" :span="2">
          {{ currentRecord.purpose }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentRecord.remarks || '无' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, Download, Document, Calendar, TrendCharts, Money
} from '@element-plus/icons-vue'
import { 
  getConsumableUsageRecords,
  createConsumableUsage,
  updateConsumableUsage,
  deleteConsumableUsage,
  getConsumableUsageStats,
  exportConsumableUsage,
  getConsumables,
  getLaboratories
} from '@/api/consumable'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const consumableOptions = ref([])
const labOptions = ref([])
const stats = ref({
  totalRecords: 0,
  monthlyRecords: 0,
  totalQuantity: 0,
  totalValue: 0
})

// 搜索表单
const searchForm = reactive({
  consumableId: '',
  labId: '',
  userId: '',
  usageDateRange: []
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
const isEdit = ref(false)
const currentRecord = ref(null)
const selectedConsumable = ref(null)

// 表单数据
const form = reactive({
  id: null,
  consumableId: '',
  quantity: 1,
  userId: '',
  usageDate: '',
  purpose: '',
  remarks: ''
})

// 表单引用
const formRef = ref()

// 表单验证规则
const rules = {
  consumableId: [{ required: true, message: '请选择耗材', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入使用数量', trigger: 'blur' }],
  userId: [{ required: true, message: '请输入使用人员ID', trigger: 'blur' }],
  usageDate: [{ required: true, message: '请选择使用日期', trigger: 'change' }],
  purpose: [{ required: true, message: '请输入使用目的', trigger: 'blur' }]
}

// 计算属性
const dialogTitle = computed(() => isEdit.value ? '编辑使用记录' : '添加使用记录')

// 权限检查函数
const hasPermission = (permission) => {
  // 这里应该根据实际的权限系统来实现
  return true
}

// 检查是否可以编辑（例如：只能编辑今天的记录）
const canEdit = (row) => {
  const today = new Date().toISOString().split('T')[0]
  return row.usageDate === today
}

// 检查是否可以删除（例如：只能删除今天的记录）
const canDelete = (row) => {
  const today = new Date().toISOString().split('T')[0]
  return row.usageDate === today
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      consumableId: searchForm.consumableId || undefined,
      userId: searchForm.userId || undefined,
      dateFrom: searchForm.usageDateRange?.[0],
      dateTo: searchForm.usageDateRange?.[1]
    }
    
    const response = await getConsumableUsageRecords(params)
    tableData.value = response.data.list || response.data.items || []
    pagination.total = response.data.total || response.data.pagination?.total || 0
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载耗材选项
const loadConsumableOptions = async () => {
  try {
    const response = await getConsumables({ size: 1000 })
    consumableOptions.value = response.data.items
  } catch (error) {
    ElMessage.error('加载耗材选项失败')
  }
}

// 加载实验室选项
const loadLabOptions = async () => {
  try {
    const response = await getLaboratories()
    labOptions.value = response.code === 200 ? (response.data.list || response.data) : []
  } catch (error) {
    ElMessage.error('加载实验室选项失败')
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await getConsumableUsageStats()
    const byMonth = response.data?.byMonth || []
    stats.value.totalRecords = (response.data?.topConsumables || []).reduce((a, c) => a + (Number(c.count) || 0), 0)
    stats.value.monthlyRecords = byMonth.find(m => m.month)?.count || 0
    stats.value.totalQuantity = 0
    stats.value.totalValue = 0
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
    consumableId: '',
    labId: '',
    userId: '',
    usageDateRange: []
  })
  pagination.page = 1
  loadData()
}

// 导出
const handleExport = async () => {
  try {
    const params = {
      consumableId: searchForm.consumableId,
      labId: searchForm.labId,
      userId: searchForm.userId,
      startDate: searchForm.usageDateRange?.[0],
      endDate: searchForm.usageDateRange?.[1]
    }
    
    await exportConsumableUsage(params)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
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
  form.usageDate = new Date().toISOString().split('T')[0]
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  handleConsumableChange(form.consumableId)
  dialogVisible.value = true
}

// 查看详情
const handleView = (row) => {
  currentRecord.value = row
  detailVisible.value = true
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条使用记录吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteConsumableUsage(row.id)
    ElMessage.success('删除成功')
    loadData()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 耗材选择变化
const handleConsumableChange = (consumableId) => {
  selectedConsumable.value = consumableOptions.value.find(c => c.id === consumableId)
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      ElMessage.error('暂不支持编辑使用记录')
      return
    } else {
      await useConsumable(form.consumableId, { quantity: form.quantity, userId: form.userId, purpose: form.purpose })
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

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    consumableId: '',
    quantity: 1,
    userId: '',
    usageDate: '',
    purpose: '',
    remarks: ''
  })
  selectedConsumable.value = null
}

// 对话框关闭处理
const handleDialogClose = () => {
  formRef.value?.resetFields()
  resetForm()
}

// 初始化
onMounted(() => {
  loadData()
  loadConsumableOptions()
  loadLabOptions()
  loadStats()
})
</script>

<style scoped lang="scss">
.usage-records {
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

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .usage-records {
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