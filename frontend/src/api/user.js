import { http } from './request'

// 用户列表（用于用户管理/教师下拉）
export const getUsersApi = (params) => {
  return http.get('/users', params)
}

// 删除用户
export const deleteUserApi = (id) => {
  return http.delete(`/users/${id}`)
}