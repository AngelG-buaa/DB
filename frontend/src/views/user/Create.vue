<template>
  <div class="user-create">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>新增用户</span>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="user-form"
      >
        <el-form-item label="用户名" prop="user_name">
          <el-input
            v-model="form.user_name"
            placeholder="请输入用户名"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="form.email"
            placeholder="请输入邮箱"
            maxlength="100"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="用户类型" prop="user_type">
          <el-radio-group v-model="form.user_type">
            <el-radio label="Student">学生</el-radio>
            <el-radio label="Teacher">教师</el-radio>
            <el-radio label="Admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item 
          v-if="form.user_type === 'Student'" 
          label="所属课程" 
          prop="course_id"
        >
          <el-select
            v-model="form.course_id"
            placeholder="请选择课程"
            filterable
            @visible-change="onCourseSelectVisible"
          >
            <el-option
              v-for="course in courses"
              :key="course.course_id"
              :label="course.course_name"
              :value="course.course_id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item 
          v-if="form.user_type === 'Student'" 
          label="专业" 
          prop="major"
        >
          <el-input
            v-model="form.major"
            placeholder="请输入专业"
            maxlength="100"
          />
        </el-form-item>
        
        <el-form-item 
          v-if="form.user_type === 'Student'" 
          label="年级" 
          prop="grade"
        >
          <el-select
            v-model="form.grade"
            placeholder="请选择年级"
          >
            <el-option
              v-for="year in gradeOptions"
              :key="year"
              :label="`${year}级`"
              :value="year"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item 
          v-if="form.user_type === 'Teacher'" 
          label="所属院系" 
          prop="department"
        >
          <el-input
            v-model="form.department"
            placeholder="请输入所属院系"
            maxlength="100"
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
import { getCoursesApi } from '@/api/course'
import { registerApi } from '@/api/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const courses = ref([])
const coursesLoaded = ref(false)

const form = reactive({
  user_name: '',
  email: '',
  password: '',
  confirmPassword: '',
  user_type: 'Student',
  course_id: null,
  major: '',
  grade: '',
  department: ''
})

// 生成年级选项（当前年份往前推5年）
const currentYear = new Date().getFullYear()
const gradeOptions = Array.from({ length: 6 }, (_, i) => currentYear - i)

const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    if (form.confirmPassword !== '') {
      formRef.value.validateField('confirmPassword')
    }
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  user_name: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  user_type: [
    { required: true, message: '请选择用户类型', trigger: 'change' }
  ],
  course_id: [
    { 
      validator: (rule, value, callback) => {
        if (form.user_type === 'Student' && !value) {
          callback(new Error('学生必须选择所属课程'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ],
  major: [
    { 
      validator: (rule, value, callback) => {
        if (form.user_type === 'Student' && !value) {
          callback(new Error('请输入专业'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  grade: [
    { 
      validator: (rule, value, callback) => {
        if (form.user_type === 'Student' && !value) {
          callback(new Error('请选择年级'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ],
  department: [
    { 
      validator: (rule, value, callback) => {
        if (form.user_type === 'Teacher' && !value) {
          callback(new Error('请输入所属院系'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 监听用户类型变化，清空相关字段
watch(() => form.user_type, (newVal) => {
  if (newVal !== 'Student') {
    form.course_id = null
    form.major = ''
    form.grade = ''
  }
  if (newVal !== 'Teacher') {
    form.department = ''
  }
  if (newVal === 'Student' && !coursesLoaded.value) {
    loadCourses()
  }
})

const loadCourses = async () => {
  try {
    const res = await getCoursesApi({ page: 1, page_size: 100 })
    if (res.code === 200) {
      courses.value = (res.data.list || []).map(c => ({ course_id: c.id, course_name: c.name }))
      coursesLoaded.value = true
    } else {
      ElMessage.error(res.message || '加载课程列表失败')
    }
  } catch (error) {
    ElMessage.error('加载课程列表失败')
  }
}

const onCourseSelectVisible = (visible) => {
  if (visible && form.user_type === 'Student' && !coursesLoaded.value) {
    loadCourses()
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 构建提交数据
    const submitData = {
      username: form.user_name,
      name: form.user_name,
      real_name: form.user_name,
      email: form.email,
      password: form.password,
      role: (form.user_type || '').toLowerCase()
    }
    
    if (form.user_type === 'Student') {
      submitData.course_id = form.course_id
      submitData.major = form.major
      submitData.grade = form.grade
    } else if (form.user_type === 'Teacher') {
      submitData.department = form.department
    }
    
    const res = await registerApi(submitData)
    if (res.code === 200) {
      ElMessage.success('用户创建成功')
      router.push('/user/list')
    }
  } catch (error) {
    const msg = error?.message || '创建失败，请重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.back()
}

onMounted(() => {
})
</script>

<style scoped>
.user-create {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-form {
  max-width: 600px;
}
</style>