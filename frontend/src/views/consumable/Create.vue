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
        <el-form-item label="耗材名称" prop="spec">
          <el-input
            v-model="form.spec"
            placeholder="请输入耗材名称/规格"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="当前库存" prop="consume_stock">
          <el-input-number
            v-model="form.consume_stock"
            :min="0"
            placeholder="请输入当前库存"
            style="width: 200px"
          />
          <span style="margin-left: 10px">个</span>
        </el-form-item>
        
        <el-form-item label="警告阈值" prop="warn_threshold">
          <el-input-number
            v-model="form.warn_threshold"
            :min="0"
            placeholder="请输入警告阈值"
            style="width: 200px"
          />
          <span style="margin-left: 10px">个</span>
          <el-text type="info" size="small" style="margin-left: 10px">
            当库存低于此值时会发出警告
          </el-text>
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

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const laboratories = ref([])
const courses = ref([])

const form = reactive({
  spec: '',
  consume_stock: 0,
  warn_threshold: 10,
  lab_id: null,
  course_id: null
})

const rules = {
  spec: [
    { required: true, message: '请输入耗材名称/规格', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  consume_stock: [
    { required: true, message: '请输入当前库存', trigger: 'blur' },
    { type: 'number', min: 0, message: '库存不能为负数', trigger: 'blur' }
  ],
  warn_threshold: [
    { required: true, message: '请输入警告阈值', trigger: 'blur' },
    { type: 'number', min: 0, message: '警告阈值不能为负数', trigger: 'blur' }
  ],
  lab_id: [
    { required: true, message: '请选择实验室', trigger: 'change' }
  ]
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

const loadCourses = async () => {
  try {
    // TODO: 调用API获取课程列表
    // const response = await api.getCourses()
    // courses.value = response.data
    
    // 模拟数据
    courses.value = [
      { course_id: 1, course_name: '大学物理实验' },
      { course_id: 2, course_name: '有机化学实验' },
      { course_id: 3, course_name: '生物学基础实验' }
    ]
  } catch (error) {
    ElMessage.error('加载课程列表失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    // TODO: 调用API创建耗材
    // await api.createConsumable(form)
    
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