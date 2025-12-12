import { http } from './request'

// 课程相关API
export const getCoursesApi = (params) => {
  return http.get('/courses', params)
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
  return http.get(`/courses/${id}/reservations`, params)
}

export const addStudentsToCourseApi = (id, data) => {
  return http.post(`/courses/${id}/students`, data)
}