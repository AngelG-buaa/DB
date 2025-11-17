<template>
  <div class="error-page">
    <div class="error-container">
      <div class="error-image">
        <svg viewBox="0 0 404 300" class="error-svg">
          <!-- 404数字 -->
          <text x="50%" y="40%" text-anchor="middle" class="error-number">404</text>
          
          <!-- 装饰性元素 -->
          <circle cx="100" cy="200" r="20" class="decoration-circle" />
          <circle cx="300" cy="180" r="15" class="decoration-circle" />
          <rect x="150" y="220" width="100" height="20" rx="10" class="decoration-rect" />
          
          <!-- 实验室相关图标 -->
          <g transform="translate(180, 160)">
            <!-- 烧杯 -->
            <path d="M10 10 L30 10 L35 40 L5 40 Z" fill="#409EFF" opacity="0.6" />
            <circle cx="20" cy="25" r="3" fill="#67C23A" opacity="0.8" />
          </g>
          
          <g transform="translate(220, 170)">
            <!-- 试管 -->
            <rect x="0" y="0" width="8" height="30" rx="4" fill="#E6A23C" opacity="0.6" />
            <rect x="0" y="20" width="8" height="10" fill="#F56C6C" opacity="0.8" />
          </g>
        </svg>
      </div>
      
      <div class="error-content">
        <h1 class="error-title">页面未找到</h1>
        <p class="error-description">
          抱歉，您访问的页面不存在或已被移除。
        </p>
        <p class="error-suggestion">
          可能的原因：
        </p>
        <ul class="error-reasons">
          <li>页面地址输入错误</li>
          <li>页面已被删除或移动</li>
          <li>您没有访问权限</li>
          <li>系统正在维护中</li>
        </ul>
        
        <div class="error-actions">
          <el-button type="primary" @click="goHome" size="large">
            <el-icon><House /></el-icon>
            返回首页
          </el-button>
          <el-button @click="goBack" size="large">
            <el-icon><ArrowLeft /></el-icon>
            返回上页
          </el-button>
          <el-button @click="refresh" size="large">
            <el-icon><Refresh /></el-icon>
            刷新页面
          </el-button>
        </div>
        
        <div class="error-help">
          <p>如果问题持续存在，请联系系统管理员</p>
          <div class="contact-info">
            <el-tag type="info">邮箱: admin@lab-system.com</el-tag>
            <el-tag type="info">电话: 400-123-4567</el-tag>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-element" v-for="i in 6" :key="i" :style="getFloatingStyle(i)">
        <div class="lab-icon">
          <svg width="30" height="30" viewBox="0 0 30 30">
            <circle cx="15" cy="15" r="12" fill="none" stroke="#409EFF" stroke-width="2" opacity="0.3" />
            <path d="M10 15 L15 10 L20 15 L15 20 Z" fill="#409EFF" opacity="0.2" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { House, ArrowLeft, Refresh } from '@element-plus/icons-vue'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goHome()
  }
}

const refresh = () => {
  window.location.reload()
}

const getFloatingStyle = (index) => {
  const positions = [
    { top: '10%', left: '10%', animationDelay: '0s' },
    { top: '20%', right: '15%', animationDelay: '1s' },
    { top: '60%', left: '5%', animationDelay: '2s' },
    { bottom: '20%', right: '10%', animationDelay: '3s' },
    { bottom: '10%', left: '20%', animationDelay: '4s' },
    { top: '40%', right: '5%', animationDelay: '5s' }
  ]
  
  return {
    ...positions[index - 1],
    position: 'absolute',
    animation: `float 6s ease-in-out infinite`,
    animationDelay: positions[index - 1].animationDelay
  }
}
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
  overflow: hidden;
}

.error-container {
  display: flex;
  align-items: center;
  gap: 60px;
  max-width: 1000px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  z-index: 1;
}

.error-image {
  flex-shrink: 0;
}

.error-svg {
  width: 300px;
  height: 200px;
}

.error-number {
  font-size: 80px;
  font-weight: bold;
  fill: #409EFF;
  opacity: 0.8;
}

.decoration-circle {
  fill: #67C23A;
  opacity: 0.6;
  animation: pulse 2s ease-in-out infinite;
}

.decoration-rect {
  fill: #E6A23C;
  opacity: 0.6;
  animation: pulse 2s ease-in-out infinite 1s;
}

.error-content {
  flex: 1;
  text-align: left;
}

.error-title {
  font-size: 36px;
  color: #303133;
  margin-bottom: 16px;
  font-weight: 600;
}

.error-description {
  font-size: 18px;
  color: #606266;
  margin-bottom: 20px;
  line-height: 1.6;
}

.error-suggestion {
  font-size: 16px;
  color: #909399;
  margin-bottom: 12px;
  font-weight: 500;
}

.error-reasons {
  list-style: none;
  padding: 0;
  margin-bottom: 30px;
}

.error-reasons li {
  padding: 8px 0;
  color: #606266;
  position: relative;
  padding-left: 20px;
}

.error-reasons li::before {
  content: '•';
  color: #409EFF;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.error-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.error-help {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.error-help p {
  color: #909399;
  margin-bottom: 12px;
}

.contact-info {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.floating-element {
  position: absolute;
}

.lab-icon {
  animation: rotate 10s linear infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  33% {
    transform: translateY(-20px) rotate(120deg);
  }
  66% {
    transform: translateY(10px) rotate(240deg);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-container {
    flex-direction: column;
    gap: 30px;
    padding: 20px;
    margin: 20px;
  }
  
  .error-svg {
    width: 250px;
    height: 150px;
  }
  
  .error-number {
    font-size: 60px;
  }
  
  .error-title {
    font-size: 28px;
    text-align: center;
  }
  
  .error-actions {
    justify-content: center;
  }
  
  .contact-info {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .error-actions {
    flex-direction: column;
  }
  
  .error-actions .el-button {
    width: 100%;
  }
}
</style>