<template>
  <div class="equipment-create">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>新增设备</span>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="equipment-form"
      >
        <el-form-item label="设备名称" prop="equip_name">
          <el-input
            v-model="form.equip_name"
            placeholder="请输入设备名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="型号" prop="model">
          <el-input
            v-model="form.model"
            placeholder="请输入设备型号"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="序列号" prop="serial_number">
          <el-input
            v-model="form.serial_number"
            placeholder="请输入设备序列号"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="所属实验室" prop="lab_id">
          <el-select
            v-model="form.lab_id"
            placeholder="请选择实验室"
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
        
        <el-form-item label="购买日期" prop="buy_date">
          <el-date-picker
            v-model="form.buy_date"
            type="date"
            placeholder="请选择购买日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="价格" prop="price">
          <el-input-number
            v-model="form.price"
            :min="0"
            :precision="2"
            placeholder="请输入价格"
            style="width: 200px"
          />
          <span style="margin-left: 10px">元</span>
        </el-form-item>
        
        <el-form-item label="设备状态" prop="equip_status">
          <el-select v-model="form.equip_status" placeholder="请选择状态">
            <el-option label="正常" value="正常" />
            <el-option label="维修中" value="维修中" />
            <el-option label="报废" value="报废" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="警告阈值" prop="warn_threshold">
          <el-input-number
            v-model="form.warn_threshold"
            :min="0"
            :max="100"
            placeholder="请输入警告阈值"
            style="width: 200px"
          />
          <span style="margin-left: 10px">%</span>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            创建
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getLabsApi } from '@/api/lab'
import { createEquipmentApi } from '@/api/equipment'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const laboratories = ref([])

const form = reactive({
  equip_name: '',
  model: '',
  serial_number: '',
  lab_id: null,
  buy_date: '',
  price: 0,
  equip_status: '正常',
  warn_threshold: 10
})

const rules = {
  equip_name: [
    { required: true, message: '请输入设备名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请输入设备型号', trigger: 'blur' },
    { max: 50, message: '长度不能超过 50 个字符', trigger: 'blur' }
  ],
  serial_number: [
    { required: true, message: '请输入设备序列号', trigger: 'blur' }
  ],
  lab_id: [
    { required: true, message: '请选择实验室', trigger: 'change' }
  ],
  buy_date: [
    { required: true, message: '请选择购买日期', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格不能为负数', trigger: 'blur' }
  ],
  equip_status: [
    { required: true, message: '请选择设备状态', trigger: 'change' }
  ],
  warn_threshold: [
    { type: 'number', min: 0, max: 100, message: '警告阈值必须在0-100之间', trigger: 'blur' }
  ]
}

const loadLaboratories = async () => {
  try {
    const res = await getLabsApi({ page: 1, page_size: 200 })
    if (res.code === 200) {
      laboratories.value = (res.data.list || []).map(l => ({ lab_id: l.id, lab_name: l.name }))
    }
  } catch (error) {
    ElMessage.error('加载实验室列表失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    const statusMap = {
      '正常': 'available',
      '维修中': 'maintenance',
      '报废': 'retired'
    }
    const payload = {
      name: form.equip_name,
      model: form.model,
      serial_number: form.serial_number,
      laboratory_id: form.lab_id,
      status: statusMap[form.equip_status],
      purchase_date: form.buy_date,
      description: ''
    }
    const res = await createEquipmentApi(payload)
    if (res.code === 200) {
      ElMessage.success('设备创建成功')
      router.push('/equipment/list')
    }
    
  } catch (error) {
    if (error !== false) {
      ElMessage.error('创建失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.back()
}

onMounted(() => {
  loadLaboratories()
})
</script>

<style scoped>
.equipment-create {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.equipment-form {
  max-width: 600px;
}
</style>