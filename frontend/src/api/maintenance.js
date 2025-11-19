import { http } from './request'

export const createMaintenanceRecordApi = (data) => {
  return http.post('/equipment/maintenance', data)
}

export const updateMaintenanceRecordApi = (id, data) => {
  return http.put(`/equipment/maintenance/${id}`, data)
}

// 设备维修列表与统计等（供维修页面使用）
export const getMaintenanceRecordsApi = (params) => {
  return http.get('/equipment/maintenance', params)
}

export const getMaintenanceRecordByIdApi = (id) => {
  return http.get(`/equipment/maintenance/${id}`)
}

export const deleteMaintenanceRecordApi = (id) => {
  return http.delete(`/equipment/maintenance/${id}`)
}

export const completeMaintenanceRecordApi = (id, data = {}) => {
  return http.post(`/equipment/maintenance/${id}/complete`, data)
}

export const getMaintenanceStatsApi = (params) => {
  return http.get('/equipment/maintenance/stats', params)
}