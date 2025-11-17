<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
  // 应用启动时检查用户登录状态
  userStore.checkLoginStatus()
})
</script>

<style lang="scss">
#app {
  height: 100vh;
  width: 100vw;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

// 滚动条样式
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

// Element Plus 样式覆盖
.el-message {
  min-width: 300px;
}

.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.8);
}

// 响应式设计
@media (max-width: 768px) {
  .el-table {
    font-size: 12px;
  }
  
  .el-button {
    padding: 8px 12px;
    font-size: 12px;
  }
}
</style>