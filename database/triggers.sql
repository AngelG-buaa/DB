-- 高校实验室预约与设备管理系统触发器
USE lab_management_system;

DELIMITER $$

-- 1. 预约状态变更时自动发送通知
CREATE TRIGGER tr_reservation_status_change
AFTER UPDATE ON reservation
FOR EACH ROW
BEGIN
    DECLARE notification_title VARCHAR(100);
    DECLARE notification_content TEXT;
    DECLARE target_user_json JSON;
    
    -- 只在状态发生变化时触发
    IF OLD.status != NEW.status THEN
        SET target_user_json = JSON_ARRAY(NEW.user_id);
        
        CASE NEW.status
            WHEN 'approved' THEN
                SET notification_title = '预约审批通过';
                SET notification_content = CONCAT('您的实验室预约申请已通过审批。预约时间：', 
                    DATE_FORMAT(NEW.reservation_date, '%Y-%m-%d'), ' ', 
                    TIME_FORMAT(NEW.start_time, '%H:%i'), '-', 
                    TIME_FORMAT(NEW.end_time, '%H:%i'));
            WHEN 'rejected' THEN
                SET notification_title = '预约审批被拒';
                SET notification_content = CONCAT('很抱歉，您的实验室预约申请被拒绝。预约时间：', 
                    DATE_FORMAT(NEW.reservation_date, '%Y-%m-%d'), ' ', 
                    TIME_FORMAT(NEW.start_time, '%H:%i'), '-', 
                    TIME_FORMAT(NEW.end_time, '%H:%i'),
                    CASE WHEN NEW.rejection_reason IS NOT NULL 
                         THEN CONCAT('。拒绝原因：', NEW.rejection_reason) 
                         ELSE '' END);
            WHEN 'cancelled' THEN
                SET notification_title = '预约已取消';
                SET notification_content = CONCAT('预约已取消。原预约时间：', 
                    DATE_FORMAT(NEW.reservation_date, '%Y-%m-%d'), ' ', 
                    TIME_FORMAT(NEW.start_time, '%H:%i'), '-', 
                    TIME_FORMAT(NEW.end_time, '%H:%i'));
            ELSE
                SET notification_title = NULL;
        END CASE;
        
        -- 插入通知记录
        IF notification_title IS NOT NULL THEN
            INSERT INTO notification (title, content, type, target_users, sender_id, priority)
            VALUES (notification_title, notification_content, 'reservation', target_user_json, NEW.approval_user_id, 'medium');
        END IF;
    END IF;
END$$

-- 2. 设备状态变更时自动记录日志和发送通知
CREATE TRIGGER tr_equipment_status_change
AFTER UPDATE ON equipment
FOR EACH ROW
BEGIN
    DECLARE lab_manager_id INT;
    DECLARE notification_content TEXT;
    DECLARE target_users_json JSON;
    
    -- 只在状态发生变化时触发
    IF OLD.equip_status != NEW.equip_status THEN
        -- 获取实验室管理员ID
        SELECT manager_id INTO lab_manager_id 
        FROM laboratory 
        WHERE lab_id = NEW.lab_id;
        
        SET target_users_json = JSON_ARRAY(lab_manager_id);
        
        CASE NEW.equip_status
            WHEN 'maintenance' THEN
                SET notification_content = CONCAT('设备"', NEW.equip_name, '"(', NEW.model, ')状态已变更为维护中，请及时处理。');
                INSERT INTO notification (title, content, type, target_users, sender_id, priority)
                VALUES ('设备维护提醒', notification_content, 'maintenance', target_users_json, 1, 'medium');
            WHEN 'fault' THEN
                SET notification_content = CONCAT('设备"', NEW.equip_name, '"(', NEW.model, ')发生故障，请立即处理。');
                INSERT INTO notification (title, content, type, target_users, sender_id, priority)
                VALUES ('设备故障警告', notification_content, 'maintenance', target_users_json, 1, 'high');
            WHEN 'scrapped' THEN
                SET notification_content = CONCAT('设备"', NEW.equip_name, '"(', NEW.model, ')已报废，请更新实验室设备清单。');
                INSERT INTO notification (title, content, type, target_users, sender_id, priority)
                VALUES ('设备报废通知', notification_content, 'maintenance', target_users_json, 1, 'medium');
        END CASE;
    END IF;
END$$

-- 3. 耗材库存低于警戒线时自动发送警告
CREATE TRIGGER tr_consumable_stock_warning
AFTER UPDATE ON consumable
FOR EACH ROW
BEGIN
    DECLARE lab_manager_id INT;
    DECLARE notification_content TEXT;
    DECLARE target_users_json JSON;
    
    -- 检查库存是否低于最小库存警戒线
    IF NEW.current_stock <= NEW.min_stock AND OLD.current_stock > OLD.min_stock THEN
        -- 获取实验室管理员ID
        SELECT manager_id INTO lab_manager_id 
        FROM laboratory 
        WHERE lab_id = NEW.lab_id;
        
        SET target_users_json = JSON_ARRAY(lab_manager_id, 1); -- 管理员和系统管理员
        SET notification_content = CONCAT('耗材"', NEW.name, '"库存不足，当前库存：', NEW.current_stock, NEW.unit, 
                                        '，最小库存：', NEW.min_stock, NEW.unit, '，请及时补充。');
        
        INSERT INTO notification (title, content, type, target_users, sender_id, priority)
        VALUES ('库存警告', notification_content, 'inventory', target_users_json, 1, 'medium');
    END IF;
END$$

-- 4. 耗材使用后自动更新库存
CREATE TRIGGER tr_consumable_usage_update_stock
AFTER INSERT ON consumable_usage
FOR EACH ROW
BEGIN
    -- 更新耗材库存
    UPDATE consumable 
    SET current_stock = current_stock - NEW.quantity,
        updated_at = CURRENT_TIMESTAMP
    WHERE consumable_id = NEW.consumable_id;
END$$

-- 5. 设备维修完成后自动更新设备状态和维护时间
CREATE TRIGGER tr_equipment_repair_completion
AFTER UPDATE ON equipment_repair
FOR EACH ROW
BEGIN
    -- 当维修状态从其他状态变为completed时
    IF OLD.repair_status != 'completed' AND NEW.repair_status = 'completed' THEN
        -- 更新设备状态为可用，并更新最后维护时间
        UPDATE equipment 
        SET equip_status = 'available',
            last_maintenance = NEW.finish_time,
            next_maintenance = DATE_ADD(NEW.finish_time, INTERVAL 6 MONTH),
            updated_at = CURRENT_TIMESTAMP
        WHERE equipment_id = NEW.equipment_id;
    END IF;
END$$

-- 6. 预约创建时检查时间冲突
CREATE TRIGGER tr_reservation_conflict_check
BEFORE INSERT ON reservation
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    DECLARE error_message VARCHAR(255);
    
    -- 检查同一实验室在同一时间段是否有其他预约
    SELECT COUNT(*) INTO conflict_count
    FROM reservation
    WHERE lab_id = NEW.lab_id
      AND reservation_date = NEW.reservation_date
      AND status IN ('approved', 'pending', 'in_progress')
      AND (
          (NEW.start_time >= start_time AND NEW.start_time < end_time) OR
          (NEW.end_time > start_time AND NEW.end_time <= end_time) OR
          (NEW.start_time <= start_time AND NEW.end_time >= end_time)
      );
    
    IF conflict_count > 0 THEN
        SET error_message = CONCAT('预约时间冲突：实验室在 ', 
                                 DATE_FORMAT(NEW.reservation_date, '%Y-%m-%d'), ' ',
                                 TIME_FORMAT(NEW.start_time, '%H:%i'), '-',
                                 TIME_FORMAT(NEW.end_time, '%H:%i'), ' 已有其他预约');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
    END IF;
    
    -- 检查实验室是否可用
    IF EXISTS (SELECT 1 FROM laboratory WHERE lab_id = NEW.lab_id AND lab_status != 'available') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '实验室当前不可用，无法预约';
    END IF;
END$$

-- 7. 用户状态变更时自动处理相关预约
CREATE TRIGGER tr_user_status_change
AFTER UPDATE ON user
FOR EACH ROW
BEGIN
    -- 当用户状态变为inactive时，取消其未来的预约
    IF OLD.status = 'active' AND NEW.status = 'inactive' THEN
        UPDATE reservation 
        SET status = 'cancelled',
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.user_id 
          AND status IN ('pending', 'approved')
          AND (reservation_date > CURDATE() OR 
               (reservation_date = CURDATE() AND start_time > CURTIME()));
    END IF;
END$$

-- 8. 实验室状态变更时处理相关预约
CREATE TRIGGER tr_laboratory_status_change
AFTER UPDATE ON laboratory
FOR EACH ROW
BEGIN
    DECLARE notification_content TEXT;
    DECLARE affected_users JSON;
    
    -- 当实验室状态变为不可用时，取消相关预约
    IF OLD.lab_status = 'available' AND NEW.lab_status != 'available' THEN
        -- 获取受影响的用户列表
        SELECT JSON_ARRAYAGG(user_id) INTO affected_users
        FROM reservation
        WHERE lab_id = NEW.lab_id 
          AND status IN ('pending', 'approved')
          AND (reservation_date > CURDATE() OR 
               (reservation_date = CURDATE() AND start_time > CURTIME()));
        
        -- 取消相关预约
        UPDATE reservation 
        SET status = 'cancelled',
            rejection_reason = CONCAT('实验室状态变更为：', NEW.lab_status),
            updated_at = CURRENT_TIMESTAMP
        WHERE lab_id = NEW.lab_id 
          AND status IN ('pending', 'approved')
          AND (reservation_date > CURDATE() OR 
               (reservation_date = CURDATE() AND start_time > CURTIME()));
        
        -- 发送通知给受影响的用户
        IF affected_users IS NOT NULL THEN
            SET notification_content = CONCAT('由于实验室"', NEW.lab_name, '"状态变更为', NEW.lab_status, 
                                            '，您的相关预约已被取消，请重新安排。');
            INSERT INTO notification (title, content, type, target_users, sender_id, priority)
            VALUES ('预约取消通知', notification_content, 'reservation', affected_users, 1, 'high');
        END IF;
    END IF;
END$$

DELIMITER ;

-- 创建索引以提高触发器性能
CREATE INDEX idx_reservation_lab_date_time ON reservation(lab_id, reservation_date, start_time, end_time);
CREATE INDEX idx_reservation_user_status ON reservation(user_id, status);
CREATE INDEX idx_equipment_lab_status ON equipment(lab_id, equip_status);
CREATE INDEX idx_consumable_stock ON consumable(lab_id, current_stock, min_stock);
CREATE INDEX idx_notification_target_users ON notification(target_users);