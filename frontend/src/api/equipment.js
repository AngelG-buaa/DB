import { http } from './request'

// 设备相关API
export const getEquipmentApi = (params) => {
  return http.get('/equipment', params)
}

export const getEquipmentByIdApi = (id) => {
  return http.get(`/equipment/${id}`)
}

export const createEquipmentApi = (data) => {
  return http.post('/equipment', data)
}

export const updateEquipmentApi = (id, data) => {
  return http.put(`/equipment/${id}`, data)
}

export const deleteEquipmentApi = (id) => {
  return http.delete(`/equipment/${id}`)
}

export const getEquipmentMaintenanceApi = (id) => {
  return http.get(`/equipment/${id}/maintenance`)
}

// 设备统计信息
export const getEquipmentStatisticsApi = () => {
  return http.get('/equipment/statistics')
}