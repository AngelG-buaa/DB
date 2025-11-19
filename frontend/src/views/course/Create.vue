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
    const api = await import('@/api/user')
    const res = await api.getUsersApi({ page: 1, page_size: 200, role: 'teacher' })
    if (res.code === 200) {
      teachers.value = (res.data.list || []).map(u => ({ user_id: u.id, user_name: u.name || u.username }))
    }
  } catch (error) {
    ElMessage.error('加载教师列表失败')
  }
}

const loadLaboratories = async () => {
  try {
    const api = await import('@/api/lab')
    const res = await api.getLabsApi({ page: 1, size: 200 })
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
    
    const api = await import('@/api/course')
    const semester = `${new Date().getFullYear()}秋`
    const code = `C${Date.now()}`
    const payload = {
      name: form.course_name,
      code,
      description: form.description,
      credits: form.credit,
      semester,
      teacher_id: form.teacher_id,
      status: 'active'
    }
    const res = await api.createCourseApi(payload)
    if (res.code === 200) {
      ElMessage.success('课程创建成功')
      router.push('/course/list')
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