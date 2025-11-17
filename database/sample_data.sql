-- 高校实验室预约与设备管理系统示例数据
USE lab_management_system;

-- 插入示例用户数据
INSERT INTO `user` (username, password, real_name, email, phone, user_type, student_id, employee_id, department, major, grade, status) VALUES
-- 管理员
('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '系统管理员', 'admin@university.edu', '13800000000', 'admin', NULL, 'A001', '信息技术中心', NULL, NULL, 'active'),

-- 教师
('teacher001', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '张教授', 'zhang@university.edu', '13800000001', 'teacher', NULL, 'T001', '计算机科学与技术学院', NULL, NULL, 'active'),
('teacher002', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '李副教授', 'li@university.edu', '13800000002', 'teacher', NULL, 'T002', '电子工程学院', NULL, NULL, 'active'),
('teacher003', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '王讲师', 'wang@university.edu', '13800000003', 'teacher', NULL, 'T003', '物理学院', NULL, NULL, 'active'),

-- 学生
('student001', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '陈小明', 'chen@student.edu', '13900000001', 'student', '2021001001', NULL, '计算机科学与技术学院', '计算机科学与技术', 2021, 'active'),
('student002', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '刘小红', 'liu@student.edu', '13900000002', 'student', '2021001002', NULL, '计算机科学与技术学院', '软件工程', 2021, 'active'),
('student003', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '赵小强', 'zhao@student.edu', '13900000003', 'student', '2022002001', NULL, '电子工程学院', '电子信息工程', 2022, 'active'),
('student004', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '孙小丽', 'sun@student.edu', '13900000004', 'student', '2022002002', NULL, '物理学院', '应用物理学', 2022, 'active');

-- 插入实验室数据
INSERT INTO `laboratory` (lab_name, location, capacity, manager_id, lab_status, description, opening_hours) VALUES
('计算机网络实验室', '信息楼301', 40, 2, 'available', '配备40台计算机，用于网络技术实验教学', '{"monday": "08:00-18:00", "tuesday": "08:00-18:00", "wednesday": "08:00-18:00", "thursday": "08:00-18:00", "friday": "08:00-18:00"}'),
('电子电路实验室', '工程楼201', 30, 3, 'available', '电子电路设计与测试实验室', '{"monday": "08:00-17:00", "tuesday": "08:00-17:00", "wednesday": "08:00-17:00", "thursday": "08:00-17:00", "friday": "08:00-17:00"}'),
('物理光学实验室', '理学楼401', 25, 4, 'available', '光学实验与研究实验室', '{"monday": "09:00-17:00", "tuesday": "09:00-17:00", "wednesday": "09:00-17:00", "thursday": "09:00-17:00", "friday": "09:00-17:00"}'),
('化学分析实验室', '化学楼101', 20, 2, 'maintenance', '化学分析与合成实验室', '{"monday": "08:00-16:00", "tuesday": "08:00-16:00", "wednesday": "08:00-16:00", "thursday": "08:00-16:00", "friday": "08:00-16:00"}'),
('生物实验室', '生物楼202', 35, 3, 'available', '生物学实验教学实验室', '{"monday": "08:00-18:00", "tuesday": "08:00-18:00", "wednesday": "08:00-18:00", "thursday": "08:00-18:00", "friday": "08:00-18:00"}');

-- 插入设备数据
INSERT INTO `equipment` (equip_name, model, lab_id, equip_status, purchase_date, price, manufacturer, serial_number, warranty_period, last_maintenance, next_maintenance, description) VALUES
-- 计算机网络实验室设备
('网络交换机', 'Cisco Catalyst 2960', 1, 'available', '2022-03-15', 3500.00, 'Cisco', 'CS2960001', 36, '2023-12-01', '2024-06-01', '24口千兆以太网交换机'),
('路由器', 'Cisco ISR 4321', 1, 'available', '2022-03-15', 8500.00, 'Cisco', 'ISR4321001', 36, '2023-12-01', '2024-06-01', '企业级路由器'),
('网络分析仪', 'Fluke Networks OptiView XG', 1, 'available', '2021-09-20', 25000.00, 'Fluke', 'FN001', 24, '2023-10-15', '2024-04-15', '网络性能分析仪'),

-- 电子电路实验室设备
('数字示波器', 'Tektronix TBS1052B', 2, 'available', '2022-01-10', 4200.00, 'Tektronix', 'TEK001', 36, '2023-11-20', '2024-05-20', '双通道数字示波器'),
('信号发生器', 'Agilent 33220A', 2, 'available', '2022-01-10', 3800.00, 'Agilent', 'AG001', 36, '2023-11-20', '2024-05-20', '任意波形发生器'),
('万用表', 'Fluke 87V', 2, 'maintenance', '2021-05-15', 1200.00, 'Fluke', 'FL001', 24, '2023-08-10', '2024-02-10', '工业级数字万用表'),

-- 物理光学实验室设备
('激光器', 'He-Ne Laser 632.8nm', 3, 'available', '2021-11-30', 15000.00, 'Thorlabs', 'TH001', 24, '2023-09-15', '2024-03-15', '氦氖激光器'),
('光谱仪', 'Ocean Optics USB2000+', 3, 'available', '2022-02-28', 12000.00, 'Ocean Optics', 'OO001', 24, '2023-10-01', '2024-04-01', 'USB接口光纤光谱仪'),
('偏振片组', 'Polarizer Set', 3, 'available', '2021-08-20', 800.00, 'Edmund Optics', 'EO001', 12, '2023-06-15', '2023-12-15', '线偏振片组合'),

-- 生物实验室设备
('显微镜', 'Olympus CX23', 5, 'available', '2022-04-10', 6500.00, 'Olympus', 'OLY001', 36, '2023-12-05', '2024-06-05', '生物显微镜'),
('离心机', 'Eppendorf 5424R', 5, 'available', '2022-04-10', 8900.00, 'Eppendorf', 'EP001', 36, '2023-12-05', '2024-06-05', '台式冷冻离心机'),
('PCR仪', 'Bio-Rad T100', 5, 'available', '2021-12-15', 18000.00, 'Bio-Rad', 'BR001', 24, '2023-08-20', '2024-02-20', 'PCR扩增仪');

-- 插入课程数据
INSERT INTO `course` (course_name, course_code, teacher_id, department, credits, semester, academic_year, max_students, description) VALUES
('计算机网络', 'CS301', 2, '计算机科学与技术学院', 3, '2024春', '2023-2024', 40, '计算机网络原理与实践'),
('数字电路设计', 'EE201', 3, '电子工程学院', 4, '2024春', '2023-2024', 30, '数字电路设计与实现'),
('光学实验', 'PHY301', 4, '物理学院', 2, '2024春', '2023-2024', 25, '光学基础实验'),
('数据结构', 'CS201', 2, '计算机科学与技术学院', 4, '2024春', '2023-2024', 50, '数据结构与算法'),
('模拟电路', 'EE101', 3, '电子工程学院', 3, '2024春', '2023-2024', 35, '模拟电路基础');

-- 插入预约记录数据
INSERT INTO `reservation` (user_id, lab_id, course_id, reservation_date, start_time, end_time, purpose, student_count, status, approval_user_id, approval_time) VALUES
-- 已完成的预约
(2, 1, 1, '2024-01-15', '14:00:00', '16:00:00', '计算机网络实验课', 35, 'completed', 1, '2024-01-14 10:00:00'),
(3, 2, 2, '2024-01-16', '09:00:00', '11:00:00', '数字电路设计实验', 28, 'completed', 1, '2024-01-15 15:30:00'),
(4, 3, 3, '2024-01-17', '10:00:00', '12:00:00', '光学干涉实验', 20, 'completed', 1, '2024-01-16 09:15:00'),

-- 待审批的预约
(2, 1, 1, '2024-01-22', '14:00:00', '16:00:00', '网络协议分析实验', 40, 'pending', NULL, NULL),
(3, 2, 2, '2024-01-23', '09:00:00', '11:00:00', '数字滤波器设计', 30, 'pending', NULL, NULL),

-- 学生个人预约
(5, 1, NULL, '2024-01-20', '16:00:00', '18:00:00', '毕业设计实验', 1, 'approved', 2, '2024-01-19 14:20:00'),
(6, 2, NULL, '2024-01-21', '13:00:00', '15:00:00', '课程设计', 1, 'approved', 3, '2024-01-20 11:45:00');

-- 插入设备维修记录
INSERT INTO `equipment_repair` (equipment_id, reporter_id, repair_person, fault_description, repair_description, repair_cost, repair_status, priority, report_time, start_time, finish_time) VALUES
(6, 3, '李维修师傅', '万用表显示屏出现花屏现象', '更换LCD显示屏模块', 350.00, 'completed', 'medium', '2024-01-10 09:30:00', '2024-01-11 08:00:00', '2024-01-11 15:30:00'),
(3, 2, '王工程师', '网络分析仪无法正常启动', '更换电源模块', 1200.00, 'in_progress', 'high', '2024-01-18 14:15:00', '2024-01-19 09:00:00', NULL),
(8, 4, NULL, '光谱仪数据传输异常', NULL, NULL, 'reported', 'medium', '2024-01-20 16:45:00', NULL, NULL);

-- 插入耗材数据
INSERT INTO `consumable` (name, specification, lab_id, category, unit, current_stock, min_stock, max_stock, unit_price, supplier, storage_location) VALUES
-- 计算机网络实验室耗材
('网线', 'CAT6 UTP', 1, '网络配件', '米', 500, 50, 1000, 2.50, '网络设备公司', '实验室储物柜A1'),
('RJ45水晶头', '8P8C', 1, '网络配件', '个', 200, 20, 500, 0.80, '网络设备公司', '实验室储物柜A2'),

-- 电子电路实验室耗材
('电阻', '1/4W 碳膜电阻包', 2, '电子元件', '包', 50, 5, 100, 15.00, '电子元件供应商', '实验室储物柜B1'),
('电容', '电解电容器套装', 2, '电子元件', '套', 30, 3, 60, 25.00, '电子元件供应商', '实验室储物柜B2'),
('面包板', '830孔面包板', 2, '实验工具', '块', 40, 5, 80, 12.00, '实验设备公司', '实验室储物柜B3'),

-- 物理光学实验室耗材
('透镜', '凸透镜f=100mm', 3, '光学元件', '个', 20, 2, 40, 45.00, '光学仪器公司', '实验室储物柜C1'),
('反射镜', '平面反射镜50mm', 3, '光学元件', '个', 15, 2, 30, 35.00, '光学仪器公司', '实验室储物柜C2'),

-- 生物实验室耗材
('载玻片', '标准载玻片', 5, '实验用品', '盒', 25, 3, 50, 8.00, '实验用品公司', '实验室储物柜E1'),
('盖玻片', '18x18mm盖玻片', 5, '实验用品', '盒', 20, 2, 40, 12.00, '实验用品公司', '实验室储物柜E2'),
('培养皿', '90mm塑料培养皿', 5, '实验用品', '包', 15, 2, 30, 18.00, '实验用品公司', '实验室储物柜E3');

-- 插入耗材使用记录
INSERT INTO `consumable_usage` (consumable_id, user_id, reservation_id, quantity, usage_date, purpose, notes) VALUES
(1, 5, 6, 10, '2024-01-20', '搭建实验网络', '用于毕业设计网络拓扑搭建'),
(2, 5, 6, 8, '2024-01-20', '制作网线', '配合网线使用'),
(3, 6, 7, 1, '2024-01-21', '电路实验', '数字电路课程设计'),
(4, 6, 7, 1, '2024-01-21', '电路实验', '滤波电路设计'),
(8, 7, NULL, 2, '2024-01-18', '生物实验', '细胞观察实验');

-- 插入系统通知
INSERT INTO `notification` (title, content, type, target_users, sender_id, priority) VALUES
('系统维护通知', '系统将于本周六晚上22:00-24:00进行维护升级，期间无法使用预约功能，请提前安排。', 'system', '[1,2,3,4,5,6,7,8]', 1, 'high'),
('设备维护提醒', '网络分析仪(设备ID:3)需要进行定期维护，请相关人员及时处理。', 'maintenance', '[1,2]', 1, 'medium'),
('库存警告', '网线库存已低于警戒线，当前库存：45米，请及时补充。', 'inventory', '[1,2]', 1, 'medium'),
('预约审批通知', '您的实验室预约申请已通过审批，预约时间：2024-01-22 14:00-16:00，实验室：计算机网络实验室。', 'reservation', '[2]', 1, 'medium');