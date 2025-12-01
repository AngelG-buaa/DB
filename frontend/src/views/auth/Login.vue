<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-left">
        <div class="brand">
          <img src="/logo.svg" alt="Logo" class="logo" />
          <h1 class="title">Lab Management</h1>
        </div>
        <div class="illustration">
          <h2>高校实验室预约与<br>设备管理系统</h2>
          <p>高效 • 便捷 • 智能</p>
        </div>
      </div>
      
      <div class="login-right">
        <div class="login-box">
          <div class="login-header">
            <h2>欢迎登录</h2>
            <p>请输入您的账号和密码</p>
          </div>
          
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @keyup.enter="handleLogin"
            size="large"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                prefix-icon="User"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            
            <el-form-item prop="userType">
              <el-select
                v-model="loginForm.userType"
                placeholder="用户类型"
                style="width: 100%"
              >
                <el-option label="学生" value="student" />
                <el-option label="教师" value="teacher" />
                <el-option label="管理员" value="admin" />
              </el-select>
            </el-form-item>
            
            <div class="form-options">
              <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
              <el-link type="primary" @click="handleForgotPassword">忘记密码？</el-link>
            </div>
            
            <el-button
              type="primary"
              :loading="loading"
              @click="handleLogin"
              class="login-btn"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
            
            <div class="register-link">
              还没有账号？
              <el-link type="primary" @click="goToRegister">立即注册</el-link>
            </div>
          </el-form>
          
          <!-- 快速登录提示 -->
          <div class="quick-login">
            <el-divider>快速体验</el-divider>
            <div class="demo-accounts">
              <el-button text bg size="small" @click="quickLogin('admin')">管理员</el-button>
              <el-button text bg size="small" @click="quickLogin('teacher')">教师</el-button>
              <el-button text bg size="small" @click="quickLogin('student')">学生</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  userType: '',
  rememberMe: false
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  userType: [{ required: true, message: '请选择用户类型', trigger: 'change' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(loginForm)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        // 错误处理已在 store 中完成
      } finally {
        loading.value = false
      }
    }
  })
}

const handleForgotPassword = () => {
  router.push('/forgot-password')
}

const goToRegister = () => {
  router.push('/register')
}

const quickLogin = (role) => {
  loginForm.userType = role
  if (role === 'admin') {
    loginForm.username = 'admin'
    loginForm.password = '123456'
  } else if (role === 'teacher') {
    loginForm.username = 'teacher1'
    loginForm.password = '123456'
  } else {
    loginForm.username = 'student1'
    loginForm.password = '123456'
  }
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  
  .login-content {
    display: flex;
    width: 1000px;
    height: 600px;
    background: #fff;
    border-radius: 24px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
    overflow: hidden;
    
    .login-left {
      flex: 1;
      background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
      padding: 40px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      color: #fff;
      position: relative;
      overflow: hidden;
      
      &::before {
        content: '';
        position: absolute;
        top: -50px;
        left: -50px;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
      }
      
      &::after {
        content: '';
        position: absolute;
        bottom: -50px;
        right: -50px;
        width: 300px;
        height: 300px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
      }
      
      .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 1;
        
        .logo {
          height: 40px;
          filter: brightness(0) invert(1);
        }
        
        .title {
          font-size: 24px;
          font-weight: 700;
          margin: 0;
        }
      }
      
      .illustration {
        z-index: 1;
        h2 {
          font-size: 40px;
          line-height: 1.2;
          margin-bottom: 20px;
          font-weight: 800;
        }
        
        p {
          font-size: 18px;
          opacity: 0.9;
          letter-spacing: 2px;
        }
      }
    }
    
    .login-right {
      flex: 1;
      padding: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .login-box {
        width: 100%;
        max-width: 360px;
        
        .login-header {
          margin-bottom: 30px;
          text-align: center;
          
          h2 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            color: var(--text-primary);
          }
          
          p {
            color: var(--text-secondary);
          }
        }
        
        .login-btn {
          width: 100%;
          height: 44px;
          font-size: 16px;
          margin-top: 20px;
          border-radius: 8px;
        }
        
        .form-options {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }
        
        .register-link {
          margin-top: 16px;
          text-align: center;
          font-size: 14px;
          color: var(--text-regular);
        }
        
        .quick-login {
          margin-top: 40px;
          
          .demo-accounts {
            display: flex;
            justify-content: center;
            gap: 10px;
          }
        }
      }
    }
  }
}

// 响应式调整
@media (max-width: 768px) {
  .login-container {
    .login-content {
      width: 100%;
      height: auto;
      flex-direction: column;
      
      .login-left {
        display: none;
      }
      
      .login-right {
        padding: 30px 20px;
      }
    }
  }
}
</style>