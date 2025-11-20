import { http } from './request'

// 实验室相关API
export const getLabsApi = (params) => {
  return http.get('/laboratories', params)
}

export const getLabByIdApi = (id) => {
  return http.get(`/laboratories/${id}`)
}

export const createLabApi = (data) => {
  return http.post('/laboratories', data)
}

export const updateLabApi = (id, data) => {
  return http.put(`/laboratories/${id}`, data)
}

export const deleteLabApi = (id) => {
  return http.delete(`/laboratories/${id}`)
}

export const getLabAvailabilityApi = (id, params) => {
  return http.get(`/laboratories/${id}/availability`, params)
}

export const getLabEquipmentApi = (id) => {
  return http.get(`/laboratories/${id}/equipment`)
}

export const getLabReservationsApi = (id, params) => {
  return http.get(`/laboratories/${id}/reservations`, params)
}