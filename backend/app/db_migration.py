#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量数据库迁移：确保 equipment_repair 表包含前端所需字段
在 app.py 启动阶段调用 run()，不足不阻塞启动。
"""

import logging
from typing import List, Dict
from backend.database import execute_query, execute_update

logger = logging.getLogger(__name__)


def _get_existing_columns(table_name: str) -> List[str]:
    try:
        sql = (
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s"
        )
        res = execute_query(sql, (table_name,))
        if res['success']:
            return [row['COLUMN_NAME'] for row in res['data']]
        logger.warning(f"查询表列失败: {res.get('error')}\n表: {table_name}")
        return []
    except Exception as e:
        logger.error(f"获取表列异常: {str(e)}")
        return []


def _ensure_equipment_repair_columns():
    table = 'equipment_repair'
    existing = set(_get_existing_columns(table))
    alters: List[Dict[str, str]] = []

    # 预期完成日期
    if 'expected_finish_date' not in existing:
        alters.append({
            'sql': f"ALTER TABLE {table} ADD COLUMN `expected_finish_date` DATE NULL COMMENT '预期完成日期' AFTER `finish_time`",
            'desc': '添加 expected_finish_date 字段'
        })

    # 备注
    if 'remarks' not in existing:
        alters.append({
            'sql': f"ALTER TABLE {table} ADD COLUMN `remarks` TEXT NULL COMMENT '备注' AFTER `warranty_info`",
            'desc': '添加 remarks 字段'
        })

    # 维修类型
    if 'repair_type' not in existing:
        alters.append({
            'sql': f"ALTER TABLE {table} ADD COLUMN `repair_type` ENUM('maintenance','repair','upgrade') DEFAULT 'repair' COMMENT '维修类型' AFTER `remarks`",
            'desc': '添加 repair_type 字段'
        })

    for alter in alters:
        try:
            res = execute_update(alter['sql'])
            if res['success']:
                logger.info(f"✅ {alter['desc']}")
            else:
                logger.warning(f"⚠️ 执行失败：{alter['desc']} - {res.get('error')}")
        except Exception as e:
            logger.error(f"❌ 执行异常：{alter['desc']} - {str(e)}")


def _get_schema_version():
    try:
        res = execute_query("SELECT version FROM schema_version LIMIT 1")
        if res['success'] and res['data']:
            return int(res['data'][0].get('version') or 0)
        return 0
    except Exception:
        return 0

def _set_schema_version(ver: int):
    try:
        execute_update("CREATE TABLE IF NOT EXISTS schema_version (version INT NOT NULL)")
        cur = execute_query("SELECT COUNT(*) AS c FROM schema_version")
        if cur['success'] and cur['data'] and cur['data'][0]['c'] > 0:
            execute_update("UPDATE schema_version SET version=%s", (ver,))
        else:
            execute_update("INSERT INTO schema_version (version) VALUES (%s)", (ver,))
    except Exception:
        pass

def run():
    """执行轻量迁移"""
    try:
        _ensure_equipment_table()
        _ensure_equipment_repair_table()
        _ensure_equipment_repair_columns()
        _ensure_reservations_columns()
        _ensure_laboratories_manager()
        _ensure_courses_lab_fields()
        _ensure_consumables_tables()
            try:
                current_ver = _get_schema_version()
                # 仅当版本落后时才创建/更新触发器和存储过程
                if current_ver < 1:
                    from backend.database import create_triggers, create_stored_procedures
                    create_triggers()
                    create_stored_procedures()
                    _set_schema_version(1)
            except Exception as e:
                logger.warning(f"触发器/存储过程创建失败或未执行: {str(e)}")
        logger.info("数据库轻量迁移执行完成")
    except Exception as e:
        logger.error(f"数据库迁移执行失败: {str(e)}")

def _ensure_equipment_table():
    """确保 equipment 表存在关键列 warranty_date"""
    try:
        cols = set(_get_existing_columns('equipment'))
        if 'warranty_date' not in cols:
            # 若存在 warranty_expiry，重命名，否则直接添加
            res = execute_query(
                "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='equipment' AND COLUMN_NAME='warranty_expiry' LIMIT 1",
                (db_config.database,)
            )
            if res['success'] and res['data']:
                alter = "ALTER TABLE equipment CHANGE COLUMN warranty_expiry warranty_date DATE NULL AFTER purchase_date"
                r = execute_update(alter)
                if r['success']:
                    logger.info("✅ equipment.warranty_expiry 重命名为 warranty_date")
                    return
                else:
                    logger.warning(f"⚠️ 重命名 warranty_date 失败: {r.get('error')}")

            # 若存在 warranty_period（月数），先添加列，再回填
            res2 = execute_query(
                "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='equipment' AND COLUMN_NAME='warranty_period' LIMIT 1",
                (db_config.database,)
            )
            add = execute_update("ALTER TABLE equipment ADD COLUMN warranty_date DATE NULL AFTER purchase_date")
            if add['success']:
                logger.info("✅ equipment.warranty_date 列已添加")
                if res2['success'] and res2['data']:
                    fill = execute_update(
                        "UPDATE equipment SET warranty_date = CASE WHEN purchase_date IS NOT NULL AND warranty_period IS NOT NULL THEN DATE_ADD(purchase_date, INTERVAL warranty_period MONTH) ELSE warranty_date END"
                    )
                    if fill['success']:
                        logger.info("✅ warranty_date 已根据 warranty_period 回填")
                    else:
                        logger.warning(f"⚠️ 回填 warranty_date 失败: {fill.get('error')}")
            else:
                logger.warning(f"⚠️ 添加 warranty_date 失败: {add.get('error')}")
    except Exception as e:
        logger.error(f"equipment 列迁移异常: {str(e)}")

def _ensure_equipment_repair_table():
    """若缺失，则创建 equipment_repair 表"""
    try:
        exists = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='equipment_repair' LIMIT 1"
        )
        if exists['success'] and exists['data']:
            return
        create_sql = (
            "CREATE TABLE equipment_repair ("
            " id INT AUTO_INCREMENT PRIMARY KEY,"
            " equipment_id INT NOT NULL,"
            " reporter_id INT NOT NULL,"
            " repair_person VARCHAR(100),"
            " fault_description TEXT NOT NULL,"
            " repair_description TEXT,"
            " repair_cost DECIMAL(10,2),"
            " repair_status ENUM('reported','in_progress','completed','cancelled') DEFAULT 'reported',"
            " priority ENUM('low','medium','high','urgent') DEFAULT 'medium',"
            " report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            " start_time TIMESTAMP NULL,"
            " finish_time TIMESTAMP NULL,"
            " expected_finish_date DATE NULL,"
            " parts_used JSON,"
            " warranty_info TEXT,"
            " remarks TEXT,"
            " repair_type ENUM('maintenance','repair','upgrade') DEFAULT 'repair',"
            " created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            " updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            " INDEX idx_equipment_id (equipment_id),"
            " INDEX idx_repair_status (repair_status),"
            " INDEX idx_report_time (report_time)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
        )
        r = execute_update(create_sql)
        if r['success']:
            logger.info("✅ equipment_repair 表已创建")
        else:
            logger.warning(f"⚠️ 创建 equipment_repair 表失败: {r.get('error')}")
    except Exception as e:
        logger.error(f"创建 equipment_repair 表异常: {str(e)}")

def _ensure_consumables_tables():
    try:
        # consumables
        exists = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='consumables' LIMIT 1"
        )
        if not (exists['success'] and exists['data']):
            sql = (
                "CREATE TABLE consumables ("
                " id INT AUTO_INCREMENT PRIMARY KEY,"
                " name VARCHAR(100) NOT NULL,"
                " model VARCHAR(100) NOT NULL,"
                " laboratory_id INT NOT NULL,"
                " unit VARCHAR(20) NOT NULL,"
                " unit_price DECIMAL(10,2) NOT NULL DEFAULT 0,"
                " current_stock DECIMAL(12,2) NOT NULL DEFAULT 0,"
                " min_stock DECIMAL(12,2) NOT NULL DEFAULT 0,"
                " supplier VARCHAR(100),"
                " purchase_date DATE,"
                " description TEXT,"
                " status ENUM('normal','low_stock','out_of_stock') DEFAULT 'normal',"
                " usage_count INT NOT NULL DEFAULT 0,"
                " created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                " updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
                " INDEX idx_laboratory_id (laboratory_id),"
                " INDEX idx_status (status),"
                " INDEX idx_purchase_date (purchase_date)"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
            )
            r = execute_update(sql)
            if r['success']:
                logger.info("✅ consumables 表已创建")
            else:
                logger.warning(f"⚠️ 创建 consumables 表失败: {r.get('error')}")

        # consumable_usage
        exists2 = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='consumable_usage' LIMIT 1"
        )
        if not (exists2['success'] and exists2['data']):
            sql2 = (
                "CREATE TABLE consumable_usage ("
                " id INT AUTO_INCREMENT PRIMARY KEY,"
                " consumable_id INT NOT NULL,"
                " user_id INT NOT NULL,"
                " quantity DECIMAL(12,2) NOT NULL,"
                " purpose VARCHAR(200),"
                " created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                " INDEX idx_consumable_id (consumable_id),"
                " INDEX idx_created_at (created_at)"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
            )
            r2 = execute_update(sql2)
            if r2['success']:
                logger.info("✅ consumable_usage 表已创建")
            else:
                logger.warning(f"⚠️ 创建 consumable_usage 表失败: {r2.get('error')}")
    except Exception as e:
        logger.error(f"创建耗材相关表异常: {str(e)}")

def _ensure_reservations_columns():
    try:
        cols = set(_get_existing_columns('reservations'))
        if 'reservation_date' not in cols:
            has_old = execute_query(
                "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='reservations' AND COLUMN_NAME='date' LIMIT 1"
            )
            if has_old['success'] and has_old['data']:
                r = execute_update("ALTER TABLE reservations CHANGE COLUMN `date` `reservation_date` DATE NOT NULL")
                if r['success']:
                    logger.info("✅ reservations.date 重命名为 reservation_date")
                else:
                    logger.warning(f"⚠️ 重命名 reservation_date 失败: {r.get('error')}")
            else:
                r = execute_update("ALTER TABLE reservations ADD COLUMN `reservation_date` DATE NOT NULL COMMENT '预约日期' AFTER `laboratory_id`")
                if r['success']:
                    logger.info("✅ reservations.reservation_date 列已添加")
                else:
                    logger.warning(f"⚠️ 添加 reservation_date 失败: {r.get('error')}")

        cols = set(_get_existing_columns('reservations'))
        if 'equipment_ids' not in cols:
            r = execute_update("ALTER TABLE reservations ADD COLUMN `equipment_ids` VARCHAR(255) NULL COMMENT '关联设备ID列表' AFTER `participant_count`")
            if r['success']:
                logger.info("✅ reservations.equipment_ids 列已添加")
            else:
                logger.warning(f"⚠️ 添加 equipment_ids 失败: {r.get('error')}")

        idxs = execute_query(
            "SELECT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='reservations'"
        )
        existing = {row.get('INDEX_NAME') for row in (idxs['data'] or [])} if idxs['success'] else set()
        if 'idx_reservation_date' not in existing:
            r = execute_update("ALTER TABLE reservations ADD INDEX idx_reservation_date (reservation_date)")
            if r['success']:
                logger.info("✅ reservations.idx_reservation_date 索引已添加")
            else:
                logger.warning(f"⚠️ 添加 idx_reservation_date 失败: {r.get('error')}")
        if 'idx_datetime' not in existing:
            r = execute_update("ALTER TABLE reservations ADD INDEX idx_datetime (reservation_date, start_time, end_time)")
            if r['success']:
                logger.info("✅ reservations.idx_datetime 复合索引已添加")
            else:
                logger.warning(f"⚠️ 添加 idx_datetime 失败: {r.get('error')}")
    except Exception as e:
        logger.error(f"reservations 列迁移异常: {str(e)}")

def _ensure_laboratories_manager():
    try:
        cols = set(_get_existing_columns('laboratories'))
        if 'manager_id' not in cols:
            r = execute_update("ALTER TABLE laboratories ADD COLUMN `manager_id` INT NULL COMMENT '负责人用户ID' AFTER `capacity`")
            if r['success']:
                logger.info("✅ laboratories.manager_id 列已添加")
            else:
                logger.warning(f"⚠️ 添加 manager_id 失败: {r.get('error')}")
        # 索引（可选）
        idxs = execute_query(
            "SELECT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='laboratories'"
        )
        existing = {row.get('INDEX_NAME') for row in (idxs['data'] or [])} if idxs['success'] else set()
        if 'idx_manager_id' not in existing:
            r2 = execute_update("ALTER TABLE laboratories ADD INDEX idx_manager_id (manager_id)")
            if r2['success']:
                logger.info("✅ laboratories.idx_manager_id 索引已添加")
            else:
                logger.warning(f"⚠️ 添加 idx_manager_id 失败: {r2.get('error')}")
    except Exception as e:
        logger.error(f"laboratories 列迁移异常: {str(e)}")

def _ensure_courses_lab_fields():
    """为 courses 表添加 requires_lab 与 laboratory_id 字段（如缺失）"""
    try:
        cols = set(_get_existing_columns('courses'))
        alters: List[Dict[str, str]] = []
        if 'requires_lab' not in cols:
            alters.append({
                'sql': "ALTER TABLE courses ADD COLUMN `requires_lab` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否需要实验室' AFTER `semester`",
                'desc': '添加 courses.requires_lab 字段'
            })
        if 'laboratory_id' not in cols:
            alters.append({
                'sql': "ALTER TABLE courses ADD COLUMN `laboratory_id` INT NULL COMMENT '关联实验室ID' AFTER `requires_lab`",
                'desc': '添加 courses.laboratory_id 字段'
            })

        for alter in alters:
            try:
                r = execute_update(alter['sql'])
                if r['success']:
                    logger.info(f"✅ {alter['desc']}")
                else:
                    logger.warning(f"⚠️ 执行失败：{alter['desc']} - {r.get('error')}")
            except Exception as e:
                logger.error(f"❌ 执行异常：{alter['desc']} - {str(e)}")

        # 索引（可选）
        idxs = execute_query(
            "SELECT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='courses'"
        )
        existing = {row.get('INDEX_NAME') for row in (idxs['data'] or [])} if idxs['success'] else set()
        if 'idx_courses_laboratory_id' not in existing:
            r2 = execute_update("ALTER TABLE courses ADD INDEX idx_courses_laboratory_id (laboratory_id)")
            if r2['success']:
                logger.info("✅ courses.idx_courses_laboratory_id 索引已添加")
            else:
                logger.warning(f"⚠️ 添加 idx_courses_laboratory_id 失败: {r2.get('error')}")
    except Exception as e:
        logger.error(f"courses 列迁移异常: {str(e)}")
