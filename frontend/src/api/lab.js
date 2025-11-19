import { http } from './request'

// 实验室相关API
export const getLabsApi = (params) => {
  return http.get('/labs', params)
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
  return http.get(`/labs/${id}/availability`, params)
}

export const getLabEquipmentApi = (id) => {
  return http.get(`/labs/${id}/equipment`)
}

export const getLabReservationsApi = (id, params) => {
  return http.get(`/labs/${id}/reservations`, params)
}