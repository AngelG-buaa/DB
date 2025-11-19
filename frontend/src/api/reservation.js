import { http } from './request'

// 预约相关API
export const getReservationsApi = (params) => {
  return http.get('/reservations', params)
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
  return http.get('/reservations/my', params)
}

export const getReservationCalendarApi = (params) => {
  return http.get('/reservations/calendar', params)
}

export const checkReservationConflictApi = (data) => {
  return http.post('/reservations/check-conflict', data)
}

export const getReservationStatsApi = (params) => {
  return http.get('/reservations/statistics', params)
}