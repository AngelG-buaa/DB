import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'
import NProgress from 'nprogress'
let isHandlingTokenExpired = false

// 创建axios实例
const request = axios.create({
  baseURL: '/api', // 基础URL
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json;charset=UTF-8'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 开始进度条
    NProgress.start()
    
    // 添加token到请求头
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    
    // 添加时间戳防止缓存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }
    
    return config
  },
  (error) => {
    NProgress.done()
    ElMessage.error('请求配置错误')
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    NProgress.done()
    
    const { data } = response
    
    // 如果是文件下载，直接返回
    if (response.config.responseType === 'blob') {
      return response
    }
    
    // 统一处理响应数据（兼容后端的 success/message/code/data 格式）
    if (typeof data?.success === 'boolean') {
      if (data.success) {
        // 规范化成功响应：统一为 code=200；若为分页响应，转换为 data.list + total
        if (data?.pagination && Array.isArray(data?.data)) {
          return {
            ...data,
            code: 200,
            data: {
              list: data.data,
              total: data.pagination?.total ?? 0,
              page: data.pagination?.page,
              page_size: data.pagination?.page_size
            }
          }
        }
        return { ...data, code: 200 }
      }
      // 业务失败场景：由后端返回 200 + success=false
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(data)
    }
    
    // 兼容旧格式：code 为数字或字符串
    if (data?.code === 200 || ['SUCCESS', 'CREATED', 'UPDATED', 'DELETED'].includes(data?.code)) {
      // 统一成功响应 code=200；处理分页形态
      if (data?.pagination && Array.isArray(data?.data)) {
        return {
          ...data,
          code: 200,
          data: {
            list: data.data,
            total: data.pagination?.total ?? 0,
            page: data.pagination?.page,
            page_size: data.pagination?.page_size
          }
        }
      }
      return { ...data, code: 200 }
    }
    
    ElMessage.error(data?.message || '请求失败')
    return Promise.reject(data)
  },
  (error) => {
    NProgress.done()
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          ElMessage.error(data.message || '请求参数错误')
          break
        case 401: {
          const requestUrl = error.response?.config?.url || ''
          if (requestUrl.includes('/auth/login')) {
            ElMessage.error(data.message || '用户名或密码错误')
          } else if (requestUrl.includes('/auth/logout')) {
          } else {
            handleTokenExpired()
          }
          break
        }
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        case 502:
          ElMessage.error('网关错误')
          break
        case 503:
          ElMessage.error('服务不可用')
          break
        case 504:
          ElMessage.error('网关超时')
          break
        default:
          ElMessage.error(data.message || `请求失败 (${status})`)
      }
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接')
    } else if (error.message === 'Network Error') {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求失败，请稍后重试')
    }
    
    return Promise.reject(error)
  }
)

// 处理token过期
const handleTokenExpired = () => {
  if (isHandlingTokenExpired) return
  isHandlingTokenExpired = true
  const userStore = useUserStore()
  ElMessageBox.confirm(
    '登录状态已过期，请重新登录',
    '提示',
    {
      confirmButtonText: '重新登录',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    userStore.logout().then(() => {
      router.replace('/login')
      isHandlingTokenExpired = false
    })
  }).catch(() => {
    userStore.logout().then(() => {
      router.replace('/login')
      isHandlingTokenExpired = false
    })
  })
}

// 封装常用请求方法
export const http = {
  get(url, params = {}, config = {}) {
    return request({
      method: 'get',
      url,
      params,
      ...config
    })
  },
  
  post(url, data = {}, config = {}) {
    return request({
      method: 'post',
      url,
      data,
      ...config
    })
  },
  
  put(url, data = {}, config = {}) {
    return request({
      method: 'put',
      url,
      data,
      ...config
    })
  },
  
  delete(url, params = {}, config = {}) {
    return request({
      method: 'delete',
      url,
      params,
      ...config
    })
  },
  
  patch(url, data = {}, config = {}) {
    return request({
      method: 'patch',
      url,
      data,
      ...config
    })
  },
  
  upload(url, formData, config = {}) {
    return request({
      method: 'post',
      url,
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      ...config
    })
  },
  
  download(url, params = {}, config = {}) {
    return request({
      method: 'get',
      url,
      params,
      responseType: 'blob',
      ...config
    })
  }
}

export default request