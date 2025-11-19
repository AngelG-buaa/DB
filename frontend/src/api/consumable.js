import { http } from './request'

// 耗材管理
export const getConsumables = (params) => {
  return http.get('/consumables', params)
}

export const createConsumable = (data) => {
  return http.post('/consumables', data)
}

export const updateConsumable = (id, data) => {
  return http.put(`/consumables/${id}`, data)
}

export const deleteConsumable = (id) => {
  return http.delete(`/consumables/${id}`)
}

export const useConsumable = (id, data) => {
  return http.post(`/consumables/${id}/use`, data)
}

export const restockConsumable = (id, data) => {
  return http.post(`/consumables/${id}/restock`, data)
}

export const getConsumableStats = () => {
  return http.get('/consumables/stats')
}

// 耗材使用记录
export const getConsumableUsageRecords = (params) => {
  return http.get('/consumables/usage', params)
}

export const createConsumableUsage = (data) => {
  return http.post('/consumables/usage', data)
}

export const updateConsumableUsage = (id, data) => {
  return http.put(`/consumables/usage/${id}`, data)
}

export const deleteConsumableUsage = (id) => {
  return http.delete(`/consumables/usage/${id}`)
}

export const getConsumableUsageStats = () => {
  return http.get('/consumables/usage/stats')
}

export const exportConsumableUsage = (params) => {
  return http.download('/consumables/usage/export', params)
}