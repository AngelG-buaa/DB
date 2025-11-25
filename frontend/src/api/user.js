import { http } from './request'

// 用户列表（用于用户管理/教师下拉）
export const getUsersApi = (params) => {
  return http.get('/users', params)
}

// 删除用户
export const deleteUserApi = (id) => {
  return http.delete(`/users/${id}`)
}

// 创建用户
export const createUserApi = (data) => {
  return http.post('/users', data)
}

// 获取用户详情
export const getUserByIdApi = (id) => {
  return http.get(`/users/${id}`)
}

// 更新用户
export const updateUserApi = (id, data) => {
  return http.put(`/users/${id}`, data)
}
