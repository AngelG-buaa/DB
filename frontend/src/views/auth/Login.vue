<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img src="/logo.svg" alt="Logo" class="logo" />
        <h1 class="title">高校实验室预约与设备管理系统</h1>
        <p class="subtitle">Laboratory Reservation & Equipment Management System</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="userType">
          <el-select
            v-model="loginForm.userType"
            placeholder="请选择用户类型"
            size="large"
            style="width: 100%"
          >
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <div class="form-options">
            <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
            <el-link type="primary" @click="handleForgotPassword">忘记密码？</el-link>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-btn"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <div class="register-link">
            还没有账号？
            <el-link type="primary" @click="goToRegister">立即注册</el-link>
          </div>
        </el-form-item>
      </el-form>
      
      <!-- 快速登录提示 -->
      <div class="quick-login">
        <el-divider>快速体验</el-divider>
        <div class="demo-accounts">
          <el-button
            type="info"
            plain
            size="small"
            @click="quickLogin('admin')"
          >
            管理员登录
          </el-button>
          <el-button
            type="success"
            plain
            size="small"
            @click="quickLogin('teacher')"
          >
            教师登录
          </el-button>
          <el-button
            type="warning"
            plain
            size="small"
            @click="quickLogin('student')"
          >
            学生登录
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="decoration-item item-1"></div>
      <div class="decoration-item item-2"></div>
      <div class="decoration-item item-3"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  userType: 'student',
  rememberMe: false
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  userType: [
    { required: true, message: '请选择用户类型', trigger: 'change' }
  ]
}

// 方法
const handleLogin = async () => {
  // 防抖：避免并发触发导致重复调用
  if (loading.value) return
  loading.value = true
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    
    await userStore.login(loginForm)
    
    // 登录成功，跳转到首页
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}

const quickLogin = (userType) => {
  // 与后端 init_database.py 中初始化的示例账号保持一致
  const demoAccounts = {
    admin: { username: 'admin', password: 'admin123' },
    teacher: { username: 'teacher', password: 'teacher123' },
    student: { username: 'student', password: 'student123' }
  }
  
  const account = demoAccounts[userType]
  if (account) {
    loginForm.username = account.username
    loginForm.password = account.password
    loginForm.userType = userType
    handleLogin()
  }
}

const handleForgotPassword = () => {
  ElMessage.info('请联系管理员重置密码')
}

const goToRegister = () => {
  router.push('/register')
}

// 生命周期
onMounted(() => {
  // 如果已经登录，直接跳转到首页
  if (userStore.isAuthenticated) {
    router.push('/')
  }
})
</script>

<style lang="scss" scoped>
.login-container {
  position: relative;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.login-box {
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  z-index: 10;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
  
  .logo {
    height: 60px;
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

.login-form {
  .el-form-item {
    margin-bottom: 20px;
  }
  
  .form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }
  
  .login-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
    font-weight: 600;
  }
  
  .register-link {
    text-align: center;
    color: #909399;
    font-size: 14px;
  }
}

.quick-login {
  margin-top: 20px;
  
  .demo-accounts {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    
    .el-button {
      flex: 1;
    }
  }
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  
  .decoration-item {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    animation: float 6s ease-in-out infinite;
    
    &.item-1 {
      width: 200px;
      height: 200px;
      top: 10%;
      left: 10%;
      animation-delay: 0s;
    }
    
    &.item-2 {
      width: 150px;
      height: 150px;
      top: 60%;
      right: 15%;
      animation-delay: 2s;
    }
    
    &.item-3 {
      width: 100px;
      height: 100px;
      bottom: 20%;
      left: 20%;
      animation-delay: 4s;
    }
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

// 响应式设计
@media (max-width: 480px) {
  .login-box {
    width: 90%;
    padding: 30px 20px;
  }
  
  .login-header .title {
    font-size: 20px;
  }
  
  .quick-login .demo-accounts {
    flex-direction: column;
    gap: 8px;
  }
}
</style>