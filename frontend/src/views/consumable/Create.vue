<template>
  <div class="consumable-create">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>新增耗材</span>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="consumable-form"
      >
        <el-form-item label="耗材名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入耗材名称" maxlength="100" />
        </el-form-item>
        
        <el-form-item label="型号/规格" prop="model">
          <el-input v-model="form.model" placeholder="请输入型号或规格" maxlength="100" />
        </el-form-item>
        
        <el-form-item label="所属实验室" prop="lab_id">
          <el-select v-model="form.lab_id" placeholder="请选择实验室" filterable>
            <el-option
              v-for="lab in laboratories"
              :key="lab.lab_id"
              :label="lab.lab_name"
              :value="lab.lab_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" placeholder="如：个、瓶、包" />
        </el-form-item>
        
        <el-form-item label="单价" prop="unit_price">
          <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width: 200px" />
        </el-form-item>
        
        <el-form-item label="当前库存" prop="current_stock">
          <el-input-number v-model="form.current_stock" :min="0" :precision="2" style="width: 200px" />
        </el-form-item>
        
        <el-form-item label="最低库存" prop="min_stock">
          <el-input-number v-model="form.min_stock" :min="0" :precision="2" style="width: 200px" />
        </el-form-item>
        
        <el-form-item label="供应商">
          <el-input v-model="form.supplier" placeholder="请输入供应商名称" />
        </el-form-item>
        
        <el-form-item label="采购日期" prop="purchase_date">
          <el-date-picker v-model="form.purchase_date" type="date" placeholder="请选择采购日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入耗材描述" />
        </el-form-item>
        
        <el-form-item label="课程关联" prop="course_id">
          <el-select
            v-model="form.course_id"
            placeholder="请选择关联课程（可选）"
            filterable
            clearable
          >
            <el-option
              v-for="course in courses"
              :key="course.course_id"
              :label="course.course_name"
              :value="course.course_id"
            />
          </el-select>
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
import { getCoursesApi } from '@/api/course'
import { createConsumable } from '@/api/consumable'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const laboratories = ref([])
const courses = ref([])

const form = reactive({
  name: '',
  model: '',
  lab_id: null,
  unit: '个',
  unit_price: 0,
  current_stock: 0,
  min_stock: 0,
  supplier: '',
  purchase_date: '',
  description: '',
  course_id: null
})

const rules = {
  name: [
    { required: true, message: '请输入耗材名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请输入型号/规格', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  lab_id: [
    { required: true, message: '请选择实验室', trigger: 'change' }
  ],
  unit: [
    { required: true, message: '请输入单位', trigger: 'blur' }
  ],
  unit_price: [
    { required: true, message: '请输入单价', trigger: 'blur' }
  ],
  current_stock: [
    { required: true, message: '请输入当前库存', trigger: 'blur' }
  ],
  min_stock: [
    { required: true, message: '请输入最低库存', trigger: 'blur' }
  ],
  purchase_date: [
    { required: true, message: '请选择采购日期', trigger: 'change' }
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

const loadCourses = async () => {
  try {
    const res = await getCoursesApi({ page: 1, page_size: 200 })
    if (res.code === 200) {
      courses.value = (res.data.list || []).map(c => ({ course_id: c.id, course_name: c.name }))
    }
  } catch (error) {
    ElMessage.error('加载课程列表失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    const payload = {
      name: form.name,
      model: form.model,
      laboratory_id: form.lab_id,
      unit: form.unit,
      unit_price: form.unit_price,
      current_stock: form.current_stock,
      min_stock: form.min_stock,
      supplier: form.supplier,
      purchase_date: form.purchase_date,
      description: form.description
    }
    await createConsumable(payload)
    ElMessage.success('耗材创建成功')
    router.push('/consumable/list')
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
  loadCourses()
})
</script>

<style scoped>
.consumable-create {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.consumable-form {
  max-width: 600px;
}
</style>