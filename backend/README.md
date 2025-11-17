# 实验室管理系统 - Python后端

基于Flask框架开发的实验室管理系统后端API，使用原生SQL操作TaurusDB数据库。

## 功能特性

- 🔐 用户认证与授权（JWT）
- 👥 用户管理（学生、教师、管理员）
- 🏢 实验室管理
- 🔧 设备管理与维修记录
- 📅 预约管理与审批
- 📚 课程管理
- 📊 统计分析
- 🛡️ 安全防护（限流、CORS、Helmet）

## 技术栈

- **运行环境**: Node.js 14+
- **Web框架**: Express.js
- **数据库**: MySQL 8.0+
- **认证**: JWT (jsonwebtoken)
- **密码加密**: bcryptjs
- **数据验证**: express-validator
- **安全防护**: helmet, express-rate-limit, cors

## 项目结构

```
backend/
├── config/
│   └── database.js          # 数据库连接配置
├── middleware/
│   ├── auth.js              # 认证中间件
│   └── validation.js        # 数据验证中间件
├── routes/
│   ├── auth.js              # 认证路由
│   ├── users.js             # 用户管理路由
│   ├── laboratories.js      # 实验室管理路由
│   ├── equipment.js         # 设备管理路由
│   ├── reservations.js      # 预约管理路由
│   └── courses.js           # 课程管理路由
├── scripts/
│   └── start.js             # 启动脚本
├── uploads/                 # 文件上传目录
├── .env.example             # 环境变量示例
├── package.json             # 项目依赖
├── server.js                # 服务器入口文件
└── README.md                # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
npm install
```

### 2. 配置环境变量

复制环境变量示例文件并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下参数：

```env
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=lab_management_system
DB_PORT=3306

# JWT配置
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRES_IN=24h

# 服务器配置
PORT=3000
NODE_ENV=development

# 文件上传配置
UPLOAD_PATH=./uploads
MAX_FILE_SIZE=5242880

# 邮件配置（可选）
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password
```

### 3. 初始化数据库

确保 MySQL 服务已启动，并创建数据库：

```sql
CREATE DATABASE lab_management_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

导入数据库结构：

```bash
mysql -u root -p lab_management_system < ../database/schema.sql
```

### 4. 启动服务

使用启动脚本：

```bash
node scripts/start.js
```

或直接启动：

```bash
npm start
```

开发模式（自动重启）：

```bash
npm run dev
```

## API 文档

### 认证相关

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 公开 |
| POST | `/api/auth/login` | 用户登录 | 公开 |
| GET | `/api/auth/profile` | 获取用户信息 | 登录用户 |
| PUT | `/api/auth/profile` | 更新用户信息 | 登录用户 |
| PUT | `/api/auth/password` | 修改密码 | 登录用户 |
| POST | `/api/auth/logout` | 用户登出 | 登录用户 |

### 用户管理

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/api/users` | 获取用户列表 | 管理员 |
| GET | `/api/users/:id` | 获取用户详情 | 本人或管理员 |
| PUT | `/api/users/:id/status` | 更新用户状态 | 管理员 |
| DELETE | `/api/users/:id` | 删除用户 | 管理员 |
| GET | `/api/users/stats/overview` | 用户统计 | 管理员 |
| GET | `/api/users/search/:keyword` | 搜索用户 | 管理员 |

### 实验室管理

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/api/laboratories` | 获取实验室列表 | 登录用户 |
| GET | `/api/laboratories/:id` | 获取实验室详情 | 登录用户 |
| POST | `/api/laboratories` | 创建实验室 | 管理员 |
| PUT | `/api/laboratories/:id` | 更新实验室 | 管理员或实验室管理员 |
| DELETE | `/api/laboratories/:id` | 删除实验室 | 管理员 |
| GET | `/api/laboratories/stats/overview` | 实验室统计 | 教师或管理员 |
| GET | `/api/laboratories/search/:keyword` | 搜索实验室 | 登录用户 |

### 设备管理

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/api/equipment` | 获取设备列表 | 登录用户 |
| GET | `/api/equipment/:id` | 获取设备详情 | 登录用户 |
| POST | `/api/equipment` | 创建设备 | 教师或管理员 |
| PUT | `/api/equipment/:id` | 更新设备 | 教师或管理员 |
| DELETE | `/api/equipment/:id` | 删除设备 | 教师或管理员 |
| POST | `/api/equipment/:id/repair` | 报告设备故障 | 登录用户 |
| PUT | `/api/equipment/repair/:repair_id` | 更新维修状态 | 教师或管理员 |
| GET | `/api/equipment/stats/overview` | 设备统计 | 教师或管理员 |
| GET | `/api/equipment/repairs/list` | 维修记录列表 | 教师或管理员 |

### 预约管理

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/api/reservations` | 获取预约列表 | 登录用户 |
| GET | `/api/reservations/:id` | 获取预约详情 | 本人或管理员 |
| POST | `/api/reservations` | 创建预约 | 登录用户 |
| PUT | `/api/reservations/:id/status` | 审批预约 | 教师或管理员 |
| PUT | `/api/reservations/:id/cancel` | 取消预约 | 本人或管理员 |
| PUT | `/api/reservations/:id/complete` | 完成预约 | 本人或管理员 |
| GET | `/api/reservations/stats/overview` | 预约统计 | 教师或管理员 |
| GET | `/api/reservations/availability/:lab_id` | 检查可用性 | 登录用户 |

### 课程管理

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/api/courses` | 获取课程列表 | 登录用户 |
| GET | `/api/courses/:id` | 获取课程详情 | 登录用户 |
| POST | `/api/courses` | 创建课程 | 管理员 |
| PUT | `/api/courses/:id` | 更新课程 | 管理员或课程教师 |
| DELETE | `/api/courses/:id` | 删除课程 | 管理员 |

## 数据库设计

系统使用 MySQL 数据库，主要包含以下表：

- `user` - 用户表
- `laboratory` - 实验室表
- `equipment` - 设备表
- `equipment_repair` - 设备维修记录表
- `course` - 课程表
- `reservation` - 预约表
- `consumable` - 耗材表
- `consumable_usage` - 耗材使用记录表
- `notification` - 通知表

详细的数据库结构请参考 `../database/schema.sql` 文件。

## 安全特性

- JWT 令牌认证
- 密码 bcrypt 加密
- 请求频率限制
- CORS 跨域保护
- Helmet 安全头设置
- 输入数据验证
- SQL 注入防护（参数化查询）

## 开发指南

### 添加新的 API 路由

1. 在 `routes/` 目录下创建新的路由文件
2. 在 `server.js` 中注册路由
3. 添加相应的验证中间件
4. 更新 API 文档

### 数据库操作

使用 `config/database.js` 中提供的方法：

```javascript
const { executeQuery, executePaginatedQuery, executeTransaction } = require('../config/database');

// 执行查询
const result = await executeQuery('SELECT * FROM user WHERE id = ?', [userId]);

// 分页查询
const result = await executePaginatedQuery('SELECT * FROM user', [], 1, 10);

// 事务操作
const result = await executeTransaction(async (connection) => {
    await connection.query('INSERT INTO ...', []);
    await connection.query('UPDATE ...', []);
});
```

### 错误处理

系统提供统一的错误处理机制，所有 API 返回格式：

```javascript
// 成功响应
{
    "success": true,
    "data": {...},
    "message": "操作成功"
}

// 错误响应
{
    "success": false,
    "message": "错误信息",
    "error": "详细错误（开发环境）"
}
```

## 部署说明

### 生产环境配置

1. 设置 `NODE_ENV=production`
2. 使用强密码和安全的 JWT 密钥
3. 配置反向代理（Nginx）
4. 启用 HTTPS
5. 配置日志记录
6. 设置进程管理器（PM2）

### PM2 部署示例

```bash
# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start server.js --name "lab-management-api"

# 设置开机自启
pm2 startup
pm2 save
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证连接参数是否正确
   - 确认数据库用户权限

2. **JWT 认证失败**
   - 检查 JWT_SECRET 是否配置
   - 验证令牌是否过期
   - 确认请求头格式正确

3. **文件上传失败**
   - 检查上传目录权限
   - 验证文件大小限制
   - 确认文件类型允许

### 日志查看

```bash
# 查看应用日志
pm2 logs lab-management-api

# 查看错误日志
pm2 logs lab-management-api --err
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。