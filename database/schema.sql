-- 高校实验室预约与设备管理系统数据库设计
-- 创建数据库
CREATE DATABASE IF NOT EXISTS lab_management_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lab_management_system;

-- 用户表（教师和学生的基础信息）
CREATE TABLE `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码',
    `real_name` VARCHAR(100) NOT NULL COMMENT '真实姓名',
    `email` VARCHAR(100) UNIQUE COMMENT '邮箱',
    `phone` VARCHAR(20) COMMENT '电话号码',
    `user_type` ENUM('student', 'teacher', 'admin') NOT NULL COMMENT '用户类型',
    `student_id` VARCHAR(20) COMMENT '学号（学生）',
    `employee_id` VARCHAR(20) COMMENT '工号（教师）',
    `department` VARCHAR(100) COMMENT '院系',
    `major` VARCHAR(100) COMMENT '专业（学生）',
    `grade` INT COMMENT '年级（学生）',
    `avatar_url` VARCHAR(255) COMMENT '头像URL',
    `status` ENUM('active', 'inactive', 'suspended') DEFAULT 'active' COMMENT '账户状态',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_username` (`username`),
    INDEX `idx_user_type` (`user_type`),
    INDEX `idx_student_id` (`student_id`),
    INDEX `idx_employee_id` (`employee_id`)
) ENGINE=InnoDB COMMENT='用户表';

-- 实验室表
CREATE TABLE `laboratory` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '实验室ID',
    `lab_name` VARCHAR(100) NOT NULL COMMENT '实验室名称',
    `location` VARCHAR(200) NOT NULL COMMENT '实验室位置',
    `capacity` INT NOT NULL DEFAULT 0 COMMENT '容纳人数',
    `manager_id` INT NOT NULL COMMENT '管理员ID',
    `lab_status` ENUM('available', 'maintenance', 'closed') DEFAULT 'available' COMMENT '实验室状态',
    `description` TEXT COMMENT '实验室描述',
    `equipment_list` TEXT COMMENT '设备清单概述',
    `safety_rules` TEXT COMMENT '安全规则',
    `opening_hours` JSON COMMENT '开放时间',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`manager_id`) REFERENCES `user`(`id`) ON DELETE RESTRICT,
    INDEX `idx_lab_name` (`lab_name`),
    INDEX `idx_location` (`location`),
    INDEX `idx_manager_id` (`manager_id`)
) ENGINE=InnoDB COMMENT='实验室表';

-- 设备表
CREATE TABLE `equipment` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '设备ID',
    `equip_name` VARCHAR(100) NOT NULL COMMENT '设备名称',
    `model` VARCHAR(100) COMMENT '设备型号',
    `lab_id` INT NOT NULL COMMENT '所属实验室ID',
    `equip_status` ENUM('available', 'in_use', 'maintenance', 'damaged') DEFAULT 'available' COMMENT '设备状态',
    `purchase_date` DATE COMMENT '购买日期',
    `price` DECIMAL(10,2) COMMENT '设备价格',
    `manufacturer` VARCHAR(100) COMMENT '制造商',
    `serial_number` VARCHAR(100) UNIQUE COMMENT '设备序列号',
    `warranty_period` INT COMMENT '保修期（月）',
    `last_maintenance` DATE COMMENT '上次维护日期',
    `next_maintenance` DATE COMMENT '下次维护日期',
    `usage_count` INT DEFAULT 0 COMMENT '使用次数',
    `description` TEXT COMMENT '设备描述',
    `operating_manual` TEXT COMMENT '操作手册',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`lab_id`) REFERENCES `laboratory`(`id`) ON DELETE CASCADE,
    INDEX `idx_equip_name` (`equip_name`),
    INDEX `idx_lab_id` (`lab_id`),
    INDEX `idx_equip_status` (`equip_status`),
    INDEX `idx_serial_number` (`serial_number`)
) ENGINE=InnoDB COMMENT='设备表';

-- 课程表
CREATE TABLE `course` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '课程ID',
    `course_name` VARCHAR(100) NOT NULL COMMENT '课程名称',
    `course_code` VARCHAR(20) NOT NULL UNIQUE COMMENT '课程代码',
    `teacher_id` INT NOT NULL COMMENT '授课教师ID',
    `department` VARCHAR(100) COMMENT '开课院系',
    `credits` INT COMMENT '学分',
    `semester` VARCHAR(20) COMMENT '学期',
    `academic_year` VARCHAR(10) COMMENT '学年',
    `student_count` INT DEFAULT 0 COMMENT '选课人数',
    `max_students` INT COMMENT '最大选课人数',
    `description` TEXT COMMENT '课程描述',
    `syllabus` TEXT COMMENT '课程大纲',
    `status` ENUM('active', 'inactive', 'completed') DEFAULT 'active' COMMENT '课程状态',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`teacher_id`) REFERENCES `user`(`id`) ON DELETE RESTRICT,
    INDEX `idx_course_name` (`course_name`),
    INDEX `idx_course_code` (`course_code`),
    INDEX `idx_teacher_id` (`teacher_id`)
) ENGINE=InnoDB COMMENT='课程表';

-- 预约记录表
CREATE TABLE `reservation` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '预约ID',
    `user_id` INT NOT NULL COMMENT '预约用户ID',
    `lab_id` INT NOT NULL COMMENT '实验室ID',
    `course_id` INT COMMENT '关联课程ID（可选）',
    `reservation_date` DATE NOT NULL COMMENT '预约日期',
    `start_time` TIME NOT NULL COMMENT '开始时间',
    `end_time` TIME NOT NULL COMMENT '结束时间',
    `purpose` TEXT NOT NULL COMMENT '使用目的',
    `student_count` INT DEFAULT 1 COMMENT '参与学生数量',
    `equipment_needed` JSON COMMENT '所需设备列表',
    `status` ENUM('pending', 'approved', 'rejected', 'completed', 'cancelled') DEFAULT 'pending' COMMENT '预约状态',
    `approval_user_id` INT COMMENT '审批人ID',
    `approval_time` TIMESTAMP NULL COMMENT '审批时间',
    `approval_notes` TEXT COMMENT '审批备注',
    `actual_start_time` TIMESTAMP NULL COMMENT '实际开始时间',
    `actual_end_time` TIMESTAMP NULL COMMENT '实际结束时间',
    `usage_report` TEXT COMMENT '使用报告',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`lab_id`) REFERENCES `laboratory`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`approval_user_id`) REFERENCES `user`(`id`) ON DELETE SET NULL,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_lab_id` (`lab_id`),
    INDEX `idx_reservation_date` (`reservation_date`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB COMMENT='预约记录表';

-- 设备维修记录表
CREATE TABLE `equipment_repair` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '维修记录ID',
    `equipment_id` INT NOT NULL COMMENT '设备ID',
    `reporter_id` INT NOT NULL COMMENT '报修人ID',
    `repair_person` VARCHAR(100) COMMENT '维修人员',
    `fault_description` TEXT NOT NULL COMMENT '故障描述',
    `repair_description` TEXT COMMENT '维修描述',
    `repair_cost` DECIMAL(10,2) COMMENT '维修费用',
    `repair_status` ENUM('reported', 'in_progress', 'completed', 'cancelled') DEFAULT 'reported' COMMENT '维修状态',
    `priority` ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium' COMMENT '优先级',
    `report_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '报修时间',
    `start_time` TIMESTAMP NULL COMMENT '开始维修时间',
    `finish_time` TIMESTAMP NULL COMMENT '完成维修时间',
    `parts_used` JSON COMMENT '使用的零件',
    `warranty_info` TEXT COMMENT '保修信息',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`reporter_id`) REFERENCES `user`(`id`) ON DELETE RESTRICT,
    INDEX `idx_equipment_id` (`equipment_id`),
    INDEX `idx_reporter_id` (`reporter_id`),
    INDEX `idx_repair_status` (`repair_status`),
    INDEX `idx_report_time` (`report_time`)
) ENGINE=InnoDB COMMENT='设备维修记录表';

-- 耗材表
CREATE TABLE `consumable` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '耗材ID',
    `name` VARCHAR(100) NOT NULL COMMENT '耗材名称',
    `specification` VARCHAR(200) COMMENT '规格型号',
    `lab_id` INT NOT NULL COMMENT '所属实验室ID',
    `category` VARCHAR(50) COMMENT '耗材类别',
    `unit` VARCHAR(20) NOT NULL COMMENT '计量单位',
    `current_stock` INT DEFAULT 0 COMMENT '当前库存',
    `min_stock` INT DEFAULT 0 COMMENT '最低库存警戒线',
    `max_stock` INT DEFAULT 0 COMMENT '最大库存',
    `unit_price` DECIMAL(10,2) COMMENT '单价',
    `supplier` VARCHAR(100) COMMENT '供应商',
    `storage_location` VARCHAR(100) COMMENT '存放位置',
    `expiry_date` DATE COMMENT '过期日期',
    `safety_info` TEXT COMMENT '安全信息',
    `usage_instructions` TEXT COMMENT '使用说明',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`lab_id`) REFERENCES `laboratory`(`id`) ON DELETE CASCADE,
    INDEX `idx_name` (`name`),
    INDEX `idx_lab_id` (`lab_id`),
    INDEX `idx_category` (`category`),
    INDEX `idx_current_stock` (`current_stock`)
) ENGINE=InnoDB COMMENT='耗材表';

-- 耗材使用记录表
CREATE TABLE `consumable_usage` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '使用记录ID',
    `consumable_id` INT NOT NULL COMMENT '耗材ID',
    `user_id` INT NOT NULL COMMENT '使用者ID',
    `reservation_id` INT COMMENT '关联预约ID',
    `quantity` INT NOT NULL COMMENT '使用数量',
    `usage_date` DATE NOT NULL COMMENT '使用日期',
    `purpose` VARCHAR(200) COMMENT '使用目的',
    `notes` TEXT COMMENT '备注',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (`consumable_id`) REFERENCES `consumable`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE RESTRICT,
    FOREIGN KEY (`reservation_id`) REFERENCES `reservation`(`id`) ON DELETE SET NULL,
    INDEX `idx_consumable_id` (`consumable_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_usage_date` (`usage_date`)
) ENGINE=InnoDB COMMENT='耗材使用记录表';

-- 系统通知表
CREATE TABLE `notification` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '通知ID',
    `title` VARCHAR(200) NOT NULL COMMENT '通知标题',
    `content` TEXT NOT NULL COMMENT '通知内容',
    `type` ENUM('system', 'reservation', 'maintenance', 'inventory') DEFAULT 'system' COMMENT '通知类型',
    `target_users` JSON COMMENT '目标用户ID列表',
    `sender_id` INT COMMENT '发送者ID',
    `priority` ENUM('low', 'medium', 'high') DEFAULT 'medium' COMMENT '优先级',
    `is_read` BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (`sender_id`) REFERENCES `user`(`id`) ON DELETE SET NULL,
    INDEX `idx_type` (`type`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB COMMENT='系统通知表';