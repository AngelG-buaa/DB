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
        
        <el-form-item label="是否需要实验室">
          <el-switch
            v-model="form.requires_lab"
            active-text="需要"
            inactive-text="不需要"
          />
        </el-form-item>
        <el-form-item v-if="form.requires_lab" label="关联实验室" prop="laboratory_id">
          <el-select
            v-model="form.laboratory_id"
            placeholder="请选择实验室"
            filterable
            style="width: 300px"
          >
            <el-option
              v-for="lab in labs"
              :key="lab.id"
              :label="lab.name"
              :value="lab.id"
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
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const teachers = ref([])
const labs = ref([])
const route = useRoute()

const form = reactive({
  course_name: '',
  credit: 1,
  teacher_id: null,
  description: '',
  requires_lab: false,
  laboratory_id: null
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
  laboratory_id: [
    {
      validator: (_rule, value, callback) => {
        if (form.requires_lab && !value) {
          callback(new Error('请选择关联实验室'))
          return
        }
        callback()
      },
      trigger: 'change'
    }
  ]
}


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

const loadLabs = async () => {
  try {
    const api = await import('@/api/lab')
    const res = await api.getLabsApi({ page: 1, page_size: 500 })
    if (res.code === 200) {
      labs.value = (res.data.list || []).map(l => ({ id: l.id, name: l.name }))
    }
  } catch (error) {
    ElMessage.error('加载实验室列表失败')
  }
}

const isEdit = ref(false)
const courseId = ref(null)
const dialogTitle = ref('新增课程')

const loadCourseDetail = async (id) => {
  try {
    const api = await import('@/api/course')
    const res = await api.getCourseByIdApi(id)
    if (res.code === 200 && res.data) {
      const d = res.data
      form.course_name = d.name || ''
      form.credit = d.credits || 1
      form.teacher_id = d.teacher?.id || null
      form.description = d.description || ''
      form.requires_lab = !!d.requires_lab
      form.laboratory_id = d.laboratory_id || null
    }
  } catch (error) {
    ElMessage.error('加载课程详情失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    const api = await import('@/api/course')
    if (isEdit.value && courseId.value) {
      const payload = {
        name: form.course_name,
        description: form.description,
        credits: form.credit,
        teacher_id: form.teacher_id,
        status: 'active',
        requires_lab: form.requires_lab ? 1 : 0,
        laboratory_id: form.requires_lab ? form.laboratory_id : null
      }
      const res = await api.updateCourseApi(courseId.value, payload)
      if (res.code === 200) {
        ElMessage.success('课程更新成功')
        router.push('/course/list')
      }
    } else {
      const semester = `${new Date().getFullYear()}秋`
      const code = `C${Date.now()}`
      const payload = {
        name: form.course_name,
        code,
        description: form.description,
        credits: form.credit,
        semester,
        teacher_id: form.teacher_id,
        status: 'active',
        requires_lab: form.requires_lab ? 1 : 0,
        laboratory_id: form.requires_lab ? form.laboratory_id : null
      }
      const res = await api.createCourseApi(payload)
      if (res.code === 200) {
        ElMessage.success('课程创建成功')
        router.push('/course/list')
      }
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
  loadLabs()
  const editId = route.query?.edit
  if (editId) {
    isEdit.value = true
    courseId.value = Number(editId)
    dialogTitle.value = '编辑课程'
    loadCourseDetail(courseId.value)
  }
})

watch(() => form.requires_lab, (val) => {
  if (!val) {
    form.laboratory_id = null
    // 清除潜在的校验错误
    formRef.value?.clearValidate(['laboratory_id'])
  }
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