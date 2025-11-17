<template>
  <div class="course-create">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>新增课程</span>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="course-form"
      >
        <el-form-item label="课程名称" prop="course_name">
          <el-input
            v-model="form.course_name"
            placeholder="请输入课程名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="学分" prop="credit">
          <el-input-number
            v-model="form.credit"
            :min="1"
            :max="10"
            placeholder="请输入学分"
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="授课教师" prop="teacher_id">
          <el-select
            v-model="form.teacher_id"
            placeholder="请选择授课教师"
            filterable
          >
            <el-option
              v-for="teacher in teachers"
              :key="teacher.user_id"
              :label="teacher.user_name"
              :value="teacher.user_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="需要实验室" prop="need_lab">
          <el-radio-group v-model="form.need_lab">
            <el-radio :label="true">是</el-radio>
            <el-radio :label="false">否</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item 
          v-if="form.need_lab" 
          label="关联实验室" 
          prop="lab_id"
        >
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
        
        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入课程描述（可选）"
            maxlength="500"
            show-word-limit
          />
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
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const teachers = ref([])
const laboratories = ref([])

const form = reactive({
  course_name: '',
  credit: 1,
  teacher_id: null,
  need_lab: false,
  lab_id: null,
  description: ''
})

const rules = {
  course_name: [
    { required: true, message: '请输入课程名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  credit: [
    { required: true, message: '请输入学分', trigger: 'blur' },
    { type: 'number', min: 1, max: 10, message: '学分范围为 1-10', trigger: 'blur' }
  ],
  teacher_id: [
    { required: true, message: '请选择授课教师', trigger: 'change' }
  ],
  need_lab: [
    { required: true, message: '请选择是否需要实验室', trigger: 'change' }
  ],
  lab_id: [
    { 
      validator: (rule, value, callback) => {
        if (form.need_lab && !value) {
          callback(new Error('需要实验室时必须选择实验室'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ]
}

// 监听需要实验室的变化，清空实验室选择
watch(() => form.need_lab, (newVal) => {
  if (!newVal) {
    form.lab_id = null
  }
})

const loadTeachers = async () => {
  try {
    // TODO: 调用API获取教师列表
    // const response = await api.getTeachers()
    // teachers.value = response.data
    
    // 模拟数据
    teachers.value = [
      { user_id: 1, user_name: '张教授' },
      { user_id: 2, user_name: '李教授' },
      { user_id: 3, user_name: '王老师' },
      { user_id: 4, user_name: '陈教授' }
    ]
  } catch (error) {
    ElMessage.error('加载教师列表失败')
  }
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
      { lab_id: 3, lab_name: '生物实验室C' },
      { lab_id: 4, lab_name: '计算机实验室D' }
    ]
  } catch (error) {
    ElMessage.error('加载实验室列表失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    // TODO: 调用API创建课程
    // await api.createCourse(form)
    
    ElMessage.success('课程创建成功')
    router.push('/course/list')
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
  loadTeachers()
  loadLaboratories()
})
</script>

<style scoped>
.course-create {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-form {
  max-width: 600px;
}
</style>