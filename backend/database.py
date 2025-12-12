#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库访问与初始化（统一入口）
"""

import os
import sys
import logging
import pymysql

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 说明：本脚本使用与官方文档一致的直连方式（PyMySQL），不依赖 .env 文件。

from app.utils.auth import AuthUtils

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== 直连配置（与官方文档一致的方式） =====
# 请填写正确且可达的数据库地址与端口，数据库名为您在华为云实例中的库名。
# 用户名、密码将从系统环境变量读取（例如 DB_USER、DB_PASSWORD），不使用 .env 文件。
TAURUS_HOST = os.getenv('TAURUS_HOST', '124.70.86.207')  # 默认使用公网地址
TAURUS_PORT = int(os.getenv('TAURUS_PORT', '3306'))
TAURUS_DB = os.getenv('TAURUS_DB', 'h_db23373478')
TAURUS_USER = os.getenv('TAURUS_USER', 'u23373478')
TAURUS_PASSWORD = os.getenv('TAURUS_PASSWORD', 'Aa614026')

DB_DSN = {
    'host': TAURUS_HOST,
    'port': TAURUS_PORT,
    'user': TAURUS_USER,
    'password': TAURUS_PASSWORD,
    'database': TAURUS_DB,
    'charset': 'utf8',
    'autocommit': True
}

class Database:
    def __init__(self, dsn: dict):
        self._dsn = dict(dsn or {})
    def get_connection(self):
        return pymysql.connect(**self._dsn)
    def execute_update(self, sql, params=None):
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                affected_rows = cursor.execute(sql, params) if params is not None else cursor.execute(sql)
            conn.commit()
            return { 'success': True, 'affected_rows': affected_rows, 'last_insert_id': cursor.lastrowid }
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.error(f"数据库操作失败: {str(e)}")
            return { 'success': False, 'error': str(e), 'affected_rows': 0 }
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    def execute_query(self, sql, params=None):
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params) if params is not None else cursor.execute(sql)
                rows = cursor.fetchall()
            return { 'success': True, 'data': rows }
        except Exception as e:
            logger.error(f"数据库查询失败: {str(e)}")
            return { 'success': False, 'error': str(e), 'data': [] }
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    def execute_transaction(self, queries):
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                results = []
                for sql, params in queries:
                    affected_rows = cursor.execute(sql, params) if params else cursor.execute(sql)
                    results.append({ 'sql': sql, 'affected_rows': affected_rows, 'last_insert_id': cursor.lastrowid })
            conn.commit()
            return { 'success': True, 'results': results }
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"事务执行失败: {str(e)}")
            return { 'success': False, 'error': str(e), 'results': [] }
        finally:
            if conn:
                conn.close()
    def execute_paginated_query(self, sql, params=None, page=1, page_size=10):
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                count_sql = f"SELECT COUNT(*) as total FROM ({sql}) as count_table"
                cursor.execute(count_sql, params) if params else cursor.execute(count_sql)
                total_result = cursor.fetchone()
                total = total_result['total'] if total_result else 0
                offset = (page - 1) * page_size
                paginated_sql = f"{sql} LIMIT %s OFFSET %s"
                paginated_params = list(params or ()) + [page_size, offset]
                cursor.execute(paginated_sql, paginated_params)
                data = cursor.fetchall()
                return { 'success': True, 'data': data, 'pagination': { 'page': page, 'page_size': page_size, 'total': total, 'total_pages': (total + page_size - 1) // page_size } }
        except Exception as e:
            logger.error(f"分页查询执行失败: {sql}, 参数: {params}, 错误: {str(e)}")
            return { 'success': False, 'error': str(e), 'data': [], 'pagination': { 'page': page, 'page_size': page_size, 'total': 0, 'total_pages': 0 } }
        finally:
            if conn:
                conn.close()

_db = Database(DB_DSN)

def get_connection():
    return _db.get_connection()

def execute_update(sql, params=None):
    return _db.execute_update(sql, params)

def execute_query(sql, params=None):
    return _db.execute_query(sql, params)


def execute_transaction(queries):
    return _db.execute_transaction(queries)

def execute_paginated_query(sql, params=None, page=1, page_size=10):
    return _db.execute_paginated_query(sql, params, page, page_size)

def test_connection():
    """测试数据库连接"""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        return False

def create_tables():
    """创建数据库表"""
    
    # 用户表
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        phone VARCHAR(20),
        role ENUM('admin', 'teacher', 'student') NOT NULL DEFAULT 'student',
        student_id VARCHAR(20),
        status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_username (username),
        INDEX idx_email (email),
        INDEX idx_role (role),
        INDEX idx_student_id (student_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # 实验室表
    laboratories_table = """
    CREATE TABLE IF NOT EXISTS laboratories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        location VARCHAR(200),
        capacity INT NOT NULL DEFAULT 0,
        description TEXT,
        status ENUM('active', 'inactive', 'maintenance') NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_name (name),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # 设备表
    equipment_table = """
    CREATE TABLE IF NOT EXISTS equipment (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        model VARCHAR(100),
        serial_number VARCHAR(100) UNIQUE,
        laboratory_id INT NOT NULL,
        status ENUM('available', 'in_use', 'maintenance', 'damaged', 'retired') NOT NULL DEFAULT 'available',
        purchase_date DATE,
        warranty_date DATE,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (laboratory_id) REFERENCES laboratories(id) ON DELETE CASCADE,
        INDEX idx_laboratory_id (laboratory_id),
        INDEX idx_status (status),
        INDEX idx_serial_number (serial_number)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # 预约表
    reservations_table = """
    CREATE TABLE IF NOT EXISTS reservations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        laboratory_id INT NOT NULL,
        reservation_date DATE NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        purpose VARCHAR(200) NOT NULL,
        participant_count INT NOT NULL DEFAULT 1,
        equipment_ids VARCHAR(255),
        status ENUM('pending', 'confirmed', 'cancelled', 'completed') NOT NULL DEFAULT 'pending',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (laboratory_id) REFERENCES laboratories(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_laboratory_id (laboratory_id),
        INDEX idx_reservation_date (reservation_date),
        INDEX idx_status (status),
        INDEX idx_datetime (reservation_date, start_time, end_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # 预约设备关联表
    reservation_equipment_table = """
    CREATE TABLE IF NOT EXISTS reservation_equipment (
        id INT AUTO_INCREMENT PRIMARY KEY,
        reservation_id INT NOT NULL,
        equipment_id INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE,
        FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
        UNIQUE KEY unique_reservation_equipment (reservation_id, equipment_id),
        INDEX idx_reservation_id (reservation_id),
        INDEX idx_equipment_id (equipment_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # 课程表
    courses_table = """
    CREATE TABLE IF NOT EXISTS courses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        code VARCHAR(20) NOT NULL,
        description TEXT,
        credits INT NOT NULL DEFAULT 1,
        semester VARCHAR(20) NOT NULL,
        teacher_id INT,
        status ENUM('active', 'inactive', 'completed') NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL,
        UNIQUE KEY unique_course_semester (code, semester),
        INDEX idx_teacher_id (teacher_id),
        INDEX idx_semester (semester),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # 课程学生关联表
    course_students_table = """
    CREATE TABLE IF NOT EXISTS course_students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        course_id INT NOT NULL,
        student_id INT NOT NULL,
        enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE KEY unique_course_student (course_id, student_id),
        INDEX idx_course_id (course_id),
        INDEX idx_student_id (student_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    tables = [
        ("users", users_table),
        ("laboratories", laboratories_table),
        ("equipment", equipment_table),
        ("reservations", reservations_table),
        ("reservation_equipment", reservation_equipment_table),
        ("courses", courses_table),
        ("course_students", course_students_table)
    ]
    
    for table_name, table_sql in tables:
        logger.info(f"创建表: {table_name}")
        result = execute_update(table_sql)
        if result['success']:
            logger.info(f"表 {table_name} 创建成功")
        else:
            logger.error(f"表 {table_name} 创建失败: {result.get('error')}")
            return False
    
    return True

def column_exists(table_name, column_name):
    """检查列是否存在"""
    sql = """
    SELECT 1
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
    LIMIT 1
    """
    result = execute_query(sql, (TAURUS_DB, table_name, column_name))
    return result['success'] and bool(result['data'])

def get_column_type(table_name, column_name):
    """获取列类型（例如 ENUM('a','b')）"""
    sql = """
    SELECT COLUMN_TYPE
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
    LIMIT 1
    """
    result = execute_query(sql, (TAURUS_DB, table_name, column_name))
    if result['success'] and result['data']:
        return result['data'][0]['COLUMN_TYPE']
    return None

def migrate_tables():
    """迁移已存在的表结构以与API一致"""
    logger.info("检查并迁移数据库表结构以对齐API")

    # equipment: warranty_expiry -> warranty_date
    if not column_exists('equipment', 'warranty_date') and column_exists('equipment', 'warranty_expiry'):
        logger.info("重命名 equipment.warranty_expiry 为 warranty_date")
        alter_sql = "ALTER TABLE equipment CHANGE COLUMN warranty_expiry warranty_date DATE"
        result = execute_update(alter_sql)
        if result['success']:
            logger.info("equipment.warranty_date 重命名成功")
        else:
            logger.error(f"重命名 warranty_date 失败: {result.get('error')}")

    # equipment: warranty_period(INT, 月) -> warranty_date(DATE)
    # 某些旧库使用 warranty_period（月数），而API期望 warranty_date（日期）
    if not column_exists('equipment', 'warranty_date') and column_exists('equipment', 'warranty_period'):
        logger.info("检测到 equipment.warranty_period，准备新增并回填 warranty_date")
        add_sql = "ALTER TABLE equipment ADD COLUMN warranty_date DATE NULL AFTER purchase_date"
        add_result = execute_update(add_sql)
        if add_result['success']:
            logger.info("equipment.warranty_date 列添加成功，开始回填数据")
            # 依据 purchase_date + warranty_period(月) 计算保修到期日
            fill_sql = (
                "UPDATE equipment "
                "SET warranty_date = CASE "
                "WHEN purchase_date IS NOT NULL AND warranty_period IS NOT NULL "
                "THEN DATE_ADD(purchase_date, INTERVAL warranty_period MONTH) "
                "ELSE NULL END"
            )
            fill_result = execute_update(fill_sql)
            if fill_result['success']:
                logger.info("equipment.warranty_date 数据回填完成")
            else:
                logger.error(f"回填 warranty_date 失败: {fill_result.get('error')}")
        else:
            logger.error(f"添加 warranty_date 列失败: {add_result.get('error')}")

    # 兜底：若 warranty_date 仍不存在（既无 warranty_expiry 也无 warranty_period），则直接添加空列
    if not column_exists('equipment', 'warranty_date'):
        logger.info("equipment.warranty_date 列缺失，执行兜底添加")
        add_sql = "ALTER TABLE equipment ADD COLUMN warranty_date DATE NULL AFTER purchase_date"
        add_result = execute_update(add_sql)
        if add_result['success']:
            logger.info("equipment.warranty_date 列已添加")
        else:
            logger.error(f"添加 warranty_date 列失败: {add_result.get('error')}")

    # equipment: ensure status enum includes 'retired'
    status_type = get_column_type('equipment', 'status')
    if status_type and 'retired' not in status_type:
        logger.info("扩展 equipment.status 枚举以包含 'retired'")
        alter_sql = (
            "ALTER TABLE equipment MODIFY COLUMN status "
            "ENUM('available','in_use','maintenance','damaged','retired') NOT NULL DEFAULT 'available'"
        )
        result = execute_update(alter_sql)
        if result['success']:
            logger.info("equipment.status 枚举更新成功")
        else:
            logger.error(f"更新 equipment.status 失败: {result.get('error')}")

    # reservations: date -> reservation_date
    if not column_exists('reservations', 'reservation_date') and column_exists('reservations', 'date'):
        logger.info("重命名 reservations.date 为 reservation_date")
        alter_sql = "ALTER TABLE reservations CHANGE COLUMN date reservation_date DATE NOT NULL"
        result = execute_update(alter_sql)
        if result['success']:
            logger.info("reservations.reservation_date 重命名成功")
        else:
            logger.error(f"重命名 reservation_date 失败: {result.get('error')}")

    # reservations: add equipment_ids if missing
    if not column_exists('reservations', 'equipment_ids'):
        logger.info("添加 reservations.equipment_ids 列")
        alter_sql = "ALTER TABLE reservations ADD COLUMN equipment_ids VARCHAR(255) NULL AFTER participant_count"
        result = execute_update(alter_sql)
        if result['success']:
            logger.info("reservations.equipment_ids 添加成功")
        else:
            logger.error(f"添加 equipment_ids 失败: {result.get('error')}")

    logger.info("数据库结构迁移检查完成")

def insert_initial_data():
    """插入初始数据"""
    
    # 检查是否已有管理员用户
    check_admin_sql = "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
    result = execute_query(check_admin_sql)
    
    if not result['success']:
        logger.error("检查管理员用户失败")
        return False
    
    admin_count = result['data'][0]['count']
    
    if admin_count > 0:
        logger.info("管理员用户已存在，跳过初始数据插入")
        return True
    
    # 创建默认管理员用户
    admin_password = AuthUtils.hash_password("admin123")
    
    insert_admin_sql = """
    INSERT INTO users (username, password, name, email, role, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """
    
    admin_data = (
        "admin",
        admin_password,
        "系统管理员",
        "admin@example.com",
        "admin",
        "active"
    )
    
    result = execute_update(insert_admin_sql, admin_data)
    
    if result['success']:
        logger.info("默认管理员用户创建成功")
        logger.info("用户名: admin")
        logger.info("密码: admin123")
    else:
        logger.error(f"创建管理员用户失败: {result.get('error')}")
        return False
    
    # 不再插入任何示例数据（教师、学生、实验室），由实际数据库数据驱动
    return True

def create_triggers():
    """创建或更新数据库触发器（直接执行定义，避免脚本解析问题）"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # 先删除可能存在的旧触发器
            for name in [
                'after_reservation_insert',
                'after_reservation_update',
                'after_equipment_repair_insert',
                'after_equipment_repair_update',
                'after_equipment_repair_delete',
                'before_equipment_repair_insert_default_times',
                'before_equipment_delete',
                'before_user_delete',
                'before_laboratory_delete',
                'after_consumable_usage_insert'
            ]:
                try:
                    cursor.execute(f"DROP TRIGGER IF EXISTS {name}")
                except Exception as drop_err:
                    logger.warning(f"删除触发器 {name} 时忽略错误: {drop_err}")

            # 使用硬编码的触发器定义（不再创建耗材库存相关触发器，改用存储过程）
            trigger_sql_list = [
                """
                CREATE TRIGGER before_equipment_repair_insert_default_times
                BEFORE INSERT ON equipment_repair
                FOR EACH ROW
                BEGIN
                    IF NEW.start_time IS NULL THEN
                        SET NEW.start_time = NOW();
                    END IF;
                    IF NEW.repair_status = 'completed' AND NEW.finish_time IS NULL THEN
                        SET NEW.finish_time = NOW();
                    END IF;
                END
                """,
                """
                CREATE TRIGGER after_equipment_repair_insert
                AFTER INSERT ON equipment_repair
                FOR EACH ROW
                BEGIN
                    IF NEW.repair_status = 'in_progress' THEN
                        UPDATE equipment SET status = 'maintenance' WHERE id = NEW.equipment_id;
                    END IF;
                END
                """,
                """
                CREATE TRIGGER after_equipment_repair_update
                AFTER UPDATE ON equipment_repair
                FOR EACH ROW
                BEGIN
                    IF NEW.repair_status IN ('completed','cancelled') AND OLD.repair_status NOT IN ('completed','cancelled') THEN
                        UPDATE equipment SET status = 'available' WHERE id = NEW.equipment_id;
                    ELSEIF NEW.repair_status = 'in_progress' AND OLD.repair_status <> 'in_progress' THEN
                        UPDATE equipment SET status = 'maintenance' WHERE id = NEW.equipment_id;
                    END IF;
                END
                """,
                """
                CREATE TRIGGER after_equipment_repair_delete
                AFTER DELETE ON equipment_repair
                FOR EACH ROW
                BEGIN
                    DECLARE cnt INT;
                    SELECT COUNT(*) INTO cnt FROM equipment_repair WHERE equipment_id = OLD.equipment_id AND repair_status = 'in_progress';
                    IF cnt = 0 THEN
                        UPDATE equipment SET status = 'available' WHERE id = OLD.equipment_id;
                    END IF;
                END
                """,
                """
                CREATE TRIGGER before_equipment_delete
                BEFORE DELETE ON equipment
                FOR EACH ROW
                BEGIN
                    DECLARE reservation_count INT;
                    SELECT COUNT(*) INTO reservation_count
                    FROM reservation_equipment re
                    JOIN reservations r ON re.reservation_id = r.id
                    WHERE re.equipment_id = OLD.id AND r.status = 'confirmed';
                    IF reservation_count > 0 THEN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot delete equipment with active reservations.';
                    END IF;
                END
                """,
                """
                CREATE TRIGGER before_user_delete
                BEFORE DELETE ON users
                FOR EACH ROW
                BEGIN
                    DECLARE reservation_count INT;
                    SELECT COUNT(*) INTO reservation_count FROM reservations WHERE user_id = OLD.id AND status = 'confirmed';
                    IF reservation_count > 0 THEN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot delete user with active reservations.';
                    END IF;
                END
                """,
                """
                CREATE TRIGGER before_laboratory_delete
                BEFORE DELETE ON laboratories
                FOR EACH ROW
                BEGIN
                    DECLARE equipment_count INT;
                    SELECT COUNT(*) INTO equipment_count FROM equipment WHERE laboratory_id = OLD.id;
                    IF equipment_count > 0 THEN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot delete laboratory with assigned equipment.';
                    END IF;
                END
                """
            ]

            for stmt in trigger_sql_list:
                cursor.execute(stmt)

        conn.commit()
        logger.info("数据库触发器创建/更新完成")
        return True
    except Exception as e:
        logger.error(f"创建数据库触发器失败: {e}")
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

def create_stored_procedures():
    """创建或更新存储过程"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # 删除旧的过程定义
            for name in ['sp_use_consumable']:
                try:
                    cursor.execute(f"DROP PROCEDURE IF EXISTS {name}")
                except Exception as drop_err:
                    logger.warning(f"删除存储过程 {name} 时忽略错误: {drop_err}")

            # 创建耗材使用的存储过程（原子：扣减库存 + 记录使用）
            proc_sql = """
            CREATE PROCEDURE sp_use_consumable(IN p_consumable_id INT, IN p_quantity DECIMAL(10,2), IN p_user_id INT, IN p_purpose VARCHAR(200))
            BEGIN
                DECLARE current_stock DECIMAL(10,2);
                SELECT current_stock INTO current_stock FROM consumables WHERE id = p_consumable_id FOR UPDATE;
                IF current_stock IS NULL THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Consumable not found';
                END IF;
                IF p_quantity <= 0 THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity must be positive';
                END IF;
                IF current_stock < p_quantity THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient stock';
                END IF;
                UPDATE consumables SET current_stock = current_stock - p_quantity, usage_count = COALESCE(usage_count,0) + 1 WHERE id = p_consumable_id;
                INSERT INTO consumable_usage (consumable_id, user_id, quantity, purpose, created_at) VALUES (p_consumable_id, p_user_id, p_quantity, p_purpose, NOW());
            END
            """
            cursor.execute(proc_sql)

        conn.commit()
        logger.info("数据库存储过程创建/更新完成")
        return True
    except Exception as e:
        logger.error(f"创建数据库存储过程失败: {e}")
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

def main():
    """主函数"""
    logger.info("开始数据库初始化...")
    
    if not test_connection():
        logger.error("无法连接到数据库，请检查您的配置和网络。")
        return
        
    logger.info("数据库连接成功")
    
    if create_tables():
        logger.info("所有表已成功创建或已存在")
    else:
        logger.error("创建表时发生错误，初始化中止")
        return
        
    migrate_tables()
    
    if insert_initial_data():
        logger.info("初始数据检查或插入完成")
    else:
        logger.error("插入初始数据时发生错误")

    if create_triggers():
        logger.info("数据库触发器已成功创建")
    else:
        logger.error("创建触发器时发生错误")

    # 创建/更新存储过程
    if create_stored_procedures():
        logger.info("数据库存储过程已成功创建")
    else:
        logger.error("创建存储过程时发生错误")
        
    logger.info("数据库初始化完成")

if __name__ == '__main__':
    main()
