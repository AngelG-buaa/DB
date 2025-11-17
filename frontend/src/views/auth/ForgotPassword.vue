<template>
  <div class="forgot-password-container">
    <div class="forgot-password-box">
      <div class="forgot-password-header">
        <img src="/logo.svg" alt="Logo" class="logo" />
        <h1 class="title">找回密码</h1>
        <p class="subtitle">请输入您的邮箱地址，我们将发送重置密码的链接</p>
      </div>
      
      <el-form
        ref="forgotPasswordFormRef"
        :model="forgotPasswordForm"
        :rules="forgotPasswordRules"
        class="forgot-password-form"
        label-width="0"
      >
        <el-form-item prop="email">
          <el-input
            v-model="forgotPasswordForm.email"
            placeholder="请输入邮箱地址"
            size="large"
            clearable
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleForgotPassword"
            class="forgot-password-btn"
          >
            {{ loading ? '发送中...' : '发送重置链接' }}
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <div class="back-to-login">
            <el-link type="primary" @click="goToLogin">
              <el-icon><ArrowLeft /></el-icon>
              返回登录
            </el-link>
          </div>
        </el-form-item>
      </el-form>
      
      <!-- 成功提示 -->
      <div v-if="emailSent" class="success-message">
        <el-icon class="success-icon"><CircleCheck /></el-icon>
        <h3>邮件已发送</h3>
        <p>我们已向 <strong>{{ forgotPasswordForm.email }}</strong> 发送了重置密码的链接</p>
        <p class="tip">请检查您的邮箱（包括垃圾邮件文件夹），并点击链接重置密码</p>
        
        <div class="resend-section">
          <p>没有收到邮件？</p>
          <el-button
            type="text"
            :disabled="countdown > 0"
            @click="handleResend"
          >
            {{ countdown > 0 ? `${countdown}秒后可重新发送` : '重新发送' }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Message, ArrowLeft, CircleCheck } from '@element-plus/icons-vue'
import { forgotPasswordApi } from '@/api/auth'

const router = useRouter()

// 响应式数据
const forgotPasswordFormRef = ref()
const loading = ref(false)
const emailSent = ref(false)
const countdown = ref(0)
let countdownTimer = null

const forgotPasswordForm = reactive({
  email: ''
})

// 表单验证规则
const forgotPasswordRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 方法
const handleForgotPassword = async () => {
  if (!forgotPasswordFormRef.value) return
  
  try {
    await forgotPasswordFormRef.value.validate()
    loading.value = true
    
    const response = await forgotPasswordApi({
      email: forgotPasswordForm.email
    })
    
    if (response.code === 200) {
      emailSent.value = true
      startCountdown()
      ElMessage.success('重置密码邮件已发送')
    }
  } catch (error) {
    console.error('发送重置邮件失败:', error)
  } finally {
    loading.value = false
  }
}

const handleResend = async () => {
  if (countdown.value > 0) return
  
  try {
    loading.value = true
    
    const response = await forgotPasswordApi({
      email: forgotPasswordForm.email
    })
    
    if (response.code === 200) {
      startCountdown()
      ElMessage.success('重置密码邮件已重新发送')
    }
  } catch (error) {
    console.error('重新发送邮件失败:', error)
  } finally {
    loading.value = false
  }
}

const startCountdown = () => {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

const goToLogin = () => {
  router.push('/login')
}

// 清理定时器
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style lang="scss" scoped>
.forgot-password-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.forgot-password-box {
  width: 400px;
  max-width: 90%;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.forgot-password-header {
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
    line-height: 1.5;
  }
}

.forgot-password-form {
  .el-form-item {
    margin-bottom: 20px;
  }
  
  .forgot-password-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
    font-weight: 600;
  }
  
  .back-to-login {
    text-align: center;
    
    .el-link {
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
  }
}

.success-message {
  text-align: center;
  
  .success-icon {
    font-size: 48px;
    color: #67c23a;
    margin-bottom: 16px;
  }
  
  h3 {
    font-size: 20px;
    color: #303133;
    margin-bottom: 16px;
  }
  
  p {
    color: #606266;
    line-height: 1.6;
    margin-bottom: 12px;
    
    &.tip {
      font-size: 14px;
      color: #909399;
      margin-bottom: 24px;
    }
  }
  
  .resend-section {
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
    
    p {
      margin-bottom: 8px;
      font-size: 14px;
    }
  }
}

// 响应式设计
@media (max-width: 480px) {
  .forgot-password-box {
    width: 95%;
    padding: 30px 20px;
  }
  
  .forgot-password-header .title {
    font-size: 20px;
  }
  
  .forgot-password-header .subtitle {
    font-size: 13px;
  }
}
</style>