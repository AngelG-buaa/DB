// 模拟API响应数据
export const mockUsers = {
  'admin': {
    user_id: 1,
    username: 'admin',
    real_name: '系统管理员',
    email: 'admin@lab-system.com',
    user_type: 'admin',
    department: '信息技术部',
    phone: '13800138000',
    status: 'active',
    created_at: '2024-01-01 00:00:00'
  },
  'teacher001': {
    user_id: 2,
    username: 'teacher001',
    real_name: '张教授',
    email: 'zhang@university.edu.cn',
    user_type: 'teacher',
    department: '计算机科学与技术学院',
    phone: '13800138001',
    status: 'active',
    created_at: '2024-01-01 00:00:00'
  },
  'student001': {
    user_id: 3,
    username: 'student001',
    real_name: '李小明',
    email: 'lixiaoming@student.edu.cn',
    user_type: 'student',
    department: '计算机科学与技术学院',
    phone: '13800138002',
    status: 'active',
    student_id: '2021001001',
    grade: '2021',
    major: '计算机科学与技术',
    class_name: '计科2101班',
    created_at: '2024-01-01 00:00:00'
  }
}

// 模拟登录API
export const mockLogin = (loginData) => {
  return new Promise((resolve, reject) => {
    // 模拟网络延迟
    setTimeout(() => {
      const { username, password, userType } = loginData
      
      // 验证用户名和密码
      const user = mockUsers[username]
      if (!user) {
        reject({
          code: 400,
          message: '用户名不存在'
        })
        return
      }
      
      if (password !== '123456') {
        reject({
          code: 400,
          message: '密码错误'
        })
        return
      }
      
      if (user.user_type !== userType) {
        reject({
          code: 400,
          message: '用户类型不匹配'
        })
        return
      }
      
      // 生成模拟token
      const token = `mock_token_${username}_${Date.now()}`
      
      resolve({
        code: 200,
        message: '登录成功',
        data: {
          token,
          userInfo: user
        }
      })
    }, 1000) // 模拟1秒延迟
  })
}

// 模拟获取用户信息API
export const mockGetUserInfo = (token) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // 从token中提取用户名
      const username = token.split('_')[2]
      const user = mockUsers[username]
      
      if (!user) {
        reject({
          code: 401,
          message: 'Token无效'
        })
        return
      }
      
      resolve({
        code: 200,
        message: '获取成功',
        data: user
      })
    }, 500)
  })
}

// 模拟退出登录API
export const mockLogout = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        code: 200,
        message: '退出成功'
      })
    }, 300)
  })
}