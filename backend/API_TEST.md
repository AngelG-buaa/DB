# API测试文档

本文档提供了实验室管理系统Python后端API的测试示例。

## 测试环境

- 服务地址: `http://localhost:5000`
- 内容类型: `application/json`
- 认证方式: Bearer Token (JWT)

## 认证接口测试

### 1. 用户登录

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

响应示例：
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "name": "管理员",
      "email": "admin@example.com",
      "role": "admin"
    }
  }
}
```

### 2. 用户注册

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "name": "测试用户",
    "email": "test@example.com",
    "role": "student",
    "student_id": "2024001"
  }'
```

### 3. 获取用户信息

```bash
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 用户管理测试

### 1. 获取用户列表

```bash
curl -X GET "http://localhost:5000/api/users?page=1&page_size=10&role=student" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. 创建用户

```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "username": "newuser",
    "password": "password123",
    "name": "新用户",
    "email": "newuser@example.com",
    "role": "teacher",
    "phone": "13800138000"
  }'
```

### 3. 更新用户信息

```bash
curl -X PUT http://localhost:5000/api/users/2 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "更新后的姓名",
    "email": "updated@example.com",
    "phone": "13900139000"
  }'
```

## 实验室管理测试

### 1. 获取实验室列表

```bash
curl -X GET "http://localhost:5000/api/laboratories?page=1&page_size=10&status=active" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. 创建实验室

```bash
curl -X POST http://localhost:5000/api/laboratories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "计算机实验室A",
    "location": "教学楼3楼301",
    "capacity": 50,
    "description": "配备50台计算机的实验室",
    "status": "active"
  }'
```

### 3. 检查实验室可用性

```bash
curl -X GET "http://localhost:5000/api/laboratories/1/availability?date=2024-01-15&start_time=09:00&end_time=11:00" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 设备管理测试

### 1. 获取设备列表

```bash
curl -X GET "http://localhost:5000/api/equipment?page=1&page_size=10&laboratory_id=1&status=available" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. 创建设备

```bash
curl -X POST http://localhost:5000/api/equipment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "投影仪",
    "model": "EPSON EB-X41",
    "serial_number": "EP2024001",
    "laboratory_id": 1,
    "status": "available",
    "purchase_date": "2024-01-01",
    "warranty_expiry": "2027-01-01",
    "description": "高清投影仪"
  }'
```

### 3. 获取设备统计

```bash
curl -X GET http://localhost:5000/api/equipment/statistics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 预约管理测试

### 1. 获取预约列表

```bash
curl -X GET "http://localhost:5000/api/reservations?page=1&page_size=10&status=confirmed&date=2024-01-15" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. 创建预约

```bash
curl -X POST http://localhost:5000/api/reservations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "laboratory_id": 1,
    "date": "2024-01-15",
    "start_time": "09:00",
    "end_time": "11:00",
    "purpose": "Python编程实验",
    "equipment_ids": [1, 2],
    "participant_count": 30
  }'
```

### 3. 更新预约状态

```bash
curl -X PUT http://localhost:5000/api/reservations/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "status": "confirmed",
    "notes": "预约已确认"
  }'
```

### 4. 获取预约统计

```bash
curl -X GET http://localhost:5000/api/reservations/statistics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 课程管理测试

### 1. 获取课程列表

```bash
curl -X GET "http://localhost:5000/api/courses?page=1&page_size=10&semester=2024春季&status=active" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. 创建课程

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Python程序设计",
    "code": "CS101",
    "description": "Python编程基础课程",
    "credits": 3,
    "semester": "2024春季",
    "teacher_id": 2,
    "status": "active"
  }'
```

### 3. 添加学生到课程

```bash
curl -X POST http://localhost:5000/api/courses/1/students \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "student_ids": [3, 4, 5]
  }'
```

### 4. 获取我的课程（学生）

```bash
curl -X GET http://localhost:5000/api/courses/my-courses \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 错误处理测试

### 1. 无效Token

```bash
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer invalid_token"
```

响应：
```json
{
  "success": false,
  "message": "无效的访问令牌",
  "error_code": "INVALID_TOKEN"
}
```

### 2. 权限不足

```bash
# 学生用户尝试访问管理员接口
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer STUDENT_JWT_TOKEN"
```

响应：
```json
{
  "success": false,
  "message": "权限不足",
  "error_code": "INSUFFICIENT_PERMISSIONS"
}
```

### 3. 数据验证错误

```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "username": "",
    "email": "invalid-email"
  }'
```

响应：
```json
{
  "success": false,
  "message": "数据验证失败",
  "errors": {
    "username": "用户名不能为空",
    "email": "邮箱格式不正确",
    "password": "密码是必填项"
  }
}
```

## 使用Postman测试

### 1. 导入环境变量

创建Postman环境，添加以下变量：
- `base_url`: `http://localhost:5000`
- `jwt_token`: 登录后获取的JWT Token

### 2. 设置认证

在请求头中添加：
```
Authorization: Bearer {{jwt_token}}
```

### 3. 测试集合

可以创建以下测试集合：
- 认证测试
- 用户管理测试
- 实验室管理测试
- 设备管理测试
- 预约管理测试
- 课程管理测试

## 性能测试

### 使用Apache Bench (ab)

```bash
# 测试登录接口
ab -n 100 -c 10 -p login.json -T application/json http://localhost:5000/api/auth/login

# 测试获取用户列表接口
ab -n 100 -c 10 -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:5000/api/users
```

### 使用wrk

```bash
# 安装wrk
# Ubuntu: sudo apt-get install wrk
# macOS: brew install wrk

# 测试API性能
wrk -t12 -c400 -d30s -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:5000/api/laboratories
```

## 注意事项

1. **JWT Token过期**: Token默认有效期为1小时，过期后需要重新登录
2. **权限控制**: 不同角色用户只能访问对应权限的接口
3. **数据验证**: 所有POST/PUT请求都会进行数据验证
4. **错误处理**: API返回统一的错误格式
5. **分页查询**: 列表接口支持分页，默认每页10条记录
6. **SSL连接**: 生产环境需要配置SSL证书连接数据库

## 常见问题

1. **500错误**: 检查数据库连接和配置
2. **401错误**: 检查JWT Token是否有效
3. **403错误**: 检查用户权限
4. **422错误**: 检查请求数据格式和验证规则