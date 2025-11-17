-- 高校实验室预约与设备管理系统存储过程
USE lab_management_system;

-- 设置分隔符
DELIMITER //

-- 1. 创建预约的存储过程
DROP PROCEDURE IF EXISTS create_reservation//
CREATE PROCEDURE create_reservation(
    IN p_user_id INT,
    IN p_lab_id INT,
    IN p_course_id INT,
    IN p_reservation_date DATE,
    IN p_start_time TIME,
    IN p_end_time TIME,
    IN p_purpose TEXT,
    IN p_student_count INT,
    IN p_equipment_needed JSON,
    OUT p_reservation_id INT,
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE v_conflict_count INT DEFAULT 0;
    DECLARE v_lab_status VARCHAR(20);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result = 'Error: 预约创建失败';
        SET p_reservation_id = -1;
    END;

    START TRANSACTION;
    
    -- 检查实验室状态
    SELECT lab_status INTO v_lab_status FROM laboratory WHERE id = p_lab_id;
    IF v_lab_status != 'available' THEN
        SET p_result = 'Error: 实验室不可用';
        SET p_reservation_id = -1;
        ROLLBACK;
    ELSE
        -- 检查时间冲突
        SELECT COUNT(*) INTO v_conflict_count
        FROM reservation 
        WHERE lab_id = p_lab_id 
        AND reservation_date = p_reservation_date
        AND status IN ('approved', 'pending')
        AND (
            (p_start_time BETWEEN start_time AND end_time) OR
            (p_end_time BETWEEN start_time AND end_time) OR
            (start_time BETWEEN p_start_time AND p_end_time)
        );
        
        IF v_conflict_count > 0 THEN
            SET p_result = 'Error: 时间冲突，该时段已被预约';
            SET p_reservation_id = -1;
            ROLLBACK;
        ELSE
            -- 创建预约
            INSERT INTO reservation (
                user_id, lab_id, course_id, reservation_date, 
                start_time, end_time, purpose, student_count, equipment_needed
            ) VALUES (
                p_user_id, p_lab_id, p_course_id, p_reservation_date,
                p_start_time, p_end_time, p_purpose, p_student_count, p_equipment_needed
            );
            
            SET p_reservation_id = LAST_INSERT_ID();
            SET p_result = 'Success: 预约创建成功';
            COMMIT;
        END IF;
    END IF;
END//

-- 2. 审批预约的存储过程
DROP PROCEDURE IF EXISTS approve_reservation//
CREATE PROCEDURE approve_reservation(
    IN p_reservation_id INT,
    IN p_approval_user_id INT,
    IN p_status ENUM('approved', 'rejected'),
    IN p_approval_notes TEXT,
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE v_current_status VARCHAR(20);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result = 'Error: 审批操作失败';
    END;

    START TRANSACTION;
    
    -- 检查预约状态
    SELECT status INTO v_current_status FROM reservation WHERE id = p_reservation_id;
    
    IF v_current_status != 'pending' THEN
        SET p_result = 'Error: 预约状态不允许审批';
        ROLLBACK;
    ELSE
        -- 更新预约状态
        UPDATE reservation 
        SET status = p_status,
            approval_user_id = p_approval_user_id,
            approval_time = NOW(),
            approval_notes = p_approval_notes
        WHERE id = p_reservation_id;
        
        SET p_result = CONCAT('Success: 预约已', IF(p_status = 'approved', '通过', '拒绝'));
        COMMIT;
    END IF;
END//

-- 3. 设备维修报告存储过程
DROP PROCEDURE IF EXISTS report_equipment_fault//
CREATE PROCEDURE report_equipment_fault(
    IN p_equipment_id INT,
    IN p_reporter_id INT,
    IN p_fault_description TEXT,
    IN p_priority ENUM('low', 'medium', 'high', 'urgent'),
    OUT p_repair_id INT,
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result = 'Error: 故障报告提交失败';
        SET p_repair_id = -1;
    END;

    START TRANSACTION;
    
    -- 更新设备状态为维修中
    UPDATE equipment SET equip_status = 'maintenance' WHERE id = p_equipment_id;
    
    -- 创建维修记录
    INSERT INTO equipment_repair (
        equipment_id, reporter_id, fault_description, priority
    ) VALUES (
        p_equipment_id, p_reporter_id, p_fault_description, p_priority
    );
    
    SET p_repair_id = LAST_INSERT_ID();
    SET p_result = 'Success: 故障报告提交成功';
    COMMIT;
END//

-- 4. 耗材使用记录存储过程
DROP PROCEDURE IF EXISTS use_consumable//
CREATE PROCEDURE use_consumable(
    IN p_consumable_id INT,
    IN p_user_id INT,
    IN p_reservation_id INT,
    IN p_quantity INT,
    IN p_purpose VARCHAR(200),
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE v_current_stock INT;
    DECLARE v_min_stock INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result = 'Error: 耗材使用记录失败';
    END;

    START TRANSACTION;
    
    -- 检查库存
    SELECT current_stock, min_stock INTO v_current_stock, v_min_stock 
    FROM consumable WHERE id = p_consumable_id;
    
    IF v_current_stock < p_quantity THEN
        SET p_result = 'Error: 库存不足';
        ROLLBACK;
    ELSE
        -- 更新库存
        UPDATE consumable 
        SET current_stock = current_stock - p_quantity 
        WHERE id = p_consumable_id;
        
        -- 记录使用
        INSERT INTO consumable_usage (
            consumable_id, user_id, reservation_id, quantity, 
            usage_date, purpose
        ) VALUES (
            p_consumable_id, p_user_id, p_reservation_id, p_quantity,
            CURDATE(), p_purpose
        );
        
        -- 检查是否需要库存警告
        IF (v_current_stock - p_quantity) <= v_min_stock THEN
            SET p_result = 'Warning: 耗材使用成功，但库存已低于警戒线';
        ELSE
            SET p_result = 'Success: 耗材使用记录成功';
        END IF;
        
        COMMIT;
    END IF;
END//

-- 5. 获取实验室使用统计的存储过程
DROP PROCEDURE IF EXISTS get_lab_usage_stats//
CREATE PROCEDURE get_lab_usage_stats(
    IN p_lab_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE,
    OUT p_total_reservations INT,
    OUT p_total_hours DECIMAL(10,2),
    OUT p_usage_rate DECIMAL(5,2)
)
BEGIN
    DECLARE v_total_available_hours DECIMAL(10,2);
    
    -- 计算总预约次数
    SELECT COUNT(*) INTO p_total_reservations
    FROM reservation 
    WHERE lab_id = p_lab_id 
    AND reservation_date BETWEEN p_start_date AND p_end_date
    AND status = 'completed';
    
    -- 计算总使用小时数
    SELECT COALESCE(SUM(TIMESTAMPDIFF(MINUTE, 
        CONCAT(reservation_date, ' ', start_time),
        CONCAT(reservation_date, ' ', end_time)
    )) / 60.0, 0) INTO p_total_hours
    FROM reservation 
    WHERE lab_id = p_lab_id 
    AND reservation_date BETWEEN p_start_date AND p_end_date
    AND status = 'completed';
    
    -- 计算可用总小时数（假设每天8小时工作时间）
    SET v_total_available_hours = DATEDIFF(p_end_date, p_start_date) * 8;
    
    -- 计算使用率
    IF v_total_available_hours > 0 THEN
        SET p_usage_rate = (p_total_hours / v_total_available_hours) * 100;
    ELSE
        SET p_usage_rate = 0;
    END IF;
END//

-- 6. 获取用户预约历史的存储过程
DROP PROCEDURE IF EXISTS get_user_reservations//
CREATE PROCEDURE get_user_reservations(
    IN p_user_id INT,
    IN p_limit INT,
    IN p_offset INT
)
BEGIN
    SELECT 
        r.id,
        r.reservation_date,
        r.start_time,
        r.end_time,
        r.purpose,
        r.status,
        l.lab_name,
        l.location,
        c.course_name,
        r.created_at
    FROM reservation r
    LEFT JOIN laboratory l ON r.lab_id = l.id
    LEFT JOIN course c ON r.course_id = c.id
    WHERE r.user_id = p_user_id
    ORDER BY r.reservation_date DESC, r.start_time DESC
    LIMIT p_limit OFFSET p_offset;
END//

-- 7. 设备维护提醒存储过程
DROP PROCEDURE IF EXISTS check_equipment_maintenance//
CREATE PROCEDURE check_equipment_maintenance()
BEGIN
    -- 查找需要维护的设备
    SELECT 
        e.id,
        e.equip_name,
        e.model,
        e.next_maintenance,
        l.lab_name,
        l.manager_id
    FROM equipment e
    JOIN laboratory l ON e.lab_id = l.id
    WHERE e.next_maintenance <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
    AND e.equip_status = 'available'
    ORDER BY e.next_maintenance ASC;
END//

-- 恢复分隔符
DELIMITER ;

-- 创建视图
-- 1. 实验室使用情况视图
CREATE OR REPLACE VIEW lab_usage_view AS
SELECT 
    l.id as lab_id,
    l.lab_name,
    l.location,
    l.capacity,
    COUNT(r.id) as total_reservations,
    COUNT(CASE WHEN r.status = 'completed' THEN 1 END) as completed_reservations,
    COUNT(CASE WHEN r.status = 'pending' THEN 1 END) as pending_reservations,
    COALESCE(AVG(TIMESTAMPDIFF(MINUTE, 
        CONCAT(r.reservation_date, ' ', r.start_time),
        CONCAT(r.reservation_date, ' ', r.end_time)
    )) / 60.0, 0) as avg_usage_hours
FROM laboratory l
LEFT JOIN reservation r ON l.id = r.lab_id
GROUP BY l.id, l.lab_name, l.location, l.capacity;

-- 2. 设备状态统计视图
CREATE OR REPLACE VIEW equipment_status_view AS
SELECT 
    l.id as lab_id,
    l.lab_name,
    COUNT(e.id) as total_equipment,
    COUNT(CASE WHEN e.equip_status = 'available' THEN 1 END) as available_count,
    COUNT(CASE WHEN e.equip_status = 'in_use' THEN 1 END) as in_use_count,
    COUNT(CASE WHEN e.equip_status = 'maintenance' THEN 1 END) as maintenance_count,
    COUNT(CASE WHEN e.equip_status = 'damaged' THEN 1 END) as damaged_count
FROM laboratory l
LEFT JOIN equipment e ON l.id = e.lab_id
GROUP BY l.id, l.lab_name;

-- 3. 用户预约统计视图
CREATE OR REPLACE VIEW user_reservation_stats AS
SELECT 
    u.id as user_id,
    u.username,
    u.real_name,
    u.user_type,
    COUNT(r.id) as total_reservations,
    COUNT(CASE WHEN r.status = 'completed' THEN 1 END) as completed_reservations,
    COUNT(CASE WHEN r.status = 'cancelled' THEN 1 END) as cancelled_reservations,
    COALESCE(SUM(TIMESTAMPDIFF(MINUTE, 
        CONCAT(r.reservation_date, ' ', r.start_time),
        CONCAT(r.reservation_date, ' ', r.end_time)
    )) / 60.0, 0) as total_usage_hours
FROM user u
LEFT JOIN reservation r ON u.id = r.user_id
GROUP BY u.id, u.username, u.real_name, u.user_type;