<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <img src="/logo.svg" alt="Logo" class="logo" />
        <h1 class="title">用户注册</h1>
        <p class="subtitle">创建您的账户</p>
      </div>
      
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        label-width="80px"
      >
        <el-form-item label="用户类型" prop="userType">
          <el-radio-group v-model="registerForm.userType">
            <el-radio label="student">学生</el-radio>
            <el-radio label="teacher">教师</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="真实姓名" prop="realName">
          <el-input
            v-model="registerForm.realName"
            placeholder="请输入真实姓名"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱地址"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入手机号"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item label="学院" prop="department">
          <el-select
            v-model="registerForm.department"
            placeholder="请选择学院"
            style="width: 100%"
          >
            <el-option label="计算机科学与技术学院" value="计算机科学与技术学院" />
            <el-option label="电子工程学院" value="电子工程学院" />
            <el-option label="物理学院" value="物理学院" />
            <el-option label="化学学院" value="化学学院" />
            <el-option label="生物学院" value="生物学院" />
            <el-option label="数学学院" value="数学学院" />
            <el-option label="材料科学与工程学院" value="材料科学与工程学院" />
          </el-select>
        </el-form-item>
        
        <!-- 学生特有字段 -->
        <template v-if="registerForm.userType === 'student'">
          <el-form-item label="学号" prop="studentId">
            <el-input
              v-model="registerForm.studentId"
              placeholder="请输入学号"
              clearable
            />
          </el-form-item>
          
          <el-form-item label="专业" prop="major">
            <el-input
              v-model="registerForm.major"
              placeholder="请输入专业"
              clearable
            />
          </el-form-item>
          
          <el-form-item label="年级" prop="grade">
            <el-select
              v-model="registerForm.grade"
              placeholder="请选择年级"
              style="width: 100%"
            >
              <el-option
                v-for="year in gradeOptions"
                :key="year"
                :label="`${year}级`"
                :value="year"
              />
            </el-select>
          </el-form-item>
        </template>
        
        <!-- 教师特有字段 -->
        <template v-if="registerForm.userType === 'teacher'">
          <el-form-item label="工号" prop="employeeId">
            <el-input
              v-model="registerForm.employeeId"
              placeholder="请输入工号"
              clearable
            />
          </el-form-item>
        </template>
        
        <el-form-item>
          <el-checkbox v-model="registerForm.agreeTerms">
            我已阅读并同意
            <el-link type="primary" @click="showTerms">《用户协议》</el-link>
          </el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRegister"
            class="register-btn"
          >
            {{ loading ? '注册中...' : '注册' }}
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <div class="login-link">
            已有账号？
            <el-link type="primary" @click="goToLogin">立即登录</el-link>
          </div>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 用户协议对话框 -->
    <el-dialog
      v-model="termsDialogVisible"
      title="用户协议"
      width="600px"
      :before-close="handleCloseTerms"
    >
      <div class="terms-content">
        <h3>高校实验室预约与设备管理系统用户协议</h3>
        <p>欢迎使用高校实验室预约与设备管理系统！在使用本系统前，请仔细阅读以下条款：</p>
        
        <h4>1. 服务条款</h4>
        <p>本系统为高校师生提供实验室预约、设备管理等服务。用户应遵守学校相关规定，合理使用系统功能。</p>
        
        <h4>2. 用户责任</h4>
        <p>用户应保证注册信息的真实性和准确性，妥善保管账户信息，不得将账户借给他人使用。</p>
        
        <h4>3. 预约规则</h4>
        <p>用户应按时使用已预约的实验室，如需取消预约请提前通知。恶意占用资源的行为将被限制使用权限。</p>
        
        <h4>4. 设备使用</h4>
        <p>用户应爱护实验室设备，按规范操作。如发现设备故障应及时报告，损坏设备需承担相应责任。</p>
        
        <h4>5. 隐私保护</h4>
        <p>我们承诺保护用户隐私，不会泄露用户个人信息。系统收集的数据仅用于提供服务和改进功能。</p>
        
        <h4>6. 免责声明</h4>
        <p>系统维护期间可能暂停服务，由此造成的不便敬请谅解。我们不对因不可抗力导致的服务中断承担责任。</p>
        
        <p>如有疑问，请联系系统管理员。</p>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="termsDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { registerApi } from '@/api/auth'

const router = useRouter()

// 响应式数据
const registerFormRef = ref()
const loading = ref(false)
const termsDialogVisible = ref(false)

const registerForm = reactive({
  userType: 'student',
  username: '',
  realName: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  department: '',
  studentId: '',
  major: '',
  grade: null,
  employeeId: '',
  agreeTerms: false
})

// 年级选项
const gradeOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 6 }, (_, i) => currentYear - i)
})

// 自定义验证函数
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateStudentId = (rule, value, callback) => {
  if (registerForm.userType === 'student' && !value) {
    callback(new Error('请输入学号'))
  } else {
    callback()
  }
}

const validateEmployeeId = (rule, value, callback) => {
  if (registerForm.userType === 'teacher' && !value) {
    callback(new Error('请输入工号'))
  } else {
    callback()
  }
}

const validateMajor = (rule, value, callback) => {
  if (registerForm.userType === 'student' && !value) {
    callback(new Error('请输入专业'))
  } else {
    callback()
  }
}

const validateGrade = (rule, value, callback) => {
  if (registerForm.userType === 'student' && !value) {
    callback(new Error('请选择年级'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules = {
  userType: [
    { required: true, message: '请选择用户类型', trigger: 'change' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度在 2 到 10 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度在 8 到 20 个字符', trigger: 'blur' },
    { pattern: /^(?=.*[a-zA-Z])(?=.*[0-9]).*$/, message: '密码必须包含字母和数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择学院', trigger: 'change' }
  ],
  studentId: [
    { validator: validateStudentId, trigger: 'blur' }
  ],
  major: [
    { validator: validateMajor, trigger: 'blur' }
  ],
  grade: [
    { validator: validateGrade, trigger: 'change' }
  ],
  employeeId: [
    { validator: validateEmployeeId, trigger: 'blur' }
  ]
}

// 方法
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  if (!registerForm.agreeTerms) {
    ElMessage.warning('请先阅读并同意用户协议')
    return
  }
  
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    const registerData = {
      username: registerForm.username,
      password: registerForm.password,
      real_name: registerForm.realName,
      email: registerForm.email,
      phone: registerForm.phone,
      user_type: registerForm.userType,
      department: registerForm.department
    }
    
    // 根据用户类型添加特定字段
    if (registerForm.userType === 'student') {
      registerData.student_id = registerForm.studentId
      registerData.major = registerForm.major
      registerData.grade = registerForm.grade
    } else if (registerForm.userType === 'teacher') {
      registerData.employee_id = registerForm.employeeId
    }
    
    const response = await registerApi(registerData)
    
    if (response.code === 200) {
      ElMessage.success('注册成功，请等待管理员审核')
      router.push('/login')
    }
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}

const showTerms = () => {
  termsDialogVisible.value = true
}

const handleCloseTerms = () => {
  termsDialogVisible.value = false
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
}

.register-box {
  width: 500px;
  max-width: 90%;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
  
  .logo {
    height: 50px;
    margin-bottom: 16px;
  }
  
  .title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }
  
  .subtitle {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.register-form {
  .el-form-item {
    margin-bottom: 18px;
  }
  
  .register-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
    font-weight: 600;
  }
  
  .login-link {
    text-align: center;
    color: #909399;
    font-size: 14px;
  }
}

.terms-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 0 10px;
  
  h3 {
    color: #303133;
    margin-bottom: 16px;
  }
  
  h4 {
    color: #606266;
    margin: 16px 0 8px 0;
  }
  
  p {
    color: #606266;
    line-height: 1.6;
    margin-bottom: 12px;
  }
}

// 响应式设计
@media (max-width: 600px) {
  .register-box {
    width: 95%;
    padding: 30px 20px;
  }
  
  .register-header .title {
    font-size: 20px;
  }
}
</style>