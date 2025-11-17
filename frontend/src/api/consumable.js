import request from '@/utils/request'

// 耗材管理
export const getConsumables = (params) => {
  return request({
    url: '/consumables',
    method: 'get',
    params
  })
}

export const getConsumableById = (id) => {
  return request({
    url: `/consumables/${id}`,
    method: 'get'
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

export const getConsumableUsageById = (id) => {
  return request({
    url: `/consumables/usage/${id}`,
    method: 'get'
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

// 获取实验室列表（用于下拉选择）
export const getLaboratories = () => {
  return request({
    url: '/laboratories',
    method: 'get'
  })
}