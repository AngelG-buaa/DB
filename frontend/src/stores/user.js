import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import Cookies from 'js-cookie'
import { loginApi, logoutApi, getUserInfoApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(Cookies.get('token') || '')
  const userInfo = ref(null)
  const permissions = ref([])
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isTeacher = computed(() => userInfo.value?.role === 'teacher')
  const isStudent = computed(() => userInfo.value?.role === 'student')
  
  // 登录
  const login = async (loginForm) => {
    try {
      const payload = { username: loginForm.username, password: loginForm.password }
      const response = await loginApi(payload)
      const ok = response.success === true || response.code === 200
      if (ok) {
        const data = response.data || {}
        const userToken = data.token || data.access_token || ''
        const info = data.user || data.profile || data
        
        token.value = userToken
        if (userToken) Cookies.set('token', userToken, { expires: 7 })
        
        userInfo.value = info
        await getUserPermissions()
        
        ElMessage.success('登录成功')
        return Promise.resolve(response)
      } else {
        ElMessage.error(response.message || '登录失败')
        return Promise.reject(response)
      }
    } catch (error) {
      return Promise.reject(error)
    }
  }
  
  // 退出登录
  const logout = async () => {
    try {
      await logoutApi()
    } catch (error) {
      console.error('退出登录接口调用失败:', error)
    } finally {
      // 清除本地数据
      token.value = ''
      userInfo.value = null
      permissions.value = []
      Cookies.remove('token')
      
      ElMessage.success('已退出登录')
    }
  }
  
  // 获取用户信息
  const getUserInfo = async () => {
    try {
      const response = await getUserInfoApi()
      if (response.success) {
        userInfo.value = response.data
        await getUserPermissions()
        return Promise.resolve(response.data)
      } else {
        return Promise.reject(response)
      }
    } catch (error) {
      // token可能已过期，清除登录状态
      await logout()
      return Promise.reject(error)
    }
  }
  
  // 获取用户权限
  const getUserPermissions = async () => {
    if (!userInfo.value) return
    
    // 根据用户类型设置权限
    const userType = userInfo.value.role
    switch (userType) {
      case 'admin':
        permissions.value = [
          'user:manage',
          'laboratory:manage',
          'equipment:manage',
          'reservation:manage',
          'consumable:manage',
          'course:manage',
          'statistics:view',
          'settings:manage'
        ]
        break
      case 'teacher':
        permissions.value = [
          'laboratory:view',
          'equipment:view',
          'equipment:maintain',
          'reservation:create',
          'reservation:approve',
          'consumable:view',
          'consumable:use',
          'course:manage',
          'statistics:view'
        ]
        break
      case 'student':
        permissions.value = [
          'laboratory:view',
          'equipment:view',
          'reservation:create',
          'reservation:view',
          'consumable:view'
        ]
        break
      default:
        permissions.value = []
    }
  }
  
  // 检查权限
  const hasPermission = (permission) => {
    return permissions.value.includes(permission)
  }
  
  // 检查角色
  const hasRole = (role) => {
    if (Array.isArray(role)) {
      return role.includes(userInfo.value?.role)
    }
    return userInfo.value?.role === role
  }
  
  // 检查登录状态
  const checkLoginStatus = async () => {
    if (token.value && !userInfo.value) {
      try {
        await getUserInfo()
      } catch (error) {
        console.error('检查登录状态失败:', error)
      }
    }
  }
  
  // 更新用户信息
  const updateUserInfo = (newUserInfo) => {
    userInfo.value = { ...userInfo.value, ...newUserInfo }
  }
  
  return {
    // 状态
    token,
    userInfo,
    permissions,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    isTeacher,
    isStudent,
    
    // 方法
    login,
    logout,
    getUserInfo,
    getUserPermissions,
    hasPermission,
    hasRole,
    checkLoginStatus,
    updateUserInfo
  }
})