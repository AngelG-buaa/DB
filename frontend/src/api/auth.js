import { http } from './request'

// 用户登录
export const loginApi = (data) => {
  return http.post('/auth/login', data)
}

// 用户注册
export const registerApi = (data) => {
  return http.post('/auth/register', data)
}

// 用户退出登录
export const logoutApi = () => {
  return http.post('/auth/logout')
}

// 获取用户信息
export const getUserInfoApi = () => {
  // 后端对应接口为 /api/auth/profile
  return http.get('/auth/profile')
}

// 修改密码
export const changePasswordApi = (data) => {
  return http.post('/auth/change-password', data)
}

// 更新用户信息
export const updateUserInfoApi = (data) => {
  // 后端对应接口为 /api/auth/profile
  return http.put('/auth/profile', data)
}

// 刷新token
export const refreshTokenApi = () => {
  return http.post('/auth/refresh-token')
}

// 忘记密码
export const forgotPasswordApi = (data) => {
  return http.post('/auth/forgot-password', data)
}

// 重置密码
export const resetPasswordApi = (data) => {
  return http.post('/auth/reset-password', data)
}