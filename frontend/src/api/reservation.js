import http from './request'

// 预约相关API
export const getReservationsApi = (params) => {
  return http.get('/reservations', { params })
}

export const getReservationByIdApi = (id) => {
  return http.get(`/reservations/${id}`)
}

export const createReservationApi = (data) => {
  return http.post('/reservations', data)
}

export const updateReservationApi = (id, data) => {
  return http.put(`/reservations/${id}`, data)
}

export const deleteReservationApi = (id) => {
  return http.delete(`/reservations/${id}`)
}

export const approveReservationApi = (id, data) => {
  return http.post(`/reservations/${id}/approve`, data)
}

export const rejectReservationApi = (id, data) => {
  return http.post(`/reservations/${id}/reject`, data)
}

export const cancelReservationApi = (id, data) => {
  return http.post(`/reservations/${id}/cancel`, data)
}

export const getMyReservationsApi = (params) => {
  return http.get('/reservations/my', { params })
}

export const getReservationCalendarApi = (params) => {
  return http.get('/reservations/calendar', { params })
}

export const checkReservationConflictApi = (data) => {
  return http.post('/reservations/check-conflict', data)
}

export const getReservationStatsApi = (params) => {
  return http.get('/reservations/stats', { params })
}

// 实验室相关API
export const getLabsApi = (params) => {
  return http.get('/labs', { params })
}

export const getLabByIdApi = (id) => {
  return http.get(`/labs/${id}`)
}

export const createLabApi = (data) => {
  return http.post('/labs', data)
}

export const updateLabApi = (id, data) => {
  return http.put(`/labs/${id}`, data)
}

export const deleteLabApi = (id) => {
  return http.delete(`/labs/${id}`)
}

export const getLabAvailabilityApi = (id, params) => {
  return http.get(`/labs/${id}/availability`, { params })
}

export const getLabEquipmentApi = (id) => {
  return http.get(`/labs/${id}/equipment`)
}

export const getLabReservationsApi = (id, params) => {
  return http.get(`/labs/${id}/reservations`, { params })
}

// 设备相关API
export const getEquipmentApi = (params) => {
  return http.get('/equipment', { params })
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

export const createMaintenanceRecordApi = (data) => {
  return http.post('/equipment/maintenance', data)
}

export const updateMaintenanceRecordApi = (id, data) => {
  return http.put(`/equipment/maintenance/${id}`, data)
}

// 课程相关API
export const getCoursesApi = (params) => {
  return http.get('/courses', { params })
}

export const getCourseByIdApi = (id) => {
  return http.get(`/courses/${id}`)
}

export const createCourseApi = (data) => {
  return http.post('/courses', data)
}

export const updateCourseApi = (id, data) => {
  return http.put(`/courses/${id}`, data)
}

export const deleteCourseApi = (id) => {
  return http.delete(`/courses/${id}`)
}

export const getCourseReservationsApi = (id, params) => {
  return http.get(`/courses/${id}/reservations`, { params })
}

// 耗材管理
export const getConsumables = (params) => {
  return request({
    url: '/consumables',
    method: 'get',
    params
  })
}

export const createConsumable = (data) => {
  return request({
    url: '/consumables',
    method: 'post',
    data
  })
}

export const updateConsumable = (id, data) => {
  return request({
    url: `/consumables/${id}`,
    method: 'put',
    data
  })
}

export const deleteConsumable = (id) => {
  return request({
    url: `/consumables/${id}`,
    method: 'delete'
  })
}

export const useConsumable = (id, data) => {
  return request({
    url: `/consumables/${id}/use`,
    method: 'post',
    data
  })
}

export const restockConsumable = (id, data) => {
  return request({
    url: `/consumables/${id}/restock`,
    method: 'post',
    data
  })
}

export const getConsumableStats = () => {
  return request({
    url: '/consumables/stats',
    method: 'get'
  })
}

// 耗材使用记录
export const getConsumableUsageRecords = (params) => {
  return request({
    url: '/consumables/usage',
    method: 'get',
    params
  })
}

export const createConsumableUsage = (data) => {
  return request({
    url: '/consumables/usage',
    method: 'post',
    data
  })
}

export const updateConsumableUsage = (id, data) => {
  return request({
    url: `/consumables/usage/${id}`,
    method: 'put',
    data
  })
}

export const deleteConsumableUsage = (id) => {
  return request({
    url: `/consumables/usage/${id}`,
    method: 'delete'
  })
}

export const getConsumableUsageStats = () => {
  return request({
    url: '/consumables/usage/stats',
    method: 'get'
  })
}

export const exportConsumableUsage = (params) => {
  return request({
    url: '/consumables/usage/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}